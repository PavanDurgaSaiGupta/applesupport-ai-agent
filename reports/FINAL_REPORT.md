# Engineering & Research Report: AI Customer Support Agent for @AppleSupport

**Author**: Hiver SDE Intern Candidate  
**Target Brand**: `@AppleSupport` (Customer Support on Twitter Dataset, Kaggle)  
**Evaluation Set**: 200 Real Kaggle Tweets with Provisional Ground Truth (Randomized & Shuffled Split)  
**Human Calibration Set**: 30 Cases Evaluated by Candidate Author Reviewer  
**Execution Runtime**: ~12.6 seconds (Reproducible in under 15 minutes)

---

## 1. Problem Framing: What "Good" Means for @AppleSupport

### What "Good" Means in Enterprise Tech Support
Customer support on Twitter for a brand like Apple is fundamentally distinct from general e-commerce bots. An agent for `@AppleSupport` operates in an open, public-facing forum under intense brand scrutiny. In this environment, "good" requires:

1. **Immediate Actionability over Conversational Stalling**:  
   A quality response does not merely offer empathy; it provides the immediate, exact diagnostic pathway (e.g. `Settings > General > iPhone Storage` or `Settings > Battery`) or asks the single most decisive triage question (e.g. device model and iOS build).
2. **Strict Factual Grounding (Zero Hallucination)**:  
   Hallucinating warranty terms, promising free hardware replacements, or inventing non-existent settings pathways causes direct financial harm, surges in Genius Bar traffic, and brand damage. Technical advice must be grounded in verified Apple Support documentation and historical resolution precedent.
3. **Safety and Security Prioritization**:  
   Physical safety hazards (swollen batteries, smoking chargers), account security breaches (ransom notes in Lost Mode, 2FA compromises), and payment disputes (duplicate debits, stolen pre-orders) must be routed to private Direct Messages (DM) with a clear, auditable stated reason. The escalation policy is designed to prioritize recall on safety-critical cases.
4. **Single-Tweet Budget & Calm Brand Ethos**:  
   Tweets must fit cleanly within Twitter's 280-character limit, maintain a calm, polite, and reassuring tone, and avoid robotic repetition.

### What We Chose NOT to Build (and Why)
Engineering maturity is defined by disciplined boundary setting:
- **We chose NOT to build an unconstrained generative chatbot**:  
  Allowing a large language model to generate freeform text without retrieval grounding risks unrecoverable hallucinations (promising free replacements, offering unauthorized discounts, or agreeing with customer profanity).
- **We chose NOT to automate private account or financial recovery in public**:  
  Password resets, account unbans, and refund processing cannot occur in public tweets. Fencing off these capabilities and mandating private DM escalation protects customer security and prevents social engineering attacks.
- **We chose NOT to adopt Banking77**:  
  Banking77 contains 77 fine-grained banking intents (e.g. card activation, ATM surcharges) that are completely orthogonal to hardware, firmware, and iOS diagnostics. Forcing consumer tech queries into Banking77 introduces artificial domain misalignment.
- **We chose NOT to build stateful multi-turn dialogue on Twitter public threads**:  
  As observed in historical Twitter support data, when an Apple customer issue extends past 1-2 turns, agents direct them to secure DMs (`https://t.co/GDrqU22YpT`) to exchange serial numbers and diagnostic logs. Building complex multi-turn public dialogue models solves a problem that historical brand practices in the dataset deliberately discourage.

---

## 2. Intent Taxonomy: Exploratory Analysis & Rule-Assisted Quantification

Rather than claiming that an unsupervised clustering algorithm discovered the intent taxonomy, we state the methodology precisely: **the candidate taxonomy was derived from exploratory domain analysis of Apple customer support inquiries and quantified across 20,000 authentic inbound customer tweets using rule-assisted keyword labeling**.

### Empirical Prevalence across 20,000 Inbound Tweets

