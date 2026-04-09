from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class StatCard(QWidget):
    def __init__(self, label: str):
        super().__init__()
        self.setStyleSheet(
            "background: #f0f0f0; border-radius: 6px; padding: 4px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        self.label = QLabel(label.upper())
        self.label.setStyleSheet("font-size: 10px; color: #888; font-weight: bold;")

        self.value = QLabel("-")
        self.value.setStyleSheet("font-size: 22px; font-weight: bold; color: #222;")

        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def set_value(self, val: str):
        self.value.setText(str(val))


class StatsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(90)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        self.tick_card = StatCard("Current tick")
        self.cpu_card = StatCard("CPU usage")
        self.running_card = StatCard("Running")
        self.remaining_card = StatCard("Remaining")

        for card in [self.tick_card, self.cpu_card, self.running_card, self.remaining_card]:
            layout.addWidget(card)

    def update(self, tick: int, cpu: float, running: str, remaining: int):
        self.tick_card.set_value(str(tick))
        self.cpu_card.set_value(f"{cpu:.0f}%")
        self.running_card.set_value(running)
        self.remaining_card.set_value(str(remaining))

    def reset(self):
        for card in [self.tick_card, self.cpu_card, self.running_card, self.remaining_card]:
            card.set_value("-")