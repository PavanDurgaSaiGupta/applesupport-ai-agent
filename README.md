# @AppleSupport AI Support Agent & Grounded Evaluation Suite

> **Hiver SDE Intern Take-Home Submission**  
> *"Whether you can turn a messy real-world dataset into a working AI system and prove it works. The proof is worth more than the system."*

An end-to-end, production-ready AI customer-support agent built for **`@AppleSupport`** using the Kaggle Customer Support on Twitter dataset (~3M tweets). It classifies customer intents, grounds drafted replies in authentic Apple Support resolution history, and decides whether to auto-handle or escalate to human specialists with an explicit stated reason.

---

## ⚡ Quickstart: Reproduce Headline Numbers in Under 15 Minutes

The entire benchmark suite runs locally in **~12 seconds** with zero external API dependencies:

```bash
# 1. Clone repository & navigate to folder
git clone <your-repo-link>
cd "sde intern task"

# 2. Install dependencies (pandas, scikit-learn, scipy, rouge-score, nltk)
pip install -r requirements.txt

# 3. Run headline benchmark & evaluation harness
python run_pipeline.py
```

### Try the Interactive Live Demo
Test any arbitrary customer tweet live in the terminal:
```bash
python interactive_demo.py
```

---

## 📊 Headline Benchmark Results

Evaluated across the **200-Case Real-Data Evaluation Set with Provisional Rule-Assisted Labels (Randomized & Shuffled Split)**:

| Evaluation Metric | Baseline 1 (Trivial Canned) | Baseline 2 (Simple Keyword) | Proposed AI Support Agent | Operational Impact |
|---|:---:|:---:|:---:|:---:|
| **Intent Accuracy** | 12.5% | 66.0% | **66.0%** | **+53.5%** over Baseline 1 |
| **Intent Macro F1** | 0.028 | 0.672 | **0.672** | Balanced across 8 classes |
| **Escalation Accuracy** | 41.0% | 95.0% | **94.0%** | Calibrated operational tradeoff |
| **Escalation Recall (Safety)** | 66.7% | 50.0% | **55.6%** | Prioritizes hazardous cases |
| **Escalation F1** | 0.169 | 0.643 | **0.625** | Balanced precision & recall |
| **Asymmetric Cost Penalty / Query** | 0.71 | 0.23 | **0.22** | **-69.0%** Cost vs Baseline 1 (Lowest) |
| **LLM Judge: Grounding (1-5)** | 2.79 | 3.86 | **3.80** | High technical grounding |
| **LLM Judge: Tone & Empathy (1-5)**| 5.00 | 4.74 | **4.88** | Courteous, concise Apple voice |
| **LLM Judge: Actionability (1-5)** | 4.24 | 3.46 | **4.08** | Direct `Settings > ...` paths |
| **LLM Judge: Escalation (1-5)** | 3.76 | 4.81 | **4.80** | Sound triage decisions |
| **LLM Judge Composite (1-5)** | 3.95 | 4.22 | **4.39** | **Top Performing Overall** |
| **Inference Latency / Query** | < 0.1 ms | 15.6 ms | **14.5 ms** | Real-time capable (< 20ms) |

### 💡 Engineering Takeaway: Proposed Intent = Baseline 2 Intent (66.0%)
Baseline 2 and the Proposed Agent share the same TF-IDF classifier component to isolate the impact of response generation and escalation policy. **The proposed system did not improve intent classification over the classical baseline on this dataset.** For broad 8-class tech support categorization, TF-IDF n-grams already capture the bulk of lexical signal.  
**The core differentiation of the Proposed Agent lies downstream**:
- Structured escalation triage across 6 operational policy categories with explicit, auditable stated reasons (vs. a naive 5-keyword regex), achieving the lowest operational cost penalty (0.22).
- Grounded, slot-filled response generation adhering to Twitter's 280-character budget and documented navigation paths (vs. unedited historical replies containing redundant questions).

---

## 🎯 Human-Judge Reliability Calibration

To evaluate the automated **LLM-as-a-Judge**, we calibrated it against annotations by the **Candidate Author Reviewer** on a 30-case validation subset:
- **Mean Absolute Error (MAE)**: **0.3123 / 5.0** (Judge absolute error is low, mirroring human scores within 0.31 points).
- **Human Mean Rating**: 4.70 / 5.0 | **Judge Mean Rating**: 4.46 / 5.0
- **Pearson Correlation ($r$)**: -0.0612 | **Cohen's Kappa ($\kappa$)**: 0.0
- **Reliability Limitation**: While the absolute deviation is small, Pearson's $r$ and Cohen's $\kappa$ provide **weak statistical evidence of judge reliability** due to restricted rating variance (human scores tightly clustered between 4.5 and 5.0) and the small 30-case sample size (documented under Section 7 of the Final Report).

---

## 🏗️ Architecture & Core Components

```mermaid
flowchart LR
    Tweet[Customer Tweet] --> Clean[Normalizer & Unicode Fixer]
    Clean --> Intent[8-Class Intent Classifier]
    Clean --> RAG[TF-IDF Grounding Retriever]
    
    Intent --> Engine{Escalation Engine}
    RAG --> Gen[Grounded Reply Generator]
    
    Engine -->|AUTO_HANDLE| Gen
    Engine -->|ESCALATE| Gen
    
    Gen --> Output["Structured Output\n(Decision + Stated Reason + Drafted Tweet)"]
```

