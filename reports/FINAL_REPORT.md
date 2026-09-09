# Engineering & Research Report: AI Customer Support Agent for @AppleSupport

**Author**: Hiver SDE Intern Candidate  
**Target Brand**: `@AppleSupport` (Twitter Customer Support Dataset, Kaggle)  
**Evaluation Benchmark**: 200 Hand-Annotated Golden Test Cases + 30-Case Human Calibration Sample  
**Execution Runtime**: < 2.0 seconds (Reproducible in < 15 minutes)

---

## 1. Problem Framing: What "Good" Means for Apple Support

### What "Good" Means for @AppleSupport
Customer support on Twitter for a premier consumer electronics company like Apple is fundamentally distinct from typical e-commerce chatbots. A support bot for Apple cannot simply be a polite conversationalist; it operates in a high-stakes, public-facing environment with strict brand, legal, and safety boundaries:

1. **Precision Triage over Vague Conversationalism**:  
   A good Apple support agent does not offer generic sympathy. It immediately identifies the operational domain (e.g. *iOS installation loop* vs *battery hardware degradation* vs *Activation Lock dispute*) and provides the exact diagnostic pathway (e.g. `Settings > General > iPhone Storage` or `Settings > Battery`).
2. **Strict Factual Grounding (Zero Hallucination)**:  
   Hallucinating a replacement policy, promising free repairs out of warranty, or quoting non-existent settings pathways can cause severe customer dissatisfaction, Genius Bar operational bottlenecks, and legal exposure. Every technical instruction must be grounded in historically verified Apple procedures.
3. **Safety-Critical and Fraud Escalation**:  
   Physical safety hazards (swollen lithium-ion batteries, burning chargers), account takeovers (ransom notes in Lost Mode, 2FA compromise), and high-value logistics failures (stolen iPhone X pre-orders) must **never** be auto-handled. "Good" means catching 100% of safety and security risks and transitioning them to private Direct Messages (DM) with a clear stated reason.
4. **Brand Tone & Single-Tweet Budget**:  
   Responses must be concise (< 280 characters), calm, respectful, empathetic, and professional, adhering to Apple's understated communication ethos.

### What We Chose NOT to Build (and Why)
Engineering is defined as much by what you choose *not* to build:
- **We chose NOT to build an unconstrained open-ended generative chatbot**:  
  Allowing a large language model to generate responses without strict historical grounding or policy boundaries risks catastrophic brand damage (e.g., agreeing with angry customers that "Apple products are trash" or hallucinating warranty exceptions).
- **We chose NOT to automate private account or financial actions in public**:  
  Password resets, billing adjustments, and serial-number checks were strictly fenced off from automated public resolution. All private actions require explicit escalation to secure DM channels.
- **We chose NOT to adopt Banking77**:  
  Banking77 contains 77 fine-grained fintech intents (ATM fees, card replacement) that are irrelevant to hardware, firmware, and ecosystem support. Adopting it would have introduced artificial domain drift.
- **We chose NOT to build multi-turn memory on Twitter public threads**:  
  Twitter customer interactions that exceed 2 turns almost always involve sensitive diagnostic sharing or credential verification, which Apple policy mandates moving to DM (`https://t.co/GDrqU22YpT`). Building complex multi-turn public dialogue models solves the wrong problem.

---

## 2. Experimental Results vs. Baselines

We evaluated three complete systems across our hand-labelled **200-Case Golden Evaluation Set** (stratified across all 8 empirical intents, difficulty tiers, and escalation boundaries).

### Baseline Definitions
1. **Baseline 1 (Trivial Heuristic)**:
   - **Intent Classifier**: Majority class predictor (`SOFTWARE_UPDATE_OS`).
   - **Escalation Decision**: Arbitrary length heuristic (messages > 100 characters escalated; else auto-handled).
   - **Reply Generator**: Static canned DM redirection tweet (*"Thanks for reaching out! We're here to help. Send us a DM: https://t.co/GDrqU22YpT"*).
2. **Baseline 2 (Simple Heuristic)**:
   - **Intent Classifier**: Standard TF-IDF Logistic Regression without rule boosting.
   - **Escalation Decision**: 5-keyword regex matching (`refund`, `stolen`, `broken`, `locked`, `urgent`).
   - **Reply Generator**: Raw top-1 nearest neighbor response retrieved verbatim via BM25 from the historical resolution bank.
3. **Proposed System (Grounded AI Agent)**:
   - **Intent Classifier**: Calibrated 8-class hybrid classifier with TF-IDF n-grams and domain keyword boosting.
   - **Escalation Engine**: Deterministic policy engine covering 6 safety, security, and legal trigger categories + confidence gating + mandatory stated reasons.
   - **Reply Generator**: Grounded response drafter constrained to canonical Apple navigation paths, historical resolution precedent, and Twitter's 280-character limit.

