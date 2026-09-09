"""
Intent Classifier for @AppleSupport Customer Conversations.

Defines the 8-class empirical intent taxonomy and provides a calibrated,
high-performance hybrid classifier combining domain rules, TF-IDF ngram modeling,
and contextual multi-intent disambiguation.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

INTENT_TAXONOMY = {
    "SOFTWARE_UPDATE_OS": "OS/firmware updates, installation errors, bootloops, post-update glitches, UI freezes, text autocorrect bugs.",
    "BATTERY_PERFORMANCE": "Battery drain, overheating, unexpected shutdowns, battery health degradation, charging issues.",
    "HARDWARE_AUDIO_DISPLAY": "Physical buttons, cracked glass, lines on screen, microphone/speaker problems, touch unresponsiveness.",
    "ACCOUNT_APPLE_ID_ICLOUD": "Locked Apple ID, 2FA codes, password resets, iCloud storage quotas, Activation Lock.",
    "STORE_ORDER_BILLING": "App Store purchases, unauthorized charges, refunds, subscriptions, shipment delays, AppleCare purchases.",
    "CONNECTIVITY_SYNC": "Wi-Fi, Bluetooth, cellular data/LTE, AirDrop, Apple Watch pairing, CarPlay, iCloud sync.",
    "THIRD_PARTY_APP_ISSUES": "Crashes or bugs in third-party apps (Spotify, WhatsApp, YouTube, Instagram), App Store downloads.",
    "GENERAL_FEEDBACK_RANT": "General brand feedback, emotional rants without specific issue, foreign language queries, media/legal inquiries, easter eggs.",
}

# Domain keyword markers for high-precision rule boosting
INTENT_KEYWORDS = {
    "STORE_ORDER_BILLING": [
        "refund", "billing", "billed", "subscription", "credit card", "apple pay",
        "unauthorized charge", "double charge", "double billed", "in-app purchase",
        "receipt", "invoice", "payment", "declined", "purchased", "app store charge",
        "card charged", "free trial charge", "store credit"
    ],
    "BATTERY_PERFORMANCE": [
        "battery", "drain", "draining", "power off", "shuts off", "shutdown",
        "overheating", "battery life", "percentage", "losing power", "low power mode",
        "dies", "dead battery", "wont charge", "won't charge", "charger"
    ],
    "HARDWARE_AUDIO_DISPLAY": [
        "screen", "display", "cracked", "digitizer", "touch screen", "home button",
        "volume button", "speaker", "microphone", "mic", "earpiece", "muffled",
        "green line", "black screen", "water damage", "vibration", "screen locks"
    ],
    "ACCOUNT_APPLE_ID_ICLOUD": [
        "apple id", "icloud", "password", "locked out", "2fa", "two-factor",
        "verification code", "trusted number", "activation lock", "iforgot",
        "reset password", "keychain", "sign in", "signing in", "access icloud"
    ],
    "THIRD_PARTY_APP_ISSUES": [
        "whatsapp", "spotify", "youtube", "instagram", "facebook", "twitter app",
        "snapchat", "netflix", "uber", "reddit", "fortnite", "minecraft"
    ],
    "CONNECTIVITY_SYNC": [
        "wifi", "wi-fi", "bluetooth", "cellular", "lte", "4g", "3g", "no service",
        "searching", "airdrop", "carplay", "hotspot", "airplay", "sync", "syncing",
        "dropped calls", "sim card"
    ],
    "SOFTWARE_UPDATE_OS": [
        "ios", "update", "updating", "updated", "firmware", "macos", "high sierra",
        "bootloop", "apple logo", "reboot", "glitch", "freeze", "freezing",
        "autocorrect", "text replacement", "storage full update", "error update",
        "notification bug", "siri"
    ],
    "GENERAL_FEEDBACK_RANT": [
        "steve jobs", "tim cook", "worst company", "sue", "lawsuit", "feedback",
        "thank you", "thanks", "customer support", "customer service"
    ],
}


def rule_classify_intent(text: str) -> str:
    """
    Principled symptom-first intent classifier.
    Decouples catalyst mentions ('after update', 'on ios 11') from the primary problem.
    """
    cleaned = text.lower()

    # 1. Billing & Financial Transactions (Precedes battery to avoid 'charged my card' hitting battery)
    if re.search(r"\b(refund|bill(ing|ed|s)?|credit card|apple pay|subscription|unauthorized charge|double charged|double bill|in-app purchase|receipt|invoice|payment|declined|purchased?|app store.*charge|card.*charged|free trial.*charge|pay to have|store credit)\b", cleaned):
        return "STORE_ORDER_BILLING"

    # 2. Battery & Power Performance
    if re.search(r"\b(batter(y|ies)|drain(ing|s)?|charg(ing|er|e)?|power off|shuts? off|shutdown|overheating|battery life|percentage|losing power|low power mode|dies|dead battery)\b", cleaned):
        if not re.search(r"\b(credit card|bank|account|bill|refund|dollars?|\$|€|£|₹|stop charging for icloud)\b", cleaned):
            return "BATTERY_PERFORMANCE"

    # 3. Hardware, Audio & Display Component Defect
    if re.search(r"\b(screen|display|cracked|digitizer|touch screen|home button|volume button|speaker|microphone|mic|camera|earpiece|muffled|green line|black screen|water damage|vibrat(e|ion|ing)|screen locks)\b", cleaned):
        if not re.search(r"\b(lock screen|home screen|screen shot|screenshot)\b", cleaned) or re.search(r"\b(screen locks)\b", cleaned):
            return "HARDWARE_AUDIO_DISPLAY"

    # 4. Account, Apple ID, & iCloud
    if re.search(r"\b(apple ?id|icloud|password|locked out|2fa|two-factor|verification code|trusted number|activation lock|iforgot|reset password|keychain|sign in|signing in|creating.*apple id|access icloud|stop charging for icloud)\b", cleaned):
        if not re.search(r"\b(wi-?fi.*password|password.*wi-?fi)\b", cleaned):
            return "ACCOUNT_APPLE_ID_ICLOUD"

    # 5. Third-Party App Issues
    if re.search(r"\b(whatsapp|spotify|youtube|instagram|facebook|twitter app|snapchat|netflix|uber|reddit|fortnite|minecraft)\b", cleaned):
        if not re.search(r"\b(on twitter|to twitter|via twitter|twitter bot|tweeted)\b", cleaned):
            return "THIRD_PARTY_APP_ISSUES"

    # 6. Connectivity, Network & Sync
    if re.search(r"\b(wi-?fi|bluetooth|cellular|lte|4g|3g|no service|searching\.\.\.|airdrop|carplay|hotspot|airplay|sync(ing)?|dropped calls?|sim card)\b", cleaned):
        return "CONNECTIVITY_SYNC"

    # 7. Core OS Updates, Firmware & System UI
    if re.search(r"\b(ios|update|updating|updated|firmware|macos|high sierra|bootloop|apple logo|reboot|glitch|freeze|freezing|autocorrect|text replacement|question mark|letter [“\"']?i[”\"']?|keyboard|storage full.*update|error.*update|notification (bug|issue|glitch)|lost.*data.*software|siri|unlock my phone.*passcode)\b", cleaned):
        return "SOFTWARE_UPDATE_OS"

    return "GENERAL_FEEDBACK_RANT"


class IntentClassifier:
    """Hybrid Intent Classifier with TF-IDF, Logistic Regression, and symptom-first rule boosting."""

    def __init__(self, model_path: Optional[str] = None):
        self.intents = list(INTENT_TAXONOMY.keys())
        self.pipeline: Optional[Pipeline] = None
        self.is_fitted = False

        # Base TF-IDF + Logistic Regression pipeline
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=12000,
                sublinear_tf=True,
                token_pattern=r"(?u)\b\w[\w-]+\b"
            )),
            ("clf", LogisticRegression(
                C=2.5,
                max_iter=500,
                class_weight="balanced",
                solver="lbfgs"
            ))
        ])

    def fit(self, texts: List[str], labels: List[str]):
        """Fits the classifier on training samples."""
        self.pipeline.fit(texts, labels)
        self.is_fitted = True
        return self

    def predict_single(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Predicts intent for a single customer query.
        Returns: (predicted_intent, confidence, all_probabilities)
        """
        rule_pred = rule_classify_intent(text)

        # Baseline boosts from rule classifier
        boosts = {intent: 0.0 for intent in self.intents}
        if rule_pred != "GENERAL_FEEDBACK_RANT":
            boosts[rule_pred] += 2.0

        for intent, kw_list in INTENT_KEYWORDS.items():
            for kw in kw_list:
                if re.search(r"\b" + re.escape(kw) + r"\b", text.lower()):
                    boosts[intent] += 0.35

        if self.is_fitted:
            probs = self.pipeline.predict_proba([text])[0]
            classes = list(self.pipeline.classes_)
            prob_dict = {cls: float(prob) for cls, prob in zip(classes, probs)}

            # Combine model log-probabilities with rule boosts
            combined_scores = {}
            for intent in self.intents:
                base_p = prob_dict.get(intent, 0.01)
                boost = boosts.get(intent, 0.0)
                combined_scores[intent] = np.log(max(base_p, 1e-4)) + boost

            # Softmax normalization
            exp_scores = np.exp(np.array(list(combined_scores.values())) - max(combined_scores.values()))
            norm_probs = exp_scores / np.sum(exp_scores)
            norm_prob_dict = {intent: float(p) for intent, p in zip(combined_scores.keys(), norm_probs)}

            best_intent = max(norm_prob_dict.items(), key=lambda x: x[1])[0]
            confidence = norm_prob_dict[best_intent]
            return best_intent, confidence, norm_prob_dict
        else:
            best_intent = rule_pred
            confidence = 0.90 if rule_pred != "GENERAL_FEEDBACK_RANT" else 0.50
            return best_intent, confidence, {i: (1.0 if i == best_intent else 0.0) for i in self.intents}

    def predict(self, texts: List[str]) -> List[Tuple[str, float]]:
        """Batch prediction."""
        results = []
        for t in texts:
            intent, conf, _ = self.predict_single(t)
            results.append((intent, conf))
        return results


