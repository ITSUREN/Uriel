# backend/analysis/zipf_law.py
"""
Zipf's Law: term rank vs. term frequency on a log-log scale, with a
fitted theoretical Zipf curve (freq ~ C / rank^s) overlaid.

Usage:
    python -m backend.analysis.zipf_law --dir data/documents --out backend/analysis/output
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt

from backend.analysis.corpus_walker import walk_corpus
from backend.analysis.plot_style import apply_style, save_fig

TOP_K = 20

def print_top_terms(stats, top_k: int = TOP_K):
    """Print the most frequent terms in a simple table."""
    print(f"\nTop {top_k} terms by frequency")
    print("-" * 36)
    print(f"{'Rank':<5} {'Term':<20} {'Frequency':>9}")
    print("-" * 36)

    for rank, (term, freq) in enumerate(
        stats.term_frequencies.most_common(top_k),
        start=1,
    ):
        print(f"{rank:<5} {term:<20} {freq:>9}")

    print("-" * 36)

def compute_zipf_data(directory: str):
    stats = None
    for _, stats in walk_corpus(directory):
        pass  # only the final stats are needed; walk_corpus still streams per-file
    if stats is None or not stats.term_frequencies:
        raise RuntimeError(f"No indexable text found under {directory}")

    freqs = sorted(stats.term_frequencies.values(), reverse=True)
    ranks = np.arange(1, len(freqs) + 1)
    return ranks, np.array(freqs), stats


def fit_zipf_exponent(ranks: np.ndarray, freqs: np.ndarray) -> tuple[float, float]:
    """log(freq) = -s*log(rank) + log(C). s == 1.0 is the 'ideal' Zipf exponent."""
    log_r, log_f = np.log(ranks), np.log(freqs)
    slope, intercept = np.polyfit(log_r, log_f, 1)
    return -slope, np.exp(intercept)


def plot_zipf(ranks, freqs, s, C, out_dir: str):
    apply_style()
    fig, ax = plt.subplots()
    ax.loglog(ranks, freqs, marker="o", markersize=3, linewidth=1,
              alpha=0.75, label="Observed term frequency")
    ideal = C / (ranks ** s)
    ax.loglog(ranks, ideal, linestyle="--", linewidth=1.8, color="#E64980",
              label=f"Zipf fit  (freq ∝ rank$^{{-{s:.2f}}}$)")
    ax.set_xlabel("Term rank (log scale)")
    ax.set_ylabel("Term frequency (log scale)")
    ax.set_title("Zipf's Law — Term Frequency vs. Rank")
    ax.legend()
    return save_fig(fig, out_dir, "zipf_law")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Zipf's Law plot for a document corpus.")
    parser.add_argument("--dir", required=True, help="Directory of documents to analyze (.pdf/.txt)")
    parser.add_argument("--out", default="backend/analysis/output")
    args = parser.parse_args()

    ranks, freqs, stats = compute_zipf_data(args.dir)
    s, C = fit_zipf_exponent(ranks, freqs)
    paths = plot_zipf(ranks, freqs, s, C, args.out)

    print(f"Processed {stats.files_processed} files, {stats.total_tokens} tokens, "
          f"{len(stats.term_frequencies)} distinct terms.")
    print(f"Fitted Zipf exponent s = {s:.3f} (ideal Zipf: s = 1.0)")
    print(f"Saved: {', '.join(paths)}")
    print(f"Fitted Zipf exponent s = {s:.3f} (ideal Zipf: s = 1.0)")
    print_top_terms(stats)