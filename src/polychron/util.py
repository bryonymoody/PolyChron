from __future__ import annotations

import ast
import copy
import platform
import re
import time
from typing import Any, Dict, Iterable, List, Literal, Tuple

import networkx as nx
import numpy as np
import packaging.version
import pandas as pd
import pydot
from networkx.drawing.nx_pydot import read_dot
from PIL import Image, ImageChops

"""Utiltiy methods
"""


def trim(im_trim: Image.Image) -> Image.Image:
    """Trims images down, cropping out dark background (<= 100/255 in all channels) unless the whole image is considerd dark (<= 100/255 in all channels)

    Parameters:
        im_trim: Input image to trim

    Returns:
        Potentially cropped version on im_trim
    """
    bg_trim = Image.new(im_trim.mode, im_trim.size)
    diff = ImageChops.difference(im_trim, bg_trim)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    return im_trim.crop(bbox)


def polygonfunc(i: str) -> list[float]:
    """finds node coords of a polygon, from a string extracted from a svg

    Parameters:
        i: substring from an svg string, which shouuld include 'points='

    Returns:
        [x0, x1, y0, y1] - A list of 4 floating point numbers, which are the bounding box of the shape. The origin used is the bottom left, rather than top left in the svg.

    Todo:
        - Instead of using regular expressions, use a SVG (or just xml parsing, which is stdlib but defusedxml should probably be used instead.) library
        - Handle being provided invalid inputs (strings without points)
    """
    x = re.findall(r'points="(.*?)"', i)[0].replace(" ", ",")
    a = x.split(",")
    # if statement checks if it's a rectangle or a kite then gets the right coords
    if -1 * float(a[7]) == -1 * float(a[3]):
        coords_converted = [float(a[2]), float(a[6]), -1 * float(a[5]), -1 * float(a[1])]
    else:
        coords_converted = [float(a[2]), float(a[6]), -1 * float(a[7]), -1 * float(a[3])]
    return coords_converted


def ellipsefunc(i: str) -> list[float]:
    """finds coords from dot file for ellipse nodes, from a string extracted from a svg

    Parameters:
        i: substring from an svg string, which shouuld include 'cx='

    Returns:
        [x0, x1, y0, y1] - A list of 4 floating point numbers, which are the bounding box of the shape. The origin used is the bottom left, rather than top left in the svg.

    Todo:
        - Instead of using regular expressions, use a SVG (or just xml parsing, which is stdlib but defusedxml should probably be used instead.) library
        - Handle being provided invalid inputs (strings without cx=)
    """
    x = re.findall(r"cx=(.*?)/>", i)[0].replace(" ", ",")
    x = x.replace("cy=", "").replace("rx=", "").replace("ry=", "").replace('"', "")
    a = x.split(",")
    coords_converted = [
        float(a[0]) - float(a[2]),
        float(a[0]) + float(a[2]),
        -1 * float(a[1]) - float(a[3]),
        -1 * float(a[1]) + float(a[3]),
    ]
    return coords_converted


def rank_func(tes: dict[str, list[str]], dot_str: str) -> str:
    """adds strings into dot string to make nodes of the same group the same rank

    Parameters:
        tes: a dictionary
        dot_str: The original dot/gv string

    Returns:
        The mutated dot/gv string

    Todo:
        - Rename parameters and variables
        - Use for key, x_rank in tes.items()
        - find the closing } of the digraph instead of always getting rid of the final 2 chars
        - use ",".join(x_rank) and an fstring
        - Close the digraph on it's own line (i.e. add a newline at the end / don't include the [:-1])

    """
    if len(tes) == 0:
        return dot_str
    rank_same = []
    for key in tes.keys():
        x_rank = tes[key]
        y_1 = str(x_rank)
        y_2 = y_1.replace("[", "")
        y_3 = y_2.replace("]", "")
        y_4 = y_3.replace("'", "")
        y_5 = y_4.replace(",", ";")
        x_2 = f"{{rank = same; {y_5};}}\n"
        rank_same.append(x_2)
    rank_string = "".join(rank_same)[:-1]
    new_string = dot_str[:-2] + rank_string + dot_str[-2]
    return new_string


