from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QSplitter, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from db.repository import get_all_runs, get_run_with_processes, delete_run

class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation history")
        self.setMinimumSize(900, 600)
        self._build_ui()
        self._load_runs()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Header
        header_row = QHBoxLayout()
        header = QLabel("Simulation history")
        header.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #333;"
        )
        header_row.addWidget(header)
        header_row.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(
            "QPushButton { border: 1px solid #ccc; border-radius: 4px; "
            "padding: 5px 14px; font-size: 12px; }"
            "QPushButton:hover { background: #f5f5f5; }"
        )
        refresh_btn.clicked.connect(self._load_runs)
        header_row.addWidget(refresh_btn)

        delete_btn = QPushButton("Delete selected")
        delete_btn.setStyleSheet(
            "QPushButton { background: #f44336; color: white; "
            "border-radius: 4px; padding: 5px 14px; font-size: 12px; }"
            "QPushButton:hover { background: #d32f2f; }"
        )
        delete_btn.clicked.connect(self._delete_selected)
        header_row.addWidget(delete_btn)
        root.addLayout(header_row)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # Runs table
        runs_widget = QWidget()
        runs_layout = QVBoxLayout(runs_widget)
        runs_layout.setContentsMargins(0, 0, 0, 0)

        runs_label = QLabel("SIMULATION RUNS")
        runs_label.setStyleSheet(
            "font-size: 10px; font-weight: bold; "
            "color: #888; letter-spacing: 1px;"
        )
        runs_layout.addWidget(runs_label)

        self.runs_table = QTableWidget()
        self.runs_table.setColumnCount(7)
        self.runs_table.setHorizontalHeaderLabels([
            "ID", "Algorithm", "Processes",
            "Avg wait", "Avg turnaround",
            "CPU util", "Date"
        ])
        self.runs_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.runs_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.runs_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.runs_table.setAlternatingRowColors(True)
        self.runs_table.setStyleSheet("""
            QTableWidget { font-size: 12px; border: 1px solid #ddd;
                           border-radius: 6px; }
            QHeaderView::section { background: #f5f5f5; font-size: 11px;
                font-weight: bold; padding: 4px; border: none;
                border-bottom: 1px solid #ddd; }
        """)
        self.runs_table.itemSelectionChanged.connect(
            self._on_run_selected
        )
        runs_layout.addWidget(self.runs_table)
        splitter.addWidget(runs_widget)

        # Process detail table
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(0, 8, 0, 0)

        detail_label = QLabel("PROCESS DETAILS FOR SELECTED RUN")
        detail_label.setStyleSheet(
            "font-size: 10px; font-weight: bold; "
            "color: #888; letter-spacing: 1px;"
        )
        detail_layout.addWidget(detail_label)

        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(8)
        self.detail_table.setHorizontalHeaderLabels([
            "Name", "Type", "Burst", "Arrival",
            "Priority", "Start", "Finish", "Waiting"
        ])
        self.detail_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.detail_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.detail_table.setAlternatingRowColors(True)
        self.detail_table.setStyleSheet("""
            QTableWidget { font-size: 12px; border: 1px solid #ddd;
                           border-radius: 6px; }
            QHeaderView::section { background: #f5f5f5; font-size: 11px;
                font-weight: bold; padding: 4px; border: none;
                border-bottom: 1px solid #ddd; }
        """)
        detail_layout.addWidget(self.detail_table)
        splitter.addWidget(detail_widget)

        splitter.setSizes([300, 200])
        root.addWidget(splitter, stretch=1)

        # Summary bar
        self.summary_label = QLabel(
            "Select a run to see process details."
        )
        self.summary_label.setStyleSheet(
            "font-size: 11px; color: #555; padding: 6px 8px; "
            "background: #f5f5f5; border-radius: 4px;"
        )
        root.addWidget(self.summary_label)

    def _load_runs(self):
        runs = get_all_runs()
        self.runs_table.setRowCount(len(runs))
        self._run_ids = []

        ALGO_COLORS = {
            "FCFS": "#E3F2FD", "SJF": "#E8F5E9",
            "SRT": "#FFF3E0", "RR": "#F3E5F5",
            "PP": "#FCE4EC", "PP+Aging": "#E0F7FA"
        }

        for row, run in enumerate(runs):
            self._run_ids.append(run.id)
            bg = QColor(ALGO_COLORS.get(run.algorithm, "#FAFAFA"))
            values = [
                str(run.id),
                run.algorithm,
                str(run.process_count),
                f"{run.avg_waiting_time} ticks",
                f"{run.avg_turnaround} ticks",
                f"{run.cpu_utilization}%",
                run.created_at.strftime("%Y-%m-%d %H:%M")
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(bg)
                self.runs_table.setItem(row, col, item)

        self.summary_label.setText(
            f"{len(runs)} simulation run(s) saved."
        )

    def _on_run_selected(self):
        row = self.runs_table.currentRow()
        if row < 0 or row >= len(self._run_ids):
            return

        run_id = self._run_ids[row]
        run = get_run_with_processes(run_id)
        if not run:
            return

        self.detail_table.setRowCount(len(run.processes))
        for r, p in enumerate(run.processes):
            values = [
                p.name, p.process_type,
                str(p.burst_time), str(p.arrival_time),
                str(p.priority), str(p.start_time),
                str(p.finish_time), str(p.waiting_time)
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.detail_table.setItem(r, col, item)

        self.summary_label.setText(
            f"Run #{run.id} - {run.algorithm} | "
            f"Avg wait: {run.avg_waiting_time} ticks | "
            f"Avg turnaround: {run.avg_turnaround} ticks | "
            f"CPU: {run.cpu_utilization}%"
        )

    def _delete_selected(self):
        row = self.runs_table.currentRow()
        if row < 0 or row >= len(self._run_ids):
            return
        run_id = self._run_ids[row]
        delete_run(run_id)
        self._load_runs()
        self.detail_table.setRowCount(0)
        self.summary_label.setText("Run deleted.")