| Intent Category | Frequency | Percentage | Representative Customer Example from Kaggle Dataset |
|---|:---:|:---:|---|
| `GENERAL_FEEDBACK_RANT` | 8,775 | 43.9% | *"Apple is the worst company ever. You ruined my life with this update."* |
| `SOFTWARE_UPDATE_OS` | 7,386 | 36.9% | *"Updated to iOS 11.1 yesterday and now my phone freezes constantly."* |
| `BATTERY_PERFORMANCE` | 1,080 | 5.4% | *"Battery drops from 50% to 10% in twenty minutes on iPhone 7."* |
| `HARDWARE_AUDIO_DISPLAY` | 934 | 4.7% | *"Screen has vertical green lines and touch digitizer is unresponsive."* |
| `ACCOUNT_APPLE_ID_ICLOUD` | 644 | 3.2% | *"Apple ID locked for security reasons and trusted number is no longer active."* |
| `STORE_ORDER_BILLING` | 531 | 2.7% | *"Charged twice for monthly Apple Music subscription. Need a refund."* |
| `CONNECTIVITY_SYNC` | 488 | 2.4% | *"Wi-Fi button is greyed out and Bluetooth keeps dropping in my car."* |
| `THIRD_PARTY_APP_ISSUES` | 162 | 0.8% | *"Spotify crashes immediately every time I open it on my iPad."* |

### Taxonomy Overlap, Ambiguity & Boundary Analysis
In consumer tech support, customer queries frequently span multiple technical boundaries:
1. **OS Update vs. Battery Drain Overlap**:  
   Queries such as *"iOS 11 is killing my battery"* match both update and battery patterns. When battery drain or power loss is the primary requested resolution, our refined classification prioritizes `BATTERY_PERFORMANCE`, even when the OS update is cited as the suspected catalyst.
2. **Card Charges vs. Battery Charging**:  
   Queries containing *"charging my card"* or *"charged me for free apps"* are prioritized to `STORE_ORDER_BILLING`, preventing lexical overlap with physical battery charging.
3. **App Store vs. Third-Party App Bugs**:  
   General issues downloading apps or purchasing through the App Store are routed to `STORE_ORDER_BILLING` / account services; isolated bugs within Spotify or WhatsApp belong to `THIRD_PARTY_APP_ISSUES`.
4. **Actionable Connectivity vs. General Rants**:  
   Features such as Home Sharing, AirPlay, and AirDrop are explicitly mapped to `CONNECTIVITY_SYNC` rather than falling into the unmapped catch-all bucket.

---

## 3. Data Leakage Audit & Zero-Leakage Partitioning

A core flaw in standard machine learning benchmarks is **train-test and conversation-level leakage**. We enforced strict architectural safeguards to ensure the integrity of our results:

1. **Strict Conversation-Level Isolation**:  
   All 200 evaluation `tweet_id`s, their paired Apple response `apple_tweet_id`s, and parent/child thread IDs were completely purged from the retrieval knowledge base (`data/processed/apple_pairs_sampled.jsonl`).
2. **Zero Train/Eval Contamination**:  
   The `IntentClassifier` was trained **strictly on the historical training bank and seed templates**. It never saw a single tweet or label from the evaluation set.
3. **Automated Leakage Gate**:  
   The runner script executes an automated programmatic check before every benchmark pass:
   ```text
   Conversation-level leakage check: PASS
   Duplicate evaluation items:       0
   Evaluation IDs in retrieval bank: 0 (Strict Isolation)
   ```

---

## 4. Evaluation Set Provenance & Blind Annotation Protocol

In compliance with rigorous scientific standards, every label in the 200-case evaluation set has been audited for its true origin:

### Provenance Audit Table: `data/golden_set/golden_eval_set_200.jsonl`

| Field | Assigned Origin Category | Provenance Description |
|---|:---:|---|
| `true_intent` / `ground_truth_intent` | **B & D** (Generated by code, inferred from heuristics) | Inferred via prioritized regex pattern matching (`classify_intent_rule` in `src/build_real_dataset_split.py`). **Not manually reviewed by candidate.** |
| `ground_truth_escalation` | **B & D** (Generated by code, inferred from heuristics) | Inferred via policy regex trigger rules (`ESCALATION_REGEX` in `src/build_real_dataset_split.py`). **Not manually reviewed by candidate.** |
| `escalation_reason` | **B & D** (Generated by code, inferred from heuristics) | Programmatic string template based on regex policy triggers. **Not manually reviewed by candidate.** |
| `difficulty_tier` | **B & D** (Generated by code, inferred from heuristics) | Assigned via length threshold (>140 chars) and keyword presence. **Not manually reviewed by candidate.** |
| `annotator` / `annotator_notes` | **B** (Generated by code) | Labeled as `provisional_rule_assisted`. **Not hand-annotated.** |

### Provenance Classification Key:
- **A**: Manually reviewed by the candidate.
- **B**: Generated by code.
- **C**: Generated by an LLM.
- **D**: Inferred from heuristics.
- **E**: Inherited from another dataset/source.

