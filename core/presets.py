from core.process import Process
from core.constants import ProcessType

PRESETS = {
    "CPU-bound": {
        "description": "Long heavy computation tasks. Tests raw throughput. All processes need lots of CPU time.",
        "processes": [
            {"name": "CPU-1", "burst": 12, "arrival": 0,  "priority": 2},
            {"name": "CPU-2", "burst": 10, "arrival": 1,  "priority": 2},
            {"name": "CPU-3", "burst": 14, "arrival": 2,  "priority": 2},
            {"name": "CPU-4", "burst": 8,  "arrival": 3,  "priority": 2},
            {"name": "CPU-5", "burst": 11, "arrival": 4,  "priority": 2},
        ]
    },

    "I/O-bound": {
        "description": "Short bursts with frequent arrivals. Tests responsiveness. Simulates processes that do quick work then wait.",
        "processes": [
            {"name": "IO-1", "burst": 2, "arrival": 0,  "priority": 2},
            {"name": "IO-2", "burst": 3, "arrival": 1,  "priority": 2},
            {"name": "IO-3", "burst": 1, "arrival": 2,  "priority": 2},
            {"name": "IO-4", "burst": 2, "arrival": 3,  "priority": 2},
            {"name": "IO-5", "burst": 3, "arrival": 4,  "priority": 2},
            {"name": "IO-6", "burst": 1, "arrival": 5,  "priority": 2},
        ]
    },

    "Mixed": {
        "description": "Short interactive tasks mixed with long batch jobs. Tests whether short tasks get good response time alongside heavy ones.",
        "processes": [
            {"name": "Batch-1", "burst": 15, "arrival": 0, "priority": 3},
            {"name": "Inter-1", "burst": 2,  "arrival": 1, "priority": 1},
            {"name": "Batch-2", "burst": 12, "arrival": 2, "priority": 3},
            {"name": "Inter-2", "burst": 3,  "arrival": 3, "priority": 1},
            {"name": "Batch-3", "burst": 10, "arrival": 5, "priority": 3},
            {"name": "Inter-3", "burst": 2,  "arrival": 6, "priority": 1},
        ]
    },

    "Real-time": {
        "description": "Tasks with different urgency levels. Tests priority scheduling. Critical tasks must run first.",
        "processes": [
            {"name": "RT-critical", "burst": 3,  "arrival": 0, "priority": 1},
            {"name": "RT-high",     "burst": 5,  "arrival": 1, "priority": 2},
            {"name": "RT-medium",   "burst": 8,  "arrival": 2, "priority": 3},
            {"name": "RT-low",      "burst": 12, "arrival": 3, "priority": 4},
            {"name": "RT-background","burst": 15, "arrival": 4, "priority": 5},
        ]
    },

    "Overload": {
        "description": "Too many processes arriving at once. Tests starvation. Low priority processes may never get CPU time.",
        "processes": [
            {"name": "P1",  "burst": 8,  "arrival": 0, "priority": 1},
            {"name": "P2",  "burst": 6,  "arrival": 0, "priority": 2},
            {"name": "P3",  "burst": 10, "arrival": 1, "priority": 1},
            {"name": "P4",  "burst": 4,  "arrival": 1, "priority": 3},
            {"name": "P5",  "burst": 12, "arrival": 2, "priority": 2},
            {"name": "P6",  "burst": 5,  "arrival": 2, "priority": 1},
            {"name": "P7",  "burst": 9,  "arrival": 3, "priority": 4},
            {"name": "P8",  "burst": 7,  "arrival": 3, "priority": 2},
            {"name": "P9",  "burst": 3,  "arrival": 4, "priority": 5},
            {"name": "P10", "burst": 11, "arrival": 4, "priority": 3},
        ]
    },

    "Sparse": {
        "description": "Processes arrive with large gaps between them. CPU sits idle between bursts. Shows low CPU utilization.",
        "processes": [
            {"name": "S1", "burst": 3, "arrival": 0,  "priority": 2},
            {"name": "S2", "burst": 4, "arrival": 15, "priority": 2},
            {"name": "S3", "burst": 2, "arrival": 30, "priority": 2},
            {"name": "S4", "burst": 5, "arrival": 45, "priority": 2},
            {"name": "S5", "burst": 3, "arrival": 60, "priority": 2},
        ]
    },
}


def get_preset_names():
    return list(PRESETS.keys())


def get_preset_description(name):
    if name not in PRESETS:
        return ""
    return PRESETS[name]["description"]


def load_preset(name):
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}")

    processes = []
    preset_data = PRESETS[name]["processes"]

    for i, p in enumerate(preset_data):
        process = Process(
            pid=i + 1,
            name=p["name"],
            burst_time=p["burst"],
            arrival_time=p["arrival"],
            priority=p["priority"],
            process_type=ProcessType.PROCESS,
        )
        processes.append(process)

    return processes