"""
Data Processing & Conversation Pair Extraction for @AppleSupport.

Extracts customer-to-brand dialogue pairs from the Kaggle TWCS dataset,
cleans Twitter-specific artifacts (while preserving hardware/OS entities),
and constructs the grounded historical resolution knowledge base.
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Iterator
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
HANDLE_PATTERN = re.compile(r"@[\w_]+")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_tweet_text(text: str, remove_handles: bool = True, remove_urls: bool = False) -> str:
    """
    Cleans tweet text:
    - Normalizes unicode artifacts (e.g., iOS 11 'I️' symbol)
    - Optionally removes handles while preserving content
    - Normalizes whitespace
    """
    if not isinstance(text, str):
        return ""
    
    # Clean known iOS 11 unicode glitch (capital I with box / question mark)
    text = text.replace("I️", "I").replace("i️", "i").replace("\ufe0f", "")
    
    # Clean HTML entities
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    
    if remove_handles:
        text = HANDLE_PATTERN.sub("", text)
        
    if remove_urls:
        text = URL_PATTERN.sub("", text)
        
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def extract_apple_conversation_pairs(
    twcs_path: str = "twcs/twcs.csv",
    output_path: str = "data/processed/apple_pairs_sampled.jsonl",
    max_pairs: int = 25000,
    chunksize: int = 150000,
) -> int:
    """
    Reconstructs (customer_tweet, apple_reply) pairs from twcs.csv.
    Streams twcs in chunks to minimize RAM usage.
    """
    if not os.path.exists(twcs_path):
        raise FileNotFoundError(f"Source dataset not found at {twcs_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    logger.info(f"Scanning {twcs_path} for @AppleSupport conversation pairs...")

    # First pass: collect AppleSupport outbound tweets and their in_response_to_tweet_id
    apple_replies: Dict[int, Dict[str, Any]] = {}
    needed_customer_ids = set()

    for chunk in pd.read_csv(
        twcs_path,
        chunksize=chunksize,
        usecols=["tweet_id", "author_id", "inbound", "created_at", "text", "in_response_to_tweet_id"],
        low_memory=False,
    ):
        apple_chunk = chunk[chunk["author_id"] == "AppleSupport"]
        for _, row in apple_chunk.iterrows():
            in_resp = row["in_response_to_tweet_id"]
            if pd.notna(in_resp):
                try:
                    resp_id = int(in_resp)
                    apple_replies[resp_id] = {
                        "apple_tweet_id": int(row["tweet_id"]),
                        "apple_created_at": str(row["created_at"]),
                        "apple_text": str(row["text"]),
                    }
                    needed_customer_ids.add(resp_id)
                except ValueError:
                    continue
        if len(needed_customer_ids) >= max_pairs * 2:
            break

    logger.info(f"Found {len(apple_replies)} AppleSupport responses to link. Scanning for customer tweets...")

    # Second pass: find matching customer tweets
    saved_pairs = 0
    with open(output_path, "w", encoding="utf-8") as f_out:
        for chunk in pd.read_csv(
            twcs_path,
            chunksize=chunksize,
            usecols=["tweet_id", "author_id", "inbound", "created_at", "text", "in_response_to_tweet_id"],
            low_memory=False,
        ):
            matching_cust = chunk[chunk["tweet_id"].isin(needed_customer_ids)]
            for _, cust_row in matching_cust.iterrows():
                cid = int(cust_row["tweet_id"])
                cust_text = str(cust_row["text"])
                cleaned_cust = clean_tweet_text(cust_text, remove_handles=True)

                # Filter out empty or uninformative customer tweets
                if len(cleaned_cust) < 15:
                    continue
                # Skip tweets that are just raw links
                if URL_PATTERN.fullmatch(cleaned_cust):
                    continue

                apple_info = apple_replies.get(cid)
                if not apple_info:
                    continue

                apple_reply_text = apple_info["apple_text"]
                cleaned_apple_reply = clean_tweet_text(apple_reply_text, remove_handles=True)

                record = {
                    "pair_id": cid,
                    "customer_tweet_id": cid,
                    "customer_raw_text": cust_text,
                    "customer_text": cleaned_cust,
                    "customer_created_at": str(cust_row["created_at"]),
                    "apple_tweet_id": apple_info["apple_tweet_id"],
                    "apple_raw_reply": apple_reply_text,
                    "apple_reply": cleaned_apple_reply,
                    "apple_created_at": apple_info["apple_created_at"],
                }

                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                saved_pairs += 1
                if saved_pairs >= max_pairs:
                    break
            if saved_pairs >= max_pairs:
                break

    logger.info(f"Extracted and saved {saved_pairs} valid conversation pairs to {output_path}")
    return saved_pairs


def load_conversation_pairs(path: str = "data/processed/apple_pairs_sampled.jsonl", limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Loads processed conversation pairs from jsonl."""
    pairs = []
    if not os.path.exists(path):
        return pairs
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            line = line.strip()
            if line:
                pairs.append(json.loads(line))
    return pairs


if __name__ == "__main__":
    extract_apple_conversation_pairs(max_pairs=10000)
