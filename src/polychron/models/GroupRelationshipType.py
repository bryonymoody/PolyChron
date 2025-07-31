from __future__ import annotations

from enum import Enum
from typing import Any


class GroupRelationshipType(Enum):
    """Enum for the possible types of group relationships"""

    ABUTTING = "abutting"
    GAP = "gap"
    OVERLAP = "overlap"

    def __str__(self) -> str:
        """Returns the string representation of the GroupRelationshipType Enum

        Returns:
            the string representation of the RelationShip type Enum
        """
        return str(self.value)

    def __eq__(self, other: str | "GroupRelationshipType" | Any) -> bool:
        """Custom equality operator

        Parameters:
            other: The other object to compare to

        Returns:
            boolean indicating if the objects are consider equal.
        """
        if isinstance(other, GroupRelationshipType):
            return self is other
        elif isinstance(other, str):
            return self.value == other
        # Otherwise fall back to the other object
        return NotImplemented

    @classmethod
    def from_string(cls, value: str) -> "GroupRelationshipType":
        """Converts a string into a GroupRelationshipType enum

        Parameters:
            value: The string value to convert

        Returns:
            The GroupRelationshipType enum instance

        Raises:
            ValueError: if the provided string does not match the enum member
        """
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"'{value}' is not a valid GroupRelationshipType")
