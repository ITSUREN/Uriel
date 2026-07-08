# backend/analysis/ir_metrics.py
"""
Precision / Recall / Accuracy / Mean Average Precision, computed against
relevance judgments you provide by hand (relevance is inherently a
subjective judgment call, so this doesn't try to infer it) -- but
everything else (corpus size, retrieved doc_ids per algorithm) is pulled
live from your running backend, for both BM25 and TF-IDF, so you never
have to run a query manually and paste results.

HOW TO USE
----------
1. Make sure the backend is running (uvicorn backend.app.main:app).
2. Fill in GROUND_TRUTH below: query text -> set of doc_ids that are
   ACTUALLY relevant to that query across the whole corpus (not just
   what any engine happens to retrieve).
3. Run:  python -m backend.analysis.ir_metrics --out backend/analysis/output
   (optionally --api http://127.0.0.1:8000 if your backend isn't on the
   default host/port)

This queries /search once per (query, algorithm) pair with top_k set to
the full corpus size, so recall/AP are computed against the algorithm's
complete ranking, not just whatever top_k your app's default happens to be.
"""
import argparse
import numpy as np
import matplotlib.pyplot as plt
import requests

from backend.analysis.plot_style import apply_style, save_fig, PALETTE

# ============================================================================
# FILL THIS IN -- this is the only thing you need to provide by hand.
# ============================================================================

# query text -> set of doc_ids ACTUALLY relevant to that query, across the
# whole corpus (your subjective ground truth, not what any engine retrieves).
GROUND_TRUTH: dict[str, set[int]] = {
    "what causes cancer": {3, 11, 16},
    "what are the applications of neural networks": {15},
    "machine learning in healthcare": {1},
    "what are things that can be done to live longer": {16},
}

ALGORITHMS = ["bm25", "tfidf"]
ALGO_COLORS = {"bm25": PALETTE[0], "tfidf": PALETTE[1]}
ALGO_LABELS = {"bm25": "BM25", "tfidf": "TF-IDF"}

# ============================================================================
# Live backend access -- corpus size and search results, no manual copying.
# ============================================================================

class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def corpus_size(self) -> int:
        resp = requests.get(f"{self.base_url}/index/stats", timeout=30)
        resp.raise_for_status()
        return resp.json()["documents"]

    def search(self, query: str, algorithm: str, top_k: int) -> list[int]:
        """Returns the ranked list of doc_ids for a query/algorithm pair."""
        resp = requests.post(
            f"{self.base_url}/search",
            json={"query": query, "algorithm": algorithm, "top_k": top_k, "expand_query": False},
            timeout=60,
        )
        resp.raise_for_status()
        return [r["doc_id"] for r in resp.json()["results"]]


def fetch_search_results(client: BackendClient, ground_truth: dict, corpus_size: int) -> dict:
    """
    Runs every query in ground_truth against every algorithm in ALGORITHMS,
    live. top_k = corpus_size so we get each algorithm's full ranking --
    recall and AP need to see far enough down the ranking to find every
    relevant doc, not just whatever top_k the app's UI defaults to.
    Returns: {algorithm: {query: [doc_id, doc_id, ...]}}
    """
    results = {algo: {} for algo in ALGORITHMS}
    for query in ground_truth:
        for algo in ALGORITHMS:
            results[algo][query] = client.search(query, algo, top_k=corpus_size)
    return results

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


def mean_average_precision(ground_truth: dict, results_by_query: dict) -> float:
    """MAP = mean of AP across all queries, for one algorithm."""
    aps = [average_precision(results_by_query[q], ground_truth[q]) for q in ground_truth]
    return sum(aps) / len(aps) if aps else 0.0


def precision_recall_curve(retrieved_ranked: list[int], relevant: set[int]):
    """precision@k, recall@k for every k from 1 to len(retrieved_ranked)."""
    precisions, recalls = [], []
    for k in range(1, len(retrieved_ranked) + 1):
        prefix = retrieved_ranked[:k]
        precisions.append(precision(prefix, relevant))
        recalls.append(recall(prefix, relevant))
    return precisions, recalls


def compute_all_metrics(ground_truth: dict, results: dict, corpus_size: int) -> dict:
    """
    results: {algorithm: {query: [doc_id, ...]}}  (from fetch_search_results)
    Returns: {algorithm: {query: {"precision":, "recall":, "accuracy":, "ap":}}}
    """
    metrics = {}
    for algo in ALGORITHMS:
        metrics[algo] = {}
        for query, relevant in ground_truth.items():
            retrieved = results[algo][query]
            metrics[algo][query] = {
                "precision": precision(retrieved, relevant),
                "recall": recall(retrieved, relevant),
                "accuracy": accuracy(retrieved, relevant, corpus_size),
                "ap": average_precision(retrieved, relevant),
            }
    return metrics

