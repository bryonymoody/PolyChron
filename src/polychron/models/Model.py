import pathlib
from dataclasses import dataclass, field
from typing import Optional

import networkx as nx
import pandas as pd
from PIL import Image


@dataclass
class Model:
    """MVP Model representing a polychron model."""

    name: str
    """The name of the model within the project (unique)"""

    path: pathlib.Path
    """The path to the directory representing this model on disk
    
    @todo - this and name are not both required, could have parent_path and an dynamic path? (i.e. avoid duplication during construction). Or even require path to be proivided for save() and load()
    """

    strat_df: Optional[pd.DataFrame] = field(default=None)
    """The stratigraphic file from CSV, if loaded.
    
    @todo - refactor this to be it's own model class which performs validation etc?"""

    strat_graph: Optional[nx.DiGraph] = field(default=None)
    """Stratigraphic Graph as a networkx digraph, after loading from csv / .dot and post processed.
    
    @todo - refactor this and others to only be setable by methods?"""

    strat_image: Optional[Image.Image] = field(default=None)
    """Rendered version of the stratigraphic graph as an image, for whicle a handle must be kept for persistence.

    @todo Could belong to the presenter instead"""

    def save(self):
        """Save the current state of this model to disk at self.path"""
        print(f"@todo - Model.save({self.path})")

    def set_strat_df(self, df: pd.DataFrame) -> bool:
        """Provided a dataframe for stratigraphic relationships, set the values locally and post-process it to produce the stratgiraphic graph"""

        self.strat_df = df
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
