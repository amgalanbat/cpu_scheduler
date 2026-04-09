from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QStatusBar, QPushButton,
    QTabWidget
)
from ui.input_panel import InputPanel
from ui.stats_panel import StatsPanel
from ui.queue_tables import QueueTables
from ui.gantt_widget import GanttWidget
from ui.results_table import ResultsTable
from ui.starvation_panel import StarvationPanel
from ui.memory_widget import MemoryWidget
from ui.comparison_window import ComparisonWindow
from ui.profiler_widget import ProfilerWidget

from db.repository import init_db, save_run
from ui.history_window import HistoryWindow

from core.worker import SimulationWorker
from core.process import ProcessState
from core.starvation import get_starving_processes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduling Simulator")
        self.setMinimumSize(1100, 700)
        self._worker = None
        self._tick_count = 0
        self._last_result = None
        self._last_algo = None
        self._last_quantum = None
        init_db()
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left sidebar
        self.input_panel = InputPanel()
        self.input_panel.process_added.connect(self._on_process_added)
        self.input_panel.run_requested.connect(self._on_run)
        self.input_panel.compare_requested.connect(self._on_compare)

        # Tab widget for right side
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab { padding: 8px 20px; font-size: 12px; }
            QTabBar::tab:selected { font-weight: bold; border-bottom: 2px solid #4CAF50; }
        """)

        # --- Tab 1: CPU Simulation ---
        cpu_tab = QWidget()
        cpu_layout = QVBoxLayout(cpu_tab)
        cpu_layout.setContentsMargins(0, 12, 12, 12)
        cpu_layout.setSpacing(10)

        reset_btn = QPushButton("Reset")
        reset_btn.setFixedWidth(80)
        reset_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #ccc;"
            "border-radius: 4px; padding: 4px 10px; font-size: 12px; color: #555; }"
            "QPushButton:hover { background: #f5f5f5; }"
        )
        reset_btn.clicked.connect(self._on_reset)
        top_row = QHBoxLayout()
        top_row.addStretch()
        top_row.addWidget(reset_btn)
        cpu_layout.addLayout(top_row)

        history_btn = QPushButton("History")
        history_btn.setFixedWidth(80)
        history_btn.setStyleSheet(
            "QPushButton { background: transparent; border: 1px solid #ccc;"
            "border-radius: 4px; padding: 4px 10px; font-size: 12px; color: #555; }"
            "QPushButton:hover { background: #f5f5f5; }"
        )
        history_btn.clicked.connect(self._on_history)
        top_row.addWidget(history_btn)
        top_row.addWidget(reset_btn)

        self.stats_panel = StatsPanel()
        self.queue_tables = QueueTables()
        self.starvation_panel = StarvationPanel()
        self.gantt = GanttWidget()
        self.results_table = ResultsTable()

        cpu_layout.addWidget(self.stats_panel)
        cpu_layout.addWidget(self.queue_tables)
        cpu_layout.addWidget(self.starvation_panel)
        cpu_layout.addWidget(self.gantt, stretch=1)
        cpu_layout.addWidget(self.results_table)

        # --- Tab 2: Memory ---
        self.memory_widget = MemoryWidget()

        self.tabs.addTab(cpu_tab, "CPU Scheduling")
        self.tabs.addTab(self.memory_widget, "Memory Allocation")

        root.addWidget(self.input_panel)
        root.addWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready - add processes to begin")

        # --- Tab 3 : Profiler ---
        self.profiler_widget = ProfilerWidget()
        self.tabs.addTab(cpu_tab, "CPU Scheduling")
        self.tabs.addTab(self.memory_widget, "Memory Allocation")
        self.tabs.addTab(self.profiler_widget, "Process Profiler")

    def _on_process_added(self, process):
        self.status.showMessage(
            f"Added {process.process_type.value} '{process.name}' "
            f"(burst={process.burst_time}, arrival={process.arrival_time})"
        )

    def _on_run(self, algo, quantum):

        self._last_algo = algo
        self._last_quantum = quantum

        processes = self.input_panel.get_processes()
        if not processes:
            return

        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()

        self._tick_count = 0
        self.stats_panel.reset()
        self.queue_tables.reset()
        self.gantt.prepare(processes)
        self.results_table.reset()
        self.starvation_panel.reset()

        speed = self.input_panel.get_speed()
        self._worker = SimulationWorker(
            processes, algo, quantum, speed=speed
        )
        self._worker.tick_ready.connect(self._on_tick)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

        self.status.showMessage(f"Running {algo} simulation...")

    def _on_tick(self, event, processes):
        self._tick_count += 1
        total = event["tick"] + 1
        cpu = (self._tick_count / total) * 100 if total > 0 else 0
        remaining = sum(
            p.remaining_time for p in processes
            if p.state != ProcessState.FINISHED
        )
        self.stats_panel.update(
            tick=event["tick"],
            cpu=cpu,
            running=event["name"],
            remaining=remaining
        )
        self.queue_tables.update_queues(processes)
        self.gantt.add_tick(event)
        starving = get_starving_processes(processes)
        algo = self.input_panel.algo_combo.currentText()
        self.starvation_panel.update_warnings(
            starving, aging_active="Aging" in algo
        )

    def _on_finished(self, result):
        self.gantt.show_final(result.timeline, result.processes)
        self.results_table.show_results(
            result.processes,
            result.avg_waiting_time,
            result.avg_turnaround_time,
            result.cpu_utilization
        )
        # Save to database
        if self._last_algo:
            run_id = save_run(self._last_algo, self._last_quantum, result)
            self.status.showMessage(
                f"Done - avg wait: {result.avg_waiting_time} ticks | "
                f"avg turnaround: {result.avg_turnaround_time} ticks | "
                f"CPU: {result.cpu_utilization}% | Run #{run_id} saved"
            )

    def _on_reset(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        self.input_panel.clear()
        self.stats_panel.reset()
        self.queue_tables.reset()
        self.gantt.reset()
        self.results_table.reset()
        self.starvation_panel.reset()
        self.status.showMessage("Reset - add processes to begin")

    def _on_compare(self, quantum):
        processes = self.input_panel.get_processes()
        if not processes:
            self.status.showMessage("Add processes before comparing.")
            return
        self._comparison_window = ComparisonWindow(processes, quantum)
        self._comparison_window.show()

    def _on_history(self):
        self._history_window = HistoryWindow()
        self._history_window.show()