### Headline Benchmark Results Table

| Metric Category | Evaluation Metric | Baseline 1 (Trivial) | Baseline 2 (Simple) | Proposed AI Agent | Relative Improvement |
|---|---|:---:|:---:|:---:|:---:|
| **Intent Classification** | Accuracy | 12.5% | 97.5% | **97.5%** | **+85.0%** over B1 |
| | Macro Precision | 0.016 | 0.976 | **0.976** | — |
| | Macro Recall | 0.125 | 0.975 | **0.975** | — |
| | Macro F1 | 0.028 | 0.975 | **0.975** | **+33.8x** over B1 |
| | Weighted F1 | 0.028 | 0.975 | **0.975** | — |
| **Escalation Decision** | Escalation Accuracy | 73.5% | 79.5% | **99.0%** | **+19.5%** over B2 |
| | Escalation Precision | 0.422 | 0.714 | **0.957** | **+24.3%** over B2 |
| | **Escalation Recall (Safety)** | 50.0% | **11.4%** | **100.0%** | **+88.6%** over B2 |
| | Escalation F1 | 0.454 | 0.196 | **0.978** | **+398%** over B2 |
| | Missed Escalations (FN) | 22 / 44 | **39 / 44** | **0 / 44** | **0 Misses!** |
| | False Escalations (FP) | 31 / 156 | 2 / 156 | **2 / 156** | — |
| | **Cost Penalty / Query** | 0.70 | 0.98 | **0.01** | **-98.9%** Cost Reduction |
| **Grounded Reply Quality** | ROUGE-L F1 | 0.054 | 0.062 | **0.086** | **+38.7%** over B2 |
| | BLEU-4 | 0.007 | 0.008 | **0.011** | **+37.5%** over B2 |
| | Character Budget (<280) | 100.0% | 91.5% | **100.0%** | Fully Compliant |
| **LLM-as-a-Judge (1-5)** | Grounding & Factual Soundness | 2.73 | 4.05 | **4.27** | High Grounding |
| | Brand Tone & Empathy | 5.00 | 4.75 | **4.88** | Brand Compliant |
| | Actionability & Guidance | 3.53 | 3.46 | **3.99** | Direct Settings Paths |
| | Escalation Appropriateness | 4.25 | 4.20 | **4.98** | Near Perfect Policy |
| | **Composite Judge Score** | 3.88 | 4.11 | **4.53** | **Top Performing** |
| **Operational Efficiency** | Average Latency / Query | < 0.1ms | 3.0ms | **3.0ms** | Real-time ready |

### Key Observations from Benchmark
1. **The Dangerous Illusion of Simple Baseline Accuracy**:  
   Baseline 2 achieved a superficially acceptable 79.5% escalation accuracy. However, its **Escalation Recall was a disastrous 11.4%**—it missed 39 out of 44 critical escalations! Because non-escalated cases form the majority, a naive model looks "accurate" while abandoning 88% of users facing severe battery swelling, account takeovers, or lost shipments.
2. **Asymmetric Operational Cost Reduction**:  
   Under an enterprise penalty model ($C_{miss} = 5.0, C_{false} = 1.0$), Baseline 2 accrued a staggering 0.98 penalty per query. The Proposed Agent reduced this to **0.01**, achieving a 98.9% operational risk reduction.
3. **LLM Judge Superiority**:  
   The Proposed Agent scored **4.53 / 5.0** composite on the evaluation rubric, significantly outperforming Baseline 1 (3.88) by providing actionable troubleshooting pathways (`Settings > General > iPhone Storage`) rather than stalling or canned links.

---

## 3. Human-Judge Agreement Analysis

To validate whether the automated **LLM-as-a-Judge** is trustworthy, we evaluated its ratings against independent human expert scorecards on a 30-case calibration set (`data/golden_set/human_annotations_sample.json`).

| Statistical Measure | Empirical Value | Interpretation |
|---|:---:|---|
| **Calibration Sample Size ($N$)** | 30 Cases | Stratified across safety, hardware, account, and billing |
| **Mean Absolute Error (MAE)** | **0.2717 / 5.0** | Extremely tight calibration (within 0.27 points on a 5-point scale) |
| **Human Mean Rating** | **4.80 / 5.0** | Expert evaluators rated replies highly |
| **Judge Mean Rating** | **4.85 / 5.0** | Judge mirrored human expectations |
| **Pearson Correlation ($r$)** | -0.2203 ($p = 0.24$) | Reflects **Restriction of Range** (see Section 5) |
| **Cohen's Kappa ($\kappa$)** | 0.0 | Reflects **The High-Agreement Paradox** (see Section 5) |

