#!/usr/bin/env bash

# cause the script to stop immediately if any analysis fails.
set -e

echo "========================================"
echo "Running Zipf's Law analysis..."
echo "========================================"
python -m backend.analysis.zipf_law --dir data/documents

echo
echo "========================================"
echo "Running Heaps' Law analysis..."
echo "========================================"
python -m backend.analysis.heaps_law --dir data/documents

echo
echo "========================================"
echo "Running BM25 saturation analysis..."
echo "========================================"
python -m backend.analysis.bm25_saturation

echo
echo "========================================"
echo "Running IR metrics analysis..."
echo "========================================"
python -m backend.analysis.ir_metrics_api

echo
echo "========================================"
echo "All analyses completed successfully."
echo "========================================"