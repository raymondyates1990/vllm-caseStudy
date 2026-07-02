"""Mini-project A: FreeBlockQueue (study module M3.1).

Implement an O(1) free-list allocator for KV cache blocks, mirroring vLLM's
`FreeKVCacheBlockQueue` in `vllm/v1/core/kv_cache_utils.py` (doubly-linked list
with sentinel head/tail). No GPU, pure Python.

Fill in every `# TODO`, then run:  python 01_free_block_queue.py
Success prints: ALL TESTS PASSED
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Block:
    block_id: int
    ref_cnt: int = 0
    prev: Optional["Block"] = None
    next: Optional["Block"] = None


class FreeBlockQueue:
    """Doubly-linked free list with sentinel head/tail for O(1) pop/append/remove.

    Invariant: `num_free` always equals the number of blocks currently linked
    between the head and tail sentinels.
    """

    def __init__(self, num_blocks: int):
        self.blocks = [Block(i) for i in range(num_blocks)]
        self._head = Block(-1)  # sentinel (not a real block)
        self._tail = Block(-1)  # sentinel
        self._head.next = self._tail
        self._tail.prev = self._head
        self.num_free = 0
        for b in self.blocks:
            self.append(b)

    def append(self, block: Block) -> None:
        """Insert `block` just before the tail sentinel. O(1)."""
        # TODO: link block between self._tail.prev and self._tail,
        #       then increment self.num_free.
        raise NotImplementedError

    def popleft(self) -> Block:
        """Remove and return the block right after the head sentinel (oldest free). O(1)."""
        # TODO: detach self._head.next, repair the neighbours' links,
        #       decrement self.num_free, clear the block's prev/next, return it.
        raise NotImplementedError

    def remove(self, block: Block) -> None:
        """Remove an arbitrary already-linked `block` from the free list. O(1)."""
        # TODO: splice block.prev <-> block.next, decrement self.num_free,
        #       clear the block's prev/next.
        raise NotImplementedError


def _test():
    q = FreeBlockQueue(3)                 # free: [0, 1, 2]
    assert q.num_free == 3

    b0 = q.popleft()
    assert b0.block_id == 0 and q.num_free == 2

    b1 = q.popleft()
    assert b1.block_id == 1 and q.num_free == 1   # free: [2]

    q.append(b0)                          # free: [2, 0]
    assert q.num_free == 2

    b2 = q.popleft()
    assert b2.block_id == 2 and q.num_free == 1   # FIFO: 2 comes before the returned 0

    q.remove(b0)                          # remove arbitrary; free: []
    assert q.num_free == 0

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    _test()
