import pathlib
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple

import networkx as nx
import pandas as pd
from PIL import Image


@dataclass
class Model:
    """MVP Model representing a polychron model.

    @todo - refactor some parts out into other clasess (which this has an isntance of)
    @todo - add setters/getters to avoid direct access of values which are not intended to be directly mutable.
    """

    name: str
    """The name of the model within the project (unique)"""

    path: pathlib.Path
    """The path to the directory representing this model on disk
    
    @todo - this and name are not both required, could have parent_path and an dynamic path? (i.e. avoid duplication during construction). Or even require path to be proivided for save() and load()
    """

    strat_df: Optional[pd.DataFrame] = field(default=None)
    """The stratigraphic file from CSV, if loaded.

    Formerly StartPage.stratfile
    
    @todo - refactor this to be it's own model class which performs validation etc?"""

    strat_graph: Optional[nx.DiGraph] = field(default=None)
    """Stratigraphic Graph as a networkx digraph, after loading from csv / .dot and post processed.

    Mutate when other files are loaded.
    
    @todo - refactor this and others to only be setable by methods?
    
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

    def save(self):
        """Save the current state of this model to disk at self.path"""
        print(f"@todo - Model.save({self.path})")

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
        """Provided a dataframe for stratigraphic relationships, set the values locally and post-process it to produce the stratgiraphic graph

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
        """Provided a dataframe for stratigraphic relationships, set the values locally and post-process it to produce the stratgiraphic graph

        @todo - make this consistent with other setters.

        @todo validate the incoming df here (and/or elsewhere)

        @todo return value"""
        # Store a copy of the dataframe
        self.phase_rel_df = df.copy()
        # Store a copy of the list of tuples extracted from teh dataframe
        self.phase_rels = phase_rels.copy()
        # Post processing of the dataframe
