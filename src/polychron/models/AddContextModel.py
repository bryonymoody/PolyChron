from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AddContextModel:
    """Dataclass / MVP model containing data required for adding a new context to the model"""

    label: str | None = None
    """The label for the new Context to be added to the model"""
