from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class RetrievedMemory:
    passage: str
    """
    The (expanded) passage text
    """

    distance: float
    """
    A distance metric between the retrieved passage and the query
    """

    confidence: Optional[float]
    """
    A confidence metric between 0 and 1. Not all memories support this, so it may be None
    """

    metadata: Any
    """
    Metadata associated with the retrieved text
    """


class BaseTextMemory(ABC):
    """
    Abstract base class for text memories.
    """

    @abstractmethod
    def add_text(self, text: str, metadata: Optional[Any] = None, rewrite: bool = False,
                 rewrite_context: Optional[str] = None):
        pass

    @abstractmethod
    def retrieve_multiple(self, queries: List[str], k: int, rewrite: bool = False, show_progress_bar: bool = False,
                          **kwargs) -> List[List[RetrievedMemory]]:
        pass

    def retrieve(self, query: str, k: int, rewrite: bool = False, **kwargs) -> List[RetrievedMemory]:
        multi_result = self.retrieve_multiple([query], k=k, rewrite=rewrite, **kwargs)
        return multi_result[0]

    @abstractmethod
    def clear(self):
        pass


