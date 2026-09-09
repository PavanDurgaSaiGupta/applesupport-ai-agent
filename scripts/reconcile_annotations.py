"""
Reconciliation Tool: Compares Blind Human Annotations vs Provisional Machine Labels.

Workflow:
1. Loads candidate reviews from data/golden_set/blind_annotation_200.csv.
2. Merges with machine baseline from data/golden_set/provisional_labels_reference_200.json.
3. Generates data/golden_set/reconciliation_200.csv.
4. Computes:
   - Intent Agreement: Accuracy, Macro F1, Cohen's Kappa (κ).
   - Escalation Agreement: Accuracy, Recall, Precision.
   - Cross-tabulation / Confusion Matrix.
5. If --apply flag is set (or all 200 cases reviewed):
   Updates data/golden_set/golden_eval_set_200.jsonl with human labels as the ground truth.
"""

import os
import sys
import csv
import json
import argparse
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, cohen_kappa_score, confusion_matrix, precision_recall_fscore_support


def reconcile(
    blind_csv_path: str = "data/golden_set/blind_annotation_200.csv",
    provisional_json_path: str = "data/golden_set/provisional_labels_reference_200.json",
    output_reconciliation_csv: str = "data/golden_set/reconciliation_200.csv",
    output_golden_jsonl: str = "data/golden_set/golden_eval_set_200.jsonl",
    apply_to_golden: bool = False,
):
    print("=" * 80)
    print("  GOLDEN EVALUATION SET: BLIND HUMAN REVIEW RECONCILIATION")
    print("=" * 80)

    if not os.path.exists(blind_csv_path):
        print(f"Error: Blind annotation file not found at {blind_csv_path}")
        sys.exit(1)

    if not os.path.exists(provisional_json_path):
        print(f"Error: Provisional reference not found at {provisional_json_path}")
        sys.exit(1)

    # 1. Load Provisional Reference
    with open(provisional_json_path, "r", encoding="utf-8") as f:
        provisional_ref = json.load(f)

    # 2. Load Blind Annotation CSV
    df_blind = pd.read_csv(blind_csv_path, dtype=str).fillna("")
    print(f"Loaded {len(df_blind)} total rows from {blind_csv_path}.")

    reconciled_rows = []
    reviewed_pairs = []

    for _, row in df_blind.iterrows():
        eid_str = str(row["example_id"]).strip()
        eid_int = int(eid_str) if eid_str.isdigit() else 0
        prov = provisional_ref.get(eid_str, {})

        c_intent = str(row.get("candidate_reviewed_intent", "")).strip()
        c_esc = str(row.get("candidate_reviewed_escalation", "")).strip()
        c_reason = str(row.get("candidate_reviewed_reason", "")).strip()
        c_diff = str(row.get("candidate_reviewed_difficulty", "")).strip()
        c_notes = str(row.get("candidate_notes", "")).strip()

        reconciled_row = {
            "example_id": eid_int,
            "tweet_id": row.get("tweet_id", prov.get("tweet_id", "")),
            "customer_query": row.get("customer_query", prov.get("customer_query", "")),
            "provisional_intent": prov.get("provisional_intent", ""),
            "candidate_reviewed_intent": c_intent,
            "provisional_escalation": prov.get("provisional_escalation", ""),
            "candidate_reviewed_escalation": c_esc,
            "candidate_reviewed_reason": c_reason,
            "candidate_reviewed_difficulty": c_diff,
            "candidate_notes": c_notes,
            "provisional_reason": prov.get("provisional_reason", ""),
            "provisional_difficulty": prov.get("provisional_difficulty", ""),
            "apple_reply": prov.get("apple_reply", "")
        }
        reconciled_rows.append(reconciled_row)

        if c_intent and c_esc:
            reviewed_pairs.append({
                "example_id": eid_int,
                "tweet_id": int(reconciled_row["tweet_id"]),
                "customer_query": reconciled_row["customer_query"],
                "provisional_intent": reconciled_row["provisional_intent"],
                "human_intent": c_intent,
                "provisional_escalation": reconciled_row["provisional_escalation"],
                "human_escalation": c_esc,
                "human_reason": c_reason,
                "human_difficulty": c_diff if c_diff else "Medium",
                "human_notes": c_notes,
                "apple_reply": reconciled_row["apple_reply"]
            })

    # Save Reconciliation CSV
    df_reconciled = pd.DataFrame(reconciled_rows)
    df_reconciled.to_csv(output_reconciliation_csv, index=False, encoding="utf-8")
    print(f"Saved side-by-side reconciliation to: {output_reconciliation_csv}")

    num_reviewed = len(reviewed_pairs)
    print(f"\nReview Status: {num_reviewed} / {len(df_blind)} cases have been human-annotated.")

    if num_reviewed == 0:
        print("\n[NOTE] No human annotations have been entered yet in blind_annotation_200.csv.")
        print("Once you fill out candidate_reviewed_intent and candidate_reviewed_escalation,")
        print("rerun this script to see agreement statistics and update the golden evaluation set.")
        return

    # 3. Statistical Analysis: Provisional vs Human Agreement
    y_prov_intent = [p["provisional_intent"] for p in reviewed_pairs]
    y_human_intent = [p["human_intent"] for p in reviewed_pairs]

    y_prov_esc = [p["provisional_escalation"] for p in reviewed_pairs]
    y_human_esc = [p["human_escalation"] for p in reviewed_pairs]

    intent_acc = accuracy_score(y_human_intent, y_prov_intent)
    intent_f1 = f1_score(y_human_intent, y_prov_intent, average="macro", zero_division=0)
    intent_kappa = cohen_kappa_score(y_human_intent, y_prov_intent)

    esc_acc = accuracy_score(y_human_esc, y_prov_esc)
    esc_p, esc_r, esc_f1, _ = precision_recall_fscore_support(
        y_human_esc, y_prov_esc, pos_label="ESCALATE", average="binary", zero_division=0
    )

    print("\n" + "-" * 80)
    print(f"  PROVISIONAL (MACHINE) vs CANDIDATE (HUMAN) AGREEMENT (N = {num_reviewed})")
    print("-" * 80)
    print(f"Intent Agreement Accuracy:     {intent_acc*100:.1f}%")
    print(f"Intent Macro F1:               {intent_f1:.3f}")
    print(f"Intent Cohen's Kappa (κ):      {intent_kappa:.3f}")
    print("-" * 80)
    print(f"Escalation Agreement Accuracy: {esc_acc*100:.1f}%")
    print(f"Escalation Recall (Safety):    {esc_r*100:.1f}%")
    print(f"Escalation Precision:          {esc_p*100:.1f}%")
    print(f"Escalation F1:                 {esc_f1:.3f}")
    print("-" * 80)

    # Confusion matrix
    labels = sorted(list(set(y_human_intent + y_prov_intent)))
    cm = confusion_matrix(y_human_intent, y_prov_intent, labels=labels)
    cm_df = pd.DataFrame(cm, index=[f"Human_{l}" for l in labels], columns=[f"Prov_{l}" for l in labels])
    print("\nIntent Confusion Matrix (Rows: Human, Columns: Provisional):")
    print(cm_df)

    # 4. Update Golden Set if requested or complete
    if apply_to_golden or num_reviewed == len(df_blind):
        print(f"\n[APPLY] Updating {output_golden_jsonl} with human-verified labels as the final gold standard...")
        updated_golden = []
        for r in reconciled_rows:
            eid = r["example_id"]
            human_item = next((p for p in reviewed_pairs if p["example_id"] == eid), None)

            if human_item:
                final_intent = human_item["human_intent"]
                final_esc = human_item["human_escalation"]
                final_reason = human_item["human_reason"] if human_item["human_reason"] else r["provisional_reason"]
                final_diff = human_item["human_difficulty"]
                annotator = "Candidate_Author_Reviewer"
                status = "human_verified"
            else:
                final_intent = r["provisional_intent"]
                final_esc = r["provisional_escalation"]
                final_reason = r["provisional_reason"]
                final_diff = r["provisional_difficulty"]
                annotator = "provisional_rule_assisted"
                status = "pending_candidate_manual_review"

            updated_golden.append({
                "id": eid,
                "tweet_id": int(r["tweet_id"]),
                "apple_tweet_id": int(provisional_ref.get(str(eid), {}).get("apple_tweet_id", 0)),
                "customer_query": r["customer_query"],
                "ground_truth_intent": final_intent,
                "ground_truth_escalation": final_esc,
                "provisional_intent": r["provisional_intent"],
                "provisional_escalation": r["provisional_escalation"],
                "escalation_reason": final_reason,
                "ground_truth_resolution": r["apple_reply"] if r["apple_reply"] else "Direct diagnostic assistance or DM handoff.",
                "difficulty": final_diff,
                "annotator": annotator,
                "label_provenance": "human_candidate_reviewed" if status == "human_verified" else "rule_assisted_heuristics",
                "manual_review_status": status,
                "is_real_kaggle_tweet": True
            })

        with open(output_golden_jsonl, "w", encoding="utf-8") as f:
            for item in updated_golden:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Successfully updated {output_golden_jsonl} with human ground truth labels!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply human labels to golden_eval_set_200.jsonl")
    args = parser.parse_args()
    reconcile(apply_to_golden=args.apply)