def node_coords_from_svg(svg_string: str) -> tuple[pd.DataFrame, list[float]]:
    """Get the coordinates of each node from a string containing the SVG representation of a graphviz DiGraph.

    Parameters:
        svg_string: The SVG version for a DiGraph. The string should be cast from a byte string and not decoded for the multi-line regular expression to behave

    Returns:
        A dataframe of coordinates, and svg scale information. Y coordinates are inverted, so the origin of coordinates is at the bottom left.
    """
    scale_info = re.search("points=(.*?)/>", svg_string).group(1).replace(" ", ",")
    scale_info = scale_info.split(",")
    scale = [float(scale_info[4]), -1 * float(scale_info[3])]
    coords_x = re.findall(r'id="node(.*?)</text>', svg_string)
    coords_temp = [polygonfunc(i) if "points" in i else ellipsefunc(i) for i in coords_x]
    node_test_pattern = r'node">(\\r)?\\n<title>(.*?)</title>'
    node_test = re.findall(node_test_pattern, svg_string)
    node_list = [i.replace("&#45;", "-") for _, i in node_test]
    new_pos = dict(zip(node_list, coords_temp))
    df = pd.DataFrame.from_dict(new_pos, orient="index", columns=["x_lower", "x_upper", "y_lower", "y_upper"])
    return df, scale


def node_coords_from_dag(graph: nx.DiGraph | pydot.Dot) -> tuple[pd.DataFrame, list[float]]:
    """Get the coordinates of each node from a Directed Acyclic Graph via SVG rendering in graphviz.

    Parameters:
        graph: The networkx or pydot Graph

    Returns:
        A dataframe of coordinates, and svg scale information. Y coordinates are inverted, so the origin of coordinates is at the bottom left.
    """
    # Ensure invalid graph attributes are removed and the graph is available in pydot form
    if "pydot" in str(type(graph)):
        graphs = graph
    else:
        # Ensure the graph is compatible with networkx < 3.4 nx_pydot
        graph = remove_invalid_attributes_networkx_lt_3_4(graph)
        graphs = nx.nx_pydot.to_pydot(graph)

    # Get the svg string for the graph via pydot
    svg_string = str(graphs.create_svg())

    # Extract and return the node coordinates and bounds information from the svg
    return node_coords_from_svg(svg_string)


def phase_info_func(file_graph: nx.DiGraph) -> Tuple[dict[Any, Any], list[Any], list[Any], list[dict[Any, Any]]]:
    """Returns a dictionary of phases and nodes in each phase

    Parameters:
        file_graph: A networkx graph to extract phase information from

    Returns:
        A tuple of results:

        - A Dictionary of phases
        - A list of
        - A list of node labels from the graph (should be strings but not guaranteed)
        - A list of node attribute dictionaries, in the order of node_list

    Todo:
        This has not been fully-reimplemented for cases where stratigraphic data was provided via .dot/.gv file, see FILE_INPUT
    """
    FILE_INPUT = None  # model.stratigraphic_graphviz_file ?
    res = []
    node_list = list(file_graph.nodes)
    nd = dict(file_graph.nodes(data=True))
    node_info = [nd[i] for i in node_list]
    if FILE_INPUT is not None:
        phase = nx.get_node_attributes(file_graph, "fillcolor")
        phase_norm = [phase[ph][phase[ph].rfind("/") + 1 : len(phase[ph])] for ph in phase]
        # ####code to get colours####
        f_str = open(str(FILE_INPUT), "r")
        dotstr = f_str.read()
        dotstr = dotstr.replace(";<", "@<")
        dotstr = dotstr.replace("14.0", "50.0")
        ##change any ';>' to '@>' then back again after
        x_phaseinf = dotstr.rsplit(";")
        for i in enumerate(x_phaseinf):
            x_phaseinf[i[0]] = x_phaseinf[i[0]].replace("@<", ";<")
        for key in phase.keys():
            res.append(phase[key])
    else:
        phase1 = nx.get_node_attributes(file_graph, "Group")
        for key in phase1.keys():
            res.append(phase1[key])
        phase_norm = res
    x_l, y_l, phase_list, phase_trck, phase_dic = edge_of_phase(
        list(nx.line_graph(file_graph)), list(set(res)), node_list, node_info
    )
    reversed_dict = {}
    if len(phase_list) > 1:
        testdic = dict(zip(x_l, y_l))
        for key, value in testdic.items():
            reversed_dict.setdefault(value, [])
            reversed_dict[value].append(key)
    return reversed_dict, [phase_norm, node_list, phase_list, phase_trck], [x_l, y_l], phase_dic


