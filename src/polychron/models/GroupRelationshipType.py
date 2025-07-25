from enum import Enum


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