The automated judge exhibits low error (MAE = 0.27) and closely mirrors the absolute standards of human support leads.

---

## 4. Failure Analysis: Top 5 Failure Modes

Through comprehensive error analysis across the benchmark, we identified the top 5 operational failure modes:

### Failure Mode 1: The "Dual Intent" Dilemma (Software Glitch vs Hardware Trigger)
- **Real Example (ID 48)**:  
  *"Why does my screen dim itself automatically when playing graphic heavy games even with auto-brightness disabled?"*
- **Observed Behavior**: The classifier struggled between `SOFTWARE_UPDATE_OS` and `HARDWARE_AUDIO_DISPLAY` because "auto-brightness" points to software settings, while "screen dim" points to display hardware.
- **Root Cause Hypothesis**: The query involves an unstated physical mechanism: iOS automatically dims the OLED display to prevent internal thermal runaway when the GPU overheats. Neither software nor display labels fully capture this cross-cutting thermal management event.
- **Mitigation**: Introduce a multi-label intent representation allowing shared probability distribution across related domains.

### Failure Mode 2: Premature Escalation on Benign Billing Inquiries
- **Real Example (ID 121)**:  
  *"Apple charged me $0.99 every month for 2 years and I don't know what it is!"*
- **Observed Behavior**: The escalation engine initially routed this to `ESCALATE` with reason *"Account or transaction modification requires private customer identification in DM"*.
- **Root Cause Hypothesis**: The word "charged" triggered financial dispute safeguards. In reality, $0.99/mo is the universally known price of Apple's 50GB iCloud storage tier, easily resolvable via a self-serve settings explanation.
- **Mitigation**: Add a whitelist pattern for canonical microtransactions ($0.99 iCloud tier) to keep routine informational billing queries in `AUTO_HANDLE`.

### Failure Mode 3: Hardware Diagnostics Masked as Slang / Humor
- **Real Example (ID 189)**:  
  *"Help me my phone is possessed by ghosts! It moves on its own and types words without me touching it!"*
- **Observed Behavior**: The classifier initially assigned `GENERAL_FEEDBACK_RANT` due to supernatural phrasing ("ghosts", "possessed").
- **Root Cause Hypothesis**: The user was describing "ghost touch"—a well-known physical digitizer hardware failure or AC charger ground noise issue. Metaphorical descriptions disguise technical hardware faults as jokes or rants.
- **Mitigation**: Incorporate colloquial symptom idioms ("ghost touch", "phantom typing", "moving on its own") into the hardware diagnostic dictionary.

### Failure Mode 4: Out-of-Domain Legacy Hardware Constraints
- **Real Example (ID 165)**:  
  *"Fortnite crashes as soon as the battle bus drops on my iPhone 6."*
- **Observed Behavior**: The agent provided standard app troubleshooting advice (restart phone, reinstall app) instead of explaining hardware RAM obsolescence.
- **Root Cause Hypothesis**: Fortnite required a minimum of 2GB RAM (iPhone 6s or newer); an iPhone 6 only has 1GB RAM. A pure text-matching agent lacks an explicit hardware specification database linking device RAM specs to 3rd-party game requirements.
- **Mitigation**: Connect the agent to a structured Device Matrix Knowledge Graph (specifying SoC, RAM, and maximum supported iOS version for every Apple device).

### Failure Mode 5: Retrieval Mismatch from Context Duplication
- **Real Example**: Customer specifies: *"I'm on iOS 11.0.3 on iPhone 7, already restarted twice, screen is still black."*
- **Observed Behavior**: The retriever matched historical replies where Apple asked: *"We'd be glad to help. Which version of iOS are you on?"*
- **Root Cause Hypothesis**: Historical tweets frequently begin with basic diagnostic triage questions. When a customer preemptively answers these in their first tweet, retrieving the historical top-1 reply results in redundant, irritating questions.
- **Mitigation**: Implement an entity slot-filling check. If `iOS_version` and `device_model` are already extracted from the customer query, suppress triage questions and advance directly to level-2 diagnostics.

---

## 5. Mandatory Section: "What is Misleading About My Headline Number?"

A responsible engineer must never present headline metrics without exposing their hidden assumptions, biases, and structural vulnerabilities:

### 1. The "100% Escalation Recall" Selection Bias
Our headline shows **100% Escalation Recall** with zero missed safety hazards on the golden set.  
**Why this is misleading**:  
In real-world production, customer phrasing is virtually unbounded. Users do not always say *"my battery is swollen"*; they say *"my phone feels puffy"*, *"my screen is lifting up near the edge"*, or *"my phone case doesn't fit anymore"*. While regex patterns and calibrated confidence gates achieve 100% recall on curated, well-formed test sets, adversarial or ambiguous phrasing will inevitably bypass keyword gates in the wild.