def edge_of_phase(
    test1: list[Any], pset: list[str], node_list: list[Any], node_info: list[dict[str[Any]]]
) -> tuple[list[str], list[str], Iterable[str], list[tuple[Any, str]], dict[str, list[str]]]:
    """Find nodes on edge of each phase

    Parameters:
        test1: a list of graph nodes (contexts and phases boundary nodes) ordered as a line_graph
        pset: a list of (unique) groups/phases
        node_list: a list of node labels
        node_info: a list of node attribute dictionaries, in the same order as node_list

    Returns:
        A tuple of:

        - a list of ???
        - a list of ???
        - An iterable (dict_keys) of groups/phases
        - a list of phases being tracked?
        - a dictionary containing a list of nodes per group/phase

    Todo:
        - This has not been fully-reimplemented for cases where stratigraphic data was provided via .dot/.gv file, see FILE_INPUT
        - Returning the keys and dictionary is redundant - only need to return the dict.
    """
    FILE_INPUT = None  # model.stratigraphic_graphviz_file ?
    x_l = []
    y_l = []
    mydict = {}
    phase_tracker = []
    if FILE_INPUT is not None:
        for i in enumerate(pset):
            temp_nodes_list = []
            for j in enumerate(node_list):
                if node_info[j[0]]["fillcolor"] == pset[i[0]]:
                    temp_nodes_list.append(node_list[j[0]])
                    p_phase = str(pset[i[0]][pset[i[0]].rfind("/") + 1 : len(pset[i[0]])])
                    node_info[j[0]].update({"Group": p_phase})
                mydict[str(pset[i[0]][pset[i[0]].rfind("/") + 1 : len(pset[i[0]])])] = temp_nodes_list
    else:
        for i in enumerate(pset):
            temp_nodes_list = []
            for j in enumerate(node_list):
                if node_info[j[0]]["Group"] == pset[i[0]]:
                    temp_nodes_list.append(node_list[j[0]])
                mydict[pset[i[0]]] = temp_nodes_list
    for i in enumerate(test1):
        for key in mydict:
            if test1[i[0]][1] in mydict[key] and test1[i[0]][0] not in mydict[key]:
                x_l.append(test1[i[0]][1])
                y_l.append(key)
                phase_lst = [list(mydict.values()).index(j) for j in list(mydict.values()) if test1[i[0]][0] in j]
                key_1 = list(mydict.keys())[phase_lst[0]]  # trying to find phase of other value
                x_l.append(test1[i[0]][0])
                y_l.append(f"{key_1}_below")
                phase_tracker.append((key_1, key))
    return x_l, y_l, mydict.keys(), phase_tracker, mydict


def node_del_fixed(graph: nx.DiGraph, node: str) -> nx.DiGraph:
    """Remove a node from the graph, replacing edges where possible.

    A new edge will not be created if the relative relationship between two nodes is already provided through another context.

    I.e. given the following graph of 4 nodes

    ```mermaid
       flowchart LR
           a --> b0
           a --> b1
           b0 --> c
           b1 --> c
    ```

    Deleting `b0` will produce the following, without a direct edge from `a --> c`

    ```mermaid
       flowchart LR
           a --> b1
           b1 --> c
    ```

    Parameters:
        graph: The graph to modify
        node: the name of the node to be removed

    Returns:
        The mutated graph

    Raises:
        NetworkXError: If the provided node is not a member of the graph

    Todo:
        - The input parameter is mutated, and returned by the function. This should probably either return a mutated copy or not return the graph.
    """
    in_nodes = [i[0] for i in list(graph.in_edges(node))]
    out_nodes = [i[1] for i in list(graph.out_edges(node))]
    graph.remove_node(node)
    for i in in_nodes:
        for j in out_nodes:
            graph.add_edge(i, j, arrowhead="none")

    graph_check = nx.transitive_reduction(graph)
    if graph.edges() != graph_check.edges():
        edges1 = list(graph.edges()).copy()
        for k in edges1:
            if k not in graph_check.edges():
                graph.remove_edge(k[0], k[1])
    return graph


def all_node_info(node_list: List[Any], x_image: List[str], node_info: List[Any]) -> List[Any]:
    """obtains node attributes from original dot file"""
    for i in node_list:
        for j in x_image:
            b_string = re.search('"(.*)" ', j)
            if b_string is not None:
                if i == b_string.group(1):
                    if i in j and "->" not in j:
                        tset = j[(j.index("[") + 1) : (len(j) - 1)]
                        atr_new = tset.replace("] [", "','")
                        atr_new = atr_new.replace("=", "':' ")
                        atr_new = atr_new.replace("' \"", '"')
                        atr_new = atr_new.replace("\"'", '"')
                        atr_new = atr_new.replace("' ", "'")
                        atr_newer = f"{{'{atr_new}}}"
                        dicc = ast.literal_eval(atr_newer)
                        node_info.append(dicc)
    return node_info


