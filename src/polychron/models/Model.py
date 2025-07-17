from __future__ import annotations

import csv
import filecmp
import json
import os
import pathlib
import shutil
import sys
from dataclasses import dataclass, field
from importlib.metadata import version
from inspect import signature
from typing import Dict, List, Literal, Optional, Tuple, get_type_hints

import networkx as nx
import packaging.version
import pandas as pd
import pydot
from graphviz import render
from networkx.drawing.nx_pydot import write_dot
from packaging.version import Version
from PIL import Image, UnidentifiedImageError

from ..automated_mcmc_ordering_coupling_copy import run_MCMC
from ..Config import get_config
from ..models.MCMCData import MCMCData
from ..util import (
    MonotonicTimer,
    node_coords_from_svg,
    phase_info_func,
    phase_labels,
    rank_func,
    remove_invalid_attributes_networkx_lt_3_4,
    trim,
)
from .InterpolatedRCDCalibrationCurve import InterpolatedRCDCalibrationCurve


@dataclass
class Model:
    """MVP Model representing a polychron model.

    Note:
        `Optional[foo]` must be used rather than `from __future__ import annotations` and `foo | None` in python 3.9 due to use of `get_type_hints`
    """

    name: str
    """The name of the model within the project (unique)"""

    path: pathlib.Path
    """The path to the directory representing this model on disk
    """

    stratigraphic_graphviz_file: Optional[pathlib.Path] = field(default=None)
    """Stratigraphic path for .dot/.gv input
    
    Formerly StartPage.FILE_INPUT
    """

    stratigraphic_df: Optional[pd.DataFrame] = field(default=None)
    """The stratigraphic file from CSV, if loaded.

    Formerly `StartPage.stratfile`
    """

    stratigraphic_dag: Optional[nx.DiGraph] = field(default=None)
    """Stratigraphic Directed Acyclic Graph, initially produced from the stratigraphic dataframe or graphviz file before being mutated.
    
    Formerly `StartPage.graph`
    """

    stratigraphic_image: Optional[Image.Image] = field(default=None)
    """Rendered version of the stratigraphic graph as an image, for whicle a handle must be kept for persistence.
    """

    radiocarbon_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe containing radiocarbon dating information, loaded from disk
    
    Formerly `StartPage.datefile`
    """

    context_no_unordered: Optional[List[str]] = field(default=None)
    """A list of stratigraphic graph nodes, initially populated within open_scientific_dating_file before being used elsewhere.

    This list is in the order from the input file, rather than a topological order.
    """

    group_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe of context grouping information loaded from disk. 

    Expected columns ["context", "Group"]
    
    Formerly `StartPage.phasefile`
    """

    group_relationship_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe containing group relationship information loaded from disk
    
    Expected columns ["above", "below"], although order of columns is used not the column names

    Formerly `phase_rel_df` in `StartPage.open_file5`
    """

    group_relationships: Optional[List[Tuple[str, str]]] = field(default=None)
    """A list of the relative relationships between groups, stored as Tuples of (above, below))

    Formerly `StartPage.phase_rels`
    """

    context_equality_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe containing context equality relationship information loaded from disk
    
    Formerly `equal_rel_df` in `StartPage.open_file6`
    """

    load_check: bool = False
    """If the chronological graph has been rendered for the current state of the model
    
    Formerly `global load_check`, where "loaded" is now True and "not_loaded" is False.
    """

    chronological_dag: Optional[nx.DiGraph] = field(default=None)
    """Chronological directed graph, produced by rendering the chronological graph
    
    Formerly `StartPage.chrono_dag`
    """

    chronological_image: Optional[Image.Image] = field(default=None)
    """Rendered version of the Chronological graph as an image, for which a handle must be kept for persistence and to avoid regenerating when not required.

    When load_check is True, this image is valid for the current state of the Model.

    Formerly `StartPage.image2`
    """

    mcmc_check: bool = False
    """If the model has been calibrated
    
    Formerly `global mcmc_check`, where "mcmc_loaded" is now True and "mcmc_notloaded" is False.
    """

    deleted_nodes: List[Tuple[str, str]] = field(default_factory=list)
    """List of deleted nodes and the reason they were deleted.

    This may include the same node multiple times (as nodes can be deleted, then added again)
    
    Formerly `StartPage.delnodes` and `StartPage.delnodes_meta`
    """

    deleted_edges: List[Tuple[str, str, str]] = field(default_factory=list)
    """List of deleted edges and the reason they were deleted

    Each entry is the (a_node, b_node, reason).

    This may include the same edges multiple times (as edges can be deleted, then added again)
    
    Formerly `StartPage.edges_del` and `StartPage.deledges_meta`
    """

    resid_or_intru_dag: Optional[nx.DiGraph] = field(default=None)
    """Copy of stratigraphic_dag for the residual or intrusive workflow

    This is mutated to show which nodes have been marked as residual or intrusive.

    This does not need saving.

    Formerly `PageTwo.graphcopy`
    """

    resid_or_intru_image: Optional[Image.Image] = field(default=None)
    """Image handle for the rendered png of the stratigraphic graph with residual or intrusive node highlighting.

    A handle to this needs to be maintained to avoid garbage collection

    Formerly `PageTwo.image`
    """

    intrusive_contexts: List[str] = field(default_factory=list)
    """List of intrusive contexts/nodes.

    Formerly `PageTwo.intru_list`
    """

    residual_contexts: List[str] = field(default_factory=list)
    """List of residual contexts/nodes.

    Formerly `PageTwo.resid_list`
    """

    intrusive_context_types: Dict[str, str] = field(default_factory=dict)
    """Dict of selected drop down choice for intrusive context/nodes.
    """

    residual_context_types: Dict[str, str] = field(default_factory=dict)
    """Dict of selected drop down choice for intrusive context/nodes.
    """

    grouped_rendering: bool = False
    """Flag indicating that the graphs should be rendered in grouped rendering mode

    Previously `global phase_true`
    """

    context_types: List[Literal["normal", "residual", "intrusive"]] = field(default_factory=list)
    """The type of each context, in the same order as as context_no_unordered.
    
    Used for calibration (MCMC)
    
    Formerly `StartPage.CONT_TYPE`
    """

    prev_group: List[str] = field(default_factory=list)
    """List of previous phases, with "start" as the 0th value.
    
    Initialised in `ManageGroupRelationshipsPresenter.full_chronograph_func`

    Formerly `StartPage.prev_phase` and `popupWindow3.prev_phase`
    """

    post_group: List[str] = field(default_factory=list)
    """List of post phases, with "end" as the final value.
    
    Initialised in `ManageGroupRelationshipsPresenter.full_chronograph_func`

    Formerly `StartPage.post_phase` and `popupWindow3.post_phase`
    """

    phi_ref: List[str] = field(default_factory=list)
    """Ordered list of groups, from oldest to youngest.
        
    Formerly `StartPage.phi_ref`
    """

    removed_nodes_tracker: List[str] = field(default_factory=list)
    """List of nodes (contexts) for which there was insufficient node or group information, and so been removed during group relationship management. 

    This is separate from nodes which were deleted by the user.
    
    Formerly `StartPage.node_del_tracker`, `PageTwo.node_del_tracker` and `popupWindow3.node_del_tracker`
    """

    mcmc_data: MCMCData = field(default_factory=MCMCData)
    """MCMC data for this model. Includes values used as inputs and outputs for the MCMC data pase
    
    If mcmc_check is true, it is implied that this has been saved to disk
    """

    stratigraphic_node_coords: Optional[Tuple[pd.DataFrame, List[float]]] = field(default=None)
    """A tuple containing node coordinates and  within the svg representation of the stratigraphic graph, and the dimensions of the svg.

    This is updated when the stratigraphic_dag is re-rendered.
    
    Formerly (part of) `global node_df`

    Todo:
        - ensure this is correct when reopening from disk? and there is no other places where this needs re-generating, for all 3 versions.
    """

    chronological_node_coords: Optional[Tuple[pd.DataFrame, List[float]]] = field(default=None)
    """A tuple containing node coordinates and  within the svg representation of the chronological graph, and the dimensions of the svg.

    This is updated when the chronological_dag is re-rendered.
    
    Formerly (part of) `global node_df`
    """

    chronological_node_coords: Optional[Tuple[pd.DataFrame, List[float]]] = field(default=None)
    """A tuple containing node coordinates and  within the svg representation of the chronological graph, and the dimensions of the svg.

    This is updated when the chronological_dag is re-rendered.
    
    Formerly (part of) `global node_df`
    """

    resid_or_intru_node_coords: Optional[Tuple[pd.DataFrame, List[float]]] = field(default=None)
    """A tuple containing node coordinates and  within the svg representation of the resid_or_intru graph, and the dimensions of the svg.

    This is updated when the resid_or_intru_dag is re-rendered.
    
    Formerly (part of) `global node_df`
    """

    __calibration: Optional[InterpolatedRCDCalibrationCurve] = field(default=None, init=False, repr=False)
    """Interpolated RCD calibration curve object, which is stored in a member variable so it is loaded once and only once"""

    def get_working_directory(self) -> pathlib.Path:
        """Get the working directory to be used for dynamically created files

        This allows the "saved" version of the model to different from the version currently being worked on. I.e. the rendered chronological graph used in the UI as changes are made can be different to the version from when save the model was last saved.
        """
        return self.path / "workdir"

    def get_chronological_graph_directory(self) -> pathlib.Path:
        """Get the path to the chronological_graph directory for this model

        Returns:
            The path to the `chronological_graph` directory for this model
        """
        return self.path / "chronological_graph"

    def get_stratigraphic_graph_directory(self) -> pathlib.Path:
        """Get the path to the stratigraphic_graph directory for this model

        Returns:
            The path to the `stratigraphic_graph` directory for this model
        """
        return self.path / "stratigraphic_graph"

    def get_mcmc_results_directory(self) -> pathlib.Path:
        """Get the path to the mcmc_results directory for this model

        Returns:
            The path to the `mcmc_results` directory for this model
        """
        return self.path / "mcmc_results"

    def get_python_only_directory(self) -> pathlib.Path:
        """Get the path to the python_only directory for this model

        Returns:
            The path to the `python_only` directory for this model
        """
        return self.path / "python_only"

    def to_json(self, pretty: bool = False):
        """Serialise this object to JSON, excluding ephemeral members"""
        # Create a dictionary containing a subset of this instance's member variables, converted to formats which can be json serialised.
        data = {}
        exclude_keys = [
            "path",  # Don't include the path, so models can be trivially copied on disk
            "stratigraphic_image",  # don't include image handles
            "chronological_image",  # don't include image handles
            "resid_or_intru_dag",  # no need to save the residual or intrusive dag, it's ephemeral
            "resid_or_intru_image",  # don't include image handles
            "intrusive_contexts",  # not needed, ephemeral
            "intrusive_context_types",  # not needed, ephemeral
            "residual_contexts",  # not needed, ephemeral
            "residual_context_types",  # not needed, ephemeral
            "stratigraphic_node_coords",  # svg coords are ephemeral
            "chronological_node_coords",  # svg coords are ephemeral
            "resid_or_intru_node_coords",  # svg coords are ephemeral
            "mcmc_data",  # don't include the mcmc_data object, which has been saved elsewhere.
            "_Model__calibration",  # don't save the interpolated calibration curve, it is already on disk. Must use the fully qualified name for __ members?
        ]
        for k, v in self.__dict__.items():
            if k not in exclude_keys:
                if v is None:
                    data[k] = v
                elif isinstance(v, tuple([str, int, float, list, dict, tuple])):
                    data[k] = v
                elif isinstance(v, pathlib.Path):
                    data[k] = str(v)
                elif isinstance(v, pd.DataFrame):
                    # For dataframes, export to json so pandas handles the type conversion, before returning to a python object.
                    data[k] = json.loads(v.to_json(orient="columns"))
                elif isinstance(v, nx.DiGraph):
                    # Encode graphs as json via networkx node_link_data, which can be de-serialised via node_link_graph. This should be safe for round-trips, other than node names being converted to strings (which they are anyway)
                    # For older networkx (for py 3.9) must use link, which is deprecated in 3.5 and removed in 3.6
                    if packaging.version.parse(nx.__version__) < packaging.version.parse("3.4.0"):
                        data[k] = nx.node_link_data(v, link="edges")
                    else:
                        data[k] = nx.node_link_data(v, edges="edges")
                else:
                    data[k] = str(v)

        indent = 2 if pretty else None
        return json.dumps({"polychron_version": version("polychron"), "model": data}, indent=indent)

    def save(self) -> None:
        """Save the current state of this model to disk at self.path

        Raises:
            RuntimeError: raised when any error occurred during saving, with a message to present to the user
        """

        # Ensure directories required exist
        try:
            self.create_dirs()
        except (OSError, NotADirectoryError) as e:
            raise RuntimeError(
                f'Unable to save "polychron_model.json", an error occurred while creating Model directories: {e}'
            )

        try:
            timer_save = MonotonicTimer().start()

            # create the representation of the Model to be saved to disk
            timer_to_json = MonotonicTimer().start()
            json_s = self.to_json(pretty=True)
            timer_to_json.stop()

            # Save the json representation of this object to disk
            timer_json_write = MonotonicTimer().start()
            json_path = self.get_python_only_directory() / "polychron_model.json"
            with open(json_path, "w") as f:
                f.write(json_s)
            timer_json_write.stop()

            # Create / Copy other files to the correct location
            timer_files = MonotonicTimer().start()
            # Save the delete contexts metadata to the working directory (superfluos)
            self.save_deleted_contexts()

            # Ensure the "saved" versions of files are up to date.
            # Prepare a dictionary of per-output location files to copy form the working dir.
            files_to_copy = {
                self.get_chronological_graph_directory(): [
                    "fi_new_chrono.png",
                    "fi_new_chrono.svg",
                    "fi_new_chrono",
                    "testdag_chrono.png",
                ],
                self.get_stratigraphic_graph_directory(): [
                    "fi_new.png",
                    "fi_new.svg",
                    "fi_new",
                    "testdag.png",
                    "deleted_contexts_meta",
                ],
                self.get_mcmc_results_directory(): ["full_results_df", "key_ref.csv", "context_no.csv"],
                self.get_python_only_directory(): ["polychron_mcmc_data.json"],
            }
            # Iterate the per output directory files, copying files if they exist and copying is required
            for dst_dir, filenames in files_to_copy.items():
                for filename in filenames:
                    src = self.get_working_directory() / filename
                    dst = dst_dir / filename
                    # Only copy the file, if the src exists and is not the same as the dst file
                    if src.is_file() and (not dst.is_file() or not filecmp.cmp(src, dst, shallow=True)):
                        shutil.copy2(src, dst)
            timer_files.stop()

            # Stop the timer and report timing if verbose
            timer_save.stop()
            if get_config().verbose:
                print("Timing - Model.save:")
                print(f"  total:      {timer_save.elapsed(): .6f}s")
                print(f"  to_json:    {timer_to_json.elapsed(): .6f}s")
                print(f"  json_write: {timer_json_write.elapsed(): .6f}s")
                print(f"  files:      {timer_files.elapsed(): .6f}s")

        except Exception as e:
            raise RuntimeError(
                f'Unable to save "polychron_model.json", an error occurred while creating Model directories: {e}'
            )

    @classmethod
    def load_from_disk(cls, path: pathlib.Path) -> "Model":
        """Get an instance of the model from serialised json on disk.

        Parameters:
            path: Path to a model directory (not the json file)

        Raises:
            RuntimeWarning: when the model could not be loaded, but in a recoverable way. I.e. the directory exits but no files are contained (so allow the model to be "loaded")
            RuntimeError: when the model could not be loaded, and the error cannot be recovered from within PolyChron. I.e. the json file is invalid/corrupt
        """

        # Ensure required files/folders are present
        if not path.is_dir():
            raise RuntimeWarning(f"Error loading from Model from path '{path}' it is not a directory")

        # Ensure the json file exists
        model_json_path = path / "python_only" / "polychron_model.json"
        # If the json file does not exist, return the default.
        if not model_json_path.is_file():
            # Return a Model instance with just the path and name set, if no json do to load
            return cls(name=path.name, path=path)

        timer_load = MonotonicTimer().start()

        # Attempt to open the Model json file, building an instance of Model
        with open(model_json_path, "r") as f:
            timer_load_json = MonotonicTimer().start()
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON file '{model_json_path}': {e}")
            timer_load_json.stop()

            timer_process = MonotonicTimer().start()

            # Raise an excpetion if required keys are missing
            if "polychron_version" not in data:
                raise RuntimeError(f"Required key 'polychron_version' missing from '{model_json_path}'")
            if "model" not in data:
                raise RuntimeError(f"Required key 'model' missing from '{model_json_path}'")

            model_data = data["model"]

            # Raise an exception if the polychron_version is not a string, or is not a valid python version number
            if not isinstance(data["polychron_version"], str):
                raise RuntimeError(f"'polychron_version' must be a string, not {type(data['polychron_version'])}")
            try:
                file_version = Version(data["polychron_version"])
            except Exception:
                raise RuntimeError(f"'polychron_version': '{data['polychron_version']}' is not a valid version number")
            # Handle version specific loading requirements. I.e. renaming members, or changing types.
            if file_version >= Version("0.2.0") and file_version < Version("0.3.0"):
                pass

            # Convert certain values back based on the hint for the data type.
            cls_type_hints = get_type_hints(cls)
            # Get the class initialiser parameters so non-init fields can be discarded
            init_parameters = set(signature(cls.__init__).parameters.keys())
            init_parameters.remove("self")
            # Also build a list of keys to remove
            keys_to_remove = []
            for k in model_data:
                if k in cls_type_hints and k in init_parameters:
                    type_hint = cls_type_hints[k]
                    # If the values is None, do nothing.
                    if model_data[k] is None:
                        pass
                    elif type_hint in [pathlib.Path, Optional[pathlib.Path]]:
                        model_data[k] = pathlib.Path(model_data[k])
                    elif type_hint in [pd.DataFrame, Optional[pd.DataFrame]]:
                        # DataFrames are encoded as json, parsed back into a dictionary before being encoded as json again. At this point, the first json decode has occurred so we should have a dictionary of dictionaries (one per column) which can be reconverted.
                        # However, this may have lost typing information for the columns, but they should have been strings anyway
                        if isinstance(model_data[k], dict):
                            model_data[k] = pd.DataFrame.from_dict(model_data[k], orient="columns")
                    elif type_hint in [nx.DiGraph, Optional[nx.DiGraph]]:
                        # Convert the node_link_data encoded networkx digraph via node_link_graph
                        # For older networkx (for py 3.9) must use link, which is deprecated in 3.5 and removed in 3.6
                        if packaging.version.parse(nx.__version__) < packaging.version.parse("3.4.0"):
                            model_data[k] = nx.node_link_graph(model_data[k], link="edges", multigraph=False)
                        else:
                            model_data[k] = nx.node_link_graph(model_data[k], edges="edges", multigraph=False)

                    elif type_hint in [Optional[List[Tuple[str, str]]]]:
                        # tuples are stored as lists in json, so must convert from a list of lists to a list of tuples
                        model_data[k] = [tuple(sub) for sub in model_data[k]]
                else:
                    # If the key is not in the typehints or __init__ kwargs it will cause the ctor to trigger a runtime assertion, so remove it.
                    print(f"Warning: unexpected Model member '{k}' during deserialisation", file=sys.stderr)
                    keys_to_remove.append(k)

            # Remove any unexpected keys
            for k in keys_to_remove:
                del model_data[k]

            # Overwrite certain elements, i.e the path (in case the model fields have been copied), but the path was included in the save file
            if "name" not in model_data:
                model_data["name"] = str(path.name)
            model_data["path"] = path

            # Ensure that some elements are not stored, if they are explicitly handled otherwise
            if "mcmc_data" in model_data:
                del model_data["mcmc_data"]

            # Create an instance of the Model
            model: Model = cls(**model_data)

            timer_process.stop()

            # If mcmc has been ran for this model, and the expected mcmc data file exists, load it.
            timer_mcmc = None
            if model.mcmc_check:
                timer_mcmc = MonotonicTimer().start()
                mcmc_data_path = model.get_python_only_directory() / "polychron_mcmc_data.json"
                if mcmc_data_path.is_file():
                    model.mcmc_data = MCMCData.load_from_disk(mcmc_data_path)
                else:
                    print(f"Failed to load MCMCData from '{mcmc_data_path}'", file=sys.stderr)
                timer_mcmc.stop()

            # Stop the timer and report timing if verbose
            timer_load.stop()
            if get_config().verbose:
                print("Timing - Model.load_from_disk:")
                print(f"  total:      {timer_load.elapsed(): .6f}s")
                print(f"  load_json:  {timer_load_json.elapsed(): .6f}s")
                print(f"  process:    {timer_process.elapsed(): .6f}s")
                if timer_mcmc is not None:
                    print(f"  timer_mcmc: {timer_mcmc.elapsed(): .6f}s")

            # Return the Model
            return model

        # If this point is reached, an error occurred and should have be propagated
        return None

    def create_dirs(self) -> None:
        """Create the expected directories for this model, including working directories.

        Formerly part of `load_Window.create_file`, `popupWindow9.make_directories` & `popupWindow10.make_directories`

        Raises:
            OSError: Propagated from `pathlib.Path.mkdir` if an OSError occurred during directory creation
            NotADirectoryError: Propagated from `pathlib.Path.mkdir` if any ancestors within the path are not a directory
        """

        # Ensure the model (and implicitly project) directory exists
        self.path.mkdir(parents=True, exist_ok=True)
        # Create each expected child directory.
        expected_model_dirs = [
            self.get_stratigraphic_graph_directory(),
            self.get_chronological_graph_directory(),
            self.get_mcmc_results_directory(),
            self.get_python_only_directory(),
            self.get_working_directory(),
        ]
        for path in expected_model_dirs:
            path.mkdir(parents=True, exist_ok=True)

        # Change the working dir to the model directory.
        os.chdir(self.path)

    def save_deleted_contexts(self) -> None:
        """Save the delete contexts metadata to disk

        Formerly `StartPage.tree2`, in `save_state_1`

        Raises:
            OSError: if any OS errors occur during csv writing (e.g. if the disk is full)
        """
        # Prepare the CSV
        cols = ("context", "Reason for deleting")
        rows = [[x[0], x[1]] for x in self.deleted_nodes]
        df = pd.DataFrame(rows, columns=cols)
        # Ensure output directory exists
        self.create_dirs()
        # Write csv to disk, which may raise OSError (e.g. if disk is full)
        path = self.get_working_directory() / "deleted_contexts_meta"
        df.to_csv(path, index=False)

    def set_stratigraphic_graphviz_file(self, file_input: str | pathlib.Path) -> None:
        """provided a .dot/.gv file path, set the model input."""
        self.stratigraphic_graphviz_file = pathlib.Path(file_input)

    def set_stratigraphic_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe for stratigraphic relationships, set the values locally and post-process it to produce the stratigraphic graph"""

        self.stratigraphic_df = df.copy()
        G = nx.DiGraph(graph_attr={"splines": "ortho"})
        set1 = set(self.stratigraphic_df.iloc[:, 0])
        set2 = set(self.stratigraphic_df.iloc[:, 1])
        set2.update(set1)
        node_set = {x for x in set2 if x == x}
        for i in set(node_set):
            G.add_node(i, shape="box", fontname="helvetica", fontsize="30.0", penwidth="1.0", color="black")
            G.nodes()[i].update({"Determination": [None, None]})
            G.nodes()[i].update({"Group": None})
        edges = []
        for i in range(len(self.stratigraphic_df)):
            a = tuple(self.stratigraphic_df.iloc[i, :])
            if not pd.isna(a[1]):
                edges.append(a[:2])
        G.add_edges_from(edges, arrowhead="none")
        self.stratigraphic_dag = G

    def set_radiocarbon_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe containing radiocarbon dating information for contexts, store a copy of the dataframe and mutate the stratigraphic dag

        Parameters:
            df (pd.Dataframe): dataframe containing radiocarbon dating information. Expected columns ["context", "date", "error"]
        """
        # Store a copy of the dataframe
        self.radiocarbon_df = df.copy()
        # Post process
        self.radiocarbon_df = self.radiocarbon_df.astype(str)

        if self.stratigraphic_dag:
            for i, j in enumerate(self.radiocarbon_df["context"]):
                self.stratigraphic_dag.nodes()[str(j)].update(
                    {"Determination": [self.radiocarbon_df["date"][i], self.radiocarbon_df["error"][i]]}
                )
        self.context_no_unordered = list(self.stratigraphic_dag.nodes())

    def set_group_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe for context grouping information, set the values locally and perform post processing"""
        # Store a copy of the dataframe
        self.group_df = df.copy()
        # Post processing of the dataframe
        if self.stratigraphic_dag:
            for i, j in enumerate(self.group_df["context"]):
                self.stratigraphic_dag.nodes()[str(j)].update({"Group": self.group_df["Group"][i]})

    def set_group_relationship_df(self, df: pd.DataFrame, group_relationships: List[Tuple[str, str]]) -> None:
        """Provided a dataframe for group relationships information, set the values locally and post-process"""
        # Store a copy of the dataframe
        self.group_relationship_df = df.copy()
        # Store a copy of the list of tuples extracted from the dataframe
        self.group_relationships = group_relationships.copy()

    def set_context_equality_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe for context equality information, set the values locally and post-process

        Columns names are not currently expected/used, but there must be atleast 2 columns.

        Parameters:
            df (pd.DataFrame): A dataframe containing context equality data.
        """
        # Store a copy of the dataframe
        self.context_equality_df = df.copy()

        # Post processing of the dataframe
        self.context_equality_df = self.context_equality_df.astype(str)
        context_1 = list(self.context_equality_df.iloc[:, 0])
        context_2 = list(self.context_equality_df.iloc[:, 1])
        for k, j in enumerate(context_1):
            self.stratigraphic_dag = nx.contracted_nodes(self.stratigraphic_dag, j, context_2[k])
            x_nod = list(self.stratigraphic_dag)
            newnode = f"{j} = {context_2[k]}"
            y_nod = [newnode if i == j else i for i in x_nod]
            mapping = dict(zip(x_nod, y_nod))
            self.stratigraphic_dag = nx.relabel_nodes(self.stratigraphic_dag, mapping)

    def render_strat_graph(self) -> None:
        """Render the stratigraphic graph as a png and svg, with or without phasing depending on model state. Also updates the location of each node via the svg"""
        # Call the appropriate render_strat method, depending if the model is set up to render in phases or not.
        if self.grouped_rendering:
            self.__render_strat_graph_phase()
        else:
            self.__render_strat_graph()

    def render_resid_or_intru_dag(self) -> None:
        """Render the residual or intrusive sratigraphic graph as a png and svg, with or without phasing depending on model state. Also updates the locatison of each node

        This graph will have different presentation information to highlight which contexts have been marked as residual or intrusive.
        """
        # Call the appropraite render_strat method, depending if the model is set up to render in phases or not.
        if self.grouped_rendering:
            self.__render_resid_or_intru_dag_phase()
        else:
            self.__render_resid_or_intru_dag()

    def __render_strat_graph(self) -> None:
        """Render the stratigraphic graph mutating the Model state

        Formerly `imgrender`
        """

        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)
        self.stratigraphic_dag.graph["graph"] = {"splines": "ortho"}
        # Ensure the graph is compatible with networkx < 3.4 nx_pydot
        self.stratigraphic_dag = remove_invalid_attributes_networkx_lt_3_4(self.stratigraphic_dag)
        write_dot(self.stratigraphic_dag, workdir / "fi_new")
        render("dot", "png", workdir / "fi_new")
        svg_path = render("dot", "svg", workdir / "fi_new")
        inp = Image.open(workdir / "fi_new.png")
        inp_final = trim(inp)
        inp_final.save(workdir / "testdag.png")
        self.stratigraphic_image = Image.open(workdir / "testdag.png")
        self.stratigraphic_node_coords = node_coords_from_svg(svg_path)

    def __render_strat_graph_phase(self) -> None:
        """Render the stratigraphic graph, with phasing mutating the Model state

        Formerly `imgrender_phase`

        Todo:
            - Consistently use graphviz.render or write_png|dot if possible throughout Model
        """
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)

        # Ensure the graph is compatible with networkx < 3.4 nx_pydot
        self.stratigraphic_dag = remove_invalid_attributes_networkx_lt_3_4(self.stratigraphic_dag)
        write_dot(self.stratigraphic_dag, workdir / "fi_new.txt")
        my_file = open(workdir / "fi_new.txt")
        file_content = my_file.read()
        new_string = rank_func(phase_info_func(self.stratigraphic_dag)[0], file_content)
        textfile = open(workdir / "fi_new.txt", "w")
        textfile.write(new_string)
        textfile.close()
        # Note: This previously set self.stratigraphic_dag to a pydot.Dot, rather than an nx.DiGraph which is expected elsewhere. This may need further testing.
        (grouped_stratigraphic_dag,) = pydot.graph_from_dot_file(workdir / "fi_new.txt")
        grouped_stratigraphic_dag.write_png(workdir / "test.png")
        grouped_stratigraphic_dag.write_svg(workdir / "test.svg")

        inp = Image.open(workdir / "test.png")
        inp = trim(inp)
        inp.save(workdir / "testdag.png")
        self.stratigraphic_image = Image.open(workdir / "testdag.png")
        self.stratigraphic_node_coords = node_coords_from_svg(workdir / "test.svg")

    def __render_resid_or_intru_dag(self) -> None:
        """Render the stratigraphic graph mutating the Model state

        Formerly `imgrender`
        """
        workdir = self.get_working_directory() / "resid_or_intru"
        workdir.mkdir(exist_ok=True, parents=True)

        self.resid_or_intru_dag.graph["graph"] = {"splines": "ortho"}
        # Ensure the graph is compatible with networkx < 3.4 nx_pydot
        self.resid_or_intru_dag = remove_invalid_attributes_networkx_lt_3_4(self.resid_or_intru_dag)
        write_dot(self.resid_or_intru_dag, workdir / "fi_new")
        render("dot", "png", workdir / "fi_new")
        svg_path = render("dot", "svg", workdir / "fi_new")
        inp = Image.open(workdir / "fi_new.png")
        inp_final = trim(inp)
        inp_final.save(workdir / "testdag.png")
        self.resid_or_intru_image = Image.open(workdir / "testdag.png")
        self.resid_or_intru_node_coords = node_coords_from_svg(svg_path)

    def __render_resid_or_intru_dag_phase(self) -> None:
        """Render the stratigraphic graph, with phasing mutating the Model state

        Formerly `imgrender_phase`
        """
        workdir = self.get_working_directory() / "resid_or_intru"
        workdir.mkdir(exist_ok=True, parents=True)
        # Ensure the graph is compatible with networkx < 3.4 nx_pydot
        self.resid_or_intru_dag = remove_invalid_attributes_networkx_lt_3_4(self.resid_or_intru_dag)
        write_dot(self.resid_or_intru_dag, workdir / "fi_new.txt")
        my_file = open(workdir / "fi_new.txt")
        file_content = my_file.read()
        new_string = rank_func(phase_info_func(self.resid_or_intru_dag)[0], file_content)
        textfile = open(workdir / "fi_new.txt", "w")
        textfile.write(new_string)
        textfile.close()
        (self.resid_or_intru_dag,) = pydot.graph_from_dot_file(workdir / "fi_new.txt")
        self.resid_or_intru_dag.write_png(workdir / "test.png")
        self.resid_or_intru_dag.write_svg(workdir / "test.svg")
        inp = Image.open(workdir / "test.png")
        inp = trim(inp)
        # Call the real .tkraise
        inp.save(workdir / "testdag.png")
        self.resid_or_intru_image = Image.open(workdir / "testdag.png")
        self.resid_or_intru_node_coords = node_coords_from_svg(workdir / "test.svg")

    def render_chrono_graph(self) -> None:
        """Render the chronological graph as a PNG and an SVG, mutating the Model state

        Formerly `imgrender2`

        Todo:
            - This should not require fi_new_chrono to exist on disk, but instead should create it from the chronological_dag if it exists?
        """
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)

        fi_new_chrono = workdir / "fi_new_chrono"
        if self.load_check and fi_new_chrono.is_file():
            render("dot", "png", fi_new_chrono)
            svg_path = render("dot", "svg", fi_new_chrono)
            inp = Image.open(workdir / "fi_new_chrono.png")
            inp_final = trim(inp)
            # scale_factor = min(canv_width/inp.size[0], canv_height/inp.size[1])
            # inp_final = inp.resize((int(inp.size[0]*scale_factor), int(inp.size[1]*scale_factor)), Image.ANTIALIAS)
            inp_final.save(workdir / "testdag_chrono.png")
            self.chronological_image = Image.open(workdir / "testdag_chrono.png")
            self.chronological_node_coords = node_coords_from_svg(svg_path)

        else:
            self.chronological_image = None

    def reopen_stratigraphic_image(self) -> None:
        """Re-open the stratigraphic image from disk

        Used when the window is reiszed as the in memory copy may have been resized

        Formerly part of `StartPage.resize`
        """
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)
        png_path = workdir / "testdag.png"
        if png_path.is_file():
            try:
                self.stratigraphic_image = Image.open(png_path)
            except (FileNotFoundError, UnidentifiedImageError):
                print("Warning: unable to open Image '{png_path}'\n  {e}", file=sys.stderr)
                self.stratigraphic_image = None

    def reopen_chronological_image(self) -> None:
        """Re-open the chrono image from disk

        Used when the window is reiszed as the in memory copy may have been resized

        Formerly part of `StartPage.resize2`
        """
        workdir = self.get_working_directory()
        png_path = workdir / "testdag_chrono.png"
        if png_path.is_file():
            try:
                self.chronological_image = Image.open(png_path)
            except (FileNotFoundError, UnidentifiedImageError):
                print("Warning: unable to open Image '{png_path}'\n  {e}", file=sys.stderr)
                self.chronological_image = None

    def record_deleted_node(self, context: str, reason: Optional[str] = None) -> None:
        """Method to add a node to the list of deleted nodes

        Parameters:
            context: the context / node which was removed
            reason: the reason the node was deleted, if provided.
        """
        self.deleted_nodes.append((context, reason))

    def record_deleted_edge(self, context_a: str, context_b: str, reason: Optional[str] = None) -> None:
        """Method to add an edge to the list of deleted edges

        Parameters:
            context_a: one context from the edge
            context_a: the other context from the edge
            reason: the reason the node was deleted, if provided.
        """
        self.deleted_edges.append((context_a, context_b, reason))

    def MCMC_func(
        self,
    ) -> Tuple[
        List[str],
        List[List[float]],
        List[List[float]],
        List[str],
        int,
        int,
        List[List[float]],
        List[List[float]],
        Dict[str[List[float]]],
        Dict[str[List[float]]],
    ]:
        """run the mcmc calibration on the current model, returning output values without (significantly) mutating state

        gathers all the inputs for the mcmc module and then runs it and returns resuslts dictionaries

        Returns:
            a tuple of calibration results

        Formerly `StartPage.MCMC_func`
        """

        if self.stratigraphic_dag is None or self.chronological_dag is None:
            raise RuntimeError("Model is not MCMC ready, the stratigraphic and chronographic dag are not valid")

        context_no = [x for x in list(self.context_no_unordered) if x not in self.removed_nodes_tracker]
        topo = list(nx.topological_sort(self.chronological_dag))
        topo_sort = [x for x in topo if (x not in self.removed_nodes_tracker) and (x in context_no)]
        topo_sort.reverse()
        context_no = topo_sort
        # Get a list containing the group per context (in reverse topological order)
        key_ref = [list(self.group_df["Group"])[list(self.group_df["context"]).index(i)] for i in context_no]
        self.context_types = [self.context_types[list(self.context_no_unordered).index(i)] for i in topo_sort]
        strat_vec = []
        resids = [j for i, j in enumerate(context_no) if self.context_types[i] == "residual"]
        intrus = [j for i, j in enumerate(context_no) if self.context_types[i] == "intrusive"]
        for i, j in enumerate(context_no):
            if self.context_types[i] == "residual":
                low = []
                up = list(self.stratigraphic_dag.predecessors(j))
            elif self.context_types[i] == "intrusive":
                low = list(self.stratigraphic_dag.successors(j))
                up = []
            else:
                up = [k for k in self.stratigraphic_dag.predecessors(j) if k not in resids]
                low = [k for k in self.stratigraphic_dag.successors(j) if k not in intrus]
            strat_vec.append([up, low])
        # strat_vec = [[list(self.stratigraphic_dag.predecessors(i)), list(self.stratigraphic_dag.successors(i))] for i in context_no]
        rcd_est = [
            int(list(self.radiocarbon_df["date"])[list(self.radiocarbon_df["context"]).index(i)]) for i in context_no
        ]
        rcd_err = [
            int(list(self.radiocarbon_df["error"])[list(self.radiocarbon_df["context"]).index(i)]) for i in context_no
        ]
        # Write calibration inputs to disk in csv
        input_1 = [
            strat_vec,
            rcd_est,
            rcd_err,
            key_ref,
            context_no,
            self.phi_ref,
            self.prev_group,
            self.post_group,
            topo_sort,
            self.context_types,
        ]
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)
        f = open(workdir / "input_file", "w")
        writer = csv.writer(f)
        writer.writerow(input_1)
        f.close()

        # Load calibration data.
        self.__calibration: InterpolatedRCDCalibrationCurve = InterpolatedRCDCalibrationCurve()

        context_no, accept, phi_accept, phi_ref, A, P, all_samples_context, all_samples_phi = run_MCMC(
            self.__calibration.df,
            strat_vec,
            rcd_est,
            rcd_err,
            key_ref,
            context_no,
            self.phi_ref,
            self.prev_group,
            self.post_group,
            topo_sort,
            self.context_types,
        )
        _, accept_group_limits, all_group_limits = phase_labels(phi_ref, self.post_group, phi_accept, all_samples_phi)
        for i, j in enumerate(context_no):
            accept_group_limits[j] = accept[i]
        for k, l in enumerate(context_no):
            all_group_limits[l] = all_samples_context[k]

        return (
            context_no,
            accept,
            phi_accept,
            phi_ref,
            A,
            P,
            all_samples_context,
            all_samples_phi,
            accept_group_limits,
            all_group_limits,
        )