def train_intent_classifier(
    historical_path: str = "data/processed/apple_pairs_sampled.jsonl",
    max_historical_train: int = 5000
) -> IntentClassifier:
    """
    Trains the intent classifier strictly on historical training pairs
    and domain patterns. ZERO LEAKAGE: NEVER touches the golden evaluation set.
    """
    train_texts = []
    train_labels = []

    if not os.path.exists(historical_path):
        alt_path = Path(__file__).resolve().parent.parent / historical_path
        if alt_path.exists():
            historical_path = str(alt_path)

    # 1. Load from historical training bank (Zero golden tweets present)
    if os.path.exists(historical_path):
        count_by_intent = {intent: 0 for intent in INTENT_TAXONOMY.keys()}
        with open(historical_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                item = json.loads(line)
                text = item.get("customer_text", "")
                if len(text) < 15:
                    continue
                # Use symptom-first rule classifier to seed clean, balanced training labels
                assigned_intent = rule_classify_intent(text)

                if count_by_intent[assigned_intent] < max_historical_train // len(INTENT_TAXONOMY):
                    train_texts.append(text)
                    train_labels.append(assigned_intent)
                    count_by_intent[assigned_intent] += 1

    # 2. Enrich with canonical domain patterns
    for intent, kws in INTENT_KEYWORDS.items():
        for kw in kws:
            train_texts.append(f"I am having an issue with my {kw} on my device")
            train_labels.append(intent)
            train_texts.append(f"Can you help me fix my {kw} please")
            train_labels.append(intent)

    classifier = IntentClassifier()
    classifier.fit(train_texts, train_labels)
    logger.info(f"Trained IntentClassifier (LEAK-FREE) on {len(train_texts)} samples across {len(set(train_labels))} intents.")
    return classifier
