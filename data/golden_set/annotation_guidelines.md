# Annotation Guidelines: 200-Case Evaluation Set for @AppleSupport

These guidelines define the protocol for **blind human review** of the 200 real Kaggle customer tweets sampled from `twcs.csv`.

---

## 1. Provenance, Anti-Anchoring & Blind Annotation Workflow

To eliminate label anchoring bias and ensure a methodologically defensible evaluation set:
- **Blind Review File**: [`data/golden_set/blind_annotation_200.csv`](blind_annotation_200.csv) contains **ONLY** the sampled queries and blank human-review columns. It contains **zero machine predictions, zero provisional labels, and zero heuristic hints**.
- **Randomized Interleaving**: The 200 cases were sampled using a documented fixed seed (`random_seed=42`) and shuffled. Cases are thoroughly interleaved across dates, intents, and difficulties rather than appearing in contiguous category blocks.
- **Independent Judgment**: The reviewer must evaluate each query independently based strictly on the customer's text.
- **Reconciliation Protocol**: After completing manual review, run:
  ```bash
  python scripts/reconcile_annotations.py
  ```
  This automatically merges your annotations with the provisional reference (`data/golden_set/provisional_labels_reference_200.json`), calculates human-vs-provisional agreement statistics (Accuracy, Macro F1, Cohen's $\kappa$), prints an intent confusion matrix, and updates [`data/golden_set/golden_eval_set_200.jsonl`](golden_eval_set_200.jsonl) with your human judgments as the definitive ground truth.

---

## 2. Target Review Columns in `blind_annotation_200.csv`

For each query, populate the following columns:

| Column | Allowed Values | Evaluation Guidance |
|---|---|---|
| `candidate_reviewed_intent` | One of the 8 canonical intents | What is the customer's **primary support problem**? (See Section 3) |
| `candidate_reviewed_escalation` | `AUTO_HANDLE` or `ESCALATE` | Can a safe public automated bot resolve this without private identity access? (See Section 4) |
| `candidate_reviewed_reason` | Free text string | Concise policy justification for the escalation decision. |
| `candidate_reviewed_difficulty` | `Easy`, `Medium`, `Hard` | Evaluated based on linguistic nuance and compound symptoms, **not string length**. (See Section 5) |
| `candidate_notes` | Free text string | Optional observations on edge cases, iOS version anomalies, or ambiguous wording. |

---

## 3. Intent Taxonomy & How to Resolve Ambiguities

### Core Principle: Primary Problem & Requested Resolution
Do **not** classify based solely on the most obvious keyword. Ask:  
> *"What is the customer's primary support problem and requested resolution?"*

#### Example Ambiguity Decisions:
- *"iOS 11 is killing my battery. Fix it."*  
  -> **`BATTERY_PERFORMANCE`** (The customer's requested resolution is about battery behavior, even though the OS update is the suspected catalyst).
- *"I bought 2 iPhones X ... I don’t see any charge on my credit card."*  
  -> **`STORE_ORDER_BILLING`** (Order tracking and credit card billing, NOT battery/charging).
- *"Why do you keep charging my card for FREE apps?"*  
  -> **`STORE_ORDER_BILLING`** (Disputed App Store charges, NOT battery).
- *"my phone died ... battery was half full"*  
  -> **`BATTERY_PERFORMANCE`** (Unexpected sudden shutdown / power failure).
- *"I can’t download apps from the app store."*  
  -> **`STORE_ORDER_BILLING`** (Apple App Store account/download failure, NOT a third-party app defect).
- *"My home sharing not working"*  
  -> **`CONNECTIVITY_SYNC`** (Local network streaming/sync protocol).

---

### The 8 Operational Intents:

1. **`SOFTWARE_UPDATE_OS`**:  
   iOS/macOS firmware updates, installation loops, bootloops, post-update system UI freezes, autocorrect glitches (e.g. iOS 11.1 capital "I" bug), and general OS settings.
2. **`BATTERY_PERFORMANCE`**:  
   Rapid battery drain, unexpected cold shutdowns, slow charging, thermal overheating during normal use, degraded battery health.
3. **`HARDWARE_AUDIO_DISPLAY`**:  
   Physical screen cracks, vertical/horizontal screen lines, dead touch digitizers, broken physical buttons, speaker/microphone defects, camera black screens, water damage.
4. **`ACCOUNT_APPLE_ID_ICLOUD`**:  
   Locked Apple IDs, forgotten passwords, 2FA code delivery issues, Activation Lock ownership disputes, iCloud storage management.
5. **`STORE_ORDER_BILLING`**:  
   App Store charges, subscription disputes, refund requests, delivery logistics, trade-in kit delays, AppleCare purchases.
6. **`CONNECTIVITY_SYNC`**:  
   Wi-Fi disconnects, Bluetooth pairing drops (car audio), cellular 'No Service' errors, AirDrop, CarPlay, Home Sharing, AirPlay.
7. **`THIRD_PARTY_APP_ISSUES`**:  
   Bugs, crashes, or feature failures confined strictly to specific non-Apple apps (Spotify, WhatsApp, YouTube, Netflix, Instagram).
8. **`GENERAL_FEEDBACK_RANT`**:  
   Emotional venting, brand praise, philosophical comments, media inquiries, or greetings without an actionable technical problem.

---

## 4. Escalation Rubric: "Safe Automated System" Rule

Do **NOT** ask: *"Did Apple historically send this person to DM?"*  
In historical Twitter support data, human agents frequently redirected customers to Direct Messages early to exchange serial numbers. Mimicking that indiscriminately defeats the purpose of automation.

Instead, ask:
> *"Would a safe automated public-support agent have enough information to resolve this without identity verification, private account access, or specialist intervention?"*

### When to ESCALATE:
1. **Physical Safety Hazards**: Thermal swelling, burning smell, sparks, melting cables, electrical hazards.
2. **Account Security & Identity**: Locked Apple ID requiring identity verification, compromised accounts, Activation Lock disputes.
3. **Financial & Transaction Disputes**: Disputed charges, unauthorized purchases, refund processing, lost/stolen delivery parcels.
4. **Hardware Failure Beyond Software Triage**: Broken glass, permanent screen lines, failed internal solder/hardware components.
5. **Explicit Customer Demand**: Direct user requests to speak with a human representative (*"speak to a human"*, *"get me an agent"*).
6. **Brand / Legal / Media Risk**: Formal threats of litigation, press inquiries, severe multi-tweet hostility.

### When to AUTO_HANDLE:
- The issue can be resolved with documented navigation paths (e.g. `Settings > General > iPhone Storage`).
- Standard device force restart procedures.
- Informational links to public Apple Support articles.
- Reassurance and polite acknowledgment for non-actionable feedback.

---

## 5. Difficulty Tier Definitions (Nuance over Length)

Do **NOT** evaluate difficulty mechanically by character count. Evaluate based on conversational nuance and multi-domain interactions:

- **Easy**: Direct, single-issue query with standard terminology and an obvious resolution pathway:
  - *"Wi-Fi doesn't work."*
  - *"How do I check my iCloud storage?"*
- **Medium**: Multi-sentence query or mild vocabulary ambiguity requiring careful reading to isolate the core problem.
- **Hard**: Subtle multi-domain compounding symptoms, colloquial slang, sarcasm, or edge-case diagnostics:
  - *"After iOS 11.0.3 my Wi-Fi drops only on my home network, Bluetooth is also disconnecting in my car, and I've already reset network settings twice."*
  - *"Why are my I's changing not showing up correctly on any of my social media platforms?"*
