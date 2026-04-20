from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from core.process import Process

class ResultsTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 12)
        layout.setSpacing(6)

        header = QLabel("FINAL RESULTS")
        header.setStyleSheet("font-size: 10px; color: #888; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Name", "Type", "Burst", "Arrival",
            "Start", "Finish", "Waiting", 
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { font-size: 12px; border: 1px solid #ddd; border-radius: 6px; }
            QHeaderView::section { background: #f5f5f5; font-size: 11px;
                                   font-weight: bold; padding: 4px; border: none;
                                   border-bottom: 1px solid #ddd; }
        """)
        self.table.setFixedHeight(160)
        layout.addWidget(self.table)

        # Summary row
        self.summary = QLabel("")
        self.summary.setStyleSheet("font-size: 11px; color: #555; padding: 2px 0;")
        layout.addWidget(self.summary)

        self.hide()

    def show_results(self, processes: list[Process], avg_wait: float,
                     avg_turnaround: float, cpu: float):
        self.table.setRowCount(len(processes))

        ROW_COLORS = [
            "#EDE7F6", "#E8F5E9", "#FFF3E0",
            "#E3F2FD", "#FCE4EC", "#F3E5F5",
            "#E0F7FA", "#FFFDE7",
        ]

        for row, p in enumerate(processes):
            bg = QColor(ROW_COLORS[row % len(ROW_COLORS)])
            values = [
                p.name,
                p.process_type.value if hasattr(p.process_type, "value") else p.process_type,
                str(p.burst_time),
                str(p.arrival_time),
                str(p.start_time),
                str(p.finish_time),
                str(p.waiting_time),
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(bg)
                self.table.setItem(row, col, item)

        self.summary.setText(
            f"Avg waiting: {avg_wait} ticks   |   "
            f"Avg turnaround: {avg_turnaround} ticks   |   "
            f"CPU utilization: {cpu}%"
        )
        self.show()

    def reset(self):
        self.table.setRowCount(0)
        self.summary.setText("")
        self.hide()