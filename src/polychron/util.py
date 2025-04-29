import pathlib
import re
import tempfile

import networkx as nx
import pandas as pd
from graphviz import render
from networkx.drawing.nx_pydot import write_dot
from PIL import Image, ImageChops

"""Utiltiy methods which do not (yet) have a home

@todo - find a better home for each of these methods

@todo - rename methods 
@todo - rename variables in methods
@todo - type annotations
"""


def trim(im_trim: Image.Image):
    """Trims images down"""
    bg_trim = Image.new(im_trim.mode, im_trim.size)
    diff = ImageChops.difference(im_trim, bg_trim)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    return im_trim.crop(bbox)


def polygonfunc(i):
    """finds node coords of a kite"""
    x = re.findall(r'points="(.*?)"', i)[0].replace(" ", ",")
    a = x.split(",")
    # if loop checks if it's a rectangle or a kite then gets the right coords
    if -1 * float(a[7]) == -1 * float(a[3]):
        coords_converted = [float(a[2]), float(a[6]), -1 * float(a[5]), -1 * float(a[1])]
    else:
        coords_converted = [float(a[2]), float(a[6]), -1 * float(a[7]), -1 * float(a[3])]
    return coords_converted


def ellipsefunc(i):
    """finds coords from dot file for ellipse nodes"""
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


def rank_func(tes, file_content):
    #  t0 = time.time()
    """adds strings into dot string to make nodes of the same phase the same rank"""
    rank_same = []
    for key in tes.keys():
        x_rank = tes[key]
        y_1 = str(x_rank)
        y_2 = y_1.replace("[", "")
        y_3 = y_2.replace("]", "")
        y_4 = y_3.replace("'", "")
        y_5 = y_4.replace(",", ";")
        x_2 = "{rank = same; " + y_5 + ";}\n"
        rank_same.append(x_2)
    rank_string = "".join(rank_same)[:-1]
    new_string = file_content[:-2] + rank_string + file_content[-2]
    return new_string


def node_coords_fromjson(graph):
    """Gets coordinates of each node"""
    global phase_true
    if "pydot" in str(type(graph)):
        graphs = graph
    else:
        graphs = nx.nx_pydot.to_pydot(graph)
    svg_string = str(graphs.create_svg())
    scale_info = re.search("points=(.*?)/>", svg_string).group(1).replace(" ", ",")
    scale_info = scale_info.split(",")
    scale = [float(scale_info[4]), -1 * float(scale_info[3])]
    coords_x = re.findall(r'id="node(.*?)</text>', svg_string)
    coords_temp = [polygonfunc(i) if "points" in i else ellipsefunc(i) for i in coords_x]
    node_test = re.findall(r'node">\\n<title>(.*?)</title>', svg_string)
    node_list = [i.replace("&#45;", "-") for i in node_test]

    new_pos = dict(zip(node_list, coords_temp))
    df = pd.DataFrame.from_dict(new_pos, orient="index", columns=["x_lower", "x_upper", "y_lower", "y_upper"])
    return df, scale


def imgrender(file: nx.DiGraph, canv_width: int, canv_height: int) -> Image.Image:
    """renders png from dotfile

    @todo - rename file parameter
    @todo - make sure this is doing things in a sensible working directory?"""

    workdir = pathlib.Path(tempfile.gettempdir()) / "polychron" / "temp"  # @Todo actually do this in the model folder?
    workdir.mkdir(parents=True, exist_ok=True)

    # global node_df
    file.graph["graph"] = {"splines": "ortho"}
    write_dot(file, workdir / "fi_new")
    render("dot", "png", workdir / "fi_new")
    render("dot", "svg", workdir / "fi_new")
    inp = Image.open(workdir / "fi_new.png")
    inp_final = trim(inp)
    inp_final.save(workdir / "testdag.png")
    outp = Image.open(workdir / "testdag.png")
    # node_df = node_coords_fromjson(file) # @todo - this is global state that needs updating somewhere?. Make the method return a tuple instead?
    return outp


def imgrender_phase(file: nx.DiGraph):
    """Renders image from dot file with all nodes of the same phase collected together

    @todo - rename file parameter
    @todo - Consistent parameters with imgrender?
    @todo - working dir / set paths explicitly"""
    workdir = pathlib.Path(tempfile.gettempdir()) / "polychron" / "temp"  # @Todo actually do this in the model folder?
    workdir.mkdir(parents=True, exist_ok=True)
    pass  # @todo
    # # global node_df
    # write_dot(file, 'fi_new.txt')
    # my_file = open("fi_new.txt")
    # file_content = my_file.read()
    # new_string = rank_func(phase_info_func(file)[0], file_content)
    # textfile = open('fi_new.txt', 'w')
    # textfile.write(new_string)
    # textfile.close()
    # (graph,) = pydot.graph_from_dot_file('fi_new.txt')
    # graph.write_png('test.png')
    # inp = Image.open("test.png")
    # inp = trim(inp)
    # # Call the real .tkraise
    # inp.save("testdag.png")
    # outp = Image.open("testdag.png")
    # node_df = node_coords_fromjson(graph)
    # return outp
