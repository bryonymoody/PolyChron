import csv
import json
import os
import pathlib
import shutil
import sys
from dataclasses import dataclass, field
from importlib.metadata import version
from typing import Any, Dict, List, Literal, Optional, Tuple

import networkx as nx
import pandas as pd
import pydot
from graphviz import render
from networkx.drawing.nx_pydot import write_dot
from PIL import Image

from ..automated_mcmc_ordering_coupling_copy import run_MCMC
from ..util import node_coords_fromjson, phase_info_func, phase_labels, rank_func, trim
from .InterpolationData import InterpolationData


@dataclass
class Model:
    """MVP Model representing a polychron model.

    @todo - refactor some parts out into other clasess (which this has an isntance of)
    @todo - add setters/getters to avoid direct access of values which are not intended to be directly mutable.
    @todo - Multiple instances of the same model will both create files on disk, overwriting one another. Add locking to prevent this?
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

    context_no_unordered: Optional[List[Any]] = field(default=None)
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

    phase_true: int = 0
    """If stratigraphic diagrams should be rendered in phases or not
    
    @todo - make a bool, rename
    @todo - should this belong to the .model.Model?
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

    CONTEXT_NO: List[Any] = field(default_factory=list)
    """List of contexts? passed in to and returned by run_MCMC, 
    @todo document it's contents
    @todo typehint
    @todo try and improve when it is set / read?"""

    ACCEPT: List[List[Any]] = field(default_factory=lambda: [[]])
    """An optional value returned from MCMC_func.
    A list of lists, where the minimum inner list length is used to dermine if more rounds of MCMC are required?
    
    Formerly StartPage.ACCEPT
    @todo - rename, rehome, typehint, docstring, maybe don't even store?
    """

    PHI_ACCEPT: Optional[Any] = field(default=None)
    """An optional value returned from MCMC_func. Appears unused.
    
    Formerly StartPage.PHI_ACCEPT
    @todo - rename, rehome, typehint, docstring, maybe don't even store?
    """

    A: int = field(default=0)
    """An integer set as a result from MCMC_func. Never actually read so doesn't need storing?

    Formerly StartPage.A
    @todo - rename, rehome, maybe don't even store?"""

    P: int = field(default=0)
    """An integer set as a result from MCMC_func. Never actually read so doesn't need storing?

    Formerly StartPage.P
    @todo - rename, rehome, maybe don't even store?"""

    ALL_SAMPS_CONT: Optional[Any] = field(default=None)
    """An optional value, initailised to None which is a MCMC_func ouptut, that is not used anywhere?

    Formerly StartPage.ALL_SAMPS_CONT
    @todo - rename, rehome, typehint, maybe don't even store?"""

    ALL_SAMPS_PHI: Optional[Any] = field(default=None)
    """An optional value, initailised to None which is a MCMC_func ouptut, that is not used anywhere?

    Formerly StartPage.ALL_SAMPS_PHI
    @todo - rename, rehome, typehint, maybe don't even store?"""

    resultsdict: Dict[Any, Any] = field(default_factory=dict)
    """A dictionary of results? returned by MCMC_func, which is used for plotting the mcmc results.
    
    Formerly StartPage.resultsdict
    @todo - rename, rehome, typehint, docstring
    """

    all_results_dict: Dict[Any, Any] = field(default_factory=dict)
    """A dictionary of all_results? returned by MCMC_func, which is used to find the phase lenghts during node finding on the results page.
    
    Formerly StartPage.all_results_dict
    @todo - rename, rehome, typehint, docstring
    """

    def get_working_directory(self) -> pathlib.Path:
        """Get the working directory to be used for dynamically created files

        This allows the "saved" version of the model to differe from the version currently being worked on. I.e. the rendered chronological graph used in the UI as changes are made can be different to the version from when save the model was last saved.

        @todo - use this.
        """
        return self.path / "temp"

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
        data = self.__dict__.copy()
        subset_keys = ["name", "path", "strat_df", "strat_graph"]
        data = {k: v for k, v in data.items() if k in subset_keys}

        # Remove anything we don't want to save to disk @todo
        # del data["key"]

        # Convert types which cannot nateively be serialised to json to other representations @Todo single pass?
        for k in data:
            if isinstance(data[k], tuple([str, int, float])):
                pass
            elif isinstance(data[k], pathlib.Path):
                data[k] = str(data[k])
            elif isinstance(data[k], pd.DataFrame):
                # For dataframes, export to json so pandas handles the type conversion, before returning to a python object.
                data[k] = json.loads(data[k].to_json())
            elif isinstance(data[k], nx.DiGraph):
                print(
                    "@todo - decide how to encode networkx graphs as json. Maybe save to .dot instead and load from disk?"
                )
                data[k] = "@todo"
            else:
                data[k] = str[data[k]]

        indent = 2 if pretty else None
        return json.dumps({"polychron_version": version("polychron"), "model": data}, indent=indent)

    def save(self) -> None:
        """Save the current state of this model to disk at self.path

        Raises:
            Exception: raised when any error occured during saving, with a message to present to the user. @todo specialise the exception type(s)

        @todo - need to ensure that on save, all temp files in the project directory are correct for the saved model & not overwrite the "saved" versions if mutating in gui without saving? On load, images should be regenerated to ensure they match the saved state of the serialised data?"""
        print(f"@todo - Model.save({self.path})")

        # Ensure directories requried exist
        if self.create_dirs():
            try:
                # create the represenation of the model to be saved to disk
                json_s = self.to_json(pretty=True)
                print(json_s)

                # Ensure the "saved" versions of files are up to date.
                # @todo - also ensure the rendered version on disk is current
                # Esnure chronological graph output files are saved
                for filename in ["fi_new_chrono.png", "fi_new_chrono.svg", "fi_new_chrono", "testdag_chrono.png"]:
                    src = self.get_working_directory() / filename
                    dst = self.get_chronological_graph_directory() / filename
                    if src.is_file():
                        shutil.copy(src, dst)

                # Ensure stratigraphic graph files are saved
                for filename in ["fi_new.png", "fi_new.svg", "fi_new", "testdag.png"]:
                    src = self.get_working_directory() / filename
                    dst = self.get_stratigraphic_graph_directory() / filename
                    if src.is_file():
                        shutil.copy(src, dst)

                # Save the delte contexts metadata (Formerly StartPage.tree2, in save_state_1)
                deleted_contexts_cols = ("context", "Reason for deleting")
                # @todo - handle newlines?
                deleted_contexts_rows = [[x[0], x[1]] for x in self.delnodes]
                deleted_contexts_df = pd.DataFrame(deleted_contexts_rows, columns=deleted_contexts_cols)
                deleted_contexts_meta_path = (
                    self.get_stratigraphic_graph_directory() / "deleted_contexts_meta"
                )  # @todo .csv
                deleted_contexts_df.to_csv(deleted_contexts_meta_path)  # @todo - for all to_csv, don't save the index

                # Ensure mcmc results are saved
                # for filename in []:
                #     src = self.get_working_directory() / filename
                #     dst = self.get_mcmc_results_directory() / filename
                #     if src.is_file():
                #         shutil.copy(src, dst)

                # if the mcmc has been ran, store some files to disk. Formerly part of StartPage.save_state_1
                if self.mcmc_check:
                    df = pd.DataFrame()
                    for i in self.all_results_dict.keys():
                        df[i] = self.all_results_dict[i][10000:]
                    full_results_df_path = self.get_mcmc_results_directory() / "full_results_df"  # @todo .csv?
                    df.to_csv(full_results_df_path)

                    key_ref = [
                        list(self.phase_df["Group"])[list(self.phase_df["context"]).index(i)] for i in self.CONTEXT_NO
                    ]
                    df1 = pd.DataFrame(key_ref)
                    df1.to_csv(self.get_mcmc_results_directory() / "key_ref.csv")
                    df2 = pd.DataFrame(self.CONTEXT_NO)
                    df2.to_csv(self.get_mcmc_results_directory() / "context_no.csv")

                # Ensure any copyable python_only files are saved
                # for filename in []:
                #     src = self.get_working_directory() / filename
                #     dst = self.get_python_only_directory() / filename
                #     if src.is_file():
                #         shutil.copy(src, dst)

                # Save the json representation of this object to disk
                json_path = self.get_python_only_directory() / "polychron_model.json"

                with open(json_path, "w") as f:
                    f.write(json_s)

            except Exception as e:
                raise Exception(f"@todo - an exeption occurred during saving:\n {e}")
        else:
            raise Exception("@todo - could not create model directories")

    @classmethod
    def load_from_disk(cls, path: pathlib.Path) -> "Model":
        """Get an instance of the model from serialised json on disk.

        @todo how to handle version compatible saving/loading?
        @todo rename method / wrap in a from_path() method which expects a json file + other sturctures?"""

        # Ensure required files/folders are present
        if not path.is_file():
            raise Exception("@todo file does not exist")

        # Attempt to open the Model json file, building an instance of Model
        with open(path, "r") as f:
            data = json.load(f)

            # Raise an excpetion if required keys are missing
            if "polychron_version" not in data:
                # @todo - missing version might just mean we assume a current one?
                raise Exception("@todo - bad json, missing version")
            if "model" not in data:
                raise Exception("@todo - bad json, missing model")

            polychron_version = data["polychron_version"]
            print(f"model saved with {polychron_version}")
            if polychron_version == "0.2.0":
                # @todo version specific stuff if required.
                pass

            model_data = data["model"]

            # Convert back to specific types
            model_data["path"] = pathlib.Path(model_data["path"])

            # Create an instance of the Model
            model: Model = cls(**model_data)

            # Perform any post-loading steps
            pass  # @todo

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
        if self.phase_true == 1:
            self.__render_strat_graph_phase()
        else:
            self.__render_strat_graph()

    def render_resid_or_intru_strat_graph(self) -> None:
        """Render the residual or intrusive sratigraphic graph as a png and svg, with or without phasing depending on model state. Also updates the locatison of each node

        This graph will have different presentation information to highlight which contexts have been marked as residual or intrusive.

        @todo - don't return?
        @todo - de-duplicate"""
        # Call the appropraite render_strat method, depending if the model is set up to render in phases or not.
        if self.phase_true == 1:
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
