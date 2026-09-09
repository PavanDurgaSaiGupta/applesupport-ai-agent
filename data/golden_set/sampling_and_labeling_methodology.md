# Sampling & Labeling Methodology: Golden Evaluation Set (200 Real Kaggle Tweets)

## 1. Objective & Design Philosophy
An AI customer-support agent cannot be judged on generic conversational fluency or perplexity alone. In technical support for Apple, an inaccurate answer can cause permanent data loss, void hardware warranty rights, or create hazardous conditions (e.g. heating a swollen lithium battery).

This **Golden Evaluation Set** comprises **200 authentic customer tweets sampled directly from Kaggle's Customer Support on Twitter (`twcs.csv`)**, verified against historical `@AppleSupport` conversation threads.

---

## 2. Sampling Strategy & Leakage Prevention

### A. Authentic Sourcing
- Sourced exclusively from genuine customer tweets addressed to `@AppleSupport` in `twcs.csv`.
- Each record retains its original Kaggle `tweet_id` and corresponding Apple response `apple_tweet_id`.

### B. Strict Conversation-Level Isolation (Zero Leakage)
To prevent the classic trap of data leakage:
1. All 200 evaluation `tweet_id`s, their paired Apple response `apple_tweet_id`s, and parent/child conversation threads were **strictly excluded** from the historical retrieval knowledge base (`data/processed/apple_pairs_sampled.jsonl`).
2. The intent classifier was trained **strictly on the historical training bank and seed templates—never touching the golden set**.
3. Automated validation is built directly into `run_pipeline.py` and `tests/test_pipeline.py`:
   ```text
   Conversation-level leakage check: PASS
   Duplicate evaluation items:       0
   Evaluation IDs in retrieval bank: 0 (Strict Isolation)
   ```

### C. Intent Stratification Across 8 Empirical Classes
Sampled across the 8 empirical intent categories identified from frequency analysis of 20,000+ real Apple Support tweets:
1. `SOFTWARE_UPDATE_OS`: iOS/macOS update glitches, installation failures, post-update slowdowns, text bugs.
2. `BATTERY_PERFORMANCE`: Rapid drain, sudden shutdown, thermal events, charging accessories.
3. `HARDWARE_AUDIO_DISPLAY`: Broken glass, home/volume button failure, camera black screen, muffled receiver mesh.
4. `ACCOUNT_APPLE_ID_ICLOUD`: Locked Apple ID, 2FA codes, iCloud storage quotas, password recovery.
5. `STORE_ORDER_BILLING`: App Store charges, refund requests, subscription cancellations, order tracking.
6. `CONNECTIVITY_SYNC`: Wi-Fi, Bluetooth, cellular/LTE, AirDrop, Apple Watch sync, CarPlay.
7. `THIRD_PARTY_APP_ISSUES`: Crashes or bugs in WhatsApp, Spotify, YouTube, Instagram, Netflix.
8. `GENERAL_FEEDBACK_RANT`: Emotional venting, foreign language routing, unannounced product speculation.

---

## 3. Labeling Protocol & Escalation Ground Truth

### A. The Core Principle: "Safe Automated System", NOT "What Apple Did"
A common mistake when labeling customer support data is copying whatever human agents did historically. On Twitter, AppleSupport agents historically redirected almost everything to Direct Messages (DM) for privacy. If an evaluation set simply copies that behavior, the "correct" answer to every query becomes "escalate to DM," defeating the entire purpose of automation.

**Our Ground Truth Rule**:
> Ground truth escalation is defined as **what a safe, competent automated support system SHOULD do based strictly on the information present in the customer's incoming message**.

### B. Escalation Decision Boundaries
An inquiry MUST be marked `ESCALATE` if and only if any of the following conditions are present:
1. **Physical Safety Hazard**: Swollen batteries, burning chargers, sparks, fire risks.
2. **Account Security & Identity**: Locked Apple ID requiring identity verification, Activation Lock ownership disputes, compromised accounts.
3. **Financial / Transactional Disputes**: Unauthorized charges, double debits, lost in-transit parcels, refund approvals.
4. **Hardware Failure Beyond Software Workaround**: Defective screen lines, broken physical switches, internal solder defects.
5. **Brand / Legal / Media Risk**: Threats of litigation, press inquiries, multi-tweet customer hostility.
6. **Explicit Customer Demand**: Direct customer demand to speak with a human being.

All other inquiries—including routine settings guidance, known software bugs, force restarts, and public policy FAQs—are classified as `AUTO_HANDLE`.

### C. Stated Reason Requirement
Every escalation decision includes an explicit, auditable stated reason (e.g. *"Account authentication or security lockout requires verified identity handoff"* or *"Financial charge dispute requires private billing agent"*).

---

## 4. Human Calibration Review
To evaluate the automated **LLM-as-a-Judge**, a 30-case validation subset (`human_annotations_sample.json`) was independently reviewed by the candidate author using the 4-dimensional evaluation rubric:
1. Grounding & Factual Soundness (1–5)
2. Brand Tone & Empathy (1–5)
3. Actionability & Triage Guidance (1–5)
4. Escalation Appropriateness (1–5)

These human ratings serve as the empirical baseline for computing Mean Absolute Error (MAE), Pearson correlation ($r$), and Cohen's Kappa ($\kappa$) against the automated evaluation harness.
