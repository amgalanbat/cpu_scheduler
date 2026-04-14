import os
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QLineEdit,
    QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from core.profiler import ProfilerWorker, ProfileResult

class ProfilerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._worker = None
        self._times = []
        self._cpu_samples = []
        self._mem_samples = []
        self._thread_samples = []
        self._child_samples = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # Header
        header = QLabel("Process profiler - real Python script execution")
        header.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #333;"
        )
        root.addWidget(header)

        sub = QLabel(
            "Select any .py file and watch its real CPU, memory, "
            "threads and child processes visualized live."
        )
        sub.setStyleSheet("font-size: 11px; color: #888;")
        sub.setWordWrap(True)
        root.addWidget(sub)

        # File selector
        file_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("No file selected...")
        self.path_input.setReadOnly(True)
        self.path_input.setStyleSheet(
            "padding: 5px; border: 1px solid #ddd; "
            "border-radius: 4px; font-size: 12px;"
        )
        file_row.addWidget(self.path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.setStyleSheet(
            "QPushButton { border: 1px solid #ccc; border-radius: 4px;"
            "padding: 5px 14px; font-size: 12px; }"
            "QPushButton:hover { background: #f5f5f5; }"
        )
        browse_btn.clicked.connect(self._browse)
        file_row.addWidget(browse_btn)
        root.addLayout(file_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.run_btn = QPushButton("Run and profile")
        self.run_btn.setEnabled(False)
        self.run_btn.setStyleSheet(
            "QPushButton { background: #4CAF50; color: white; "
            "padding: 7px 20px; border-radius: 4px; "
            "font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background: #45a049; }"
            "QPushButton:disabled { background: #aaa; }"
        )
        self.run_btn.clicked.connect(self._run)
        btn_row.addWidget(self.run_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(
            "QPushButton { background: #f44336; color: white; "
            "padding: 7px 20px; border-radius: 4px; "
            "font-weight: bold; font-size: 12px; }"
            "QPushButton:hover { background: #d32f2f; }"
            "QPushButton:disabled { background: #aaa; }"
        )
        self.stop_btn.clicked.connect(self._stop)
        btn_row.addWidget(self.stop_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(
            "QPushButton { border: 1px solid #ccc; border-radius: 4px;"
            "padding: 7px 20px; font-size: 12px; }"
            "QPushButton:hover { background: #f5f5f5; }"
        )
        clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        # Status bar
        self.status_label = QLabel(
            "Ready - select a Python script to profile."
        )
        self.status_label.setStyleSheet(
            "font-size: 11px; color: #555; padding: 4px 8px;"
            "background: #f5f5f5; border-radius: 4px;"
        )
        root.addWidget(self.status_label)

        # Stat cards
        stats_row = QHBoxLayout()
        self.duration_card   = self._stat_card("Duration", "-")
        self.peak_cpu_card   = self._stat_card("Peak CPU", "-")
        self.avg_cpu_card    = self._stat_card("Avg CPU", "-")
        self.peak_mem_card   = self._stat_card("Peak memory", "-")
        self.peak_thread_card = self._stat_card("Peak threads", "-")
        self.peak_child_card  = self._stat_card("Peak children", "-")
        for card in [
            self.duration_card, self.peak_cpu_card, self.avg_cpu_card,
            self.peak_mem_card, self.peak_thread_card, self.peak_child_card
        ]:
            stats_row.addWidget(card[0])
        root.addLayout(stats_row)

        # Splitter: charts on left, live tables on right
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Charts panel
        charts_widget = QWidget()
        charts_layout = QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)

        self.fig, (self.ax_cpu, self.ax_mem, self.ax_threads) = \
            plt.subplots(3, 1, figsize=(8, 6), sharex=True)
        self.fig.patch.set_facecolor("#fafafa")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        charts_layout.addWidget(self.canvas)
        splitter.addWidget(charts_widget)

        # Right panel: thread + child tables
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(8, 0, 0, 0)
        right_layout.setSpacing(8)

        thread_label = QLabel("ACTIVE THREADS")
        thread_label.setStyleSheet(
            "font-size: 10px; font-weight: bold; "
            "color: #888; letter-spacing: 1px;"
        )
        right_layout.addWidget(thread_label)

        self.thread_table = QTableWidget()
        self.thread_table.setColumnCount(2)
        self.thread_table.setHorizontalHeaderLabels(["Thread ID", "Status"])
        self.thread_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.thread_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.thread_table.setStyleSheet(
            "QTableWidget { font-size: 11px; border: 1px solid #ddd; "
            "border-radius: 4px; }"
            "QHeaderView::section { background: #f5f5f5; font-size: 10px; "
            "font-weight: bold; padding: 3px; }"
        )
        right_layout.addWidget(self.thread_table)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ddd;")
        right_layout.addWidget(line)

        child_label = QLabel("CHILD PROCESSES")
        child_label.setStyleSheet(
            "font-size: 10px; font-weight: bold; "
            "color: #888; letter-spacing: 1px;"
        )
        right_layout.addWidget(child_label)

        self.child_table = QTableWidget()
        self.child_table.setColumnCount(4)
        self.child_table.setHorizontalHeaderLabels(
            ["PID", "Name", "CPU %", "Memory MB"]
        )
        self.child_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.child_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.child_table.setStyleSheet(
            "QTableWidget { font-size: 11px; border: 1px solid #ddd; "
            "border-radius: 4px; }"
            "QHeaderView::section { background: #f5f5f5; font-size: 10px; "
            "font-weight: bold; padding: 3px; }"
        )
        right_layout.addWidget(self.child_table)

        # Explanation box
        self.explain_label = QLabel("")
        self.explain_label.setStyleSheet(
            "font-size: 11px; color: #555; padding: 8px; "
            "background: #fff8e1; border-radius: 4px; "
            "border: 1px solid #ffe082;"
        )
        self.explain_label.setWordWrap(True)
        self.explain_label.hide()
        right_layout.addWidget(self.explain_label)
        right_layout.addStretch()

        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])
        root.addWidget(splitter, stretch=1)

        self._draw_empty()

    def _stat_card(self, label: str, value: str):
        card = QWidget()
        card.setStyleSheet(
            "background: #f0f0f0; border-radius: 6px; padding: 4px;"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(
            "font-size: 10px; color: #888; font-weight: bold;"
        )
        val = QLabel(value)
        val.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #222;"
        )
        layout.addWidget(lbl)
        layout.addWidget(val)
        return card, val

    def _draw_empty(self):
        for ax in [self.ax_cpu, self.ax_mem, self.ax_threads]:
            ax.clear()
            ax.set_facecolor("#fafafa")
        self.ax_cpu.set_ylabel("CPU %", fontsize=8)
        self.ax_mem.set_ylabel("Memory MB", fontsize=8)
        self.ax_threads.set_ylabel("Threads", fontsize=8)
        self.ax_threads.set_xlabel("Time (s)", fontsize=8)
        self.ax_cpu.text(
            0.5, 0.5, "Run a script to see live profiling",
            transform=self.ax_cpu.transAxes,
            ha="center", va="center", fontsize=10, color="#aaa"
        )
        self.fig.tight_layout()
        self.canvas.draw()

    def _redraw_live(self):
        if not self._times:
            return
        for ax in [self.ax_cpu, self.ax_mem, self.ax_threads]:
            ax.clear()
            ax.set_facecolor("#fafafa")
        
        # Memory chart - remove last sample if it's a zero caused by process exit
        mem_samples = self._mem_samples
        if len(mem_samples) > 2 and mem_samples[-1] == 0:
            mem_samples = mem_samples[:-1]
            times_mem = self._times[:-1]
        else:
            times_mem = self._times

        # Thread chart - same fix
        thread_samples = self._thread_samples
        if len(thread_samples) > 2 and thread_samples[-1] == 0:
            thread_samples = thread_samples[:-1]
            times_threads = self._times[:-1]
        else:
            times_threads = self._times

        # CPU chart
        self.ax_cpu.plot(
            self._times, self._cpu_samples,
            color="#7986CB", linewidth=1.5
        )
        self.ax_cpu.fill_between(
            self._times, self._cpu_samples,
            alpha=0.15, color="#7986CB"
        )
        self.ax_cpu.set_ylabel("CPU %", fontsize=8)
        self.ax_cpu.set_ylim(bottom=0)
        if self._cpu_samples:
            reasonable_max = min(max(self._cpu_samples), 200)
            self.ax_cpu.set_ylim(0, max(reasonable_max + 10, 20))

        # Memory chart
        # self.ax_mem.plot(
        #     self._times, self._mem_samples,
        #     color="#4DB6AC", linewidth=1.5
        # )
        # self.ax_mem.fill_between(
        #     self._times, self._mem_samples,
        #     alpha=0.15, color="#4DB6AC"
        # )
        self.ax_mem.plot(times_mem, mem_samples, color="#4DB6AC", linewidth=1.5)
        self.ax_mem.fill_between(times_mem, mem_samples, alpha=0.15, color="#4DB6AC")
        self.ax_mem.set_ylabel("Memory MB", fontsize=8)
        self.ax_mem.set_ylim(bottom=0)

        # Thread count chart
        self.ax_threads.step(
            self._times, self._thread_samples,
            color="#FF8A65", linewidth=1.5, where="post"
        )
        self.ax_threads.fill_between(
            self._times, self._thread_samples,
            alpha=0.15, color="#FF8A65", step="post"
        )
        self.ax_threads.set_ylabel("Threads", fontsize=8)
        self.ax_threads.set_ylim(bottom=0)
        self.ax_threads.set_xlabel("Time (s)", fontsize=8)
        self.ax_threads.yaxis.set_major_locator(
            plt.MaxNLocator(integer=True)
        )

        self.fig.tight_layout()
        self.canvas.draw()

    def _update_thread_table(self, sample):
        self.thread_table.setRowCount(len(sample.threads))
        for row, t in enumerate(sample.threads):
            tid_item = QTableWidgetItem(str(t.thread_id))
            tid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item = QTableWidgetItem(t.status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setBackground(QColor("#E8F5E9"))
            self.thread_table.setItem(row, 0, tid_item)
            self.thread_table.setItem(row, 1, status_item)

    def _update_child_table(self, sample):
        self.child_table.setRowCount(len(sample.children))
        for row, c in enumerate(sample.children):
            values = [str(c.pid), c.name,
                      f"{c.cpu_percent}%", f"{c.memory_mb} MB"]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor("#E3F2FD"))
                self.child_table.setItem(row, col, item)

    def _update_explanation(self, sample):
        parts = []
        tc = sample.thread_count
        cc = sample.child_count

        if tc > 1:
            parts.append(
                f"This script is using {tc} threads - it is doing "
                f"concurrent work within a single process."
            )
        elif tc == 1:
            parts.append(
                "This script uses 1 thread - it is running sequentially "
                "with no concurrency."
            )

        if cc > 0:
            parts.append(
                f"{cc} child process(es) detected - the script spawned "
                f"separate OS processes (e.g. via multiprocessing)."
            )

        if sample.cpu_percent > 80:
            parts.append(
                "CPU usage is high - the script is doing intensive "
                "computation right now."
            )
        elif sample.cpu_percent < 5 and tc >= 1:
            parts.append(
                "CPU usage is low - the script may be waiting on I/O, "
                "sleeping, or blocked."
            )

        if parts:
            self.explain_label.setText(" ".join(parts))
            self.explain_label.show()
        else:
            self.explain_label.hide()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Python script", "", "Python files (*.py)"
        )
        if path:
            self.path_input.setText(path)
            self.run_btn.setEnabled(True)
            self.status_label.setText(
                f"Selected: {os.path.basename(path)}"
            )

    def _run(self):
        path = self.path_input.text()
        if not path:
            return

        self._times = []
        self._cpu_samples = []
        self._mem_samples = []
        self._thread_samples = []
        self._child_samples = []
        self._draw_empty()
        self._reset_cards()
        self.thread_table.setRowCount(0)
        self.child_table.setRowCount(0)
        self.explain_label.hide()

        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText(
            f"Profiling {os.path.basename(path)}..."
        )

        # self._worker = ProfilerWorker(path, interval=0.1)
        self._worker = ProfilerWorker(path, interval=0.2)
        self._worker.sample_ready.connect(self._on_sample)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _stop(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Stopped.")

    def _clear(self):
        self._stop()
        self._times = []
        self._cpu_samples = []
        self._mem_samples = []
        self._thread_samples = []
        self._child_samples = []
        self._reset_cards()
        self._draw_empty()
        self.thread_table.setRowCount(0)
        self.child_table.setRowCount(0)
        self.explain_label.hide()
        self.status_label.setText(
            "Ready - select a Python script to profile."
        )

    def _on_sample(self, elapsed, cpu, mem, threads, children):
        self._times.append(elapsed)
        self._cpu_samples.append(cpu)
        self._mem_samples.append(mem)
        self._thread_samples.append(threads)
        self._child_samples.append(children)
        self._redraw_live()

        # Update live tables from latest worker sample
        if self._worker and self._worker.samples:
            latest = self._worker.samples[-1]
            self._update_thread_table(latest)
            self._update_child_table(latest)
            self._update_explanation(latest)

        self.status_label.setText(
            f"Profiling... {elapsed:.1f}s | CPU: {cpu:.1f}% | "
            f"Mem: {mem:.1f} MB | Threads: {threads} | "
            f"Children: {children}"
        )

    def _on_finished(self, result: ProfileResult):
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.duration_card[1].setText(f"{result.duration}s")
        self.peak_cpu_card[1].setText(f"{result.peak_cpu}%")
        self.avg_cpu_card[1].setText(f"{result.avg_cpu}%")
        self.peak_mem_card[1].setText(f"{result.peak_memory_mb} MB")
        self.peak_thread_card[1].setText(str(result.peak_threads))
        self.peak_child_card[1].setText(str(result.peak_children))
        exit_str = "OK" if result.exit_code == 0 else f"exit {result.exit_code}"
        self.status_label.setText(
            f"Done - {os.path.basename(result.script_path)} | "
            f"Duration: {result.duration}s | "
            f"Peak CPU: {result.peak_cpu}% | "
            f"Peak threads: {result.peak_threads} | {exit_str}"
        )

    def _on_error(self, message: str):
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"Error: {message}")

    def _reset_cards(self):
        for card in [
            self.duration_card, self.peak_cpu_card, self.avg_cpu_card,
            self.peak_mem_card, self.peak_thread_card, self.peak_child_card
        ]:
            card[1].setText(" - ")