# ============================================================================
# Plotting
# ============================================================================

METRIC_LABELS = {"precision": "Precision", "recall": "Recall", "accuracy": "Accuracy", "ap": "Average Precision"}


def _short(q: str, n: int = 20) -> str:
    return q if len(q) <= n else q[: n - 3] + "..."

def dump_metrics_report(ground_truth: dict, results: dict, metrics: dict,
                         map_scores: dict, corpus_size: int, out_dir: str) -> str:
    """
    Writes a single compact text report with every computed number --
    handy for citing exact figures in a report without re-running or
    re-deriving anything from the graphs.
    """
    import os
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "ir_metrics_report.txt")

    lines = []
    lines.append("=" * 72)
    lines.append("IR EVALUATION REPORT")
    lines.append("=" * 72)
    lines.append(f"Corpus size: {corpus_size} documents")
    lines.append(f"Queries evaluated: {len(ground_truth)}")
    lines.append(f"Algorithms: {', '.join(ALGO_LABELS[a] for a in ALGORITHMS)}")
    lines.append("")

    for query, relevant in ground_truth.items():
        lines.append("-" * 72)
        lines.append(f"Query: {query!r}")
        lines.append(f"  Ground truth relevant doc_ids: {sorted(relevant)}")
        for algo in ALGORITHMS:
            m = metrics[algo][query]
            retrieved = results[algo][query]
            lines.append(
                f"  [{ALGO_LABELS[algo]:6}] "
                f"P={m['precision']:.3f}  R={m['recall']:.3f}  "
                f"Acc={m['accuracy']:.3f}  AP={m['ap']:.3f}  "
                f"| top-5 retrieved: {retrieved[:5]}"
            )
        lines.append("")

    lines.append("-" * 72)
    lines.append("MEAN AVERAGE PRECISION (across all queries)")
    for algo in ALGORITHMS:
        lines.append(f"  {ALGO_LABELS[algo]:6}: MAP = {map_scores[algo]:.4f}")
    lines.append("=" * 72)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path

def plot_metric_single_algorithm(metric: str, algo: str, metrics: dict, queries: list, out_dir: str):
    """Separate graph: one algorithm, one metric, one bar per query."""
    apply_style()
    values = [metrics[algo][q][metric] for q in queries]
    fig, ax = plt.subplots(figsize=(max(6, len(queries) * 1.4), 5))
    ax.bar(range(len(queries)), values, color=ALGO_COLORS[algo], width=0.55)
    ax.set_xticks(range(len(queries)))
    ax.set_xticklabels([_short(q) for q in queries], rotation=20, ha="right")
    ax.set_ylabel(METRIC_LABELS[metric])
    ax.set_ylim(0, 1.05)
    ax.set_title(f"{METRIC_LABELS[metric]} by Query — {ALGO_LABELS[algo]}")
    return save_fig(fig, out_dir, f"ir_{metric}_{algo}")


def plot_metric_comparison(metric: str, metrics: dict, queries: list, out_dir: str):
    """Superimposed graph: both algorithms, grouped bars, one metric."""
    apply_style()
    x = np.arange(len(queries))
    width = 0.35
    fig, ax = plt.subplots(figsize=(max(7, len(queries) * 1.8), 5.5))
    for i, algo in enumerate(ALGORITHMS):
        offset = (i - 0.5) * width
        values = [metrics[algo][q][metric] for q in queries]
        ax.bar(x + offset, values, width, label=ALGO_LABELS[algo], color=ALGO_COLORS[algo])
    ax.set_xticks(x)
    ax.set_xticklabels([_short(q) for q in queries], rotation=20, ha="right")
    ax.set_ylabel(METRIC_LABELS[metric])
    ax.set_ylim(0, 1.05)
    ax.set_title(f"{METRIC_LABELS[metric]} by Query — BM25 vs TF-IDF")
    ax.legend()
    return save_fig(fig, out_dir, f"ir_{metric}_comparison")


