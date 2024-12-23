import csv
import json
from collections import defaultdict

def calculate_metrics(ai_findings, ground_truth, health_map):
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    ai_pathologies = {finding['pathology'] for finding in ai_findings} if ai_findings else set()
    ground_truth_pathologies = {truth['pathology'] for truth in ground_truth} if ground_truth else set()

    # Flatten health map for reverse lookup
    reverse_health_map = {}
    for key, values in health_map.items():
        for value in values:
            reverse_health_map[value] = key

    # Map AI findings and ground truth to their categories
    mapped_ai_pathologies = {reverse_health_map.get(pathology, pathology) for pathology in ai_pathologies}
    mapped_ground_truth_pathologies = {reverse_health_map.get(pathology, pathology) for pathology in ground_truth_pathologies}

    # If ground truth is empty, all AI findings are false positives
    if not mapped_ground_truth_pathologies:
        for pathology in mapped_ai_pathologies:
            fp[pathology] += 1

    # If AI findings are empty, all ground truth pathologies are false negatives
    if not mapped_ai_pathologies:
        for pathology in mapped_ground_truth_pathologies:
            fn[pathology] += 1

    # Standard calculation for non-empty AI findings and ground truth
    if mapped_ai_pathologies and mapped_ground_truth_pathologies:
        for pathology in mapped_ai_pathologies:
            if pathology in mapped_ground_truth_pathologies:
                tp[pathology] += 1
            else:
                fp[pathology] += 1

        for pathology in mapped_ground_truth_pathologies:
            if pathology not in mapped_ai_pathologies:
                fn[pathology] += 1

    return tp, fp, fn

def calculate_f1_recall_precision(tp, fp, fn):
    metrics = {}
    for pathology in tp.keys() | fp.keys() | fn.keys():
        true_positive = tp[pathology]
        false_positive = fp[pathology]
        false_negative = fn[pathology]

        recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
        precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        metrics[pathology] = {
            'recall': recall,
            'precision': precision,
            'f1_score': f1_score
        }
    return metrics

def main():
    file_path = '/Users/alinakhan/Desktop/mVgdata.csv'
    max_rows = 9841  # Set the maximum number of rows to process

    tp_total = defaultdict(int)
    fp_total = defaultdict(int)
    fn_total = defaultdict(int)

    health_map = {
        "Fracture": [
            "Clavicle Fracture",
            "Humerus Fracture",
            "Rib Fracture",
            "Scapula Fracture",
            "Old Rib Fracture",
            "Old Healed Clavicle Fracture",
            "Clavicle Fracture with PO"
        ],
        "Lung Opacity": [
            "Alveolar Lung Opacity",
            "Interstitial Lung Opacity"
        ],
        "Support Devices": [
            "Esophageal Stent",
            "Foreign Body - Pacemaker",
            "Foreign Body - CV Line",
            "Foreign Body - NG Tube",
            "Foreign Body - ETT",
            "Foreign Body - ICD",
            "Foreign Body - Chest Leads",
            "Foreign Body - Tracheostomy Tube",
            "Foreign Body - Sternal Sutures",
            "Foreign Body - Cardiac Valves",
            "Foreign Body - Chemoport",
            "Foreign Body - Spinal Fusion",
            "NJ Tube",
            "Surgical Staples"
        ],
        "Pleural Other": [
            "Pleural Calcification",
            "Pleural Plaque",
            "Pleural Thickening"
        ],
        "Atelectasis": [
            "Atelectasis",
            "Lung Collapse",
            "Lobe Collapse"
        ],
        "Diaphragmatic Dysfunction": [
            "Diaphragmatic Hump",
            "Elevated Diaphragm",
            "Flattened Diaphragm",
            "Tented Diaphragm"
        ],
        "Cifo-scoliosis": [
            "Scoliosis"
        ],
        "Interstitial Disease": [
            "Interstitial Lung Opacity",
            "ILD (Interstitial Lung Disease)"
        ],
        "Pleural Effusion": [
            "Pleural Effusion"
        ],
        "Abnormal Cardiac Silhouette": [
            "Cardiomegaly"
        ],
        "Emphysema": [
            "COPD (Chronic Obstructive Pulmonary Disease)",
            "Bullous Emphysema"
        ],
        "Tuberculosis": [
            "Tuberculosis",
            "Old TB",
            "Milliary Tuberculosis"
        ],
        "Consolidation": [
            "Consolidation"
        ],
        "Pneumothorax": [
            "Pneumothorax"
        ],
        "Hilar/Mediastinal Disease": [
            "Hilar Lymphadenopathy",
            "Hilar Prominence",
            "Mediastinal Shift",
            "Tracheal and Mediastinal Shift",
            "Mediastinal Mass",
            "Mediastinal Widening"
        ],
        "Lung Lesion": [
            "Lung Mass",
            "Nodule",
            "Reticular Nodule",
            "Multiple Nodules",
            "Cavity",
            "Cannonball Metastases"
        ],
        "Edema": [
            "Edema"
        ]
    }

    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)

        # Read the header
        headers = next(reader)
        print("Column names:", headers)

        # Find the indexes of the columns
        ai_findings_index = headers.index('AI 2  findings')
        ground_truth_index = headers.index('Ground truth')

        row_count = 0
        for row in reader:
            if row_count >= max_rows:
                break

            try:
                ai_findings_json = row[ai_findings_index].strip()
                ground_truth_json = row[ground_truth_index].strip()

                # Handle case where JSON data is empty or cell is empty
                if not ai_findings_json or ai_findings_json == "[]":
                    ai_findings = []
                else:
                    ai_findings = json.loads(ai_findings_json)

                if not ground_truth_json or ground_truth_json == "[]":
                    ground_truth = []
                else:
                    ground_truth = json.loads(ground_truth_json)

            except json.JSONDecodeError as e:
                print(f"Skipping row due to JSONDecodeError: {e}")
                print(f"Offending row: {row}")  # Print the offending row for debugging
                row_count += 1  # Ensure row_count is incremented even if row is skipped
                continue

            tp, fp, fn = calculate_metrics(ai_findings, ground_truth, health_map)

            for key in tp:
                tp_total[key] += tp[key]
            for key in fp:
                fp_total[key] += fp[key]
            for key in fn:
                fn_total[key] += fn[key]

            # Debug: Print metrics for each row
            print(f"Row {row_count}: TP={tp}, FP={fp}, FN={fn}")

            row_count += 1

    metrics = calculate_f1_recall_precision(tp_total, fp_total, fn_total)



    print("True Positives (TP):", dict(tp_total))
    print("False Positives (FP):", dict(fp_total))
    print("False Negatives (FN):", dict(fn_total))
    print("Metrics (Recall, Precision, F1 Score):", metrics)

if __name__ == "__main__":
    main()
