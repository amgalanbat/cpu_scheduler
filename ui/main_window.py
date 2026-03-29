from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QStatusBar, QPushButton
)
from ui.input_panel import InputPanel
from ui.stats_panel import StatsPanel
from ui.queue_tables import QueueTables
from ui.gantt_widget import GanttWidget
from ui.results_table import ResultsTable
from core.worker import SimulationWorker
from core.process import ProcessState
from ui.comparison_window import ComparisonWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduling Simulator")
        self.setMinimumSize(1100, 700)
        self._worker = None
        self._tick_count = 0
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

        # Right side
        main_area = QWidget()
        self.main_layout = QVBoxLayout(main_area)
        self.main_layout.setContentsMargins(0, 12, 12, 12)
        self.main_layout.setSpacing(10)

        # Reset button (top right)
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
        self.main_layout.addLayout(top_row)

        self.stats_panel = StatsPanel()
        self.queue_tables = QueueTables()
        self.gantt = GanttWidget()
        self.results_table = ResultsTable()

        self.main_layout.addWidget(self.stats_panel)
        self.main_layout.addWidget(self.queue_tables)
        self.main_layout.addWidget(self.gantt, stretch=1)
        self.main_layout.addWidget(self.results_table)

        root.addWidget(self.input_panel)
        root.addWidget(main_area)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready — add processes to begin")

    def _on_process_added(self, process):
        self.status.showMessage(
            f"Added {process.process_type.value} '{process.name}' "
            f"(burst={process.burst_time}, arrival={process.arrival_time})"
        )

    def _on_run(self, algo, quantum):
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

        speed = self.input_panel.get_speed()
        self._worker = SimulationWorker(processes, algo, quantum, speed=speed)
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

    def _on_finished(self, result):
        self.gantt.show_final(result.timeline, result.processes)
        self.results_table.show_results(
            result.processes,
            result.avg_waiting_time,
            result.avg_turnaround_time,
            result.cpu_utilization
        )
        self.status.showMessage(
            f"Done — avg wait: {result.avg_waiting_time} ticks | "
            f"avg turnaround: {result.avg_turnaround_time} ticks | "
            f"CPU: {result.cpu_utilization}%"
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
        self.status.showMessage("Reset — add processes to begin")

    def _on_compare(self, quantum):
        processes = self.input_panel.get_processes()
        if not processes:
            self.status.showMessage("Add processes before comparing.")
            return
        self._comparison_window = ComparisonWindow(processes, quantum)
        self._comparison_window.show()