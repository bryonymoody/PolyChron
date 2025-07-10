import pytest

from polychron.models.RemoveContextModel import RemoveContextModel


class TestRemoveContextModel:
    """Unit Tests for the `models.RemoveContextModel` class which contains data related to users removing a context from the model"""

    def test_init(self):
        """Test the constructor default values and explicit setting of initial values"""
        obj = RemoveContextModel("foo")
        assert obj.context == "foo"
        assert obj.reason is None

        obj = RemoveContextModel("foo", "bar")
        assert obj.context == "foo"
        assert obj.reason == "bar"

        # Assert that an excetpion is raised if no arguments provided
        with pytest.raises(TypeError):
            obj = RemoveContextModel()

    def test_context(self):
        """Test getting and setting the context"""
        obj = RemoveContextModel("foo")
        assert obj.context == "foo"

        obj.context = "bar"
        assert obj.context == "bar"

    def test_reason(self):
        """Test getting and setting the reason"""
        obj = RemoveContextModel("foo")
        assert obj.reason is None

        obj.reason = "bar"
        assert obj.reason == "bar"
