# Decision Log: 14 Non-Obvious Engineering Decisions & Tradeoffs

This log details the core architectural, design, and evaluation decisions made while building the `@AppleSupport` AI Support Agent, along with the rejected alternatives and explicit engineering tradeoffs.

---

### 1. Brand Selection: `@AppleSupport` over Airline or Telco Datasets
- **Decision**: Focused solely on `@AppleSupport` rather than airlines (e.g. Delta/AmericanAir) or telecom brands.
- **Why**: Apple Support operates at extreme volume (~100k tweets in TWCS) with an unambiguous, highly formalized triaging workflow (device diagnostics -> OS version verification -> DM referral for private hardware/billing checks). Unlike airlines where support queries are mostly volatile flight delay complaints, tech hardware support has concrete, verifiable ground truth procedures (Settings pathways, force restart combinations, hardware recalls).
- **Tradeoff**: Apple has strict public-to-private boundary policies (moving to DM very early), which biases conversational depth in public tweets.

### 2. Intent Taxonomy: 8 Empirical Operational Classes instead of Banking77
- **Decision**: Defined an 8-class taxonomy derived empirically from initial inbound customer tweets to `@AppleSupport`, rejecting the secondary Banking77 dataset.
- **Why**: Banking77 is tailored to fintech transactions (card limits, ATM fees, overdrafts), completely misaligned with consumer electronics triage (thermal events, iOS boot loops, display digitizers). An 8-class taxonomy captures >95% of Apple customer support inquiries without suffering from the label dilution of a 77-class space.
- **Tradeoff**: Requires custom annotation of training and golden sets rather than using off-the-shelf benchmarks.

### 3. Reconstructing Customer-Agent Conversation Pairs via Inverted Index
- **Decision**: Streamed `twcs.csv` in chunks to index outbound `@AppleSupport` tweets, then mapped them back to inbound customer tweets using `in_response_to_tweet_id`.
- **Why**: The raw dataset mixes inbound customer inquiries and outbound brand replies across 2.8 million unorganized rows. Extracting clean, chronological pairs was essential to create a grounded resolution bank.
- **Tradeoff**: Multi-turn customer threads were collapsed into (first query, first response) pairs to maintain deterministic evaluation.

### 4. Explicit Unicode Glitch Cleaning (`I️` -> `I`)
- **Decision**: Hardcoded an explicit regex preprocessor to replace the corrupted unicode character sequence `\ufe0f` and `I️` with standard ASCII `I`.
- **Why**: When iOS 11.1 launched in October 2017, Apple introduced a notorious text autocorrect glitch where typing capital "I" rendered as "A [?]" or unicode boxes. Thousands of tweets in the dataset contained this exact corruption, which degraded standard tokenizers.
- **Tradeoff**: Custom character normalization specific to late-2017 iOS anomalies.

### 5. Deterministic Policy Gate for Escalation over Pure Machine Learning
- **Decision**: Built a hybrid deterministic policy engine with explicit regex triggers for the 6 core escalation categories rather than relying solely on a black-box classifier.
- **Why**: In safety-critical support, false negatives on thermal hazards (swollen batteries), legal threats, or account takeovers can cause physical injury or legal liability. A pure statistical model trained on imbalanced data has an unacceptable tail risk of missing rare, catastrophic prompts.
- **Tradeoff**: Requires periodic maintenance of pattern dictionaries as new product issues arise.

### 6. Asymmetric Cost-Weighted Penalty Function ($C_{miss} = 5.0$ vs $C_{false} = 1.0$)
- **Decision**: Evaluated escalation using an asymmetric cost matrix penalizing missed escalations 5x heavier than unnecessary escalations.
- **Why**: In enterprise support economics, a false escalation costs ~30 seconds of an agent's time to politely redirect the customer. A missed escalation on an exploding battery or stolen identity risks catastrophic PR, customer churn, or regulatory action.
- **Tradeoff**: Slight bias toward over-escalation on ambiguous border queries.

