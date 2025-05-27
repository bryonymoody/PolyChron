import csv
import filecmp
import json
import os
import pathlib
import shutil
import sys
from dataclasses import dataclass, field
from importlib.metadata import version
from typing import Any, Dict, List, Literal, Optional, Tuple, get_type_hints

import networkx as nx
import pandas as pd
import pydot
from graphviz import render
from networkx.drawing.nx_pydot import write_dot
from PIL import Image

from ..automated_mcmc_ordering_coupling_copy import run_MCMC
from ..models.MCMCData import MCMCData
from ..util import node_coords_fromjson, phase_info_func, phase_labels, rank_func, trim
from .InterpolationData import InterpolationData


@dataclass
class Model:
    """MVP Model representing a polychron model.

    @todo - refactor some parts out into other clasess (which this has an isntance of)
    @todo - add setters/getters to avoid direct access of values which are not intended to be directly mutable.
    @todo - Multiple instances of the same model will both create files on disk, overwriting one another. Add locking to prevent this?
    @todo - stop this being a dataclass? it's got complex enough that it's own ctor might be required(for **kwargs to allow robust partial deserialisetion)
    """

    name: str
    """The name of the model within the project (unique)"""

    path: pathlib.Path
    """The path to the directory representing this model on disk
    
    @todo - this and name are not both required, could have parent_path and an dynamic path? (i.e. avoid duplication during construction). Or even require path to be proivided for save() and load()
    """

    strat_dot_file_input: Optional[pathlib.Path] = field(default=None)
    """Stratigraphic path for .dot/.gv input
    
    Formerly StartPage.FILE_INPUT
    
    @todo rename"""

    strat_df: Optional[pd.DataFrame] = field(default=None)
    """The stratigraphic file from CSV, if loaded.

    Formerly StartPage.stratfile
    
    @todo - refactor this to be it's own model class which performs validation etc?"""

    strat_graph: Optional[nx.DiGraph] = field(default=None)
    """Stratigraphic Graph as a networkx digraph, after loading from csv / .dot and post processed.

    Mutate when other files are loaded.
    
    @todo @enhancement - When a new strat_df is loaded, clear other members, or re-apply the smae changes to strat_graph?
    """

    strat_image: Optional[Image.Image] = field(default=None)
    """Rendered version of the stratigraphic graph as an image, for whicle a handle must be kept for persistence.

    @todo Could belong to the presenter instead"""

    date_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe containing scientific dating information loaded from disk
    
    Fromerly StartPage.datefile

    @todo - refactor this to be it's own model class which performs validation etc?"""

    context_no_unordered: Optional[List[str]] = field(default=None)
    """A list of stratigraphic graph nodes, initially populated within open_scientific_dating_file before being used elsewhere.

    @todo - correct annotation
    @todo - better name? make this private/protected?
    @todo - does this belong to a separate class which represents a stratigraphic graph instead?
    @todo - make this only settable by method?
    """

    phase_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe containing phase / context grouping information loaded from disk
    
    Fromerly StartPage.phasefile

    @todo - refactor this to be it's own model class which performs validation etc?"""

    phase_rel_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe containing phase / group relationships information loaded from disk
    
    Fromerly  just phase_rel_df in StartPage.open_file5
    
    @todo - refactor this to be it's own model class which performs validation etc?"""

    phase_rels: Optional[List[Tuple[str, str]]] = field(default=None)
    """A list of tuples of group/phase labels, (above, below) for the relative relationships between two groups/phases

    @todo - better name? make this private/protected?
    @todo - does this belong to a separate class which represents a stratigraphic graph instead?
    @todo - make this only settable by method?
    """

    equal_rel_df: Optional[pd.DataFrame] = field(default=None)
    """Dataframe containing context equality relationship information loaded from disk
    
    Fromerly  just phase_rel_df in StartPage.open_file5

    @todo - define and validate the column names?
    
    @todo - refactor this to be it's own model class which performs validation etc?"""

    load_check: bool = False
    """If the chronological graph has been rendered for the current state of the model
    
    Formerly a global load_check, where "loaded" is now True and "not_loaded" is False.

    @todo - make this a private / protected
    @todo - rename
    @todo - double check all occurences have been met
    """

    chrono_dag: Optional[nx.DiGraph] = field(default=None)
    """Chronological directed graph, produced by rendereing the chronological graph
    
    @todo - move function which generates this into this class (or an object for the chronograph with it's other bits)
    @todo - rename?
    @todo - setter&getter with protected member?
    """

    chrono_image: Optional[Image.Image] = field(default=None)
    """Rendered version of the Chronological graph as an image, for whicle a handle must be kept for persistence and to avoid regenerating when not required.

    When load_check is True, this image is valid for the current state of the Model.

    @todo - migrate generation of this into a class method, and only provide a public getter.

    Formerly StartPage.image2
    """

    mcmc_check: bool = False
    """If the model has been calibrated
    
    Formerly a global mcmc_check, where "mcmc_loaded" is now True and "mcmc_notloaded" is False.

    @todo - make this a private / protected
    @todo - rename
    @todo - double check all occurences have been met
    """

    delnodes: List[Tuple[str, str]] = field(default_factory=list)
    """List of deleted nodes and the reason they were deleted
    
    Formerly StartPage.delnodes and StartPage.delnodes_meta
    @todo - make a list of a dataclass instead? Not using a dict so the same node can be deleted, added, then deleted again
    """

    deledges: List[Tuple[str, str, str]] = field(default_factory=list)
    """List of deleted edges and the reason they were deleted

    Each entry is the a node, b node and reason.
    
    Formerly StartPage.edges_del and StartPage.deledges_meta
    @todo - make a list of a dataclass instead? Not using a dict so the same node can be deleted, added, then deleted again
    """

    resid_or_intru_strat_graph: Optional[nx.DiGraph] = field(default=None)
    """Copy of strat_graph for the residual or intrusive window

    This is mutated to show which nodes have been marked as residual or intrusive.

    Formerly PageTwo.graphcopy

    @todo - move this a model class for the residual or intrusive page.
    """

    resid_or_intru_strat_image: Optional[Image.Image] = field(default=None)
    """Image handle for the rendered png of the stratigraphic graph with residual or intrusive node highlighting.

    A handle to this needs to be maintained to avoid garbage collection

    Formerly PageTwo.image

    @todo - move this a model class for the residual or intrusive page.
    """

    intru_list: List[str] = field(default_factory=list)
    """List of intrusive contexts/nodes.

    Formerly PageTwo.intru_list

    @todo - move this a model class for the residual or intrusive page.
    """

    resid_list: List[str] = field(default_factory=list)
    """List of residual contexts/nodes.

    Formerly PageTwo.resid_list

    @todo - move this a model class for the residual or intrusive page.
    """

    intru_dropdowns: Dict[str, str] = field(default_factory=dict)
    """Dict of selected drop down choice for intrusive context/nodes.

    @todo - move this a model class for the residual or intrusive page?
    @todo - rename?
    @todo - make this a Dict[str, Enum] or Dict[str, Optional[Literal[]]]? 
    """

    resid_dropdowns: Dict[str, str] = field(default_factory=dict)
    """Dict of selected drop down choice for intrusive context/nodes.

    @todo - move this a model class for the residual or intrusive page?
    @todo - rename?
    @todo - make this a Dict[str, Enum] or Dict[str, Optional[Literal[]]]? 
    """

    phase_true: bool = False
    """If stratigraphic diagrams should be rendered in phases or not
    
    @todo - rename
    @todo - initalse these variables with values from the model on load?
    """

    CONT_TYPE: List[Literal["normal", "residual", "intrusive"]] = field(default_factory=list)
    """Context types, in the same order as context_no_unordered.
    
    Used for calibration / MCMC"""

    prev_phase: List[str] = field(default_factory=list)
    """List of previous phases, with "start" as the 0th value.
    
    Initialised in ManageGroupRelationshipsPresenter.full_chronograph_func

    @todo determine order?"""

    post_phase: List[str] = field(default_factory=list)
    """List of post phases, with "end" as the final value.
    
    Initialised in ManageGroupRelationshipsPresenter.full_chronograph_func

    @todo determine order?"""

    phi_ref: List[str] = field(default_factory=list)
    """Ordered list of context labels.
    
    @todo - ask bryony for a better description
    
    Formerly StartPage.PHI_REF"""

    node_del_tracker: List[str] = field(default_factory=list)
    """List of contexts / nodes for which there was insufficent node or phase info, and has been removed during group relationship management
    
    @todo - double check this description"""

    key_ref: List[Any] = field(default_factory=list)
    """List of something @todo. Generated and used during calibration, used in popupWindow9/10 too 
    
    @todo better docstring
    @todo rename?
    """

    mcmc_data: MCMCData = field(default_factory=MCMCData)
    """MCMC data for this model. Includes values used as inputs and outputs for the MCMC data pase
    
    if mcmc_check is true, it is implied that this has been saved to disk
    """

    node_df: Optional[Tuple[pd.DataFrame, List[float]]] = field(default=None)
    """A tuple contianing a dataframe of node coordinates within the most recently rendered svg graph, and a list of scaled float values.

    Set and used for node right-click detection
    
    Values are returend from node_coords_fromjson

    Previously this was the global variable node_df
    """

    def get_working_directory(self) -> pathlib.Path:
        """Get the working directory to be used for dynamically created files

        This allows the "saved" version of the model to differe from the version currently being worked on. I.e. the rendered chronological graph used in the UI as changes are made can be different to the version from when save the model was last saved.

        @todo - consider the file size implications of this (i.e. we have everything twice).
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
        """Serialise this object to JSON

        @todo decide which bits to exclude form saving/loading, and generate on reconstruction instead.
        @todo - how to handle dataframes, Image.Image, files on disk, relative vs abs paths in the case a directory has been copied.
        """
        # Create a dictionary contianing a subset of this instance's member variables, converted to formats which can be json serialised.
        data = {}
        exclude_keys = [
            "path",  # Don't include the path, so models can be trivially copied on disk
            "strat_image",  # don't include image handles
            "chrono_image",  # don't include image handles
            "resid_or_intru_strat_image",  # don't include image handles
            "node_df",  # don't include the the locations of images from svgs?
            "mcmc_data",  # don't include the mcmc_data object, which has been saved elsewhere. @todo include a relative path in it's place?
        ]
        for k, v in self.__dict__.items():
            if k not in exclude_keys:
                if v is None:
                    # @todo - decide what to do for None values, include or not.
                    data[k] = v
                    # pass
                elif isinstance(v, tuple([str, int, float, list, dict, tuple])):
                    # @todo - may need to recurse into lists, dicts and tuples to make sure their members are all json serialiseable
                    data[k] = v
                elif isinstance(v, pathlib.Path):
                    data[k] = str(v)
                elif isinstance(v, pd.DataFrame):
                    # For dataframes, export to json so pandas handles the type conversion, before returning to a python object.
                    # @todo - this is a lot of float > str and str > float conversion for calibration data which is not free.
                    data[k] = json.loads(v.to_json(orient="columns"))
                elif isinstance(v, nx.DiGraph):
                    # Encode graphs as json via networkx node_link_data, which can be de-serialised via node_link_graph. This should be safe for round-trips, other than node names being converted to strings (which they are anyway)
                    # explicitly set edges value to future behaviour for networkx
                    data[k] = nx.node_link_data(v, edges="edges")
                else:
                    data[k] = str(v)

        indent = 2 if pretty else None
        return json.dumps({"polychron_version": version("polychron"), "model": data}, indent=indent)

    def save(self) -> None:
        """Save the current state of this model to disk at self.path

        Raises:
            Exception: raised when any error occured during saving, with a message to present to the user. @todo specialise the exception type(s)

        Todo:
            @todo - need to ensure that on save, all temp files in the project directory are correct for the saved model & not overwrite the "saved" versions if mutating in gui without saving? On load, images should be regenerated to ensure they match the saved state of the serialised data?
            @todo - delete out of date files on save. I.e. MCMC should be deleted if the model has been mutated?
            @todo - de-duplicate saving things to disk. I.e. full_results_df is included int he MCMCData json file as well as it's own file (but may not be the same data?)
            @todo - stripout save timing
        """
        import time

        time_start = time.monotonic()

        # Ensure directories requried exist
        if self.create_dirs():
            try:
                # create the represenation of the model to be saved to disk
                json_s = self.to_json(pretty=True)
                print(f"json_s len: {len(json_s)}")

                time_copy_start = time.monotonic()

                # Save the delete contexts metadata to the working directory (superfluos)
                self.save_deleted_contexts()

                # Ensure the "saved" versions of files are up to date.
                # @todo - also ensure the rendered version on disk is current
                # Esnure chronological graph output files are saved
                for filename in ["fi_new_chrono.png", "fi_new_chrono.svg", "fi_new_chrono", "testdag_chrono.png"]:
                    src = self.get_working_directory() / filename
                    dst = self.get_chronological_graph_directory() / filename
                    # Only copy the file, if the src exists and is not the same as the dst file
                    if src.is_file() and (not dst.is_file() or not filecmp.cmp(src, dst, shallow=True)):
                        shutil.copy(src, dst)

                # Ensure stratigraphic graph files are saved
                for filename in ["fi_new.png", "fi_new.svg", "fi_new", "testdag.png", "deleted_contexts_meta"]:
                    src = self.get_working_directory() / filename
                    dst = self.get_stratigraphic_graph_directory() / filename
                    # Only copy the file, if the src exists and is not the same as the dst file
                    if src.is_file() and (not dst.is_file() or not filecmp.cmp(src, dst, shallow=True)):
                        shutil.copy(src, dst)

                # Ensure mcmc results are saved
                for filename in ["full_results_df", "key_ref.csv", "context_no.csv"]:
                    src = self.get_working_directory() / filename
                    dst = self.get_mcmc_results_directory() / filename
                    # Only copy the file, if the src exists and is not the same as the dst file
                    if src.is_file() and (not dst.is_file() or not filecmp.cmp(src, dst, shallow=True)):
                        shutil.copy(src, dst)

                # Ensure any copyable python_only files are saved
                for filename in ["polychron_mcmc_data.json"]:
                    src = self.get_working_directory() / filename
                    dst = self.get_python_only_directory() / filename
                    # Only copy the file, if the src exists and is not the same as the dst file
                    if src.is_file() and (not dst.is_file() or not filecmp.cmp(src, dst, shallow=True)):
                        shutil.copy(src, dst)

                # Save the json representation of this object to disk
                json_path = self.get_python_only_directory() / "polychron_model.json"

                time_copy_end = time.monotonic()

                with open(json_path, "w") as f:
                    f.write(json_s)

                time_end = time.monotonic()
                print(f"elapsed_save {time_end - time_start: .6f}s")
                print(f"  elapsed_tojson {time_copy_start - time_start: .6f}s")
                print(f"  elapsed_copy {time_copy_end - time_copy_start: .6f}s")
                print(f"  elapsed_write {time_end - time_copy_end: .6f}s")

            except Exception as e:
                raise Exception(f"@todo - an exeption occurred during saving:\n {e}")
        else:
            raise Exception("@todo - could not create model directories")

    @classmethod
    def load_from_disk(cls, path: pathlib.Path) -> "Model":
        """Get an instance of the model from serialised json on disk.

        Parameters:
            path: Path to a model directory (not the json file)

        Raises:
            RuntimeWarning - when the model could not be loaded, but in a recoverable way. I.e. the directory exits but no files are contained (so allow the model to be "loaded") @todo - probably change this?
            RuntiemError - when the model could not be loaded, but use of this model directory should be prevented?

        Todo:
            - @todo how to handle version compatible saving/loading?
            - @todo async loading of mcmc data?
        """

        # Ensure required files/folders are present
        if not path.is_dir():
            raise RuntimeWarning(f"Error loading from Model from path '{path}' it is not a directory")

        # Ensure the json file exists
        model_json_path = path / "python_only" / "polychron_model.json"  # @todo - reduce string literals?
        if not model_json_path.is_file():
            # @todo - decide if this should be an exception or not.
            # raise RuntimeWarning(f"Error loading Model from json file '{model_json_path}' it is not a file")
            # Return a Model instance with just the path and name set, if no json do to load
            return cls(name=path.name, path=path)

        # Attempt to open the Model json file, building an instance of Model
        with open(model_json_path, "r") as f:
            data = json.load(f)

            # Raise an excpetion if required keys are missing
            if "polychron_version" not in data:
                # @todo - missing version might just mean we assume a current one?
                raise RuntimeError("@todo - bad json, missing version")
            if "model" not in data:
                raise RuntimeError("@todo - bad json, missing model")

            model_data = data["model"]

            polychron_version = data["polychron_version"]
            if polychron_version == "0.2.0":
                pass

            # Convert certain values back based on the hint for the data type.
            # @todo - find a more robust way to compare type hints to literal types? in the case of unions etc?
            cls_type_hints = get_type_hints(cls)
            # Also build a list of keys to remove
            unexpected_keys = []
            for k in model_data:
                if k in cls_type_hints:
                    type_hint = cls_type_hints[k]

                    # If the values is None, do nothing. @todo - should this only be possible for Optionals?
                    if model_data[k] is None:
                        pass
                    elif type_hint in [pathlib.Path, Optional[pathlib.Path]]:
                        model_data[k] = pathlib.Path(model_data[k])
                    elif type_hint in [pd.DataFrame, Optional[pd.DataFrame]]:
                        # DataFrames are encoded as json, parsed back into a dictionary before being encoded as json again. At this point, the first json decode has occurred so we should have a dictionary of dictionaries (one per column) which can be reconverted.
                        # However, this may have lost typing information for the columns, but they were probably all strings anyway? @todo check this.
                        if isinstance(model_data[k], dict):
                            model_data[k] = pd.DataFrame.from_dict(model_data[k], orient="columns")
                    elif type_hint in [nx.DiGraph, Optional[nx.DiGraph]]:
                        # Convert the node_link_data encoded networkx digraph via node_link_graph
                        # explicitly set edges value to future behaviour for networkx
                        model_data[k] = nx.node_link_graph(model_data[k], edges="edges", multigraph=False)

                    elif type_hint in [Optional[List[Tuple[str, str]]]]:
                        # phase_rels needs to be returned to a tuple. @todo need to do this less specifically?
                        model_data[k] = [tuple(sub) for sub in model_data[k]]
                else:
                    # If the key is not in the typehints, it will cause the ctor to trigger a rutnime assertion, so remove it.
                    # @todo - make this visible in the UI?
                    print(f"Warning: unexected Model member '{k}' during deserialisation")
                    unexpected_keys.append(k)

                # @todo -  trycast.isassignable? maybe to check for the correct type?
                # if the type hint is not subscripted, do a direct comparions
                # print(f"> {type_hint}")
                # if get_origin(type_hint) is None:
                #     print(f"unsubscripted ({type_hint}) is instance {model_data[k]}? {isinstance(model_data[k], type_hint)}")
                # else:
                #     # For each substitution
                #     for x in get_args(type_hint):
                #         if get_origin(x) is None:
                #             print(f"subscripted ({x}) is instance  {model_data[k]}? {isinstance(model_data[k], x)}")
                #         else:
                #             "recursion needed @todo"

                # if type(model_data[k]) != type_hint:
                #     print(f"{k}: {type(model_data[k])} != {type_hint}, {isinstance(model_data[k], type_hint)}")

            # for k, v in model_data.items():
            #     print(k, type(v))

            # Remove any unexpected keys
            for k in unexpected_keys:
                del model_data[k]

            # Overwrite certain elements, i.e the path (in case the model fiels have been copied), but the path was included in the save file
            model_data["path"] = path

            # Ensure that some elements are not stored, if they are explictly handled otherwise
            if "mcmc_data" in model_data:
                del model_data["mcmc_data"]

            # Create an instance of the Model
            model: Model = cls(**model_data)

            # If mcmc has been ran for this model, and the expected mcmc data file exists, load it.
            if model.mcmc_check:
                mcmc_data_path = model.get_python_only_directory() / "polychron_mcmc_data.json"
                if mcmc_data_path.is_file():
                    model.mcmc_data = MCMCData.load_from_disk(mcmc_data_path)
                else:
                    print(f"Failed to load MCMCData {mcmc_data_path} @todo - exception?.")

            # Handle non-json loading of files (copy over temp?)
            pass  # @todo

            # Perform any post-loading steps            model.path = path
            # @todo - validate that the name of the model matches the path? Or don't store the name of the model, infer it from the path? (maybe always set it to the name of the model directory, so on disk it's ok until first re-saved)
            # @todo - others

            # Return the Model
            return model

        # If this point is reached, an error occurred and should be propagated @todo
        return None

    def create_dirs(self) -> bool:
        """Create the expected directories for this model, including wokring directories.

        Returns:
            Boolean indicating success of directory creation

        Formerly part of load_Window.create_file, popupWindow9.make_directories & popupWindow10.make_directories"""

        try:
            # Ensure the model (and implictly project) directory exists
            self.path.mkdir(parents=True, exist_ok=True)
            # Create each expected child directory. @todo make this class members instead so they can be accessed directly?
            # @todo - these directories do not get consistently used by 0.1.
            expected_model_dirs = [
                self.get_stratigraphic_graph_directory(),
                self.get_chronological_graph_directory(),
                self.get_mcmc_results_directory(),
                self.get_python_only_directory(),
                self.get_working_directory(),
            ]
            for path in expected_model_dirs:
                path.mkdir(parents=True, exist_ok=True)

            # Change the working dir to the model directory. @todo decide if this is desirbale or not.
            os.chdir(self.path)

        except Exception as e:
            # @todo - better error handling. Should be due to permsissions, invalid filepaths or disk issues only
            print(e, file=sys.stderr)
            return False
        return True

    def save_deleted_contexts(self) -> None:
        """Save the delete contexts metadata to disk

        Formerly StartPage.tree2, in save_state_1

        Todo:
            @todo - .csv extension on the file
            @todo - for all to_csv, use index=False
            @todo - handle newlines in the CSV export correctly.
        """

        cols = ("context", "Reason for deleting")
        rows = [[x[0], x[1]] for x in self.delnodes]
        df = pd.DataFrame(rows, columns=cols)
        path = self.get_working_directory() / "deleted_contexts_meta"
        df.to_csv(path)

    def set_strat_dot_file_input(self, file_input: str | pathlib.Path) -> None:
        """provdided a .dot/.gv file path, set the model input."""
        self.strat_dot_file_input = pathlib.Path(file_input)

    def set_strat_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe for stratigraphic relationships, set the values locally and post-process it to produce the stratgiraphic graph

        @todo return value"""

        self.strat_df = df.copy()
        G = nx.DiGraph(graph_attr={"splines": "ortho"})
        set1 = set(self.strat_df.iloc[:, 0])
        set2 = set(self.strat_df.iloc[:, 1])
        set2.update(set1)
        node_set = {x for x in set2 if x == x}
        for i in set(node_set):
            G.add_node(i, shape="box", fontname="helvetica", fontsize="30.0", penwidth="1.0", color="black")
            G.nodes()[i].update({"Determination": [None, None]})
            G.nodes()[i].update({"Group": None})
        edges = []
        for i in range(len(self.strat_df)):
            a = tuple(self.strat_df.iloc[i, :])
            if not pd.isna(a[1]):
                edges.append(a)
        G.add_edges_from(edges, arrowhead="none")
        self.strat_graph = G

    def set_date_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe for date information, set the values locally and perform follow up actions

        @todo return value"""
        # Store a copy of the dataframe
        self.date_df = df.copy()
        # Post process
        self.date_df = self.date_df.applymap(str)
        # @todo - better handling of loading strat graph after date.
        if self.strat_graph:
            for i, j in enumerate(self.date_df["context"]):
                self.strat_graph.nodes()[str(j)].update(
                    {"Determination": [self.date_df["date"][i], self.date_df["error"][i]]}
                )
        # @todo - consider a better way to manage this.
        self.context_no_unordered = list(self.strat_graph.nodes())

    def set_phase_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe for phase / context grouping information, set the values locally and perform post processing

        Formerly phasefile

        @todo validation

        @todo return value"""
        # Store a copy of the dataframe
        self.phase_df = df.copy()
        # Post processing of the dataframe
        # @todo - better handling of loading strat graph after date.
        if self.strat_graph:
            for i, j in enumerate(self.phase_df["context"]):
                self.strat_graph.nodes()[str(j)].update({"Group": self.phase_df["Group"][i]})

    def set_phase_rel_df(self, df: pd.DataFrame, phase_rels: List[Tuple[str, str]]) -> None:
        """Provided a dataframe for phase / group relationships information, set the values locally and post-process

        @todo - make this consistent with other setters.

        @todo validate the incoming df here (and/or elsewhere)

        @todo return value"""
        # Store a copy of the dataframe
        self.phase_rel_df = df.copy()
        # Store a copy of the list of tuples extracted from the dataframe
        self.phase_rels = phase_rels.copy()
        # Post processing of the dataframe

    def set_equal_rel_df(self, df: pd.DataFrame) -> None:
        """Provided a dataframe for context equality relationship information, set the values locally and post-process

        @todo - make this consistent with other setters.

        @todo validate the incoming df here (and/or elsewhere). I.e. c,d; d,c is a runtime error, or loading a context equalities file that has alrady been applied is an error

        @todo return value"""
        # Store a copy of the dataframe
        self.equal_rel_df = df.copy()

        # Post processing of the dataframe
        self.equal_rel_df = self.equal_rel_df.applymap(str)
        context_1 = list(self.equal_rel_df.iloc[:, 0])
        context_2 = list(self.equal_rel_df.iloc[:, 1])
        for k, j in enumerate(context_1):
            self.strat_graph = nx.contracted_nodes(self.strat_graph, j, context_2[k])
            x_nod = list(self.strat_graph)
            newnode = str(j) + " = " + str(context_2[k])
            y_nod = [newnode if i == j else i for i in x_nod]
            mapping = dict(zip(x_nod, y_nod))
            self.strat_graph = nx.relabel_nodes(self.strat_graph, mapping)

    def render_strat_graph(self) -> None:
        """Render the sratigraphic graph as a png and svg, with or without phasing depending on model state. Also updates the locatison of each node via the svg

        @todo - don't return?
        @todo - de-duplicate"""
        # Call the appropraite render_strat method, depending if the model is set up to render in phases or not.
        if self.phase_true:
            self.__render_strat_graph_phase()
        else:
            self.__render_strat_graph()

    def render_resid_or_intru_strat_graph(self) -> None:
        """Render the residual or intrusive sratigraphic graph as a png and svg, with or without phasing depending on model state. Also updates the locatison of each node

        This graph will have different presentation information to highlight which contexts have been marked as residual or intrusive.

        @todo - don't return?
        @todo - de-duplicate"""
        # Call the appropraite render_strat method, depending if the model is set up to render in phases or not.
        if self.phase_true:
            self.__render_resid_or_intru_strat_graph_phase()
        else:
            self.__render_resid_or_intru_strat_graph()

    def __render_strat_graph(self) -> None:
        """Render the stratigraphic graph mutating the Model state

        Formerly imgrender

        @todo - de-duplicate with the residual or intrusive verisons. Both might not striclty be required.
        @todo - better filenames + subdirectory.
        """

        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)  # @todo shouldn't be neccesary?
        self.strat_graph.graph["graph"] = {"splines": "ortho"}
        write_dot(self.strat_graph, workdir / "fi_new")
        render("dot", "png", workdir / "fi_new")
        render("dot", "svg", workdir / "fi_new")
        inp = Image.open(workdir / "fi_new.png")
        inp_final = trim(inp)
        inp_final.save(workdir / "testdag.png")
        self.strat_image = Image.open(workdir / "testdag.png")
        self.node_df = node_coords_fromjson(self.strat_graph)

    def __render_strat_graph_phase(self) -> None:
        """Render the stratigraphic graph, with phasing mutating the Model state

        Formerly imgrender_phase

        @todo - de-duplicate with the residual or intrusive verisons. Both might not striclty be required.
        @todo - better filenames + subdirectory."""
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)  # @todo shouldn't be neccesary?

        write_dot(self.strat_graph, workdir / "fi_new.txt")
        my_file = open(workdir / "fi_new.txt")
        file_content = my_file.read()
        new_string = rank_func(phase_info_func(self.strat_graph)[0], file_content)
        textfile = open(workdir / "fi_new.txt", "w")
        textfile.write(new_string)
        textfile.close()
        (self.strat_graph,) = pydot.graph_from_dot_file(workdir / "fi_new.txt")
        self.strat_graph.write_png(workdir / "test.png")
        inp = Image.open(workdir / "test.png")
        inp = trim(inp)
        # Call the real .tkraise
        inp.save(workdir / "testdag.png")
        self.strat_image = Image.open(workdir / "testdag.png")
        self.node_df = node_coords_fromjson(self.strat_graph)

    def __render_resid_or_intru_strat_graph(self) -> None:
        """Render the stratigraphic graph mutating the Model state

        Formerly imgrender

        @todo - de-duplicate with the residual or intrusive verisons. Both might not striclty be required.
        @todo - better filenames + subdirectory.
        """

        workdir = (
            self.get_working_directory() / "resid_or_intru"
        )  # @todo - make this render into a subfolder? 0.1 does not.
        workdir.mkdir(exist_ok=True)

        self.resid_or_intru_strat_graph.graph["graph"] = {"splines": "ortho"}
        write_dot(self.resid_or_intru_strat_graph, workdir / "fi_new")
        render("dot", "png", workdir / "fi_new")
        render("dot", "svg", workdir / "fi_new")
        inp = Image.open(workdir / "fi_new.png")
        inp_final = trim(inp)
        inp_final.save(workdir / "testdag.png")
        self.resid_or_intru_strat_image = Image.open(workdir / "testdag.png")
        self.node_df = node_coords_fromjson(self.resid_or_intru_strat_graph)

    def __render_resid_or_intru_strat_graph_phase(self) -> None:
        """Render the stratigraphic graph, with phasing mutating the Model state

        Formerly imgrender_phase

        @todo - de-duplicate with the residual or intrusive verisons. Both might not striclty be required.
        @todo - better filenames + subdirectory."""
        workdir = (
            self.get_working_directory() / "resid_or_intru"
        )  # @todo - make this render into a subfolder? 0.1 does not.
        workdir.mkdir(exist_ok=True)

        write_dot(self.resid_or_intru_strat_graph, workdir / "fi_new.txt")
        my_file = open(workdir / "fi_new.txt")
        file_content = my_file.read()
        new_string = rank_func(phase_info_func(self.resid_or_intru_strat_graph)[0], file_content)
        textfile = open(workdir / "fi_new.txt", "w")
        textfile.write(new_string)
        textfile.close()
        (self.resid_or_intru_strat_graph,) = pydot.graph_from_dot_file(workdir / "fi_new.txt")
        self.resid_or_intru_strat_graph.write_png(workdir / "test.png")
        inp = Image.open(workdir / "test.png")
        inp = trim(inp)
        # Call the real .tkraise
        inp.save(workdir / "testdag.png")
        self.resid_or_intru_strat_image = Image.open(workdir / "testdag.png")
        self.node_df = node_coords_fromjson(self.resid_or_intru_strat_graph)

    def render_chrono_graph(self) -> None:
        """Render the chronological graph as a PNG and an SVG, mutating the Model state

        Formerly imgrender2

        @todo - better temporary file names / paths?
        @todo - working dir / set paths explicitly"""
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)  # @todo - shouldnt be neccessary
        fi_new_chrono = workdir / "fi_new_chrono"  # @todo make this a model member?
        if self.load_check and fi_new_chrono.is_file():
            render("dot", "png", fi_new_chrono)
            render("dot", "svg", fi_new_chrono)  # @todo - is the svg needed?
            inp = Image.open(workdir / "fi_new_chrono.png")
            inp_final = trim(inp)
            # scale_factor = min(canv_width/inp.size[0], canv_height/inp.size[1])
            # inp_final = inp.resize((int(inp.size[0]*scale_factor), int(inp.size[1]*scale_factor)), Image.ANTIALIAS)
            inp_final.save(workdir / "testdag_chrono.png")
            self.chrono_image = Image.open(workdir / "testdag_chrono.png")
        else:
            self.chrono_image = None  # formerly 'No_image'

    def reopen_strat_image(self) -> None:
        """Re-open the stratigraphic image from disk

        Used when the window is reiszed as the in memory copy may have been resized

        Formerly part of StartPage.resize

        @todo - instead of re-opening from disk, maybe keep a separate in-memory copy.
        @todo - actual path"""
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)  # @todo - shouldnt be neccessary
        png_path = workdir / "testdag.png"
        if png_path.is_file():
            self.strat_image = Image.open(png_path)

    def reopen_chrono_image(self) -> None:
        """Re-open the chrono image from disk

        Used when the window is reiszed as the in memory copy may have been resized

        Formerly part of StartPage.resize2

        @todo - instead of re-opening from disk, maybe keep a separate in-memory copy.
        @todo - actual path"""
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)  # @todo - shouldnt be neccessary
        png_path = workdir / "testdag_chrono.png"
        if png_path.is_file():
            self.chrono_image = Image.open(png_path)

    def record_deleted_node(self, context: str, reason: Optional[str] = None) -> None:
        """Method to add a node to the list of deleted nodes

        Patameters:
            context: the context / node which was removed
            reason: the reason the node was deleted, if provided.

        Todo:
            @todo Make this the only way to mutate delnodes?
        """
        self.delnodes.append((context, reason))

    def record_deleted_edge(self, context_a: str, context_b: str, reason: Optional[str] = None) -> None:
        """Method to add an edge to the list of deleted edges

        Patameters:
            context_a: one context from the edge
            context_a: the other context from the edge
            reason: the reason the node was deleted, if provided.

        Todo:
            @todo Make this the only way to mutate deledges?
            @todo include the ccall to remove_edge here (or anotehr func which does both)
        """
        self.deledges.append((context_a, context_b, reason))

    def MCMC_func(self) -> Tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]:
        """run the mcmc calibration on the current model, returning output values without (significantly) mutating state

        gathers all the inputs for the mcmc module and then runs it and returns resuslts dictionaries

        Returns a tuple of calibration results @todo move into a dataclass of it's own?

        Formerly StartPage.MCMC_func
        @todo type hints
        @todo decide if this should mutate state or not (key_ref and CONT_TYPE). it does orinally, but might be better not to as mcmc func needs to be executed multiple times."""

        # @todo - validate that the model is in a state which can be MCMC'd
        if self.chrono_dag is None:
            print("Error: model is not MCMC ready @todo.")
            return  # @todo temp

        context_no = [x for x in list(self.context_no_unordered) if x not in self.node_del_tracker]
        topo = list(nx.topological_sort(self.chrono_dag))
        topo_sort = [x for x in topo if (x not in self.node_del_tracker) and (x in context_no)]
        topo_sort.reverse()
        context_no = topo_sort
        self.key_ref = [list(self.phase_df["Group"])[list(self.phase_df["context"]).index(i)] for i in context_no]
        self.CONT_TYPE = [self.CONT_TYPE[list(self.context_no_unordered).index(i)] for i in topo_sort]
        strat_vec = []
        resids = [j for i, j in enumerate(context_no) if self.CONT_TYPE[i] == "residual"]
        intrus = [j for i, j in enumerate(context_no) if self.CONT_TYPE[i] == "intrusive"]
        # @todo - should this be strat_graph or chrono_dag???
        for i, j in enumerate(context_no):
            if self.CONT_TYPE[i] == "residual":
                low = []
                up = list(self.strat_graph.predecessors(j))
            elif self.CONT_TYPE[i] == "intrusive":
                low = list(self.strat_graph.successors(j))
                up = []
            else:
                up = [k for k in self.strat_graph.predecessors(j) if k not in resids]
                low = [k for k in self.strat_graph.successors(j) if k not in intrus]
            strat_vec.append([up, low])
        # strat_vec = [[list(self.strat_graph.predecessors(i)), list(self.strat_graph.successors(i))] for i in context_no]
        rcd_est = [int(list(self.date_df["date"])[list(self.date_df["context"]).index(i)]) for i in context_no]
        rcd_err = [int(list(self.date_df["error"])[list(self.date_df["context"]).index(i)]) for i in context_no]
        # self.prev_phase, self.post_phase = self.prev_phase, self.post_phase  # @todo - redundent statement
        # Write calibration inputs to disk in csv. @todo make optional?
        input_1 = [
            strat_vec,
            rcd_est,
            rcd_err,
            self.key_ref,
            context_no,
            self.phi_ref,
            self.prev_phase,
            self.post_phase,
            topo_sort,
            self.CONT_TYPE,
        ]
        workdir = self.get_working_directory()
        workdir.mkdir(parents=True, exist_ok=True)  # @todo - shouldnt be neccessary
        f = open(workdir / "input_file", "w")  # @todo .csv
        writer = csv.writer(f)
        #  for i in input_1:
        writer.writerow(input_1)
        f.close()

        # Load calibration data. @todo - pass this into this method rather than loading here.
        calibration: InterpolationData = InterpolationData()
        calibration.load()

        # @todo run_mcmc takes args, and also returns them, even when pass by ref?
        CONTEXT_NO, ACCEPT, PHI_ACCEPT, PHI_REF, A, P, ALL_SAMPS_CONT, ALL_SAMPS_PHI = run_MCMC(
            calibration.get_dataframe(),
            strat_vec,
            rcd_est,
            rcd_err,
            self.key_ref,
            context_no,
            self.phi_ref,
            self.prev_phase,
            self.post_phase,
            topo_sort,
            self.CONT_TYPE,
        )
        _, resultsdict, all_results_dict = phase_labels(PHI_REF, self.post_phase, PHI_ACCEPT, ALL_SAMPS_PHI)
        for i, j in enumerate(CONTEXT_NO):
            resultsdict[j] = ACCEPT[i]
        for k, l in enumerate(CONTEXT_NO):
            all_results_dict[l] = ALL_SAMPS_CONT[k]

        return (
            CONTEXT_NO,
            ACCEPT,
            PHI_ACCEPT,
            PHI_REF,
            A,
            P,
            ALL_SAMPS_CONT,
            ALL_SAMPS_PHI,
            resultsdict,
            all_results_dict,
        )