def phase_length_finder(con_1: str, con_2: str, group_limits: dict[str, list[float]]) -> List[Any]:
    """Find the group/phase length between any two contexts or phase boundaries

    Parameters:
        con_1: Context or phase boundary node id to find the phase length between
        con_2: Context or phase boundary node id to find the phase length between
        group_limits: Dictionary containing a list of group limits from MCMC calibration per context/phase_boundary label in the chronological_dag

    Returns:
        List of potential phase durations in years.
        An empty list is returned if either context label is not present in the mcmc calibration data.
        If the length of samples is not the same for the provided contexts, the shorter value is used. This should not occur in regular usage.

    Todo:
        - Special case handling when con_1 == con_2?

    """
    if con_1 not in group_limits or con_2 not in group_limits:
        return []
    phase_lengths = [np.abs(a - b) for a, b in zip(group_limits[con_1], group_limits[con_2])]

    # unused code building a version of phase_lengths with sequential elements of the same value removed
    # un_phase_lens = []
    # for i in range(len(phase_lengths) - 1):
    #     if phase_lengths[i] != phase_lengths[i + 1]:
    #         un_phase_lens.append(phase_lengths[i])
    return phase_lengths


def imagefunc(dotfile: Any) -> Any:
    """Sets note attributes to a dot string from the provided file"""
    file = read_dot(dotfile)
    #  code to get colours####
    f_string = open(str(dotfile), "r")
    dotstr = f_string.read()
    dotstr = dotstr.replace(";<", "@<")
    dotstr = dotstr.replace("14.0", "50.0")
    # change any ';>' to '@>' then back again after
    x_image = dotstr.rsplit(";")
    for i in enumerate(x_image):
        x_image[i[0]] = x_image[i[0]].replace("@<", ";<")
    node_list = list(file.nodes)
    node_info_init = list()
    node_info = all_node_info(node_list, x_image, node_info_init)
    for k in enumerate(node_list):
        node_info[k[0]].update(
            {"Determination": "None", "Find_Type": "None", "Group": node_info[k[0]]["fillcolor"], "color": "black"}
        )
    individ_attrs = zip(node_list, node_info)
    attrs = dict(individ_attrs)  # add the dictionary of attributed to a node
    nx.set_node_attributes(file, attrs)
    return file


def phase_relabel(graph: nx.DiGraph) -> nx.DiGraph:
    """Relabels the phase labels to be alphas and betas, for display only,
    still refer to them with a's and b's

    Parameters:
        graph: The graph to modify

    Returns:
        The mutated graph

    Todo:
        - The input parameter is mutated, and returned by the function. This should probably either return a mutated copy or not return the graph.
        - Ideally this should not create labels for nodes which do not start with a_/b_ but contain them, and ideally should only mutate for valid groups, in case user provided context labels include a_ (not currently prevented, although it may be as a workaround)
    """
    label_dict = {}
    for i in graph.nodes():
        if "a_" in i:
            if "b_" in i:
                label_str = i.replace("a_", "<&alpha;<SUB>")
                label_str = label_str.replace(" = b_", "</SUB> = &beta;<SUB>") + "</SUB>>"
                label_dict[i] = label_str
            else:
                label_str = i.replace("a_", "<&alpha;<SUB> ") + "</SUB>>"
                label_dict[i] = label_str
        elif ("b_" in i) and ("a_" not in i):
            label_str = i.replace("b_", "<&beta;<SUB>") + "</SUB>>"
            label_dict[i] = label_str
    # sets the new phase labels to the node attribute labels
    nx.set_node_attributes(graph, label_dict, "label")
    return graph


def alp_beta_node_add(group: str, graph: nx.DiGraph) -> None:
    """Adds an alpha and beta node for the named group to the graph

    Parameters:
        group: The group label to add alpha and beta nodes for
        graph: The graph to be mutated
    """
    graph.add_node(f"a_{group}", shape="diamond", fontsize="20.0", fontname="helvetica", penwidth="1.0")
    graph.add_node(f"b_{group}", shape="diamond", fontsize="20.0", fontname="helvetica", penwidth="1.0")


