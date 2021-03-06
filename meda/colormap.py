import pkg_resources
import re
from pathlib import Path
from typing import Optional, List

import numpy as np
import pandas as pd
import matplotlib.colors as mcolors


def get_ncl_colormap(
        name,
        index: Optional[np.ndarray] = None,
        count: Optional[int] = None,
        spread_start=None,
        spread_end=None,
        face_color="white"
) -> Optional[mcolors.ListedColormap]:
    """
    Generate Matplotlib colormap from NCL color map files in resource directory.

    Parameters
    ----------
    name
        ncl color map name without extension.
    index
    face_color
    count
    spread_start
    spread_end

    Returns
    -------
    matplotlib.colors.ListedColormap
    """
    raw_colormap = _get_raw_ncl_colormap(name)
    if raw_colormap is None or (index is None and count is None):
        return raw_colormap

    if count is not None:
        # generate index
        total_colors = raw_colormap.N
        if spread_start is None:
            spread_start = 0
        if spread_end is None:
            spread_end = len(total_colors) - 1
        index = np.linspace(spread_start, spread_end, count, endpoint=True, dtype=int)

    colors = []
    if index[0] == -1:
        colors = [face_color]
        index = index[1:]
    raw_colors = raw_colormap(index)
    colors.extend(raw_colors)
    color_map = mcolors.ListedColormap(colors)
    return color_map


def _get_raw_ncl_colormap(name) -> mcolors.ListedColormap:
    """
    Generate Matplotlib colormap from NCL color map files in resource directory.

    Parameters
    ----------
    name
        ncl color map name without extension.

    Returns
    -------
    matplotlib.colors.ListedColormap
    """
    color_map_dir = pkg_resources.resource_filename("meda", "resources/colormap/ncl")
    color_map_path = Path(color_map_dir, f"{name}.rgb")
    if not color_map_path.exists():
        color_map_path = Path(color_map_dir, f"{name}.gp")
    if not color_map_path.exists():
        return None

    prog = re.compile(r"\s+(\d+)\s+(\d+)\s+(\d+)")
    with open(color_map_path, "r") as f:
        buff = f.read()
        r = prog.findall(buff)
        rgbs = np.asarray(r, dtype="i4") / 255
        color_map = mcolors.ListedColormap(rgbs, name)
        return color_map


def generate_colormap_using_ncl_colors(color_names, name):
    color_map_dir = pkg_resources.resource_filename("meda", "resources/colormap/ncl")
    color_names_csv = Path(color_map_dir, "ncl_colors.csv")
    df = pd.read_csv(color_names_csv)
    rgbs = []
    for color_name in color_names:
        color_record = df[df["name"] == color_name].iloc[0]
        rgbs.append(color_record[["R", "G", "B"]].values/255)

    color_map = mcolors.ListedColormap(rgbs, name)
    return color_map
