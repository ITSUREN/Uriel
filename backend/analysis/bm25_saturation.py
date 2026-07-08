# backend/analysis/bm25_saturation.py
"""
BM25 term-frequency saturation curves.

score(tf) = idf * (tf * (k1+1)) / (tf + k1 * (1 - b + b * (L/avgL)))

Matches backend/app/algorithms/bm25.py's formula exactly. idf is fixed
at 1.0 since we're isolating the *shape* of the saturation curve for a
single term, not its absolute scale.

Usage:
    python -m backend.analysis.bm25_saturation --out backend/analysis/output
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt

from backend.analysis.plot_style import apply_style, save_fig

IDF = 1.0


def bm25_term_score(tf: np.ndarray, k1: float, b: float, length_ratio: float = 1.0) -> np.ndarray:
    return IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * length_ratio))


def plot_k1_sweep(tf, k1_values, b, out_dir):
    apply_style()
    fig, ax = plt.subplots()
    for k1 in k1_values:
        ax.plot(tf, bm25_term_score(tf, k1, b), linewidth=2, label=f"k1 = {k1}")
    ax.set_xlabel("Raw term frequency (tf) in document")
    ax.set_ylabel("BM25 term score contribution")
    ax.set_title(f"BM25 Saturation — Effect of k1  (b = {b})")
    ax.legend(title="k1 (saturation speed)")
    return save_fig(fig, out_dir, "bm25_saturation_k1")


def plot_b_sweep(tf, k1, b_values, length_ratio, out_dir):
    apply_style()
    fig, ax = plt.subplots()
    for b in b_values:
        ax.plot(tf, bm25_term_score(tf, k1, b, length_ratio), linewidth=2, label=f"b = {b}")
    ax.set_xlabel("Raw term frequency (tf) in document")
    ax.set_ylabel("BM25 term score contribution")
    ax.set_title(f"BM25 Saturation — Effect of b  (k1 = {k1}, L/avgL = {length_ratio})")
    ax.legend(title="b (length normalization)")
    return save_fig(fig, out_dir, "bm25_saturation_b")


def plot_length_ratio_effect(tf, k1, b, ratios, out_dir):
    apply_style()
    fig, ax = plt.subplots()
    for ratio in ratios:
        label = f"L/avgL = {ratio}" + ("  (avg length)" if ratio == 1.0 else "")
        ax.plot(tf, bm25_term_score(tf, k1, b, ratio), linewidth=2, label=label)
    ax.set_xlabel("Raw term frequency (tf) in document")
    ax.set_ylabel("BM25 term score contribution")
    ax.set_title(f"BM25 Saturation — Effect of Document Length  (k1 = {k1}, b = {b})")
    ax.legend(title="Relative document length")
    return save_fig(fig, out_dir, "bm25_saturation_length")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate BM25 saturation curve plots.")
    parser.add_argument("--out", default="backend/analysis/output")
    args = parser.parse_args()

    tf = np.linspace(0.01, 30, 300)
    p1 = plot_k1_sweep(tf, [0.5, 1.2, 1.5, 2.0, 3.0], b=0.75, out_dir=args.out)
    p2 = plot_b_sweep(tf, k1=1.5, b_values=[0.0, 0.25, 0.5, 0.75, 1.0], length_ratio=1.5, out_dir=args.out)
    p3 = plot_length_ratio_effect(tf, k1=1.5, b=0.75, ratios=[0.5, 1.0, 2.0, 4.0], out_dir=args.out)

    print("Saved:", *p1, *p2, *p3, sep="\n  ")