def phase_labels(
    phi_ref: list[str],
    post_group: list[Literal["abutting", "gap", "overlap", "end"]],
    phi_accept: list[list[float]],
    all_samps_phi: list[list[float]],
) -> tuple[list[str], dict[str, list[float]], dict[str, list[float]]]:
    """Provides group/phase limits for a group/phase

    Parameters:
        phi_ref: Ordered list of group/phase labels
        post_group: Ordered list containing the relationship between the nth group, and the n+1th group
        phi_accept: Accepted group boundaries from MCMC simulation. The length of the outer list depends on the values of post_group
        all_samps_phi: all samples for group boundaries from MCMC, including rejected samples. The length of the outer list depends on the values of post_group

    Returns:
        A 3-element tuple of:

        - The list of labels for group boundary nodes
        - A dictionary of group limits from accepted phi samples
        - A dictionary of group limits from all phi samples
    """
    labels = [f"a_{phi_ref[0]}"]
    i = 0
    results_dict = {labels[0]: phi_accept[i]}
    all_results_dict = {labels[0]: all_samps_phi[i]}
    for idx, post_type in enumerate(post_group):
        i = i + 1
        if post_type == "abutting":
            labels.append(f"b_{phi_ref[idx]} = a_{phi_ref[idx + 1]}")
            results_dict[f"a_{phi_ref[idx + 1]} = b_{phi_ref[idx]}"] = phi_accept[i]
            all_results_dict[f"a_{phi_ref[idx + 1]} = b_{phi_ref[idx]}"] = all_samps_phi[i]
            # results_dict[f"a_{phi_ref[idx + 1]}"] = phi_accept[i]
        elif post_type == "end":
            labels.append(f"b_{phi_ref[-1]}")
            results_dict[f"b_{phi_ref[idx]}"] = phi_accept[i]
            all_results_dict[f"b_{phi_ref[idx]}"] = all_samps_phi[i]
        elif post_type == "gap":
            labels.append(f"b_{phi_ref[idx]}")
            labels.append(f"a_{phi_ref[idx + 1]}")
            results_dict[f"b_{phi_ref[idx]}"] = phi_accept[i]
            all_results_dict[f"b_{phi_ref[idx]}"] = all_samps_phi[i]
            i = i + 1
            results_dict[f"a_{phi_ref[idx + 1]}"] = phi_accept[i]
            all_results_dict[f"a_{phi_ref[idx + 1]}"] = all_samps_phi[i]
        else:  # post_type == "overlap"
            labels.append(f"a_{phi_ref[idx + 1]}")
            labels.append(f"b_{phi_ref[idx]}")
            results_dict[f"a_{phi_ref[idx + 1]}"] = phi_accept[i]
            all_results_dict[f"a_{phi_ref[idx + 1]}"] = all_samps_phi[i]
            i = i + 1
            results_dict[f"b_{phi_ref[idx]}"] = phi_accept[i]
            all_results_dict[f"b_{phi_ref[idx]}"] = all_samps_phi[i]
    # returns dictionary of results do we can plot probability density functions
    return labels, results_dict, all_results_dict


def del_empty_phases(phi_ref: list[str], del_phase: set[str], phasedict: dict[tuple[str, str], str]) -> list[list[str]]:
    """Checks for any phase rels that need changing due to missing dates

    Parameters:
        phi_ref: Ordered list of group/phase labels
        del_phase: Groups/Phases which should be removed
        phasedict: Dictionary of directed relationships between groups

    Returns:
        List of pairs of group labels which a new 'gap' relationship should be created for

    Todo:
        Should duplicates be removed from the retuned list?

    """
    del_phase = [i for i in phi_ref if i in del_phase]
    del_phase_dict_1 = {}
    for j in del_phase:
        del_phase_dict = {}
        rels_list = [i for i in phasedict.keys() if j in i]
        for rels in rels_list:
            if rels[0] == j:
                del_phase_dict["lower"] = rels[1]
            if rels[1] == j:
                del_phase_dict["upper"] = rels[0]
        del_phase_dict_1[j] = del_phase_dict
    if phi_ref[-1] in del_phase_dict_1.keys():
        del_phase_dict_1[phi_ref[-1]]["upper"] = "end"
    if phi_ref[0] in del_phase_dict_1.keys():
        del_phase_dict_1[phi_ref[0]]["lower"] = "start"
    # We then have to run the loop again in case any phases are next to each other, this checks that
    for j in del_phase:
        rels_list = [i for i in phasedict.keys() if j in i]
        for rels in rels_list:
            if rels[0] == j:
                if rels[1] in del_phase:
                    del_phase_dict_1[j]["lower"] = del_phase_dict_1[rels[1]]["lower"]
    del_phase.reverse()
    for k in del_phase:
        rels_list = [i for i in phasedict.keys() if k in i]
        for rels in rels_list:
            if rels[1] == k:
                if rels[0] in del_phase:
                    del_phase_dict_1[k]["upper"] = del_phase_dict_1[rels[0]]["upper"]
    new_group_rels = [
        [del_phase_dict_1[l]["upper"], del_phase_dict_1[l]["lower"]]
        for l in del_phase_dict_1.keys()
        if del_phase_dict_1[l]["upper"] != "end"
        if del_phase_dict_1[l]["lower"] != "start"
    ]
    return new_group_rels


