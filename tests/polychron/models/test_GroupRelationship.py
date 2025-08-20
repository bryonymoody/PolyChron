from __future__ import annotations

from typing import Any

import pytest

from polychron.models.GroupRelationship import GroupRelationship


class TestGroupRelationship:
    """Unit Tests for the `models.GroupRelationship` which is an enum for the different types"""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("abutting", GroupRelationship.ABUTTING),
            ("gap", GroupRelationship.GAP),
            ("overlap", GroupRelationship.OVERLAP),
            ("foo", None),
            ("GaP", None),
        ],
    )
    def test_init(self, value: str, expected: GroupRelationship | None):
        """Test the constructor default values and explicit setting of initial values"""
        # If an object was expected to be returned, check it was
        if expected is not None:
            obj = GroupRelationship(value)
            assert obj == expected
        # If an exception should have been raised, check it was
        else:
            with pytest.raises(ValueError, match=r"is not a valid GroupRelationship"):
                GroupRelationship(value)

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
        obj = GroupRelationship(value)
        str_obj = str(obj)
        assert str_obj == value

    @pytest.mark.parametrize(
        ("a", "b", "expected"),
        [
            # Check ABUTTING matches or does not match in both directions
            (GroupRelationship.ABUTTING, GroupRelationship.ABUTTING, True),
            (GroupRelationship.ABUTTING, "abutting", True),
            (GroupRelationship.ABUTTING, GroupRelationship.GAP, False),
            (GroupRelationship.ABUTTING, "gap", False),
            ("abutting", GroupRelationship.ABUTTING, True),
            (GroupRelationship.GAP, GroupRelationship.ABUTTING, False),
            ("gap", GroupRelationship.ABUTTING, False),
            # Check gap matches against obj and str versions in one direction
            (GroupRelationship.GAP, GroupRelationship.GAP, True),
            (GroupRelationship.GAP, "gap", True),
            # Check overlap matches against obj and str versions in one direction
            (GroupRelationship.OVERLAP, GroupRelationship.OVERLAP, True),
            (GroupRelationship.OVERLAP, "overlap", True),
        ],
    )
    def test_eq(self, a: GroupRelationship | str | Any, b: GroupRelationship | str | Any, expected: bool):
        """Test comparison to objects behaves as expected"""
        result = a == b
        assert expected == result

    def test_hash(self):
        """Test that the Group Relationship enum can be hashed, by using as a dictionary key"""
        d = {}
        d[GroupRelationship.ABUTTING] = "abutting"
        assert GroupRelationship.ABUTTING in d
        d[GroupRelationship.GAP] = "gap"
        assert GroupRelationship.GAP in d
        d[GroupRelationship.OVERLAP] = "overlap"
        assert GroupRelationship.OVERLAP in d

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("abutting", GroupRelationship.ABUTTING),
            ("gap", GroupRelationship.GAP),
            ("overlap", GroupRelationship.OVERLAP),
            ("foo", None),
            ("GaP", None),
        ],
    )
    def test_from_string(self, value: str, expected: GroupRelationship | None):
        """Test the explicitly calling from_string"""
        # If an object was expected to be returned, check it was
        if expected is not None:
            obj = GroupRelationship(value)
            assert obj == expected
        # If an exception should have been raised, check it was
        else:
            with pytest.raises(ValueError, match=r"is not a valid GroupRelationship"):
                GroupRelationship(value)
