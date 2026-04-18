from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QColor
from core.process import Process
from core.constants import ProcessState

QUEUE_COLORS = {
    "ready":   ("#e8eaf6", "#3949ab"),
    "running": ("#e8f5e9", "#2e7d32"),
    "waiting": ("#fff8e1", "#f57f17"),
    "finished":("#f5f5f5", "#757575"),
}

class QueueBox(QWidget):
    def __init__(self, title: str, color_key: str):
        super().__init__()
        self._color_key = color_key
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        self.setStyleSheet("border: 1px solid #ddd; border-radius: 6px;")

        header = QLabel(title.upper())
        header.setStyleSheet("font-size: 10px; color: #888; font-weight: bold; letter-spacing: 1px; border: none;")
        layout.addWidget(header)

        self.list = QListWidget()
        self.list.setStyleSheet("border: none; font-size: 12px;")
        layout.addWidget(self.list)

    def set_processes(self, processes: list[Process]):
        self.list.clear()
        bg, fg = QUEUE_COLORS[self._color_key]
        for p in processes:
            item = QListWidgetItem(f"{p.name}  (burst {p.burst_time})")
            item.setBackground(QColor(bg))
            item.setForeground(QColor(fg))
            self.list.addItem(item)


class QueueTables(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(160)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        self.ready_box = QueueBox("Ready queue", "ready")
        self.running_box = QueueBox("Running", "running")
        self.waiting_box = QueueBox("Finished", "finished")

        for box in [self.ready_box, self.running_box, self.waiting_box]:
            layout.addWidget(box)

    def update_queues(self, processes: list[Process]):
        ready = [p for p in processes if p.state == ProcessState.READY]
        running = [p for p in processes if p.state == ProcessState.RUNNING]
        finished = [p for p in processes if p.state == ProcessState.FINISHED]

        self.ready_box.set_processes(ready)
        self.running_box.set_processes(running)
        self.waiting_box.set_processes(finished)

    def reset(self):
        for box in [self.ready_box, self.running_box, self.waiting_box]:
            box.list.clear()