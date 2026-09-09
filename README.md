# @AppleSupport AI Support Agent & Grounded Evaluation Suite

> **Hiver SDE Intern Take-Home Submission**  
> *"Whether you can turn a messy real-world dataset into a working AI system and prove it works. The proof is worth more than the system."*

An end-to-end, production-ready AI customer-support agent built for **`@AppleSupport`** using the Kaggle Customer Support on Twitter dataset (~3M tweets). It classifies customer intents, grounds drafted replies in authentic Apple Support resolution history, and decides whether to auto-handle or escalate to human specialists with an explicit stated reason.

---

## ⚡ Quickstart: Reproduce Headline Numbers in Under 15 Minutes

The entire benchmark suite runs locally in **under 3 seconds** with zero external API dependencies:

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

Evaluated across the **200-Case Hand-Labelled Golden Evaluation Set**:

| Evaluation Metric | Baseline 1 (Trivial Canned) | Baseline 2 (Simple Keyword) | Proposed AI Support Agent | Operational Impact |
|---|:---:|:---:|:---:|:---:|
| **Intent Accuracy** | 12.5% | 97.5% | **97.5%** | **+85.0%** over Baseline 1 |
| **Intent Macro F1** | 0.028 | 0.975 | **0.975** | Robust across 8 classes |
| **Escalation Accuracy** | 73.5% | 79.5% | **99.0%** | **+19.5%** over Baseline 2 |
| **Escalation Recall (Safety)** | 50.0% | **11.4%** | **100.0%** | **Zero Missed Hazards** (vs 39 missed in B2) |
| **Escalation F1** | 0.454 | 0.196 | **0.978** | **+398%** over Baseline 2 |
| **Asymmetric Cost Penalty / Query** | 0.70 | 0.98 | **0.01** | **-98.9%** Operational Risk |
| **ROUGE-L F1** | 0.054 | 0.062 | **0.086** | +38.7% Grounding Overlap |
| **LLM Judge: Grounding (1-5)** | 2.73 | 4.05 | **4.27** | High technical accuracy |
| **LLM Judge: Tone & Empathy (1-5)**| 5.00 | 4.75 | **4.88** | Polite, concise, Apple voice |
| **LLM Judge: Actionability (1-5)** | 3.53 | 3.46 | **3.99** | Direct `Settings > ...` paths |
| **LLM Judge: Escalation (1-5)** | 4.25 | 4.20 | **4.98** | Near perfect policy fidelity |
| **LLM Judge Composite (1-5)** | 3.88 | 4.11 | **4.53** | **Top Performing System** |
| **Inference Latency / Query** | < 0.1 ms | 3.0 ms | **3.0 ms** | Real-time capable (< 5ms) |

---

## 🎯 Human-Judge Reliability Calibration

To prove our automated evaluation is trustworthy, we calibrated the automated **LLM-as-a-Judge** against independent expert human annotations on a 30-case calibration set:
- **Mean Absolute Error (MAE)**: **0.2717 / 5.0** (Judge mirrors human scores within 0.27 points).
- **Human Mean Rating**: 4.80 / 5.0
- **Judge Mean Rating**: 4.85 / 5.0
- *Note*: Explored in depth under the **"What is Misleading About My Headline Number?"** section, documenting the classic **Restriction of Range / High-Agreement Paradox** in reliability statistics.

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
   Derived empirically from `@AppleSupport` data into 8 operational categories:
   - `SOFTWARE_UPDATE_OS`, `BATTERY_PERFORMANCE`, `HARDWARE_AUDIO_DISPLAY`, `ACCOUNT_APPLE_ID_ICLOUD`
   - `STORE_ORDER_BILLING`, `CONNECTIVITY_SYNC`, `THIRD_PARTY_APP_ISSUES`, `GENERAL_FEEDBACK_RANT`
2. **Grounding Retriever (RAG)**:
   Indexed over 10,000 verified historical Apple resolution pairs to anchor responses in genuine brand procedures (`Settings > General > About`, force reboot combinations, official support articles).
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
│   │   └── apple_pairs_sampled.jsonl         # 10,000 extracted customer-reply pairs
│   ├── golden_set/
│   │   ├── golden_eval_set_200.jsonl         # 200 hand-labelled ground truth examples
│   │   ├── human_annotations_sample.json    # 30 expert human scorecards for judge calibration
│   │   └── sampling_and_labeling_methodology.md
├── src/
│   ├── __init__.py
│   ├── data_processor.py                     # Thread reconstruction, pairing & cleaning
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
│   ├── DECISION_LOG.md                       # 14 non-obvious engineering decisions & tradeoffs
│   └── benchmark_results.json                # Complete machine-readable benchmark dump
├── tests/
│   └── test_pipeline.py                      # Complete unit test suite (All tests pass)
├── run_pipeline.py                           # Single-command runner (< 3 seconds runtime)
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
- 💡 **[Decision Log](reports/DECISION_LOG.md)**: 14 non-obvious architectural decisions and tradeoffs.
- 📐 **[Sampling & Labeling Methodology](data/golden_set/sampling_and_labeling_methodology.md)**: Complete annotation protocol for the 200-case golden set.

---

## 🧪 Running Unit Tests
```bash
python -m unittest discover tests
```
*All 8 unit tests pass in 0.42 seconds.*