### 7. Grounding Generation via Historical Retrieval (RAG) rather than Freeform LLM
- **Decision**: Grounded reply drafting strictly in historical AppleSupport resolutions and verified Settings pathways (`Settings > General > About`) rather than letting an LLM generate arbitrary text.
- **Why**: LLMs are notorious for hallucinating non-existent warranties, promising free replacements at Genius Bars, or inventing incorrect settings toggles. Retrieval-grounded generation ensures every response is anchored in real Apple procedures.
- **Tradeoff**: Response variety is constrained to historically validated solution templates.

### 8. Strict Single-Tweet Budget Constraint (< 280 Characters)
- **Decision**: Calibrated all drafted replies to fit strictly within Twitter's 280-character limit.
- **Why**: Enterprise Twitter support bots that post 4-tweet threads look spammy and fail customer engagement tests. True Apple Support tweets are crisp, empathetic, and direct.
- **Tradeoff**: Cannot explain full complex multi-step repairs directly in the tweet; must focus on immediate triage step or DM transition.

### 9. Hand-Curating Exactly 200 Stratified Golden Cases instead of Pseudo-Labeling
- **Decision**: Manually authored and verified 200 high-fidelity test queries with ground-truth intent, escalation decisions, explicit reasons, and resolution paths.
- **Why**: Automated pseudo-labeling on noisy Twitter data propagates errors and rewards trivial heuristics. A hand-curated golden set provides an unimpeachable ground truth.
- **Tradeoff**: High upfront engineering time spent crafting and verifying edge cases across 8 intents.

### 10. Inclusion of 20% Hard / Adversarial Edge Cases in Evaluation Set
- **Decision**: Allocated 40 of the 200 cases (20%) specifically to adversarial inputs: emotional rants without technical issues, viral microwave hoaxes, foreign languages, press inquiries, and deceased estate requests.
- **Why**: Routine queries are easy for any baseline to handle. The true measure of a production-grade agent is whether it avoids PR disasters when confronted with edge cases.
- **Tradeoff**: Depresses absolute headline accuracy compared to a naive uniform random sample.

### 11. Multi-Dimensional LLM Judge Rubric over Raw BLEU/Perplexity
- **Decision**: Evaluated reply quality across 4 explicit axes (Grounding, Tone, Actionability, Escalation Appropriateness) on a 1-5 scale rather than relying solely on BLEU or ROUGE.
- **Why**: BLEU and ROUGE penalize paraphrasing and reward exact string overlaps. A support tweet can have 0% BLEU overlap with a human reference while being technically superior and more helpful.
- **Tradeoff**: Requires calibration against human annotations to prove judge validity.

### 12. Empirical Measurement of the "High-Agreement Paradox"
- **Decision**: Explicitly calculated and reported both continuous correlation (Pearson $r$) and discrete agreement (Cohen's Kappa $\kappa$) alongside Mean Absolute Error (MAE) on human calibration cases.
- **Why**: When raters agree closely on high-performing systems (both human and judge rating between 4.5 and 5.0), variance approaches zero, causing Pearson's $r$ and Cohen's $\kappa$ to mathematically collapse despite low MAE (0.27). We openly documented this phenomenon rather than hiding it.
- **Tradeoff**: Forces a nuanced discussion of statistical limitations in the final report.

### 13. Sublinear In-Memory TF-IDF Indexing for <15 Minute Reproduction
- **Decision**: Pre-indexed 10,000 historical resolution pairs using sublinear TF-IDF vectors in Python memory.
- **Why**: Heavy neural vector databases (Pinecone, Weaviate, Milvus) require Docker containers, external API keys, or long embedding downloads that violate the 15-minute reproduction guarantee. Our pipeline reproduces in **under 2 seconds**.
- **Tradeoff**: Semantic paraphrase retrieval is bounded by character/word n-gram overlap rather than deep contextual embeddings.

### 14. Mandating Explicit "Stated Reason" on All Escalation Outputs
- **Decision**: Made `escalation_reason` a mandatory output attribute alongside the binary `decision`.
- **Why**: A customer support manager or QA lead will never trust an AI that escalates a ticket without saying *why*. Explaining *"Thermal event, battery swelling, or bodily injury risk requires immediate human safety protocol"* builds operator trust and allows auditable routing.
- **Tradeoff**: Requires explicit reasoning generation for every inference pass.
