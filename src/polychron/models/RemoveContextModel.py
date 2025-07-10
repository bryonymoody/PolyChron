from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RemoveContextModel:
    """Dataclass / MVP model containing data required for removing a context from the model"""

    context: str
    """The label for the Context to be removed from the model"""

    reason: str | None = None
    """The reason the context was removed"""
