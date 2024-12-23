# Pathology Data Analyzer

This Python program evaluates the performance of an AI-based pathology detection system by calculating metrics such as True Positives (TP), False Positives (FP), False Negatives (FN), recall, precision, and F1 score. It processes CSV data containing AI predictions and ground truth labels, applying a hierarchical health mapping for grouped evaluations.

---

## Features
- **Input**: CSV file containing AI findings and ground truth data in JSON format.
- **Health Mapping**: Maps specific pathologies into broader categories for grouped analysis.
- **Metrics Calculation**: Computes TP, FP, FN, recall, precision, and F1 score for each category.
- **Robust Error Handling**: Skips invalid rows with JSON parsing errors and prints debugging information.

---

## Requirements
- Python 3.7 or higher
- Libraries: 
  - `csv`
  - `json`
  - `collections`

