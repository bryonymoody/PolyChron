from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RemoveStratigraphicRelationshipModel:
    """Dataclass / MVP model containing data required for removing a stratigraphic relationship between two contexts from the model"""

    context_u: str
    """The label for the origin context to be removed"""

    context_v: str
    """The label for the origin context to be removed"""

    reason: str | None = None
    """The reason the context was removed"""

    def edge_label(self) -> str:
        """Get the label representing the edge being removed

        Returns:
            The label for the edge being removed
        """

        return f"'{self.context_u}' and '{self.context_v}'"
