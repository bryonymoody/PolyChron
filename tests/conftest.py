import pathlib

import pandas as pd
import pytest

from polychron.models.Model import Model


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
