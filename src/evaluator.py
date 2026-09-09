"""
Evaluation Suite: Automated Classification, Escalation, and Text Metrics.

Computes:
- Intent Classification: Accuracy, Macro F1, Weighted F1, Per-class metrics, Confusion Matrix
- Escalation: Precision, Recall, F1, Cost-Weighted Penalty Matrix
- Reply Quality: ROUGE-1/2/L, BLEU-4, Length & Policy compliance
"""

import math
from typing import List, Dict, Any, Tuple
from collections import Counter
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
from rouge_score import rouge_scorer
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


class BenchmarkEvaluator:
    """Evaluates agent predictions against golden ground truth annotations."""

    def __init__(self, intents: List[str]):
        self.intents = intents
        self.rouge_evaluator = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        self.smooth_fn = SmoothingFunction().method1

    def evaluate_intent_classification(
        self,
        y_true: List[str],
        y_pred: List[str]
    ) -> Dict[str, Any]:
        """Calculates multi-class intent classification metrics."""
        acc = accuracy_score(y_true, y_pred)
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, average="macro", zero_division=0
        )
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_true, y_pred, average="weighted", zero_division=0
        )
        per_class_p, per_class_r, per_class_f1, per_class_support = precision_recall_fscore_support(
            y_true, y_pred, labels=self.intents, zero_division=0
        )

        per_class_metrics = {}
        for idx, intent in enumerate(self.intents):
            per_class_metrics[intent] = {
                "precision": round(float(per_class_p[idx]), 4),
                "recall": round(float(per_class_r[idx]), 4),
                "f1": round(float(per_class_f1[idx]), 4),
                "support": int(per_class_support[idx])
            }

        cm = confusion_matrix(y_true, y_pred, labels=self.intents).tolist()

        return {
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(p_macro), 4),
            "macro_recall": round(float(r_macro), 4),
            "macro_f1": round(float(f1_macro), 4),
            "weighted_f1": round(float(f1_weighted), 4),
            "per_class": per_class_metrics,
            "confusion_matrix": cm,
            "intents": self.intents
        }

    def evaluate_escalation_decisions(
        self,
        y_true: List[str],
        y_pred: List[str],
        cost_missed_escalation: float = 5.0,
        cost_false_escalation: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculates escalation metrics with asymmetric operational cost weighting:
        - Missed escalation (leaving a user with a swollen battery or hacked account): Cost = 5.0
        - False escalation (routing a simple settings toggle to human agent): Cost = 1.0
        """
        acc = accuracy_score(y_true, y_pred)
        
        # Binary stats for 'ESCALATE' as positive class
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == "ESCALATE" and yp == "ESCALATE")
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == "AUTO_HANDLE" and yp == "ESCALATE")
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == "ESCALATE" and yp == "AUTO_HANDLE")
        tn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == "AUTO_HANDLE" and yp == "AUTO_HANDLE")

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Asymmetric cost-weighted penalty score (lower is better, normalized per sample)
        total_penalty = (fn * cost_missed_escalation) + (fp * cost_false_escalation)
        normalized_cost = total_penalty / len(y_true) if y_true else 0.0

        return {
            "accuracy": round(float(acc), 4),
            "escalate_precision": round(float(precision), 4),
            "escalate_recall": round(float(recall), 4),
            "escalate_f1": round(float(f1), 4),
            "true_positives_escalated": tp,
            "false_positives_over_escalated": fp,
            "false_negatives_missed_escalated": fn,
            "true_negatives_auto_handled": tn,
            "total_cost_penalty": round(total_penalty, 2),
            "cost_per_query": round(normalized_cost, 4)
        }

    def evaluate_reply_quality(
        self,
        hypotheses: List[str],
        references: List[str]
    ) -> Dict[str, Any]:
        """Calculates n-gram similarity (ROUGE-1, ROUGE-2, ROUGE-L, BLEU-4) and length compliance."""
        rouge1_f1s, rouge2_f1s, rougeL_f1s = [], [], []
        bleu_scores = []
        under_280_chars = 0

        for hyp, ref in zip(hypotheses, references):
            # ROUGE
            scores = self.rouge_evaluator.score(ref, hyp)
            rouge1_f1s.append(scores["rouge1"].fmeasure)
            rouge2_f1s.append(scores["rouge2"].fmeasure)
            rougeL_f1s.append(scores["rougeL"].fmeasure)

            # BLEU
            hyp_tokens = hyp.lower().split()
            ref_tokens = [ref.lower().split()]
            bleu = sentence_bleu(ref_tokens, hyp_tokens, smoothing_function=self.smooth_fn)
            bleu_scores.append(bleu)

            if len(hyp) <= 280:
                under_280_chars += 1

        n = len(hypotheses)
        return {
            "rouge1_f1": round(float(sum(rouge1_f1s) / n), 4) if n else 0.0,
            "rouge2_f1": round(float(sum(rouge2_f1s) / n), 4) if n else 0.0,
            "rougeL_f1": round(float(sum(rougeL_f1s) / n), 4) if n else 0.0,
            "bleu4": round(float(sum(bleu_scores) / n), 4) if n else 0.0,
            "char_limit_compliance_rate": round(under_280_chars / n, 4) if n else 0.0
        }
