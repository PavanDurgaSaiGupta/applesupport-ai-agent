"""
Human-Judge Agreement & Reliability Calibration.

Computes statistical agreement between the automated LLM Judge and
expert human annotations on the calibration set (Cohen's Kappa, Pearson r, Spearman rho, MAE).
"""

import json
import os
import math
from typing import Dict, Any, List, Tuple
import numpy as np
from scipy import stats
from sklearn.metrics import cohen_kappa_score

from src.llm_judge import LLMJudge
from src.agent import AppleSupportAgent


def bucket_score(score: float) -> str:
    """Discretizes continuous 1-5 score into categorical bins for Cohen's Kappa."""
    if score >= 4.5:
        return "HIGH_QUALITY"
    elif score >= 3.5:
        return "ACCEPTABLE"
    else:
        return "NEEDS_IMPROVEMENT"


def evaluate_human_judge_agreement(
    agent: AppleSupportAgent,
    human_annotations_path: str = "data/golden_set/human_annotations_sample.json",
    golden_eval_path: str = "data/golden_set/golden_eval_set_200.jsonl"
) -> Dict[str, Any]:
    """
    Evaluates agent on the 30 human-annotated cases and computes statistical agreement.
    """
    if not os.path.exists(human_annotations_path) or not os.path.exists(golden_eval_path):
        raise FileNotFoundError("Missing calibration datasets.")

    # Load golden records indexed by id
    golden_records = {}
    with open(golden_eval_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            golden_records[item["id"]] = item

    # Load human scorecards
    with open(human_annotations_path, "r", encoding="utf-8") as f:
        human_scorecards = json.load(f)

    judge = LLMJudge()
    human_scores = []
    judge_scores = []
    human_buckets = []
    judge_buckets = []
    detailed_comparisons = []

    for card in human_scorecards:
        cid = card["case_id"]
        gt_item = golden_records.get(cid)
        if not gt_item:
            continue

        # Run agent
        agent_out = agent.process(gt_item["customer_query"])

        # Run Judge
        judge_out = judge.evaluate_response(
            customer_query=gt_item["customer_query"],
            predicted_intent=agent_out["intent"],
            escalation_decision=agent_out["escalation_decision"],
            drafted_reply=agent_out["drafted_reply"],
            ground_truth_intent=gt_item["ground_truth_intent"],
            ground_truth_escalation=gt_item["ground_truth_escalation"],
            ground_truth_resolution=gt_item["ground_truth_resolution"]
        )

        h_comp = card["composite_score"]
        j_comp = judge_out["composite_score"]

        human_scores.append(h_comp)
        judge_scores.append(j_comp)
        human_buckets.append(bucket_score(h_comp))
        judge_buckets.append(bucket_score(j_comp))

        detailed_comparisons.append({
            "case_id": cid,
            "query": gt_item["customer_query"][:80] + "...",
            "human_composite": h_comp,
            "judge_composite": j_comp,
            "absolute_diff": round(abs(h_comp - j_comp), 2)
        })

    # Statistical Computations
    pearson_r, pearson_p = stats.pearsonr(human_scores, judge_scores)
    spearman_rho, spearman_p = stats.spearmanr(human_scores, judge_scores)
    kappa = cohen_kappa_score(human_buckets, judge_buckets)
    mae = float(np.mean(np.abs(np.array(human_scores) - np.array(judge_scores))))

    return {
        "sample_size": len(human_scores),
        "cohen_kappa": round(float(kappa), 4),
        "pearson_r": round(float(pearson_r), 4),
        "pearson_p_value": float(pearson_p),
        "spearman_rho": round(float(spearman_rho), 4),
        "spearman_p_value": float(spearman_p),
        "mean_absolute_error": round(float(mae), 4),
        "human_mean_score": round(float(np.mean(human_scores)), 2),
        "judge_mean_score": round(float(np.mean(judge_scores)), 2),
        "detailed_sample": detailed_comparisons[:5]
    }