def plot_map_comparison(ground_truth: dict, results: dict, out_dir: str):
    """Single superimposed MAP graph: one bar per algorithm."""
    apply_style()
    map_scores = {algo: mean_average_precision(ground_truth, results[algo]) for algo in ALGORITHMS}
    fig, ax = plt.subplots(figsize=(4.5, 5.5))
    bars = ax.bar(
        [ALGO_LABELS[a] for a in ALGORITHMS],
        [map_scores[a] for a in ALGORITHMS],
        color=[ALGO_COLORS[a] for a in ALGORITHMS],
        width=0.5,
    )
    ax.set_ylim(0, 1.05)
    ax.set_title("Mean Average Precision — BM25 vs TF-IDF")
    for bar, algo in zip(bars, ALGORITHMS):
        ax.text(bar.get_x() + bar.get_width() / 2, map_scores[algo] + 0.03,
                f"{map_scores[algo]:.3f}", ha="center", fontweight="bold")
    return save_fig(fig, out_dir, "ir_map_comparison"), map_scores


def plot_pr_curves_single_algorithm(algo: str, ground_truth: dict, results: dict, out_dir: str):
    """Separate graph: one algorithm, precision-recall curve per query."""
    apply_style()
    fig, ax = plt.subplots()
    for query, relevant in ground_truth.items():
        precisions, recalls = precision_recall_curve(results[algo][query], relevant)
        ax.plot(recalls, precisions, marker="o", markersize=3, linewidth=1.5, label=_short(query, 30))
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title(f"Precision–Recall Curve by Query — {ALGO_LABELS[algo]}")
    ax.legend(fontsize=8)
    return save_fig(fig, out_dir, f"ir_pr_curve_{algo}")


def plot_pr_curves_comparison(ground_truth: dict, results: dict, out_dir: str):
    """
    Superimposed graph: both algorithms overlaid per query (same color per
    query, solid vs dashed per algorithm) so you can see, per query, which
    algorithm dominates across the recall range.
    """
    apply_style()
    fig, ax = plt.subplots()
    query_colors = {q: PALETTE[i % len(PALETTE)] for i, q in enumerate(ground_truth)}
    linestyles = {"bm25": "-", "tfidf": "--"}
    for query, relevant in ground_truth.items():
        for algo in ALGORITHMS:
            precisions, recalls = precision_recall_curve(results[algo][query], relevant)
            ax.plot(recalls, precisions, linestyle=linestyles[algo], linewidth=1.6,
                     color=query_colors[query], alpha=0.85,
                     label=f"{_short(query, 22)} — {ALGO_LABELS[algo]}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.05)
    ax.set_title("Precision–Recall Curve — BM25 (solid) vs TF-IDF (dashed)")
    ax.legend(fontsize=7, ncol=1)
    return save_fig(fig, out_dir, "ir_pr_curve_comparison")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute and plot IR evaluation metrics from a live backend.")
    parser.add_argument("--api", default="http://127.0.0.1:8000", help="Base URL of the running backend")
    parser.add_argument("--out", default="backend/analysis/output")
    args = parser.parse_args()

    if not GROUND_TRUTH:
        raise SystemExit("GROUND_TRUTH is empty -- fill it in at the top of backend/analysis/ir_metrics.py.")

    client = BackendClient(args.api)
    corpus_size = client.corpus_size()
    print(f"Corpus size (from {args.api}/index/stats): {corpus_size} documents")

    results = fetch_search_results(client, GROUND_TRUTH, corpus_size)
    metrics = compute_all_metrics(GROUND_TRUTH, results, corpus_size)
    queries = list(GROUND_TRUTH.keys())

    saved = []
    for metric in ("precision", "recall", "accuracy", "ap"):
        for algo in ALGORITHMS:
            saved += plot_metric_single_algorithm(metric, algo, metrics, queries, args.out)
        saved += plot_metric_comparison(metric, metrics, queries, args.out)

    for algo in ALGORITHMS:
        saved += plot_pr_curves_single_algorithm(algo, GROUND_TRUTH, results, args.out)
    saved += plot_pr_curves_comparison(GROUND_TRUTH, results, args.out)

    (map_paths, map_scores) = plot_map_comparison(GROUND_TRUTH, results, args.out)
    saved += map_paths

    report_path = dump_metrics_report(GROUND_TRUTH, results, metrics, map_scores, corpus_size, args.out)

    print()
    for algo in ALGORITHMS:
        print(f"MAP ({ALGO_LABELS[algo]}) = {map_scores[algo]:.4f}")
    print()
    print("Saved:", *saved, report_path, sep="\n  ")