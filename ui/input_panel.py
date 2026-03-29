from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QButtonGroup, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.process import Process, ProcessType
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QSlider
)

class InputPanel(QWidget):
    compare_requested = pyqtSignal(int)
    process_added = pyqtSignal(Process)
    process_removed = pyqtSignal(int)
    run_requested = pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(280)
        self._pid_counter = 1
        self._processes = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Algorithm selection
        layout.addWidget(self._section_label("Algorithm"))
        self.algo_combo = QComboBox()
        # self.algo_combo.addItems(["FCFS", "SJF", "RR"])
        self.algo_combo.addItems(["FCFS", "SJF", "SRT", "RR", "PP"])
        self.algo_combo.currentTextChanged.connect(self._on_algo_changed)
        layout.addWidget(self.algo_combo)

        # Quantum (RR only)
        self.quantum_widget = QWidget()
        q_layout = QHBoxLayout(self.quantum_widget)
        q_layout.setContentsMargins(0, 0, 0, 0)
        q_layout.addWidget(QLabel("Quantum:"))
        self.quantum_spin = QSpinBox()
        self.quantum_spin.setRange(1, 20)
        self.quantum_spin.setValue(2)
        q_layout.addWidget(self.quantum_spin)
        self.quantum_widget.setVisible(False)
        layout.addWidget(self.quantum_widget)

        layout.addWidget(self._divider())

        # Process inputs
        layout.addWidget(self._section_label("Add process / thread"))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name (e.g. P1)")
        layout.addWidget(self.name_input)

        row1 = QHBoxLayout()
        self.burst_spin = QSpinBox()
        self.burst_spin.setRange(1, 100)
        self.burst_spin.setPrefix("Burst: ")
        self.arrival_spin = QSpinBox()
        self.arrival_spin.setRange(0, 100)
        self.arrival_spin.setPrefix("Arrival: ")
        row1.addWidget(self.burst_spin)
        row1.addWidget(self.arrival_spin)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(0, 100)
        self.priority_spin.setPrefix("Priority: ")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Process", "Thread"])
        row2.addWidget(self.priority_spin)
        row2.addWidget(self.type_combo)
        layout.addLayout(row2)

        add_btn = QPushButton("+ Add")
        add_btn.clicked.connect(self._add_process)
        layout.addWidget(add_btn)

        layout.addWidget(self._divider())

        # Process list
        layout.addWidget(self._section_label("Processes"))
        self.process_list = QListWidget()
        self.process_list.setMaximumHeight(200)
        layout.addWidget(self.process_list)

        remove_btn = QPushButton("Remove selected")
        remove_btn.clicked.connect(self._remove_process)
        layout.addWidget(remove_btn)

        layout.addWidget(self._divider())

        # Speed control
        layout.addWidget(self._section_label("Simulation speed"))
        speed_row = QHBoxLayout()
        slow_label = QLabel("Slow")
        slow_label.setStyleSheet("font-size: 11px; color: #888;")
        fast_label = QLabel("Fast")
        fast_label.setStyleSheet("font-size: 11px; color: #888;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        speed_row.addWidget(slow_label)
        speed_row.addWidget(self.speed_slider)
        speed_row.addWidget(fast_label)
        layout.addLayout(speed_row)
        layout.addWidget(self._divider())

        # Run button
        self.run_btn = QPushButton("Run simulation")
        self.compare_btn = QPushButton("Compare all algorithms")
        self.compare_btn.setStyleSheet(
            "QPushButton { background: #1565C0; color: white; "
            "padding: 8px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background: #0D47A1; }"
        )
        self.compare_btn.clicked.connect(
            lambda: self.compare_requested.emit(self.quantum_spin.value())
        )
        layout.addWidget(self.compare_btn)
        self.run_btn.setStyleSheet(
            "QPushButton { background: #4CAF50; color: white; "
            "padding: 8px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background: #45a049; }"
            "QPushButton:disabled { background: #aaa; }"
        )
        self.run_btn.clicked.connect(self._on_run)
        layout.addWidget(self.run_btn)

        layout.addStretch()

    def _section_label(self, text):
        label = QLabel(text.upper())
        label.setStyleSheet("font-size: 10px; color: #888; font-weight: bold; letter-spacing: 1px;")
        return label

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ddd;")
        return line

    def _on_algo_changed(self, algo):
        self.quantum_widget.setVisible(algo == "RR")

    def _add_process(self):
        name = self.name_input.text().strip() or f"P{self._pid_counter}"
        ptype = ProcessType.PROCESS if self.type_combo.currentText() == "Process" else ProcessType.THREAD

        p = Process(
            pid=self._pid_counter,
            name=name,
            burst_time=self.burst_spin.value(),
            arrival_time=self.arrival_spin.value(),
            priority=self.priority_spin.value(),
            process_type=ptype,
        )
        self._pid_counter += 1
        self._processes.append(p)

        label = (f"{p.name} | burst={p.burst_time} "
                 f"arr={p.arrival_time} pri={p.priority} "
                 f"[{p.process_type.value}]")
        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, p.pid)
        self.process_list.addItem(item)

        self.name_input.clear()
        self.process_added.emit(p)

    def _remove_process(self):
        row = self.process_list.currentRow()
        if row >= 0:
            item = self.process_list.takeItem(row)
            pid = item.data(Qt.ItemDataRole.UserRole)
            self._processes = [p for p in self._processes if p.pid != pid]
            self.process_removed.emit(pid)

    def _on_run(self):
        if not self._processes:
            return
        algo = self.algo_combo.currentText()
        quantum = self.quantum_spin.value()
        self.run_requested.emit(algo, quantum)

    def get_processes(self):
        return list(self._processes)

    def clear(self):
        self._processes = []
        self._pid_counter = 1
        self.process_list.clear()

    def get_speed(self) -> float:
        # Slider 1=slow(0.8s) to 10=fast(0.05s)
        val = self.speed_slider.value()
        return round(0.8 - (val - 1) * (0.75 / 9), 3)