def group_rels_delete_empty(
    file_graph: nx.DiGraph,
    new_group_rels: list[list[str]],
    p_list: list[tuple[str, str]],
    phasedict: dict[tuple[str, str], str],
    phase_nodes: list[str],
    graph_data: tuple[nx.DiGraph, list[list[Any]], list[Any], list[Any]],
) -> Tuple[nx.DiGraph, List[str], Dict[str, str]]:
    """Adds edges between phases that had gaps due to no contexts being left in them

    Parameters:
        file_graph: The input graph
        new_group_rels: list of new edges to create. Each element must be a list/tuple of 2 group labels.
        p_list: a list of (unique) groups/phases, each contianing 2 elements.
        phasedict: A dictionary containing the type of relationship between two phases
        phase_nodes: a list of group/phase node labels, which is modified to include newly created nodes
        graph_data: A collection of graph_data information

    Returns:
        A tuple of:

        - The modified DiGraph
        - A list of groups/phases which need to be remove
        - A dictionary of newly combined group/phase boundary nodes (i.e. `a_x = b_y`) and the associated label

    Todo:
        - phase_nodes is only written to, never read from. Can it be removed?
    """
    phase_relabel(file_graph)
    # adds edges between phases that had gaps due to no contexts being left in them
    label_dict = {}
    null_phases = []  # keep track of phases we need to delete
    [file_graph.add_edge(f"a_{i[0]}", f"b_{i[1]}", arrowhead="none") for i in new_group_rels]
    for p in p_list:
        relation = phasedict[p]
        if relation == "gap":
            if p[0] not in graph_data[1][2]:
                phasedict.pop[p]
                null_phases.append(p)
            elif p[1] not in graph_data[1][2]:
                null_phases.append(p)
            else:
                file_graph.add_edge(f"a_{p[0]}", f"b_{p[1]}", arrowhead="none")
        if relation == "overlap":
            if p[0] not in graph_data[1][2]:
                null_phases.append(p)
            elif p[1] not in graph_data[1][2]:
                null_phases.append(p)
            else:
                file_graph.add_edge(f"b_{p[1]}", f"a_{p[0]}", arrowhead="none")
        if relation == "abutting":
            if p[0] not in graph_data[1][2]:
                null_phases.append(p)
            elif p[1] not in graph_data[1][2]:
                null_phases.append(p)
            else:
                file_graph = nx.contracted_nodes(file_graph, f"a_{p[0]}", f"b_{p[1]}")
                x_nod = list(file_graph)
                newnode = str(f"a_{p[0]} = b_{p[1]}")
                label_str = f"<&alpha;<SUB>{p[0]}</SUB> = &beta;<SUB>{p[1]}</SUB>>"
                label_dict[newnode] = label_str
                phase_nodes.append(f"a_{p[0]} = b_{p[1]}")
                y_nod = [newnode if i == f"a_{p[0]}" else i for i in x_nod]
                mapping = dict(zip(x_nod, y_nod))
                file_graph = nx.relabel_nodes(file_graph, mapping)
    return file_graph, null_phases, label_dict


