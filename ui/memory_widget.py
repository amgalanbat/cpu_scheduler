import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QComboBox, QFrame,
    QScrollArea
)
from PyQt6.QtCore import Qt
from core.memory import MemoryManager, AllocationAlgorithm, MemoryBlock
from typing import List
import random

BLOCK_COLORS = [
    "#7986CB", "#4DB6AC", "#FF8A65", "#FFD54F",
    "#A1887F", "#90A4AE", "#F06292", "#AED581",
    "#4FC3F7", "#CE93D8",
]

class MemoryCanvas(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.fig, self.ax = plt.subplots(figsize=(10, 3))
        self.fig.patch.set_facecolor("#fafafa")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumHeight(180)
        layout.addWidget(self.canvas)
        self._pid_colors = {}
        self._color_index = 0

    def get_color(self, pid: int) -> str:
        if pid not in self._pid_colors:
            self._pid_colors[pid] = BLOCK_COLORS[
                self._color_index % len(BLOCK_COLORS)
            ]
            self._color_index += 1
        return self._pid_colors[pid]

    def render(self, blocks: List[MemoryBlock], total: int):
        self.ax.clear()
        self.ax.set_facecolor("#fafafa")
        self.fig.patch.set_facecolor("#fafafa")

        y = 0.3
        height = 0.4

        for block in blocks:
            x = block.start / total
            w = block.size / total

            if block.is_free:
                color = "#e0e0e0"
                label = f"Free\n{block.size}"
                text_color = "#999"
            else:
                color = self.get_color(block.pid)
                label = f"{block.process_name}\n{block.size}"
                text_color = "#333"

            self.ax.barh(
                y, w, left=x, height=height,
                color=color, edgecolor="white",
                linewidth=1.5, align="center"
            )

            if w > 0.04:
                self.ax.text(
                    x + w / 2, y, label,
                    ha="center", va="center",
                    fontsize=8, color=text_color,
                    fontweight="bold"
                )

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_xticks([i / 10 for i in range(11)])
        self.ax.set_xticklabels(
            [str(int(i * total / 10)) for i in range(11)],
            fontsize=8
        )
        self.ax.set_yticks([])
        self.ax.set_xlabel("Memory address", fontsize=9)
        self.ax.set_title("Memory layout", fontsize=9, color="#555")
        self.fig.tight_layout()
        self.canvas.draw()

    def reset(self):
        self._pid_colors = {}
        self._color_index = 0
        self.ax.clear()
        self.canvas.draw()


class MemoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._manager = MemoryManager(total_memory=256)
        self._pid_counter = 1
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Top controls
        controls = QHBoxLayout()

        # Total memory
        controls.addWidget(QLabel("Total memory (units):"))
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(64, 1024)
        self.memory_spin.setValue(256)
        self.memory_spin.setSingleStep(64)
        self.memory_spin.valueChanged.connect(self._on_memory_changed)
        controls.addWidget(self.memory_spin)

        controls.addWidget(QLabel("  Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["First Fit", "Best Fit", "Worst Fit"])
        controls.addWidget(self.algo_combo)

        controls.addStretch()

        reset_btn = QPushButton("Reset memory")
        reset_btn.setStyleSheet(
            "QPushButton { border: 1px solid #ccc; border-radius: 4px; "
            "padding: 4px 12px; font-size: 12px; }"
            "QPushButton:hover { background: #f5f5f5; }"
        )
        reset_btn.clicked.connect(self._on_reset)
        controls.addWidget(reset_btn)
        root.addLayout(controls)

        # Memory canvas
        self.canvas = MemoryCanvas()
        root.addWidget(self.canvas)

        # Stats row
        stats_row = QHBoxLayout()
        self.usage_label = QLabel("Usage: 0%")
        self.usage_label.setStyleSheet("font-size: 12px; color: #555;")
        self.frag_label = QLabel("Fragmentation: 0%")
        self.frag_label.setStyleSheet("font-size: 12px; color: #e53935;")
        self.blocks_label = QLabel("Blocks: 1 free")
        self.blocks_label.setStyleSheet("font-size: 12px; color: #555;")
        stats_row.addWidget(self.usage_label)
        stats_row.addWidget(QLabel(" | "))
        stats_row.addWidget(self.frag_label)
        stats_row.addWidget(QLabel(" | "))
        stats_row.addWidget(self.blocks_label)
        stats_row.addStretch()
        root.addLayout(stats_row)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #ddd;")
        root.addWidget(line)

        # Allocation controls
        alloc_row = QHBoxLayout()
        alloc_row.addWidget(QLabel("Process name:"))
        from PyQt6.QtWidgets import QLineEdit
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. P1")
        self.name_input.setFixedWidth(80)
        alloc_row.addWidget(self.name_input)

        alloc_row.addWidget(QLabel("  Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 256)
        self.size_spin.setValue(32)
        alloc_row.addWidget(self.size_spin)

        alloc_btn = QPushButton("Allocate")
        alloc_btn.setStyleSheet(
            "QPushButton { background: #4CAF50; color: white; "
            "padding: 5px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background: #45a049; }"
        )
        alloc_btn.clicked.connect(self._on_allocate)
        alloc_row.addWidget(alloc_btn)

        alloc_row.addWidget(QLabel("  Free PID:"))
        self.free_spin = QSpinBox()
        self.free_spin.setRange(1, 999)
        alloc_row.addWidget(self.free_spin)

        free_btn = QPushButton("Deallocate")
        free_btn.setStyleSheet(
            "QPushButton { background: #f44336; color: white; "
            "padding: 5px 16px; border-radius: 4px; font-weight: bold; }"
            "QPushButton:hover { background: #d32f2f; }"
        )
        free_btn.clicked.connect(self._on_deallocate)
        alloc_row.addWidget(free_btn)
        alloc_row.addStretch()
        root.addLayout(alloc_row)

        # Log
        self.log = QLabel("Ready - allocate memory to processes above.")
        self.log.setStyleSheet(
            "font-size: 11px; color: #555; "
            "background: #f9f9f9; padding: 6px; border-radius: 4px;"
        )
        self.log.setWordWrap(True)
        root.addWidget(self.log)

        root.addStretch()

    def _get_algorithm(self) -> AllocationAlgorithm:
        text = self.algo_combo.currentText()
        return {
            "First Fit": AllocationAlgorithm.FIRST_FIT,
            "Best Fit":  AllocationAlgorithm.BEST_FIT,
            "Worst Fit": AllocationAlgorithm.WORST_FIT,
        }[text]

    def _on_allocate(self):
        name = self.name_input.text().strip() or f"P{self._pid_counter}"
        size = self.size_spin.value()
        algo = self._get_algorithm()

        result = self._manager.allocate(
            self._pid_counter, name, size, algo
        )

        if result.success:
            self.log.setText(
                f"Allocated {size} units to '{name}' (PID {self._pid_counter}) "
                f"using {algo.value}."
            )
            self._pid_counter += 1
            self.name_input.clear()
        else:
            self.log.setText(
                f"Allocation failed for '{name}' ({size} units): {result.message}"
            )
        self._refresh()

    def _on_deallocate(self):
        pid = self.free_spin.value()
        success = self._manager.deallocate(pid)
        if success:
            self.log.setText(f"Deallocated memory for PID {pid}.")
        else:
            self.log.setText(f"No allocation found for PID {pid}.")
        self._refresh()

    def _on_memory_changed(self, value):
        self._manager = MemoryManager(total_memory=value)
        self._pid_counter = 1
        self.log.setText(f"Memory reset to {value} units.")
        self._refresh()

    def _on_reset(self):
        self._manager.reset()
        self._pid_counter = 1
        self.canvas.reset()
        self.log.setText("Memory reset.")
        self._refresh()

    def _refresh(self):
        self.canvas.render(self._manager.blocks, self._manager.total_memory)
        free_blocks = sum(1 for b in self._manager.blocks if b.is_free)
        used_blocks = sum(1 for b in self._manager.blocks if not b.is_free)
        self.usage_label.setText(f"Usage: {self._manager.get_usage()}%")
        self.frag_label.setText(
            f"Fragmentation: {self._manager.get_fragmentation()}%"
        )
        self.blocks_label.setText(
            f"Blocks: {used_blocks} used, {free_blocks} free"
        )