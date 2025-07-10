import pytest

from polychron.models.RemoveStratigraphicRelationshipModel import RemoveStratigraphicRelationshipModel


class TestRemoveStratigraphicRelationshipModel:
    """Unit Tests for the `models.RemoveStratigraphicRelationshipModel` class which contains data related to users removing a context from the model"""

    def test_init(self):
        """Test the constructor default values and explicit setting of initial values"""
        obj = RemoveStratigraphicRelationshipModel("foo", "bar")
        assert obj.context_u == "foo"
        assert obj.context_v == "bar"
        assert obj.reason is None

        obj = RemoveStratigraphicRelationshipModel("foo", "bar", "baz")
        assert obj.context_u == "foo"
        assert obj.context_v == "bar"
        assert obj.reason == "baz"

        # Assert that an excetpion is raised if no arguments provided
        with pytest.raises(TypeError):
            obj = RemoveStratigraphicRelationshipModel()

        # Assert that an excetpion is raised if 1 argument is provided
        with pytest.raises(TypeError):
            obj = RemoveStratigraphicRelationshipModel("foo")

    def test_context_u(self):
        """Test getting and setting the context"""
        obj = RemoveStratigraphicRelationshipModel("foo", "bar")
        assert obj.context_u == "foo"

        obj.context_u = "baz"
        assert obj.context_u == "baz"

    def test_context_v(self):
        """Test getting and setting the context"""
        obj = RemoveStratigraphicRelationshipModel("foo", "bar")
        assert obj.context_v == "bar"

        obj.context_v = "baz"
        assert obj.context_v == "baz"

    def test_reason(self):
        """Test getting and setting the reason"""
        obj = RemoveStratigraphicRelationshipModel("foo", "bar")
        assert obj.reason is None

        obj.reason = "baz"
        assert obj.reason == "baz"

    def test_edge_label(self):
        """Test getting the string describing the edge is as expected"""
        obj = RemoveStratigraphicRelationshipModel("foo", "bar")
        assert obj.edge_label() == "'foo' and 'bar'"
