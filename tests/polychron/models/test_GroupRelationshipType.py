from __future__ import annotations

from typing import Any

import pytest

from polychron.models.GroupRelationshipType import GroupRelationshipType


class TestGroupRelationshipType:
    """Unit Tests for the `models.GroupRelationshipType` which is an enum for the different types"""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("abutting", GroupRelationshipType.ABUTTING),
            ("gap", GroupRelationshipType.GAP),
            ("overlap", GroupRelationshipType.OVERLAP),
            ("foo", None),
            ("GaP", None),
        ],
    )
    def test_init(self, value: str, expected: GroupRelationshipType | None):
        """Test the constructor default values and explicit setting of initial values"""
        # If an object was expected to be returned, check it was
        if expected is not None:
            obj = GroupRelationshipType(value)
            assert obj == expected
        # If an exception should have been raised, check it was
        else:
            with pytest.raises(ValueError, match=r"is not a valid GroupRelationshipType"):
                GroupRelationshipType(value)

    @pytest.mark.parametrize(
        ("value"),
        [
            ("abutting"),
            ("gap"),
            ("overlap"),
        ],
    )
    def test_str(self, value: str):
        """test conversion from enum to string"""
        # If an object was expected to be returned, check it was
        obj = GroupRelationshipType(value)
        str_obj = str(obj)
        assert str_obj == value

    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            # Check ABUTTING matches or does not match in both directions
            (GroupRelationshipType.ABUTTING, GroupRelationshipType.ABUTTING, True),
            (GroupRelationshipType.ABUTTING, "abutting", True),
            (GroupRelationshipType.ABUTTING, GroupRelationshipType.GAP, False),
            (GroupRelationshipType.ABUTTING, "gap", False),
            ("abutting", GroupRelationshipType.ABUTTING, True),
            (GroupRelationshipType.GAP, GroupRelationshipType.ABUTTING, False),
            ("gap", GroupRelationshipType.ABUTTING, False),
            # Check gap matches against obj and str versions in one direction
            (GroupRelationshipType.GAP, GroupRelationshipType.GAP, True),
            (GroupRelationshipType.GAP, "gap", True),
            # Check overlap matches against obj and str versions in one direction
            (GroupRelationshipType.OVERLAP, GroupRelationshipType.OVERLAP, True),
            (GroupRelationshipType.OVERLAP, "overlap", True),
        ],
    )
    def test_eq(self, a: GroupRelationshipType | str | Any, b: GroupRelationshipType | str | Any, expected: bool):
        """Test comparison to objects behaves as expected"""
        result = a == b
        assert expected == result

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("abutting", GroupRelationshipType.ABUTTING),
            ("gap", GroupRelationshipType.GAP),
            ("overlap", GroupRelationshipType.OVERLAP),
            ("foo", None),
            ("GaP", None),
        ],
    )
    def test_from_string(self, value: str, expected: GroupRelationshipType | None):
        """Test the explicitly calling from_string"""
        # If an object was expected to be returned, check it was
        if expected is not None:
            obj = GroupRelationshipType(value)
            assert obj == expected
        # If an exception should have been raised, check it was
        else:
            with pytest.raises(ValueError, match=r"is not a valid GroupRelationshipType"):
                GroupRelationshipType(value)
