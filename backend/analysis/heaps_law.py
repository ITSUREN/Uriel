# backend/analysis/heaps_law.py
"""
Heaps' Law: vocabulary size (V) vs. corpus size in tokens (N), traced
file-by-file as the corpus is walked, with a fitted power law
V = K * N^beta overlaid.

Usage:
    python -m backend.analysis.heaps_law --dir data/documents --out backend/analysis/output
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional
from backend.analysis.corpus_walker import walk_corpus, CorpusStats
from backend.analysis.plot_style import apply_style, save_fig


def compute_heaps_data(directory: str):
    traces = []
    stats: Optional[CorpusStats] = None
    for trace, stats in walk_corpus(directory):
        traces.append(trace)
    if stats is None:
        raise RuntimeError(f"No indexable text found under {directory}")
    if not traces:
        raise RuntimeError(f"No indexable text found under {directory}")

    n_values = np.array([t.cumulative_tokens for t in traces], dtype=float)
    v_values = np.array([t.cumulative_vocab_size for t in traces], dtype=float)
    mask = n_values > 0  # drop any leading zero-token (empty/skipped) files, avoids log(0)
    return n_values[mask], v_values[mask], traces, stats


def fit_heaps_law(n_values: np.ndarray, v_values: np.ndarray) -> tuple[float, float]:
    """log(V) = beta*log(N) + log(K). Typical corpora: beta in [0.4, 0.6]."""
    log_n, log_v = np.log(n_values), np.log(v_values)
    beta, log_k = np.polyfit(log_n, log_v, 1)
    return beta, np.exp(log_k)


def plot_heaps(n_values, v_values, beta, k, out_dir: str):
    apply_style()
    fig, ax = plt.subplots()
    ax.loglog(n_values, v_values, marker="o", markersize=3, linewidth=1,
              alpha=0.75, label="Observed vocabulary growth")
    fitted = k * (n_values ** beta)
    ax.loglog(n_values, fitted, linestyle="--", linewidth=1.8, color="#E64980",
              label=f"Heaps' fit  (V = {k:.2f}·N$^{{{beta:.2f}}}$)")
    ax.set_xlabel("Total tokens processed, N (log scale)")
    ax.set_ylabel("Distinct vocabulary size, V (log scale)")
    ax.set_title("Heaps' Law — Vocabulary Growth vs. Corpus Size")
    ax.legend()
    return save_fig(fig, out_dir, "heaps_law")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Heaps' Law plot for a document corpus.")
    parser.add_argument("--dir", required=True, help="Directory of documents to analyze (.pdf/.txt)")
    parser.add_argument("--out", default="backend/analysis/output")
    args = parser.parse_args()

    n_values, v_values, traces, stats = compute_heaps_data(args.dir)
    beta, k = fit_heaps_law(n_values, v_values)
    paths = plot_heaps(n_values, v_values, beta, k, args.out)

    print(f"Processed {len(traces)} files, {stats.total_tokens} tokens, "
          f"{len(stats.term_frequencies)} distinct terms.")
    print(f"Fitted Heaps' Law: K = {k:.3f}, beta = {beta:.3f} (typical range: 0.4-0.6)")
    print(f"Saved: {', '.join(paths)}")