# backend/analysis/ir_metrics.py
"""
Precision / Recall / Accuracy / Mean Average Precision, computed against
relevance judgments you provide by hand (relevance is inherently a
subjective judgment call, so this doesn't try to infer it).

HOW TO USE
----------
1. Run queries against your running backend (POST /search), note the
   ordered list of doc_ids returned.
2. For each query, decide which doc_ids in the WHOLE corpus are
   actually relevant -- not just the ones retrieved. This is ground truth.
3. Fill in GROUND_TRUTH, SEARCH_RESULTS, and CORPUS_SIZE below.
4. Run:  python -m backend.analysis.ir_metrics --out backend/analysis/output
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt

from backend.analysis.plot_style import apply_style, save_fig

# ============================================================================
# FILL THIS IN -- everything below is derived from these three things.
# ============================================================================

# query text -> set of doc_ids ACTUALLY relevant to that query, across the
# whole corpus (your subjective ground truth, not what the engine retrieved).
GROUND_TRUTH: dict[str, set[int]] = {
    # "machine learning in healthcare": {3, 7, 12, 40},
    # "climate change statistics": {2, 9},
}

# query text -> ranked list of doc_ids the engine returned, in order
# (rank 1 first). Copy straight from a POST /search response's
# results[].doc_id.
SEARCH_RESULTS: dict[str, list[int]] = {
    # "machine learning in healthcare": [12, 3, 5, 40, 8, 7, 21],
    # "climate change statistics": [2, 14, 9, 33],
}

# Total documents in the corpus (GET /index/stats -> "documents").
# Needed for accuracy, which counts true negatives -- precision/recall
# alone never need to know the full population size.
CORPUS_SIZE: int = 0  # e.g. 9

# ============================================================================
# Metric formulas
# ============================================================================

def precision(retrieved: list[int], relevant: set[int]) -> float:
    """Precision = |retrieved ∩ relevant| / |retrieved|"""
    if not retrieved:
        return 0.0
    retrieved_set = set(retrieved)
    return len(retrieved_set & relevant) / len(retrieved_set)


def recall(retrieved: list[int], relevant: set[int]) -> float:
    """Recall = |retrieved ∩ relevant| / |relevant|"""
    if not relevant:
        return 0.0
    retrieved_set = set(retrieved)
    return len(retrieved_set & relevant) / len(relevant)


def accuracy(retrieved: list[int], relevant: set[int], corpus_size: int) -> float:
    """
    Accuracy = (TP + TN) / (TP + TN + FP + FN) over the WHOLE corpus:
      TP = retrieved and relevant     FP = retrieved but not relevant
      FN = relevant but not retrieved TN = neither (everything else)
    """
    retrieved_set = set(retrieved)
    tp = len(retrieved_set & relevant)
    fp = len(retrieved_set - relevant)
    fn = len(relevant - retrieved_set)
    tn = corpus_size - tp - fp - fn
    denom = tp + tn + fp + fn
    return (tp + tn) / denom if denom > 0 else 0.0


def average_precision(retrieved_ranked: list[int], relevant: set[int]) -> float:
    """
    AP = (1/|relevant|) * sum of precision@k at every rank k where the
    retrieved doc is relevant. Rewards ranking relevant docs higher,
    unlike plain precision/recall which ignore order.
    """
    if not relevant:
        return 0.0
    hits, precisions_at_hits = 0, []
    for k, doc_id in enumerate(retrieved_ranked, start=1):
        if doc_id in relevant:
            hits += 1
            precisions_at_hits.append(hits / k)
    return sum(precisions_at_hits) / len(relevant) if precisions_at_hits else 0.0


def mean_average_precision(ground_truth, search_results) -> float:
    """MAP = mean of AP across all queries."""
    aps = [
        average_precision(search_results[q], ground_truth[q])
        for q in ground_truth if q in search_results
    ]
    return sum(aps) / len(aps) if aps else 0.0


def precision_recall_curve(retrieved_ranked: list[int], relevant: set[int]):
    """precision@k, recall@k for every k from 1 to len(retrieved_ranked)."""
    precisions, recalls = [], []
    for k in range(1, len(retrieved_ranked) + 1):
        prefix = retrieved_ranked[:k]
        precisions.append(precision(prefix, relevant))
        recalls.append(recall(prefix, relevant))
    return precisions, recalls

# ============================================================================
# Plotting
# ============================================================================

def plot_per_query_bars(ground_truth, search_results, corpus_size, out_dir: str):
    apply_style()
    queries = [q for q in ground_truth if q in search_results]
    if not queries:
        raise RuntimeError("No overlapping queries between GROUND_TRUTH and SEARCH_RESULTS.")

    precisions = [precision(search_results[q], ground_truth[q]) for q in queries]
    recalls = [recall(search_results[q], ground_truth[q]) for q in queries]
    accuracies = [accuracy(search_results[q], ground_truth[q], corpus_size) for q in queries]
    aps = [average_precision(search_results[q], ground_truth[q]) for q in queries]

    x = np.arange(len(queries))
    width = 0.2
    fig, ax = plt.subplots(figsize=(max(8, len(queries) * 1.8), 5.5))
    ax.bar(x - 1.5 * width, precisions, width, label="Precision")
    ax.bar(x - 0.5 * width, recalls, width, label="Recall")
    ax.bar(x + 0.5 * width, accuracies, width, label="Accuracy")
    ax.bar(x + 1.5 * width, aps, width, label="Average Precision")
    ax.set_xticks(x)
    ax.set_xticklabels([q if len(q) <= 20 else q[:17] + "..." for q in queries], rotation=20, ha="right")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.set_title("Precision / Recall / Accuracy / AP by Query")
    ax.legend()
    return save_fig(fig, out_dir, "ir_metrics_per_query")


def plot_precision_recall_curves(ground_truth, search_results, out_dir: str):
    apply_style()
    queries = [q for q in ground_truth if q in search_results]
    fig, ax = plt.subplots()
    for q in queries:
        precisions, recalls = precision_recall_curve(search_results[q], ground_truth[q])
        label = q if len(q) <= 30 else q[:27] + "..."
        ax.plot(recalls, precisions, marker="o", markersize=3, linewidth=1.5, label=label)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title("Precision–Recall Curve by Query")
    ax.legend(fontsize=8)
    return save_fig(fig, out_dir, "ir_precision_recall_curve")


def plot_map_summary(ground_truth, search_results, out_dir: str):
    apply_style()
    map_score = mean_average_precision(ground_truth, search_results)
    fig, ax = plt.subplots(figsize=(4, 5))
    ax.bar(["MAP"], [map_score], width=0.5, color="#4C6EF5")
    ax.set_ylim(0, 1.05)
    ax.set_title("Mean Average Precision")
    ax.text(0, map_score + 0.03, f"{map_score:.3f}", ha="center", fontweight="bold")
    return save_fig(fig, out_dir, "ir_map_summary")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute and plot IR evaluation metrics.")
    parser.add_argument("--out", default="backend/analysis/output")
    args = parser.parse_args()

    if not GROUND_TRUTH or not SEARCH_RESULTS:
        raise SystemExit(
            "GROUND_TRUTH and SEARCH_RESULTS are still empty -- fill them in "
            "at the top of backend/analysis/ir_metrics.py before running this."
        )
    if CORPUS_SIZE <= 0:
        raise SystemExit("Set CORPUS_SIZE at the top of backend/analysis/ir_metrics.py before running this.")

    p1 = plot_per_query_bars(GROUND_TRUTH, SEARCH_RESULTS, CORPUS_SIZE, args.out)
    p2 = plot_precision_recall_curves(GROUND_TRUTH, SEARCH_RESULTS, args.out)
    p3 = plot_map_summary(GROUND_TRUTH, SEARCH_RESULTS, args.out)

    print(f"MAP = {mean_average_precision(GROUND_TRUTH, SEARCH_RESULTS):.4f}")
    print("Saved:", *p1, *p2, *p3, sep="\n  ")