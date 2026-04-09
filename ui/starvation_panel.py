from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from core.process import Process

class StarvationPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            "background: #FFF3E0; border: 1px solid #FFB74D; border-radius: 6px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        title = QLabel("STARVATION WARNINGS")
        title.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #E65100; "
            "letter-spacing: 1px; border: none;"
        )
        layout.addWidget(title)

        self.message = QLabel("No starvation detected.")
        self.message.setStyleSheet("font-size: 12px; color: #BF360C; border: none;")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)

        self.hide()

    def update_warnings(self, starving: list[Process], aging_active: bool = False):
        if not starving:
            self.hide()
            return

        names = ", ".join(p.name for p in starving)
        aging_note = " Aging is actively boosting their priority." if aging_active else ""
        self.message.setText(
            f"Process(es) {names} have been waiting too long and are starving!{aging_note}"
        )
        self.show()

    def reset(self):
        self.message.setText("No starvation detected.")
        self.hide()