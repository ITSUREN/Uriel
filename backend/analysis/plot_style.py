# backend/analysis/plot_style.py
"""Shared matplotlib styling so every analysis graph looks consistent
and report-ready without repeating rcParams in every script."""
import os
import matplotlib.pyplot as plt
from cycler import cycler

PALETTE = ["#4C6EF5", "#F76707", "#12B886", "#E64980", "#7048E8", "#FAB005"]


def apply_style():
    plt.rcParams.update({
        "figure.figsize": (8, 5.5),
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 11.5,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.9,
        "axes.grid": True,
        "grid.color": "#dddddd",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,
        "axes.axisbelow": True,
        "axes.prop_cycle": cycler(color=PALETTE),
        "legend.frameon": False,
        "legend.fontsize": 10,
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_fig(fig, out_dir: str, name: str, formats=("png", "svg")):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for fmt in formats:
        path = os.path.join(out_dir, f"{name}.{fmt}")
        fig.savefig(path)
        paths.append(path)
    return paths