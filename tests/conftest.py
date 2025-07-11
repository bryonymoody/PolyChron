import pathlib

import pandas as pd
import pytest

import polychron.Config  # must import the full Config module, to access the module-scoped __config_instance
from polychron.models.Model import Model


@pytest.fixture(autouse=True)
def monkeypatch_Config__config_instance(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    """Default fixture which monkeypatches polychron.Config.__config_instance to ensure that the users real config file and projects directory are not used.

    `polychron.Config.__config_instance`, which is returned by `get_config()` is explictly set to a Config object with a temporary projects directory
    """
    # Apply the monkeypatch
    monkeypatch.setattr(
        polychron.Config, "__config_instance", polychron.Config.Config(projects_directory=tmp_path / "projects")
    )
    # Yield control to the test(s)
    return
    # Don't restore __config_instance to the original value, we do not want it to be used


@pytest.fixture(autouse=True)
def monkeypatch_Config_get_config_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    """Default fixture which monkeypatches polychron.Config.Config._get_config_filepath, to ensure the user's home folder is not accessed unintentionally.

    `polychron.Config.Config.get_config_dir` is patched to return a the pytest temporary diretory

    This is overridden by a fixture in test_Config.py which allows the real method to be tested on a per-test basis
    """
    # Apply the monkeypatch
    monkeypatch.setattr(polychron.Config.Config, "_get_config_filepath", lambda: tmp_path / "config.yaml")
    return


@pytest.fixture
def test_data_path() -> pathlib.Path:
    """Fixture providing the path to tests data on disk (at `tests/data`)"""
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture
def test_data_model_demo(tmp_path: pathlib.Path, test_data_path: pathlib.Path) -> Model:
    """Function-scoped fixture providing a Model instance built from the input files in `tests/data/demo`

    Todo:
        - This might be better as a session scoped test to avoid re-reading CSVs, but then must use tmp_path_factory instead.
        - Some of this should be abstracted into Model better (group_rels etc)
    """
    # Construct a model with required parameters
    model = Model("demo", tmp_path / "test_projects" / "demo" / "demo")
    # Read and set stratigraphic graph from csv
    model.set_stratigraphic_df(pd.read_csv(test_data_path / "demo" / "1-strat.csv", dtype=str))
    # Read and set scientific dating data from csv
    model.set_radiocarbon_df(pd.read_csv(test_data_path / "demo" / "2-dates.csv", dtype=str))
    # Read and set context grouping data from csv
    model.set_group_df(pd.read_csv(test_data_path / "demo" / "3-context-grouping.csv", dtype=str))
    # Read and set group relationship data from csv
    group_df = pd.read_csv(test_data_path / "demo" / "4-group-ordering.csv", dtype=str)
    group_rels = [(str(group_df["above"][i]), str(group_df["below"][i])) for i in range(len(group_df))]
    model.set_group_relationship_df(group_df, group_rels)
    # Read and set context equality data from csv
    model.set_context_equality_df(pd.read_csv(test_data_path / "demo" / "5-context-equality.csv", dtype=str))

    return model
