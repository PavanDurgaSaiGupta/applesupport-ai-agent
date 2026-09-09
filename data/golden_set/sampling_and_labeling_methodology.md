# Sampling & Labeling Methodology: Golden Evaluation Set (200 Cases)

## 1. Objective & Philosophy
An AI agent for customer support cannot be evaluated on generic perplexity or loose BLEU scores alone. In technical support for a high-value brand like Apple, an incorrect answer can brick a device, forfeit warranty rights, or create physical safety hazards (e.g. heating swollen batteries). 

This Golden Evaluation Set comprises **200 rigorously curated and annotated customer cases**, constructed to test the core trilemma of support automation:
1. **Accurate Diagnosis (Intent Classification)**
2. **Grounded Resolution Guidance (Reply Drafting)**
3. **Safety & Cost-Effective Triage (Escalation Decision & Reason)**

---

## 2. Sampling Strategy
To avoid the standard pitfall of uniform random sampling—which massively overrepresents easy, repetitive questions like *"how do I update my phone"*—we employed **Stratified Boundary Sampling**:

1. **Stratification Across 8 Empirical Intents**:
   - Exactly 25 cases per intent class (200 total) across the entire spectrum of Apple Support operations:
     - `SOFTWARE_UPDATE_OS`: Firmware freezes, iOS 11 text bugs, OTA verify errors, APFS transitions.
     - `BATTERY_PERFORMANCE`: Thermal throttling, premature shutdown, swollen batteries, lifecycle health.
     - `HARDWARE_AUDIO_DISPLAY`: Broken digitizers, muffled receiver mesh, butterfly keys, staingate.
     - `ACCOUNT_APPLE_ID_ICLOUD`: 2FA loss, Activation Lock, deceased estates, iCloud storage discrepancies.
     - `STORE_ORDER_BILLING`: In-app refund fraud, missing shipments, trade-ins, educational discounts.
     - `CONNECTIVITY_SYNC`: Wi-Fi chip solder failures, AirDrop mDNS conflicts, CarPlay, Bluetooth RF attenuation.
     - `THIRD_PARTY_APP_ISSUES`: App store update loops, RAM watchdog kills, background battery drains.
     - `GENERAL_FEEDBACK_RANT`: Emotional venting, foreign languages, legal threats, media inquiries, viral hoaxes.

2. **Difficulty Tiering**:
   - **Tier 1: Easy (40%, 80 cases)**: Standard inquiries with canonical Apple documentation answers (e.g., clearing app cache, turning off auto-join Wi-Fi).
   - **Tier 2: Medium (40%, 80 cases)**: Queries involving ambiguous symptoms, device interactions, or settings dependencies (e.g., GPS drift due to router BSSID, carrier APN provisioning).
   - **Tier 3: Hard / Edge Cases (20%, 40 cases)**: Adversarial or high-risk inputs including physical safety hazards, legal threats, phishing alerts, deceased estate access, and multi-turn hostility.

3. **Escalation Distribution**:
   - `AUTO_HANDLE`: 115 cases (57.5%)
   - `ESCALATE`: 85 cases (42.5%)
   Reflects a realistic automation target: deflect ~60% of routine diagnostic burden while strictly capturing the 40% that require human empathy, physical repair, or private credential access.

---

## 3. Annotation Protocol & Labeling Guidelines

Every case was annotated according to formal operational rubrics:

### A. Intent Taxonomy Rules
- A query mentioning battery drain caused immediately by an iOS update is tagged `BATTERY_PERFORMANCE` if the primary diagnostic is battery inspection, or `SOFTWARE_UPDATE_OS` if the issue is an installation loop.
- A query reporting an unwanted charge on an account is classified `STORE_ORDER_BILLING` rather than `ACCOUNT_APPLE_ID_ICLOUD`.
- Non-English tweets are classified under `GENERAL_FEEDBACK_RANT` to trigger the language-specific routing protocol.

### B. Escalation Decision Boundaries
An agent MUST escalate (`ESCALATE`) if and only if any of the following **Escalation Triggers** are met:
1. **Physical Safety Hazard**: Swollen batteries, smoking chargers, sparks.
2. **Account Security & Identity**: Locked Apple ID requiring personal identity verification, Activation Lock disputes, ransom extortion.
3. **Financial / Transactional Action**: Charge disputes, double billing, lost in-transit parcels, refund approvals.
4. **Hardware Failure Beyond Software Workaround**: Defective screen lines, broken chassis switches, failed Wi-Fi hardware chips.
5. **Brand / Legal / Media Risk**: Threats of litigation, press inquiries, multi-tweet customer hostility/distress.
6. **Explicit Customer Demand**: Direct customer demand for human agent handoff.

If none of these triggers are present, the case MUST be marked `AUTO_HANDLE`.

### C. Stated Reason Requirement
Every escalation decision must include a concise, auditable reason (e.g. *"Account security lockout requires private verification"* or *"Hardware display panel defect requires Genius Bar repair"*).

---

## 4. Quality Assurance & Calibration Set
To measure inter-annotator agreement and validate the automated **LLM-as-a-Judge**, a subset of 30 cases (`human_annotations_sample.json`) was independently scored by experienced support evaluators across 4 dimensions:
1. Grounding & Factual Soundness (1–5)
2. Brand Tone & Empathy (1–5)
3. Actionability & Triage Guidance (1–5)
4. Escalation Appropriateness (1–5)

These human scores serve as the empirical ground truth for computing **Cohen's Kappa ($\kappa$)** and **Pearson correlation ($r$)** against the automated evaluation harness.
