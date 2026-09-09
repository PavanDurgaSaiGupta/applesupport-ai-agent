"""
FastAPI Backend Adapter for @AppleSupport AI Agent.

Serves the internal operations dashboard and exposes REST endpoints
backed by the real AppleSupportAgent pipeline and repository benchmark files.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agent import AppleSupportAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("web_api")

app = FastAPI(
    title="AppleSupport AI Support Agent API",
    description="Internal operations and evaluation console API for @AppleSupport triage agent.",
    version="1.0.0"
)

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize single agent instance
logger.info("Initializing AppleSupportAgent instance...")
agent = AppleSupportAgent()
logger.info("AppleSupportAgent initialized successfully.")

# Paths to data and benchmark files
BENCHMARK_FINAL_PATH = os.path.join("reports", "benchmark_results.json")
BENCHMARK_VAL_PATH = os.path.join("reports", "benchmark_results_validation.json")
VAL_SET_PATH = os.path.join("data", "splits", "val_set.jsonl")
FINAL_TEST_PATH = os.path.join("data", "splits", "final_test_200.jsonl")
TRAIN_DATA_PATH = os.path.join("data", "processed", "apple_pairs_sampled.jsonl")


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Incoming customer support tweet / query")


@app.get("/api/health")
def get_health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "backend": "online"}


@app.post("/api/analyze")
def analyze_message(req: AnalyzeRequest) -> Dict[str, Any]:
    """
    Executes the full triage and drafting pipeline for an incoming customer tweet.
    Calls AppleSupportAgent.process_query(message) and returns the real structured result.
    """
    cleaned_query = req.message.strip()
    if not cleaned_query:
        raise HTTPException(status_code=400, detail="Query message cannot be empty.")

    try:
        result = agent.process_query(cleaned_query)
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Agent pipeline processing error: {str(e)}")


@app.get("/api/benchmark")
def get_benchmark() -> Dict[str, Any]:
    """
    Reads actual benchmark data from repository files:
    - reports/benchmark_results.json (Frozen Final Holdout Set, N=200)
    - reports/benchmark_results_validation.json (Validation Split, N=100)
    Returns them as strictly separate sections.
    """
    output: Dict[str, Any] = {
        "final": None,
        "validation": None
    }

    if os.path.exists(BENCHMARK_FINAL_PATH):
        try:
            with open(BENCHMARK_FINAL_PATH, "r", encoding="utf-8") as f:
                output["final"] = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {BENCHMARK_FINAL_PATH}: {e}")
            output["final_error"] = str(e)
    else:
        output["final_error"] = f"File not found: {BENCHMARK_FINAL_PATH}"

    if os.path.exists(BENCHMARK_VAL_PATH):
        try:
            with open(BENCHMARK_VAL_PATH, "r", encoding="utf-8") as f:
                output["validation"] = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {BENCHMARK_VAL_PATH}: {e}")
            output["validation_error"] = str(e)
    else:
        output["validation_error"] = f"File not found: {BENCHMARK_VAL_PATH}"

    return output


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    """
    Derives real project status and integrity metrics directly from repository files.
    Computes exact overlap counts across Train, Val, and Final sets.
    """
    # 1. Final holdout cases and human review status
    final_total = 0
    final_human_reviewed = 0
    annotators = set()
    final_tweet_ids = set()
    final_conv_ids = set()

    if os.path.exists(FINAL_TEST_PATH):
        with open(FINAL_TEST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                final_total += 1
                if item.get("manual_review_status") == "human_verified":
                    final_human_reviewed += 1
                if item.get("annotator"):
                    annotators.add(item.get("annotator"))
                if item.get("tweet_id"):
                    final_tweet_ids.add(str(item.get("tweet_id")))
                if item.get("conversation_id"):
                    final_conv_ids.add(str(item.get("conversation_id")))

    # 2. Validation split cases
    val_total = 0
    val_tweet_ids = set()
    val_conv_ids = set()

    if os.path.exists(VAL_SET_PATH):
        with open(VAL_SET_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                val_total += 1
                if item.get("tweet_id"):
                    val_tweet_ids.add(str(item.get("tweet_id")))
                if item.get("conversation_id"):
                    val_conv_ids.add(str(item.get("conversation_id")))

    # 3. Training / Retrieval Bank entries
    train_total = 0
    train_tweet_ids = set()
    train_conv_ids = set()

    if os.path.exists(TRAIN_DATA_PATH):
        with open(TRAIN_DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                train_total += 1
                if item.get("customer_tweet_id"):
                    train_tweet_ids.add(str(item.get("customer_tweet_id")))
                if item.get("conversation_id"):
                    train_conv_ids.add(str(item.get("conversation_id")))

    # 4. Mathematically compute overlaps
    train_val_tweet_overlap = len(train_tweet_ids & val_tweet_ids)
    train_final_tweet_overlap = len(train_tweet_ids & final_tweet_ids)
    val_final_tweet_overlap = len(val_tweet_ids & final_tweet_ids)

    train_val_conv_overlap = len((train_conv_ids & val_conv_ids) - {""})
    train_final_conv_overlap = len((train_conv_ids & final_conv_ids) - {""})
    val_final_conv_overlap = len((val_conv_ids & final_conv_ids) - {""})

    leakage_passed = (
        train_val_tweet_overlap == 0
        and train_final_tweet_overlap == 0
        and val_final_tweet_overlap == 0
        and train_val_conv_overlap == 0
        and train_final_conv_overlap == 0
        and val_final_conv_overlap == 0
    )

    review_complete = (final_total > 0 and final_human_reviewed == final_total)

    return {
        "backend_status": "online",
        "dataset": "AppleSupport",
        "golden_total": final_total,
        "human_reviewed": final_human_reviewed,
        "manual_review_status": "COMPLETE" if review_complete else "PENDING",
        "annotator_id": list(annotators)[0] if annotators else "Unknown",
        "validation_total": val_total,
        "train_retrieval_total": train_total,
        "train_validation_overlap": train_val_tweet_overlap + train_val_conv_overlap,
        "train_final_overlap": train_final_tweet_overlap + train_final_conv_overlap,
        "validation_final_overlap": val_final_tweet_overlap + val_final_conv_overlap,
        "leakage_status": "PASS" if leakage_passed else "FAIL",
        "frozen_holdout_status": "FROZEN (Evaluated Once)"
    }


@app.get("/api/failures")
def get_failure_modes() -> List[Dict[str, Any]]:
    """
    Returns the 5 empirically identified failure modes documented in Section 8 of FINAL_REPORT.md.
    """
    return [
        {
            "id": 1,
            "title": "Metaphorical Language & Slang Disguising Hardware Defects",
            "example": "Why are my I's changing not showing up correctly on any of my social media platforms? [image link] (Tweet ID 700)",
            "observed": "Classifier vacillated between THIRD_PARTY_APP_ISSUES and OS font rendering bug.",
            "root_cause": "The query involves the iOS 11.1 unicode text rendering glitch. Colloquial descriptions often omit technical keywords like 'unicode' or 'autocorrect'.",
            "mitigation": "Expand the diagnostic keyword dictionary with observed colloquial error descriptions."
        },
        {
            "id": 2,
            "title": "Multi-Domain Interactivity (OS Update Triggering Thermal Throttling)",
            "example": "iPhone 6s, iOS 11, connected to WiFi, downloading 9 app updates and battery drains 15% in 3 min (Tweet ID 246506)",
            "observed": "Model was forced into single label among SOFTWARE_UPDATE_OS, BATTERY_PERFORMANCE, and THIRD_PARTY_APP_ISSUES.",
            "root_cause": "Compounded hardware-software interaction: concurrent network downloads, background app installations, and heavy processor load causing rapid battery draw. Single-label taxonomy forces an artificial choice.",
            "mitigation": "Support multi-label probability representations allowing joint classification."
        },
        {
            "id": 3,
            "title": "Hardware Obsolescence vs Software Bug",
            "example": "my iphone 6s+ , got freeze daily and apps get unresponsive ..it has been happing since installed ios 11 (Tweet ID 154468)",
            "observed": "Agent provided standard app restart troubleshooting instead of identifying hardware indexing and degradation boundaries.",
            "root_cause": "Older devices running major new OS releases experience background spotlight indexing and thermal throttling. Text-matching without hardware compatibility metadata cannot deduce hardware boundaries.",
            "mitigation": "Integrate an in-memory Device Matrix Knowledge Graph mapping device hardware specs against documented OS requirements."
        },
        {
            "id": 4,
            "title": "False Positive Escalation on Benign Storage Microtransactions",
            "example": "Inquiries inquiring about the recurring $0.99 monthly Apple charge.",
            "observed": "The word 'charged' triggered high-severity financial dispute safeguards.",
            "root_cause": "$0.99/mo is the universally known price of Apple's 50GB iCloud storage tier, resolvable via self-serve settings explanation.",
            "mitigation": "Implement a whitelist for standard recurring microtransactions ($0.99 iCloud storage) to keep informational billing inquiries in AUTO_HANDLE."
        },
        {
            "id": 5,
            "title": "Retrieval Mismatch from Preemptive Context Duplication",
            "example": "Customer specifies: 'I have an iPhone 6s Plus and just did the most recent update.'",
            "observed": "Retriever pulled historical reply where Apple asked: 'Which device model do you have?'",
            "root_cause": "Historical support tweets frequently begin with basic diagnostic triage questions. When a customer preemptively answers these in their first tweet, retrieving the historical top-1 reply results in redundant questions.",
            "mitigation": "Implement slot-filling extraction for device_model and os_version. If already present in query, advance directly to level-2 diagnostics."
        }
    ]


# Function to mount web static files once web directory exists
def mount_static_app():
    if os.path.exists("web"):
        app.mount("/", StaticFiles(directory="web", html=True), name="web")

mount_static_app()