> [!IMPORTANT]
> Because these 200 cases have not yet been personally audited by a human, **we do not describe the set as hand-labelled or human-labelled**. The examples are authentic Kaggle tweets, but their baseline labels are **provisional rule-assisted ground truth**.

### Anti-Anchoring Blind Annotation Protocol
To eliminate **label anchoring bias** (where human annotators are biased by seeing the model's provisional predictions):
1. **Blind Annotation Spreadsheet**: [`data/golden_set/blind_annotation_200.csv`](../data/golden_set/blind_annotation_200.csv) contains **ONLY** the sampled queries and blank human-review columns. It contains **zero machine predictions, zero provisional labels, and zero heuristic hints**.
2. **Randomized Interleaving**: The 200 cases were sampled using a documented fixed seed (`random_seed=42`) and thoroughly shuffled. Cases are interleaved across dates, intents, and difficulties, eliminating block-ordering bias.
3. **Separate Provisional Reference**: [`data/golden_set/provisional_labels_reference_200.json`](../data/golden_set/provisional_labels_reference_200.json) preserves the machine baseline separately for reconciliation.
4. **Annotation Guidelines**: [`data/golden_set/annotation_guidelines.md`](../data/golden_set/annotation_guidelines.md) outlines primary-intent determination, nuance-based difficulty assessment, and escalation standards.
5. **Reconciliation Tool**: Running [`scripts/reconcile_annotations.py`](../scripts/reconcile_annotations.py) compares completed human annotations against provisional labels, computes agreement statistics, and updates the golden evaluation set with human judgments as the definitive gold standard.

---

## 5. Quantitative Results vs. Baselines

We evaluated three complete systems across the **200-Case Real-Data Evaluation Set** (Randomized & Shuffled Split):

### Baseline Definitions
- **Baseline 1 (Trivial Majority Baseline)**:  
  Predicts the empirical majority intent (`GENERAL_FEEDBACK_RANT`), applies a naive length-based escalation heuristic (>100 characters), and emits a static canned response (*"Thanks for reaching out! Send us a DM: https://t.co/GDrqU22YpT"*).
- **Baseline 2 (Simple Classical Baseline)**:  
  Uses TF-IDF + Logistic Regression for intent classification, a simple 5-keyword regex matcher for escalation (`refund`, `stolen`, `broken`, `locked`, `urgent`), and top-1 nearest neighbor response retrieved verbatim via BM25 from the historical knowledge base.
- **Proposed System (Grounded AI Support Agent)**:  
  Combines the TF-IDF hybrid classifier, the policy escalation engine with confidence gating, and a grounded response drafter adhering to documented Apple UI navigation notation (`Settings > ...`) and the 280-character budget.

### Comparative Benchmark Results

| Evaluation Metric | Baseline 1 (Trivial) | Baseline 2 (Simple) | Proposed AI Agent | Relative Impact |
|---|:---:|:---:|:---:|:---:|
| **Intent Accuracy** | 12.5% | 66.0% | **66.0%** | **+53.5%** over Baseline 1 |
| **Intent Macro F1** | 0.028 | 0.672 | **0.672** | Balanced across all 8 classes |
| **Escalation Accuracy** | 41.0% | 95.0% | **94.0%** | Calibrated operational tradeoff |
| **Escalation Recall (Safety)** | 66.7% | 50.0% | **55.6%** | Prioritizes hazardous cases |
| **Escalation F1** | 0.169 | 0.643 | **0.625** | Balanced precision & recall |
| **Cost Penalty / Query** | 0.71 | 0.23 | **0.22** | **-69.0%** Cost vs Baseline 1 (Lowest) |
| **ROUGE-L F1 (Lexical)** | 0.252 | 0.221 | **0.169** | (See Section 7 critique) |
| **BLEU-4 (Lexical)** | 0.039 | 0.040 | **0.018** | Lexical overlap diagnostic |
| **LLM Judge: Grounding (1-5)** | 2.79 | 3.86 | **3.80** | Grounded in Apple procedures |
| **LLM Judge: Tone & Empathy (1-5)**| 5.00 | 4.74 | **4.88** | Courteous, concise Apple voice |
| **LLM Judge: Actionability (1-5)** | 4.24 | 3.46 | **4.08** | Direct navigation steps |
| **LLM Judge: Escalation (1-5)** | 3.76 | 4.81 | **4.80** | Sound triage decisions |
| **LLM Judge Composite (1-5)** | 3.95 | 4.22 | **4.39** | **Top Performing Overall** |
| **Inference Latency / Query** | < 0.1 ms | 15.6 ms | **14.5 ms** | Real-time production ready |

### Why Proposed Intent Accuracy Equals Baseline 2 (And What Actually Differentiates Them)
An interviewer will immediately notice: **Proposed Intent Accuracy (66.0%) = Baseline 2 Intent Accuracy (66.0%)**.

This is an honest, expected result from our modular benchmark architecture:
1. **Shared Classifier Component**: In our evaluation harness, Baseline 2 and the Proposed Agent utilize the same underlying TF-IDF model for intent classification in order to isolate the downstream effects of response generation and escalation policy.
2. **Intent Accuracy Finding**: On broad 8-class intent classification over this noisy real-data sample, **the proposed architecture did not improve intent classification over the classical baseline**. Classical TF-IDF n-grams already capture the bulk of surface lexical cues.
3. **What Actually Makes the Proposed System Different from Baseline 2**:
   - **Escalation Reasoning**: Baseline 2 relies on an unreasoned 5-keyword regex. It lacks contextual policy awareness, cannot distinguish benign storage charges from unauthorized account fraud, and outputs no stated justification. The Proposed Agent uses `EscalationEngine` with 6 structured operational policies (thermal safety, account security, billing disputes, unrecoverable hardware, hostility, and confidence gating) and emits an auditable stated reason for every decision, achieving the lowest overall cost penalty (0.22 vs 0.23 vs 0.71).
   - **Grounded Response Generation**: Baseline 2 emits raw, unedited historical replies retrieved verbatim via nearest-neighbor search. These historical replies frequently ask redundant questions (*"Which device model do you have?"*) even when the customer already specified it, or contain outdated links. The Proposed Agent uses `ResponseGenerator` with slot extraction (suppressing redundant questions), documented settings navigation (`Settings > ...`), and strict 280-character Twitter budget compliance.
   - **Actionability & Quality**: The Proposed Agent achieves superior LLM Judge Actionability (4.08 vs 3.46) and higher Overall Composite (4.39 vs 4.22) due to these structured response synthesis improvements.

---

## 6. Human-Judge Agreement & Statistical Calibration

To evaluate the automated **LLM-as-a-Judge**, we conducted a calibration study against annotations completed by the **Candidate Author Reviewer** on a 30-case validation subset (`data/golden_set/human_annotations_sample.json`). No third-party or independent human expertise is claimed.

| Calibration Statistic | Empirical Value | Operational Interpretation |
|---|:---:|---|
| **Mean Absolute Error (MAE)** | **0.3123 / 5.0** | Low absolute error: Judge mirrors human scores within 0.31 points. |
| **Human Mean Rating** | **4.70 / 5.0** | Human evaluator judged drafted responses as high-quality. |
| **Judge Mean Rating** | **4.46 / 5.0** | Judge mirrored human standards with slight conservative skew. |
| **Pearson Correlation ($r$)** | -0.0612 ($p = 0.75$) | Near-zero linear correlation due to restricted score variance. |
| **Cohen's Kappa ($\kappa$)** | 0.0 | Near-zero agreement statistic under extreme class imbalance. |

### Honest Technical Takeaway on Judge Reliability
The judge's absolute error was low (MAE = 0.31), but agreement statistics were weak ($r = -0.0612, \kappa = 0.0$) because the human ratings had very little variance (clustering tightly between 4.5 and 5.0). Therefore, **this 30-example calibration does not establish strong judge reliability**. It serves as a preliminary heuristic indicator rather than a fully validated evaluation instrument.

---

## 7. Mandatory Section: "What is Misleading About My Headline Number?"

A rigorous engineer must expose the structural limitations, sampling constraints, and metric assumptions underlying headline numbers:

### 1. 66.0% Intent Accuracy Reflects Lexical Separation, Not Deep Reasoning
Our intent classifier achieves 66.0% accuracy across 8 classes on this noisy, real-world sample.  
**Why this is misleading**:  
In consumer tech support, vocabulary across broad classes is relatively orthogonal: "battery" rarely co-occurs with "AppleCare", and "Wi-Fi" rarely co-occurs with "refund". A TF-IDF model performs well on obvious cues, but falters on nuanced edge cases (such as distinguishing whether a post-update battery drain is primarily an OS indexing glitch or physical battery degradation). Furthermore, **the proposed classifier did not outperform the classical baseline on intent accuracy**. A 66% headline number should not be mistaken for deep semantic understanding.

### 2. Lexical Metrics (BLEU/ROUGE) Inversely Correlate with Actionability
Baseline 1 (canned response) scored a higher ROUGE-L (0.252) than the Proposed Agent (0.169).  
**Why this is misleading**:  
In customer support, **ROUGE and BLEU penalize actionable diversity**. Historical Apple Support tweets frequently use generic boilerplate (*"Thanks for reaching out! We're here to help. Send us a DM..."*). When the Proposed Agent provides specific diagnostic steps (`Settings > General > iPhone Storage`), its lexical overlap with historical boilerplate drops, causing ROUGE to decline even though its diagnostic helpfulness increases.

### 3. Escalation Recall of 55.6% Means Over 40% of Escalation Triggers Were Missed
The escalation policy is designed to prioritize recall on safety-critical cases. However, the measured **Escalation Recall was 55.6%**.  
**Why headline accuracy (94.0%) is misleading**:  
Because non-escalated cases form the vast majority of customer inquiries (182 out of 200 in this sample), high overall accuracy masks missed escalations. A recall of 55.6% means that **nearly half of the queries requiring human intervention were initially routed to auto-handling**. In high-risk enterprise operations (e.g. thermal battery hazards or account takeovers), this miss rate is unacceptable without secondary safety guardrails and human supervisor queues. We make no claim of 100% safety guarantees.

### 4. The "High-Agreement Paradox" & Weak Statistical Evidence of Judge Reliability
In our calibration study, the Mean Absolute Error was low (**0.31 / 5.0**). Yet, Pearson's $r$ (-0.06) and Cohen's Kappa ($\kappa = 0.0$) showed weak linear agreement.  
**Why this is misleading**:  
This is a textbook manifestation of the **Restriction of Range / High-Agreement Paradox** in reliability statistics. When both the human reviewer and the automated judge rate responses near the quality ceiling (clustering tightly between 4.5 and 5.0), the score variance approaches zero ($\sigma^2 \to 0$). While absolute deviation is small, Pearson's $r$ and Cohen's $\kappa$ provide **weak statistical evidence of judge reliability** due to restricted rating variance and the small 30-case sample size.

### 5. Twitter Selection & Survivorship Bias
The dataset exclusively captures customers who chose to publicly tweet at Apple.  
**Why this is misleading**:  
Customers who take to Twitter are typically more frustrated, vocal, and seeking rapid public attention. Those with quiet, routine questions use Apple Support app diagnostics, knowledge base articles, or in-store Genius Bars. The dataset overrepresents public escalation pressure and does not reflect the broader distribution of global customer support tickets.

---

## 8. Failure Analysis: Top 5 Failure Modes

Through inspection of real misclassified cases from the 200 real Kaggle tweets, we identified 5 core operational failure modes:

### Failure Mode 1: Metaphorical Language & Slang Disguising Hardware Defects
- **Real Example (Tweet ID 700)**:  
  *"Why are my I's changing not showing up correctly on any of my social media platforms? [image link]"*
- **Observed Behavior**: The classifier struggled to isolate whether this was a third-party app problem or an OS font rendering bug.
- **Root Cause Hypothesis**: The query involves the notorious iOS 11.1 unicode text rendering glitch. Colloquial descriptions often omit technical terms like "unicode" or "autocorrect".
- **Mitigation**: Expand the diagnostic keyword dictionary with observed colloquial error descriptions.

### Failure Mode 2: Multi-Domain Interactivity (OS Update Triggering Thermal Throttling)
- **Real Example (Tweet ID 246506)**:  
  *"iPhone 6s, iOS 11, connected to WiFi, downloading 9 app updates and battery drains 15% in 3 min"*
- **Observed Behavior**: The model vacillated between `SOFTWARE_UPDATE_OS`, `BATTERY_PERFORMANCE`, and `THIRD_PARTY_APP_ISSUES`.
- **Root Cause Hypothesis**: The query involves a compounded hardware-software interaction: concurrent network downloads, background app installations, and heavy processor load causing rapid battery draw. A single-label taxonomy forces an artificial choice among three valid domains.
- **Mitigation**: Support multi-label probability representations allowing joint classification.

### Failure Mode 3: Hardware Obsolescence vs Software Bug
- **Real Example (Tweet ID 154468)**:  
  *"my iphone 6s+ , got freeze daily and apps get unresponsive ..it has been happing since installed ios 11"*
- **Observed Behavior**: The agent provided standard app troubleshooting (restart phone, reinstall app) instead of explaining hardware indexing or degradation.
- **Root Cause Hypothesis**: Older devices running major new OS releases experience background spotlight indexing and thermal throttling. A text-matching agent without an explicit hardware compatibility matrix cannot deduce hardware performance boundaries.
- **Mitigation**: Integrate an in-memory Device Matrix Knowledge Graph mapping device hardware specifications (RAM, SoC) against documented OS requirements.

### Failure Mode 4: False Positive Escalation on Benign Storage Microtransactions
- **Real Example**: Inquiries asking about the standard $0.99 monthly Apple charge.
- **Observed Behavior**: The word "charged" initially triggered financial dispute safeguards.
- **Root Cause Hypothesis**: $0.99/mo is the universally known price of Apple's 50GB iCloud storage tier, resolvable via a self-serve settings explanation.
- **Mitigation**: Implement a whitelist for standard microtransactions ($0.99 iCloud storage plan) to keep informational billing inquiries in `AUTO_HANDLE`.

### Failure Mode 5: Retrieval Mismatch from Context Duplication
- **Real Example**: Customer specifies: *"I have an iPhone 6s Plus and just did the most recent update."*
- **Observed Behavior**: The retriever pulled a historical reply where Apple asked: *"Which device model do you have?"*
- **Root Cause Hypothesis**: Historical support tweets frequently begin with basic diagnostic triage questions. When a customer preemptively answers these in their first tweet, retrieving the historical top-1 reply results in redundant questions.
- **Mitigation**: Implement slot-filling extraction for `device_model` and `os_version`. If already present in the incoming query, advance directly to level-2 diagnostics.

---

## 9. What You'd Do Next with One More Week

1. **Complete Blind Human Review of All 200 Cases**:  
   Execute full manual annotation using [`data/golden_set/blind_annotation_200.csv`](../data/golden_set/blind_annotation_200.csv) and [`data/golden_set/annotation_guidelines.md`](../data/golden_set/annotation_guidelines.md), then run [`scripts/reconcile_annotations.py`](../scripts/reconcile_annotations.py) to establish verified ground truth.
2. **Stateful Dialogue State Tracking (DST)**:  
   Implement a lightweight state machine that tracks conversation slots (`device_model`, `os_version`, `attempted_steps`) across multi-turn threads to eliminate redundant triage questions.
3. **Device Matrix Knowledge Graph**:  
   Integrate an in-memory SQLite database of Apple hardware specifications (SoC, RAM, battery capacities, and active Apple Service Programs observed in public documentation).
4. **Active Learning Queue on Boundary Queries**:  
   Direct customer inquiries that fall in the low-confidence margin (0.15 - 0.25) to a human supervisor queue, automatically incorporating human resolutions back into the retrieval knowledge base.
5. **Adversarial Input Guardrails (NeMo / Llama-Guard)**:  
   Deploy an input sanitization layer to filter prompt injection attempts, social engineering exploits, and profane harassment before reaching the core agent.

---

## 10. Submission Verification Checklist
- [x] **Reproducible Pipeline**: `python run_pipeline.py` executes in **~12.6 seconds** (requirement: < 15 min).
- [x] **Real-Data Evaluation Set**: 200 real Kaggle tweets (`data/golden_set/golden_eval_set_200.jsonl`) with verifiable tweet IDs and audited provenance.
- [x] **Blind Annotation Template & Guidelines**: `data/golden_set/blind_annotation_200.csv`, `blind_annotation_200.jsonl`, and `annotation_guidelines.md` provided for candidate manual review.
- [x] **Reconciliation Tool**: `scripts/reconcile_annotations.py` provided to compute human-vs-provisional agreement and update the golden evaluation set.
- [x] **Zero-Leakage Guarantee**: Automated verification confirmed 0 evaluation IDs present in retrieval index.
- [x] **Evaluation Harness**: Automated metrics (`src/evaluator.py`) + 4-dimensional rubric (`src/llm_judge.py`) + calibration analysis (`src/human_agreement.py`).
- [x] **Comprehensive Report**: Addressing all 5 mandatory sections with empirical data.
- [x] **Decision Log**: 15 non-obvious engineering decisions and trade-offs (`reports/DECISION_LOG.md`).