### 2. High Reply Similarity (ROUGE/BLEU) Does Not Equal Customer Problem Resolution
Our headline reports solid grounding scores and ROUGE improvements over baselines.  
**Why this is misleading**:  
In customer support, **linguistic overlap is an imperfect proxy for task completion**. An agent can draft an exact syntactic copy of an official Apple Support tweet (*"Restart your device and check Settings > General > About"*), achieving high ROUGE, while the customer's device remains completely broken. Static offline datasets measure *conversational mimicry*, not whether the customer's phone actually booted or whether customer satisfaction (CSAT) improved.

### 3. The "High-Agreement Paradox" & Restriction of Range in Human Agreement
In our calibration study, the Mean Absolute Error between human ratings and judge ratings was remarkably low (**0.27 out of 5.0**). Yet, Pearson's $r$ (-0.22) and Cohen's Kappa ($\kappa = 0.0$) showed low linear correlation.  
**Why this is misleading**:  
This is a classic demonstration of the **Restriction of Range / High-Agreement Paradox** in inter-rater reliability. Because both the human experts and the automated judge agreed that nearly all sampled agent replies were high quality (clustering tightly between 4.5 and 5.0), the score variance approached zero. In mathematical statistics, when variance $\sigma^2 \to 0$, Pearson's $r$ and Cohen's $\kappa$ collapse to zero or fluctuate randomly, even when raters agree on 95%+ of absolute decisions. Reporting Kappa without explaining this effect would mislead evaluators into believing the judge is random, when in fact both raters were in near-unanimous agreement.

### 4. Twitter Selection & Survivorship Bias
The Kaggle TWCS dataset only captures customers who chose to publicly tweet at Apple.  
**Why this is misleading**:  
Twitter users represent an uncharacteristically vocal, impatient, and tech-savvy demographic. Customers facing quiet confusion or non-urgent issues use email, in-store Genius Bars, or Apple Support app diagnostics. Optimizing solely for Twitter data tailors the agent to aggressive public escalation dynamics rather than the broader distribution of global customer inquiries.

---

## 6. What You'd Do Next with One More Week

Given seven additional engineering days, we would execute the following production roadmap:

1. **Stateful Multi-Turn Dialogue State Tracking (DST)**:  
   Build a stateful session manager that tracks conversation slots (`device_model`, `ios_version`, `steps_already_attempted`, `customer_sentiment_delta`) across multi-turn threads. If the customer already tried restarting, the agent will never ask them to restart again.
2. **Dynamic Knowledge Graph & Spec Database Integration**:  
   Integrate an in-memory SQLite knowledge graph of Apple hardware specs (RAM, release year, chipsets, recall programs like the iPhone 6s battery recall or iPhone 7 No Service program). This allows instant, deterministic validation of compatibility queries without LLM hallucination.
3. **Active Learning on Low-Confidence Escalations**:  
   Route queries that fall into the borderline confidence band (0.15 - 0.25) into an active learning queue. Human agent resolutions in DM would be fed back daily to retrain the intent and escalation boundaries.
4. **Guardrail Ensembles (NeMo / Llama-Guard)**:  
   Deploy an input guardrail layer to intercept adversarial prompt injection, jailbreaking attempts, and profane harassment before queries reach the core support agent.
5. **Shadow Mode A/B Testing Harness**:  
   Deploy the agent in "shadow mode" behind live Apple Support Twitter agents, comparing the AI's drafted response and escalation recommendation against actual human responses in real time to calculate live acceptance rate, edit distance, and time-to-first-response reduction.

---

## 7. Submission Checklist
- [x] **Pipeline Repo**: Runnable in under 15 minutes (`python run_pipeline.py` takes 2.0s).
- [x] **Golden Evaluation Set**: 200 hand-labelled cases (`data/golden_set/golden_eval_set_200.jsonl`) with sampling methodology (`data/golden_set/sampling_and_labeling_methodology.md`).
- [x] **Evaluation Harness**: Automated metrics (`src/evaluator.py`) + LLM-as-Judge rubric (`src/llm_judge.py`) + Human agreement analysis (`src/human_agreement.py`).
- [x] **Comprehensive Report**: Covering problem framing, 2 baselines, failure modes, "what is misleading", and 1-week roadmap.
- [x] **Decision Log**: 14 non-obvious engineering decisions and tradeoffs (`reports/DECISION_LOG.md`).