def chrono_edge_add(
    file_graph: nx.DiGraph,
    graph_data,
    xs_ys,
    phasedict: dict[tuple[str, str], str],
    phase_trck: list[tuple[str, str]],
    post_dict: dict[str, Literal["abutting", "gap", "overlap"]],
    prev_dict: dict[str, Literal["abutting", "gap", "overlap"]],
) -> Tuple[nx.DiGraph, List[Any], List[str]]:
    """chrono_edge_add"""
    xs = xs_ys[0]
    ys = xs_ys[1]
    phase_nodes = []
    phase_norm, node_list = graph_data[1][0], graph_data[1][1]
    all_node_phase = dict(zip(node_list, phase_norm))
    for i in node_list:  # loop adds edges between phases
        if i not in xs:
            if i not in ys:
                file_graph.add_edge(f"b_{all_node_phase[i]}", i, arrowhead="none")
                file_graph.add_edge(i, f"a_{all_node_phase[i]}", arrowhead="none")
            else:
                file_graph.add_edge(i, f"a_{all_node_phase[i]}", arrowhead="none")
        elif i in xs:
            if i not in ys:
                file_graph.add_edge(f"b_{all_node_phase[i]}", i, arrowhead="none")
    if phasedict is not None:
        p_list = list(set(phase_trck))  # phases before any get removed due to having no dates

        phase_nodes.append(f"a_{p_list[0][0]}")
        up_phase = [i[0] for i in p_list]
        low_phase = [i[1] for i in p_list]
        act_phases = set(up_phase + low_phase)  # actual phases we are working with
        del_phase = act_phases - set(graph_data[1][2])
        graph = nx.DiGraph(graph_attr={"splines": "ortho"})
        if len(phase_trck) != 0:
            graph.add_edges_from(phase_trck, arrows="none")
            phi_ref = list(reversed(list(nx.topological_sort(graph))))
            graph_temp = nx.transitive_reduction(graph)
            a = set(graph.edges())
            b = set(graph_temp.edges())
            if len(list(a - b)) != 0:
                rem = list(a - b)[0]
                file_graph.remove_edge(rem[0], rem[1])
        new_group_rels = del_empty_phases(phi_ref, del_phase, phasedict)
        # changes diplay labels to alpha ans betas
        file_graph, null_phases, label_dict = group_rels_delete_empty(
            file_graph, new_group_rels, p_list, phasedict, phase_nodes, graph_data
        )

        phi_ref = [i for i in phi_ref if i in set(graph_data[1][2])]
        phase_nodes.append(f"b_{p_list[len(p_list) - 1][0]}")

    # replace phase rels with gap for phases adjoined due to missing phases
    for i in new_group_rels:
        post_dict[i[1]] = "gap"
        prev_dict[i[0]] = "gap"
    nx.set_node_attributes(file_graph, label_dict, "label")
    return (file_graph, phi_ref, null_phases)


def chrono_edge_remov(file_graph: nx.DiGraph) -> tuple[nx.DiGraph, list[list[Any]], list[Any], list[Any]]:
    """Removes any excess edges so we can render the chronograph

    Parameters:
        file_graph: The input graph

    Returns:
        A tuple containing:

        - A tuple of Graph data, containing:
            - phases in a dict and nodes at the edge of that phase
            - phases for each context
            - contexts
            - phases in "below form"
            - dictionary of phases and contexts in them
        - A list containing 2 elements `[xs, ys]` which  gives any edges removed becuase phase boundaries need to go in
        - A list of phases

    """
    xs, ys = [], []
    # gets a list of all the edges and splits into above and below
    for x, y in list(file_graph.edges):
        xs.append(x)
        ys.append(y)
    graph_data = phase_info_func(file_graph)
    phase_list = list(graph_data[1][2])
    phase_dic = graph_data[3]
    # case with more than one phase
    if len(phase_list) != 1:
        if len(graph_data[1][3]) == 0:
            file_graph.add_edge(phase_dic[phase_list[0]][0], phase_dic[phase_list[1]][0], arrowhead="none")
            graph_data = phase_info_func(file_graph)
        x_l, y_l = graph_data[2][0], graph_data[2][1]
        evenlist, oddlist, elist, olist = [], [], [], []
        for i in range(len(x_l)):
            if i % 2 == 0:
                evenlist.append(x_l[i])
                elist.append(y_l[i])
            else:
                oddlist.append(x_l[i])
                olist.append(y_l[i])
        for j in range(len(evenlist)):
            file_graph.remove_edge(oddlist[j], evenlist[j])

        for node in phase_list:
            alp_beta_node_add(node, file_graph)
        file_graph = phase_relabel(file_graph)

        for i, j in enumerate(elist):
            file_graph.add_edge(f"b_{j}", evenlist[i], arrowhead="none")
        for i, j in enumerate(olist):
            file_graph.add_edge(oddlist[i], f"a_{j.replace('_below', '')}", arrowhead="none")
    # case when there's only one phase
    elif len(phase_list) == 1:
        evenlist = []
        oddlist = []
        for nd in graph_data[1][1]:
            if len(list(file_graph.predecessors(nd))) == 0:
                evenlist.append(nd)  # if no predecesors, adds to list for nodes to connect to phase boundary
            if len(list(file_graph.edges(nd))) == 0:
                oddlist.append(nd)
        for node in list(phase_list):
            alp_beta_node_add(node, file_graph)
        for node in list(phase_list):
            alp_beta_node_add(node, file_graph)
        phase_lab = phase_list[0]
        for z in evenlist:
            file_graph.add_edge(f"b_{phase_lab}", z, arrowhead="none")

        for m in oddlist:
            file_graph.add_edge(m, f"a_{phase_lab}", arrowhead="none")
    return graph_data, [xs, ys], phase_list