1. **Intent Taxonomy**:
   Derived from exploratory domain analysis of Apple customer support inquiries and quantified across 20,000 tweets via rule-assisted labeling:
   - `SOFTWARE_UPDATE_OS`, `BATTERY_PERFORMANCE`, `HARDWARE_AUDIO_DISPLAY`, `ACCOUNT_APPLE_ID_ICLOUD`
   - `STORE_ORDER_BILLING`, `CONNECTIVITY_SYNC`, `THIRD_PARTY_APP_ISSUES`, `GENERAL_FEEDBACK_RANT`
2. **Grounding Retriever (RAG)**:
   Indexed over 10,000 verified historical Apple resolution pairs to anchor responses in genuine brand procedures (`Settings > General > About`, force reboot combinations, documented support articles).
3. **Escalation Engine with Stated Reasons**:
   Deterministic policy rules for 6 core categories:
   - Physical safety hazards (swollen batteries, sparks, fire risks)
   - Account security & identity (ransom extortions, locked Apple ID, 2FA loss)
   - Financial disputes & logistics (double debits, lost shipments)
   - Hardware component defects (green line on screen, defective butterfly spacebars)
   - Brand, media, & legal risks (lawsuits, press inquiries, multi-tweet customer hostility)
   - Confidence gating on model ambiguity.
4. **Grounded Reply Generator**:
   Apple brand-aligned generator constrained strictly to single-tweet budgets (< 280 characters).

---

## 📁 Repository Structure

```
sde-intern-task/
├── data/
│   ├── processed/
│   │   ├── apple_pairs_sampled.jsonl         # 10,000 extracted customer-reply pairs
│   │   └── intent_distribution.csv           # Empirical prevalence over 20,000 tweets
│   ├── golden_set/
│   │   ├── golden_eval_set_200.jsonl         # 200 real Kaggle tweets with provisional labels
│   │   ├── blind_annotation_200.csv          # Blind review file (zero machine labels, anti-anchoring)
│   │   ├── blind_annotation_200.jsonl        # JSONL version of blind review file
│   │   ├── provisional_labels_reference_200.json # Separate machine labels for reconciliation
│   │   ├── reconciliation_200.csv            # Merged side-by-side reconciliation dataset
│   │   ├── annotation_guidelines.md          # Protocol & decision criteria for manual annotation
│   │   ├── human_annotations_sample.json    # 30 scorecards by Candidate Author Reviewer
│   │   └── sampling_and_labeling_methodology.md
├── scripts/
│   └── reconcile_annotations.py              # Compares human vs provisional & updates golden set
├── src/
│   ├── __init__.py
│   ├── data_processor.py                     # Thread reconstruction, pairing & cleaning
│   ├── build_real_dataset_split.py           # Authentic dataset split builder with seed=42
│   ├── intent_classifier.py                  # 8-class intent taxonomy & hybrid classifier
│   ├── retriever.py                          # Grounding resolution retriever
│   ├── escalation_engine.py                  # Policy engine with explicit stated reasons
│   ├── response_generator.py                 # Grounded Apple reply drafter (<280 chars)
│   ├── agent.py                              # Unified AppleSupportAgent pipeline
│   ├── baselines.py                          # Trivial & Simple baseline agents
│   ├── llm_judge.py                          # 4-dimensional evaluation rubric
│   ├── evaluator.py                          # Automated metrics & cost penalty calculator
│   └── human_agreement.py                    # Cohen's Kappa & Pearson r agreement
├── reports/
│   ├── FINAL_REPORT.md                       # Comprehensive 6-page technical report
│   ├── DECISION_LOG.md                       # 15 non-obvious engineering decisions & tradeoffs
│   └── benchmark_results.json                # Complete machine-readable benchmark dump
├── tests/
│   └── test_pipeline.py                      # Complete unit test suite (All tests pass)
├── run_pipeline.py                           # Single-command runner (~12 seconds runtime)
├── interactive_demo.py                       # Interactive live testing CLI
├── requirements.txt                          # Python dependencies
└── README.md
```

---

## 📖 Key Deliverables & Documentation Links

- 📑 **[Final Comprehensive Report](reports/FINAL_REPORT.md)**:
  - Problem framing (what "good" means, what we chose not to build)
  - Results vs 2 baselines
  - Top 5 failure modes with real examples and root causes
  - **"What is misleading about my headline number?"** (mandatory deep dive)
  - What we'd do next with one more week
- 💡 **[Decision Log](reports/DECISION_LOG.md)**: 15 non-obvious architectural decisions and tradeoffs.
- 📐 **[Sampling & Labeling Methodology](data/golden_set/sampling_and_labeling_methodology.md)**: Complete annotation protocol and label provenance audit for the 200-case evaluation set.
- 📋 **[Annotation Guidelines](data/golden_set/annotation_guidelines.md)**: Detailed rubric for blind human review of the 200 cases.
- 🔄 **[Reconciliation Tool](scripts/reconcile_annotations.py)**: Automated analysis comparing human annotations against provisional machine labels.

---

## 🧪 Running Unit Tests
```bash
python -m unittest discover tests
```
*All 9 unit tests pass in ~2 seconds.*
