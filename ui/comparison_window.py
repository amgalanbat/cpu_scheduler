import copy
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from core.process import Process
from core.scheduler import Scheduler

PROCESS_COLORS = [
    "#7986CB", "#4DB6AC", "#FF8A65", "#FFD54F",
    "#A1887F", "#90A4AE", "#F06292", "#AED581",
]

ALGO_COLORS = {
    "FCFS": "#7986CB",
    "SJF":  "#4DB6AC",
    "SRT":  "#FF8A65",
    "RR":   "#FFD54F",
    "PP":   "#F06292",
}

class AlgoGanttCard(QFrame):
    """A single algorithm's Gantt chart card."""
    def __init__(self, algo_name: str):
        super().__init__()
        self.algo_name = algo_name
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame { border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.title = QLabel(algo_name)
        self.title.setStyleSheet(
            f"font-weight: bold; font-size: 13px; "
            f"color: {ALGO_COLORS.get(algo_name, '#333')}; border: none;"
        )
        layout.addWidget(self.title)

        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.fig.patch.set_facecolor("#fafafa")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumHeight(140)
        layout.addWidget(self.canvas)

        self.stat_label = QLabel("")
        self.stat_label.setStyleSheet("font-size: 11px; color: #666; border: none;")
        layout.addWidget(self.stat_label)

    def render(self, timeline: list[dict], processes: list[Process],
               avg_wait: float, avg_turnaround: float, cpu: float):
        color_map = {}
        for i, p in enumerate(processes):
            color_map[p.pid] = PROCESS_COLORS[i % len(PROCESS_COLORS)]

        self.ax.clear()
        self.ax.set_facecolor("#fafafa")
        self.fig.patch.set_facecolor("#fafafa")

        pid_order, seen = [], set()
        for e in timeline:
            if e["pid"] not in seen:
                pid_order.append(e["pid"])
                seen.add(e["pid"])

        pid_to_y = {pid: i for i, pid in enumerate(pid_order)}
        name_map = {e["pid"]: e["name"] for e in timeline}

        for event in timeline:
            self.ax.barh(
                pid_to_y[event["pid"]], 1,
                left=event["tick"], height=0.5,
                color=color_map.get(event["pid"], "#ccc"),
                edgecolor="white", linewidth=0.4,
                align="center"
            )

        self.ax.set_yticks(list(pid_to_y.values()))
        self.ax.set_yticklabels([name_map[p] for p in pid_order], fontsize=8)
        if timeline:
            max_tick = max(e["tick"] for e in timeline) + 1
            self.ax.set_xlim(0, max_tick)
            self.ax.set_xticks(range(0, max_tick + 1))
        self.ax.tick_params(axis="x", labelsize=7)
        self.ax.set_xlabel("Ticks", fontsize=8)
        self.ax.invert_yaxis()
        self.fig.tight_layout(pad=0.5)
        self.canvas.draw()

        self.stat_label.setText(
            f"Avg wait: {avg_wait}  |  Avg turnaround: {avg_turnaround}  |  CPU: {cpu}%"
        )


class ComparisonWindow(QWidget):
    def __init__(self, processes: list[Process], quantum: int = 2):
        super().__init__()
        self.setWindowTitle("Algorithm comparison")
        self.setMinimumSize(1200, 800)
        self._processes = processes
        self._quantum = quantum
        self._results = {}
        self._build_ui()
        self._run_all()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QLabel("Side-by-side algorithm comparison")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        root.addWidget(header)

        sub = QLabel(
            f"Same {len(self._processes)} processes - "
            "each algorithm runs independently"
        )
        sub.setStyleSheet("font-size: 12px; color: #888;")
        root.addWidget(sub)

        # Scrollable Gantt grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        gantt_container = QWidget()
        self.gantt_layout = QHBoxLayout(gantt_container)
        self.gantt_layout.setSpacing(10)
        scroll.setWidget(gantt_container)
        root.addWidget(scroll, stretch=1)

        # Comparison table
        table_label = QLabel("SUMMARY COMPARISON")
        table_label.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #888; letter-spacing: 1px;"
        )
        root.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Algorithm", "Avg waiting", "Avg turnaround",
            "CPU utilization", "Total time"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setFixedHeight(180)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 12px; border: 1px solid #ddd; border-radius: 6px; }
            QHeaderView::section { background: #f5f5f5; font-size: 11px;
                font-weight: bold; padding: 4px; border: none;
                border-bottom: 1px solid #ddd; }
        """)
        root.addWidget(self.table)

    def _run_all(self):
        algorithms = ["FCFS", "SJF", "SRT", "RR", "PP"]
        cards = []

        for algo in algorithms:
            # Deep copy processes so each algo gets a fresh set
            fresh = [copy.deepcopy(p) for p in self._processes]
            try:
                scheduler = Scheduler(algorithm=algo, quantum=self._quantum)
                for p in fresh:
                    scheduler.add_process(p)
                result = scheduler.run()
                self._results[algo] = result

                card = AlgoGanttCard(algo)
                card.render(
                    result.timeline, fresh,
                    result.avg_waiting_time,
                    result.avg_turnaround_time,
                    result.cpu_utilization
                )
                self.gantt_layout.addWidget(card)
                cards.append((algo, result))
            except Exception as e:
                error_card = AlgoGanttCard(algo)
                error_card.stat_label.setText(f"Error: {e}")
                self.gantt_layout.addWidget(error_card)

        self._populate_table(cards)

    def _populate_table(self, cards: list):
        if not cards:
            return

        # Find best values for highlighting
        best_wait = min(r.avg_waiting_time for _, r in cards)
        best_turnaround = min(r.avg_turnaround_time for _, r in cards)
        best_cpu = max(r.cpu_utilization for _, r in cards)

        self.table.setRowCount(len(cards))
        for row, (algo, result) in enumerate(cards):
            values = [
                algo,
                f"{result.avg_waiting_time} ticks",
                f"{result.avg_turnaround_time} ticks",
                f"{result.cpu_utilization}%",
                f"{result.total_time} ticks",
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Highlight best values in green
                if col == 1 and result.avg_waiting_time == best_wait:
                    item.setBackground(QColor("#C8E6C9"))
                elif col == 2 and result.avg_turnaround_time == best_turnaround:
                    item.setBackground(QColor("#C8E6C9"))
                elif col == 3 and result.cpu_utilization == best_cpu:
                    item.setBackground(QColor("#C8E6C9"))

                self.table.setItem(row, col, item)