def edge_label(src: str, dst: str) -> str:
    """Renders a string for the edge from src to dst.

    Used for deleted edges

    Previously part of Start_page.edge_render

    Parameters:
        src (str): The context label for the start of the directed edge
        dst (str): The context label for the destination of the directed edge
    """
    assert src is not None
    assert dst is not None

    return f"{src} above {dst}"


def remove_invalid_attributes_networkx_lt_3_4(graph: nx.DiGraph) -> nx.DiGraph:
    """Function which removes 'contraction' attribtues from the provided networkx DiGraph if they are set and networkx is less than 3.4.

    This is required for networkx-pydot interaction, as networkx < 3.4 does not correctly escape these values in it's pydot interface, leading to unescaped `:` errors.

    Networkx 3.4 requires python 3.10+, so while python 3.9 support is required we must also support older networkx releases which include this bug.

    Parameters:
        graph: The DiGraph to remove contraction attributes from

    returns:
        The graph with invalid contraction attribtues removed
    """
    # Check the version of networkx requires this
    if packaging.version.parse(nx.__version__) < packaging.version.parse("3.4.0") and isinstance(graph, nx.DiGraph):
        # Copy the graph, to avoid mutating the original
        mutated_graph = copy.deepcopy(graph)
        # For each node in the graph, pop the contraction attribute
        for i in mutated_graph.nodes:
            mutated_graph.nodes[i].pop("contraction", None)
        # For each edge in the graph, pop the contraction attribute (caused by setting context equalities)
        for e in mutated_graph.edges:
            mutated_graph.edges[e].pop("contraction", None)
        return mutated_graph
    else:
        return graph


class MonotonicTimer:
    """A monotonic timer, for capturing execution time for sections of code"""

    __start: int | None = None
    __stop: int | None = None

    def start(self) -> "MonotonicTimer":
        """Record the start of the timed period

        Returns:
            returns itself, so that .start can be chained on the ctor.
        """
        self.__start = time.monotonic_ns()
        self.__stop = None
        return self

    def stop(self) -> "MonotonicTimer":
        """Record the end of the timed period

        Returns:
            returns itself, so that .elapsed/elapsed_ns can be chained on calls to stop.

        Raises:
            RuntimeError: stop must be called after start"""
        if self.__start is None:
            raise RuntimeError("MonotonicTimer.start must be called before MonotonicTimer.stop")
        self.__stop = time.monotonic_ns()
        return self

    def elapsed_ns(self) -> int:
        """Get the elapsed time in nanoseconds

        Timing precision is platform specific, see the time.monotonic_ns docs

        Returns:
            Elapsed time between the most recent calls to start and stop in nanoseconds

        Raises:
            RunmtimeError: start() and stop() must have been called before elapsed_ns"""
        if self.__start is None:
            raise RuntimeError("MonotonicTimer.start must be called before MonotonicTimer.elapsed_ns")
        if self.__stop is None:
            raise RuntimeError("MonotonicTimer.stop must be called before MonotonicTimer.elapsed_ns")

        return self.__stop - self.__start

    def elapsed(self) -> float:
        """Get the elapsed time in seconds.

        Timing precision is platform specific, see the time.monotonic_ns docs

        Returns:
            Elapsed time between the most recent calls to start and stop in fractional seconds

        Raises:
            RunmtimeError: start() and stop() must have been called before elapsed_ns
        """
        return self.elapsed_ns() / 1e9


def get_right_click_binding(double: bool = False) -> str:
    """Get the platform-specific tkinter binding for right-clicking.

    This is different on a Mac than everywhere else

    Parameters:
        double: if the bind should be for double clicking

    Returns:
        the bind string for right click
    """
    number = "2" if platform.system() == "Darwin" else "3"
    return f"<Button-{number}>" if not double else f"<Double-Button-{number}>"
