from polychron.models.AddContextModel import AddContextModel


class TestAddContextModel:
    """Unit Tests for the `models.AddContextModel` class which contains data related to users adding a new context to the model"""

    def test_init(self):
        """Test the constructor default values and explicit setting of initial values"""
        obj = AddContextModel()
        assert obj.label is None

        obj = AddContextModel("foo")
        assert obj.label == "foo"

    def test_label(self):
        """Test getting and setting the new context label"""
        obj = AddContextModel()
        assert obj.label is None

        obj.label = "foo"
        assert obj.label == "foo"

        obj.label = "bar"
        assert obj.label == "bar"
