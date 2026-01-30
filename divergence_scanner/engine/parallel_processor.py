"""Parallel processing helpers."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, List, Any


class ParallelProcessor:
    def __init__(self, max_workers: int = 8) -> None:
        self.max_workers = max_workers

    def run(self, func: Callable[[Any], Any], items: Iterable[Any]) -> List[Any]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(func, items))
