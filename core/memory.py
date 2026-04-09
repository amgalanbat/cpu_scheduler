from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class AllocationAlgorithm(Enum):
    FIRST_FIT = "First Fit"
    BEST_FIT  = "Best Fit"
    WORST_FIT = "Worst Fit"

@dataclass
class MemoryBlock:
    start: int
    size: int
    pid: Optional[int] = None
    process_name: Optional[str] = None
    is_free: bool = True

@dataclass
class MemoryAllocationResult:
    success: bool
    block_index: int = -1
    message: str = ""

class MemoryManager:
    def __init__(self, total_memory: int = 256):
        self.total_memory = total_memory
        self.blocks: List[MemoryBlock] = [
            MemoryBlock(start=0, size=total_memory)
        ]

    def allocate(self, pid: int, name: str, size: int,
                 algorithm: AllocationAlgorithm) -> MemoryAllocationResult:
        if algorithm == AllocationAlgorithm.FIRST_FIT:
            return self._first_fit(pid, name, size)
        elif algorithm == AllocationAlgorithm.BEST_FIT:
            return self._best_fit(pid, name, size)
        elif algorithm == AllocationAlgorithm.WORST_FIT:
            return self._worst_fit(pid, name, size)
        return MemoryAllocationResult(False, message="Unknown algorithm")

    def deallocate(self, pid: int) -> bool:
        freed = False
        for block in self.blocks:
            if block.pid == pid:
                block.pid = None
                block.process_name = None
                block.is_free = True
                freed = True
        if freed:
            self._merge_free_blocks()
        return freed

    def _first_fit(self, pid: int, name: str,
                   size: int) -> MemoryAllocationResult:
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                return self._split_and_allocate(i, pid, name, size)
        return MemoryAllocationResult(False, message="No suitable block found")

    def _best_fit(self, pid: int, name: str,
                  size: int) -> MemoryAllocationResult:
        best_idx = -1
        best_size = float("inf")
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size < best_size:
                    best_size = block.size
                    best_idx = i
        if best_idx == -1:
            return MemoryAllocationResult(False, message="No suitable block found")
        return self._split_and_allocate(best_idx, pid, name, size)

    def _worst_fit(self, pid: int, name: str,
                   size: int) -> MemoryAllocationResult:
        worst_idx = -1
        worst_size = -1
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                if block.size > worst_size:
                    worst_size = block.size
                    worst_idx = i
        if worst_idx == -1:
            return MemoryAllocationResult(False, message="No suitable block found")
        return self._split_and_allocate(worst_idx, pid, name, size)

    def _split_and_allocate(self, idx: int, pid: int, name: str,
                             size: int) -> MemoryAllocationResult:
        block = self.blocks[idx]
        if block.size > size:
            remainder = MemoryBlock(
                start=block.start + size,
                size=block.size - size
            )
            self.blocks.insert(idx + 1, remainder)
        block.size = size
        block.pid = pid
        block.process_name = name
        block.is_free = False
        return MemoryAllocationResult(True, block_index=idx)

    def _merge_free_blocks(self):
        merged = []
        for block in self.blocks:
            if merged and merged[-1].is_free and block.is_free:
                merged[-1].size += block.size
            else:
                merged.append(block)
        self.blocks = merged

    def get_fragmentation(self) -> float:
        free_blocks = [b for b in self.blocks if b.is_free]
        if not free_blocks:
            return 0.0
        largest_free = max(b.size for b in free_blocks)
        total_free = sum(b.size for b in free_blocks)
        if total_free == 0:
            return 0.0
        return round((1 - largest_free / total_free) * 100, 1)

    def get_usage(self) -> float:
        used = sum(b.size for b in self.blocks if not b.is_free)
        return round((used / self.total_memory) * 100, 1)

    def reset(self):
        self.blocks = [MemoryBlock(start=0, size=self.total_memory)]