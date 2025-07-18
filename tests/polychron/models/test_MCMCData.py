import json
import pathlib
from importlib.metadata import version
from unittest.mock import patch

import pandas as pd
import pytest

from polychron.models.MCMCData import MCMCData


class TestMCMCData:
    """Unit Tests for the `models.Project` class which represents a project directory on disk and the models it contains"""

    def test_init(self):
        """Test the ctor default values and values which can be overridden"""
        # Test that the default ctor does not raise, and initialises some values as expected
        obj = MCMCData()
        assert obj.contexts == []
        assert obj.accept_samples_context == []
        assert obj.accept_samples_phi == []
        assert obj.A == 0
        assert obj.P == 0
        assert obj.all_samples_context == []
        assert obj.all_samples_phi == []
        assert obj.accept_group_limits == {}
        assert obj.all_group_limits == {}

        # Test that values can be overridden in the dataclass ctor
        contexts = ["a", "b", "c"]
        accept_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        accept_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        A = 12
        P = 12
        all_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        all_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        accept_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        all_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        obj = MCMCData(
            contexts=contexts,
            accept_samples_context=accept_samples_context,
            accept_samples_phi=accept_samples_phi,
            A=A,
            P=P,
            all_samples_context=all_samples_context,
            all_samples_phi=all_samples_phi,
            accept_group_limits=accept_group_limits,
            all_group_limits=all_group_limits,
        )
        assert obj.contexts == contexts
        assert obj.accept_samples_context == accept_samples_context
        assert obj.accept_samples_phi == accept_samples_phi
        assert obj.A == A
        assert obj.P == P
        assert obj.all_samples_context == all_samples_context
        assert obj.all_samples_phi == all_samples_phi
        assert obj.accept_group_limits == accept_group_limits
        assert obj.all_group_limits == all_group_limits

    def test_contexts(self):
        "Test getting and setting contexts"
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.contexts == []
        # Explicitly set the value
        contexts = ["a", "b", "c"]
        obj.contexts = contexts
        # Assert it has been updated
        assert obj.contexts == contexts

    def test_accept_samples_context(self):
        "Test getting and setting test_accept_samples_context"
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.accept_samples_context == []
        # Explicitly set the value
        accept_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        obj.accept_samples_context = accept_samples_context
        # Assert it has been updated
        assert obj.accept_samples_context == accept_samples_context

    def test_accept_samples_phi(self):
        "Test getting and setting accept_samples_phi"
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.accept_samples_phi == []
        # Explicitly set the value
        accept_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        obj.accept_samples_phi = accept_samples_phi
        # Assert it has been updated
        assert obj.accept_samples_phi == accept_samples_phi

    def test_A(self):
        """Test getting and setting A"""
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.A == 0
        # Explicitly set the value
        A = 12
        obj.A = A
        # Assert it has been updated
        assert obj.A == A

    def test_P(self):
        """Test getting and setting P"""
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.P == 0
        # Explicitly set the value
        P = 12
        obj.P = P
        # Assert it has been updated
        assert obj.P == P

    def test_all_samples_context(self):
        """Test getting and setting all_samples_context"""
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.all_samples_context == []
        # Explicitly set the value
        all_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        obj.all_samples_context = all_samples_context
        # Assert it has been updated
        assert obj.all_samples_context == all_samples_context

    def test_all_samples_phi(self):
        """Test getting and setting all_samples_phi"""
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.all_samples_phi == []
        # Explicitly set the value
        all_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        obj.all_samples_phi = all_samples_phi
        # Assert it has been updated
        assert obj.all_samples_phi == all_samples_phi

    def test_accept_group_limits(self):
        """Test getting and setting accept_group_limits"""
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.accept_group_limits == {}
        # Explicitly set the value
        accept_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        obj.accept_group_limits = accept_group_limits
        # Assert it has been updated
        assert obj.accept_group_limits == accept_group_limits

    def test_all_group_limits(self):
        """Test getting and setting all_group_limits"""
        # Create a default instance
        obj = MCMCData()
        # Assert the default value is as exected
        assert obj.all_group_limits == {}
        # Explicitly set the value
        all_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        obj.all_group_limits = all_group_limits
        # Assert it has been updated
        assert obj.all_group_limits == all_group_limits

    def test_save_results_dataframes(self, tmp_path: pathlib.Path):
        """Test saving the results dataframes, using a temporary path via a fixture"""
        # Create a MCMCData instance to save
        obj = MCMCData()
        # Populate with data to check was written to disk.
        contexts = ["a", "b", "c"]
        obj.contexts = contexts
        # all_group_limits requires more than 10000 elements per row for any to be written to disk
        all_group_limits = {
            "a_1": [float(x) for x in range(10005)],
            "a_2 = b_1": [float(x) for x in range(10005)],
        }
        obj.all_group_limits = all_group_limits

        # Prepare method input data
        group_df = pd.DataFrame({"context": contexts, "Group": ["1", "2", "1"]})

        # Call save_results_dataframes
        obj.save_results_dataframes(tmp_path, group_df)

        # Check expected files exist and contain expected (amount of) data
        full_results_df_path = tmp_path / "full_results_df"
        assert full_results_df_path.is_file()
        df_from_disk = pd.read_csv(full_results_df_path)
        # Assert the number of columns in the csv
        assert len(df_from_disk.columns) == len(all_group_limits)
        # Assert the number of rows in the csv
        assert len(df_from_disk) == max([len(x) - 10000 for x in all_group_limits.values()])

        key_ref_csv_path = tmp_path / "key_ref.csv"
        assert key_ref_csv_path.is_file()
        df_from_disk = pd.read_csv(key_ref_csv_path)
        # Assert the number of columns in the csv
        assert len(df_from_disk.columns) == 1
        # Assert there is one row per context/group from teh group df
        assert len(df_from_disk) == len(group_df)

        context_no_csv_path = tmp_path / "context_no.csv"
        assert context_no_csv_path.is_file()
        df_from_disk = pd.read_csv(context_no_csv_path)
        # Assert the number of columns in the csv
        assert len(df_from_disk.columns) == 1
        # Assert there is one row per context/group from teh group df
        assert len(df_from_disk) == len(obj.contexts)

        # Assert that an exceptions may be raised if a bad path is provided
        existing_file_as_path = tmp_path / "a_file"
        existing_file_as_path.touch()
        with pytest.raises(OSError, match="Cannot save file into a non-existent directory"):
            obj.save_results_dataframes(existing_file_as_path, group_df)

    def test_to_json(self):
        """Test converting an MCMCData instance to json"""
        # Prepare the MCMCData instance with some data
        contexts = ["a", "b", "c"]
        accept_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        accept_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        A = 12
        P = 12
        all_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        all_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        accept_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        all_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        obj = MCMCData(
            contexts=contexts,
            accept_samples_context=accept_samples_context,
            accept_samples_phi=accept_samples_phi,
            A=A,
            P=P,
            all_samples_context=all_samples_context,
            all_samples_phi=all_samples_phi,
            accept_group_limits=accept_group_limits,
            all_group_limits=all_group_limits,
        )

        # Convert to json
        json_str = obj.to_json()
        # Ensure there is some json
        assert len(json_str) > 0
        # And as it was not prettified it should contain a single line
        assert len(json_str.splitlines()) == 1

        # Check it can be parsed as json (no asswrtions)
        parsed_data = json.loads(json_str)
        # Check members are included as expected
        assert "polychron_version" in parsed_data
        assert "mcmc_data" in parsed_data
        mcmc_data = parsed_data["mcmc_data"]
        assert "contexts" in mcmc_data
        assert "accept_samples_context" in mcmc_data
        assert "accept_samples_phi" in mcmc_data
        assert "A" in mcmc_data
        assert "P" in mcmc_data
        assert "all_samples_context" in mcmc_data
        assert "all_samples_phi" in mcmc_data
        assert "accept_group_limits" in mcmc_data
        assert "all_group_limits" in mcmc_data

        # Check pretty printing returns a string of more than 1 line
        json_str = obj.to_json(pretty=True)
        # Ensure there is some json
        assert len(json_str) > 0
        # Ensure it contains more than one line
        assert len(json_str.splitlines()) > 1

        # Assert that if any values were None (they should not be, but could be) that they are eoncded as json correctly.
        obj = MCMCData(contexts=None)
        json_str = obj.to_json()
        # Ensure there is some json
        assert len(json_str) > 0

    def test_save(self, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture):
        """Test that saving MCMCData instances behaves as intended"""
        # Prepare the MCMCData instance with some data
        contexts = ["a", "b", "c"]
        accept_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        accept_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        A = 12
        P = 12
        all_samples_context = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        all_samples_phi = [
            [1.0, 2.0, 3.0],
            [1.0, 2.0, 3.0],
        ]
        accept_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        all_group_limits = {
            "a_1": [1.0, 2.0, 3.0],
            "a_2 = b_1": [1.0, 2.0, 3.0],
            "a": [1.0, 2.0, 3.0],
        }
        obj = MCMCData(
            contexts=contexts,
            accept_samples_context=accept_samples_context,
            accept_samples_phi=accept_samples_phi,
            A=A,
            P=P,
            all_samples_context=all_samples_context,
            all_samples_phi=all_samples_phi,
            accept_group_limits=accept_group_limits,
            all_group_limits=all_group_limits,
        )
        group_df = pd.DataFrame({"context": contexts, "Group": ["1", "2", "1"]})

        # Save the instance
        obj.save(tmp_path, group_df)

        # Check that expected files have been produced. Other tests cover the values included in these files
        assert (tmp_path / "polychron_mcmc_data.json").is_file()
        assert (tmp_path / "full_results_df").is_file()
        assert (tmp_path / "key_ref.csv").is_file()
        assert (tmp_path / "context_no.csv").is_file()

        # Use capsys to check that if verbose saving is used something is printed
        capsys.readouterr()
        obj.save(tmp_path, group_df, verbose=True)
        captured = capsys.readouterr()
        assert len(captured.out) > 0

        # Assert that if a bad path is provided, an exception will be raised
        with pytest.raises(RuntimeError):
            obj.save(tmp_path / "does" / "not" / "exist", group_df)

        # Assert that if a file system error were to occur during saving, this would be propagated.
        with patch("builtins.open", side_effect=IOError("Mock IOError")):
            with pytest.raises(IOError, match="Mock IOError"):
                obj.save(tmp_path, group_df)

    def test_load_from_disk(self, tmp_path: pathlib.Path, capsys: pytest.CaptureFixture):
        """Test loading MCMC objects from serialised data on disk"""
        # A RuntimeError should be raised if the provided path is not a file
        with pytest.raises(RuntimeError):
            MCMCData.load_from_disk(tmp_path / "not_a_file")

        # A JSONDecodeError should be raised if the file exists but is not valid json
        with open(tmp_path / "invalid_json.json", "w") as fp:
            fp.write("{")
        with pytest.raises(json.JSONDecodeError):
            MCMCData.load_from_disk(tmp_path / "invalid_json.json")

        # A RuntimeError should be raised if the "polychron_version" is missing
        with open(tmp_path / "empty_json.json", "w") as fp:
            json.dump({}, fp)
        with pytest.raises(RuntimeError):
            MCMCData.load_from_disk(tmp_path / "empty_json.json")

        # A RuntimeError should be raised if the "polychron_version" present but "mcmc_data" is missing
        with open(tmp_path / "mcmc_data_missing.json", "w") as fp:
            json.dump({"polychron_version": version("polychron")}, fp)
        with pytest.raises(RuntimeError):
            MCMCData.load_from_disk(tmp_path / "mcmc_data_missing.json")

        # If a valid json file with the required keys is present, but "mcmc_data" is empty, an object should be returned with default values
        with open(tmp_path / "empty_mcmc_data.json", "w") as fp:
            mcmc_data = {}
            json.dump({"polychron_version": version("polychron"), "mcmc_data": mcmc_data}, fp)
        obj = MCMCData.load_from_disk(tmp_path / "empty_mcmc_data.json")
        assert obj == MCMCData()

        # If a valid json file with the required keys is present, but an unknown key is included in mcmc_data, a warning should be printed to stderr
        with open(tmp_path / "invalid_mcmc_data_key.json", "w") as fp:
            mcmc_data = {"invalid_key": ""}
            json.dump({"polychron_version": version("polychron"), "mcmc_data": mcmc_data}, fp)
        # clear the capture region
        capsys.readouterr()
        # Parse the partial data
        obj = MCMCData.load_from_disk(tmp_path / "invalid_mcmc_data_key.json")
        # Capture output
        captured = capsys.readouterr()
        # Ensure something was printed to stderr
        assert len(captured.err) > 0

        # If valid json with atleast one valid key is provided, ensure it is accepted.
        # This may need ammending to ensure all required data is included in teh save data?
        with open(tmp_path / "valid_file.json", "w") as fp:
            mcmc_data = {"contexts": ["a", "b", "c"]}
            json.dump({"polychron_version": version("polychron"), "mcmc_data": mcmc_data}, fp)
        # Parse the partial data
        obj = MCMCData.load_from_disk(tmp_path / "valid_file.json")
        # Assert the cotnexts value matches
        assert obj.contexts == ["a", "b", "c"]

        # This may need ammending to ensure all required data is included in teh save data?
        with open(tmp_path / "valid_file.json", "w") as fp:
            mcmc_data = {"contexts": ["a", "b", "c"]}
            json.dump({"polychron_version": version("polychron"), "mcmc_data": mcmc_data}, fp)
        # Parse the partial data
        obj = MCMCData.load_from_disk(tmp_path / "valid_file.json")
        # Assert the cotnexts value matches
        assert obj.contexts == ["a", "b", "c"]
