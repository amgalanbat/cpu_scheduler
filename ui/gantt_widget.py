import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from core.process import Process

PROCESS_COLORS = [
    "#7986CB", "#4DB6AC", "#FF8A65", "#FFD54F",
    "#A1887F", "#90A4AE", "#F06292", "#AED581",
]

class GanttWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)

        self.fig, self.ax = plt.subplots(figsize=(10, 3))
        self.fig.patch.set_facecolor("#fafafa")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self._color_map = {}
        self._timeline = []
        self._processes = []
        self._draw_empty()

    def _draw_empty(self):
        self.ax.clear()
        self.ax.set_facecolor("#fafafa")
        self.ax.set_xlabel("Time (ticks)", fontsize=9)
        self.ax.set_yticks([])
        self.ax.text(
            0.5, 0.5, "Run a simulation to see the Gantt chart",
            transform=self.ax.transAxes,
            ha="center", va="center",
            fontsize=10, color="#aaa"
        )
        self.canvas.draw()

    def prepare(self, processes: list[Process]):
        """Call before simulation starts to assign colors."""
        self._processes = processes
        self._timeline = []
        self._color_map = {}
        for i, p in enumerate(processes):
            self._color_map[p.pid] = PROCESS_COLORS[i % len(PROCESS_COLORS)]
        self.ax.clear()
        self.ax.set_facecolor("#fafafa")
        self.canvas.draw()

    def add_tick(self, tick_event: dict):
        """Add one tick event and redraw."""
        self._timeline.append(tick_event)
        self._redraw()

    def show_final(self, timeline: list[dict], processes: list[Process]):
        """Draw the complete final Gantt chart."""
        self._timeline = timeline
        self._processes = processes
        self._redraw(final=True)

    def _redraw(self, final: bool = False):
        self.ax.clear()
        self.ax.set_facecolor("#fafafa")
        self.fig.patch.set_facecolor("#fafafa")

        if not self._timeline:
            return

        # Get unique process names in order of appearance
        pid_order = []
        seen = set()
        for event in self._timeline:
            if event["pid"] not in seen:
                pid_order.append(event["pid"])
                seen.add(event["pid"])

        pid_to_y = {pid: i for i, pid in enumerate(pid_order)}
        name_map = {e["pid"]: e["name"] for e in self._timeline}

        # Draw each tick as a bar
        for event in self._timeline:
            pid = event["pid"]
            tick = event["tick"]
            y = pid_to_y[pid]
            color = self._color_map.get(pid, "#ccc")
            self.ax.barh(
                y, 1, left=tick, height=0.5,
                color=color, edgecolor="white",
                linewidth=0.5, align="center"
            )

        # Y axis labels
        self.ax.set_yticks(list(pid_to_y.values()))
        self.ax.set_yticklabels(
            [name_map[pid] for pid in pid_to_y],
            fontsize=9
        )

        # X axis
        if self._timeline:
            max_tick = max(e["tick"] for e in self._timeline) + 1
            self.ax.set_xlim(0, max_tick)
            self.ax.set_xticks(range(0, max_tick + 1))
            self.ax.tick_params(axis="x", labelsize=8)

        self.ax.set_xlabel("Time (ticks)", fontsize=9)
        self.ax.set_ylim(-0.5, len(pid_to_y) - 0.5)
        self.ax.invert_yaxis()

        # Legend
        legend_patches = [
            mpatches.Patch(color=self._color_map.get(pid, "#ccc"), label=name_map[pid])
            for pid in pid_to_y
        ]
        self.ax.legend(
            handles=legend_patches,
            loc="upper right",
            fontsize=8,
            framealpha=0.7
        )

        title = "Gantt chart — final" if final else "Gantt chart — live"
        self.ax.set_title(title, fontsize=9, color="#555")
        self.fig.tight_layout()
        self.canvas.draw()

    def reset(self):
        self._timeline = []
        self._processes = []
        self._color_map = {}
        self._draw_empty()