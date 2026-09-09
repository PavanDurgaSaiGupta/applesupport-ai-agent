# Annotation Guidelines: 200-Case Evaluation Set for @AppleSupport

These guidelines define the protocol for human review of the 200 real Kaggle customer tweets sampled from `twcs.csv`.

---

## 1. Provenance Transparency & Review Status

In compliance with rigorous scientific standards:
- **Current Status**: The baseline labels in `golden_eval_set_200.jsonl` were generated programmatically via domain-informed keyword and policy regex heuristics (Category B & D).
- **No Hand-Label Claim**: Until each case is reviewed and verified by a human annotator, the evaluation set is explicitly designated as **provisional rule-assisted ground truth**.
- **Annotation Files**:
  - Review Spreadsheet: [`data/golden_set/annotation_template_200.csv`](annotation_template_200.csv)
  - Review JSONL: [`data/golden_set/annotation_template_200.jsonl`](annotation_template_200.jsonl)

---

## 2. Target Annotation Fields

For each customer query, the human annotator must review and populate the following blank fields:

| Field | Allowed Values | Description |
|---|---|---|
| `candidate_reviewed_intent` | One of the 8 canonical intents | The primary operational category of the customer's request. |
| `candidate_reviewed_escalation` | `AUTO_HANDLE` or `ESCALATE` | Whether an autonomous public bot should resolve the query or hand off to a human specialist. |
| `candidate_reviewed_reason` | Free text string | The operational policy justification for the escalation decision. |
| `candidate_reviewed_difficulty` | `Easy`, `Medium`, `Hard` | Complexity rating based on ambiguity, slang, or multi-domain overlap. |
| `candidate_notes` | Free text string | Observations on edge cases, customer sentiment, or specific iOS version context. |

---

## 3. 8-Class Intent Taxonomy & Disambiguation Rules

### 1. `SOFTWARE_UPDATE_OS`
- **Scope**: iOS/macOS installation freezes, update download failures, bootloops, post-update UI stutter, autocorrect bugs (e.g. the iOS 11.1 "I" bug), and general operating system settings.
- **Representative Query**: *"The newest update. I made sure to download it yesterday and now my phone freezes."*
- **Disambiguation**: If a customer mentions an app crashing immediately following an OS update, classify as `SOFTWARE_UPDATE_OS` if the system UI itself is affected; classify as `THIRD_PARTY_APP_ISSUES` if only one external app fails.

### 2. `BATTERY_PERFORMANCE`
- **Scope**: Rapid battery drain, unexpected cold shutdowns, slow charging, overheating/thermal warming during normal use, battery capacity degradation.
- **Representative Query**: *"My iPhone 7 battery drops from 40% to 1% in five minutes. What is happening?"*
- **Disambiguation**: If battery drain began directly after an OS update, evaluate primary focus: if customer asks *"how do I fix my battery?"*, classify as `BATTERY_PERFORMANCE`; if customer asks *"can I downgrade from iOS 11?"*, classify as `SOFTWARE_UPDATE_OS`.

### 3. `HARDWARE_AUDIO_DISPLAY`
- **Scope**: Physical screen cracks, vertical/horizontal screen lines, dead touch digitizer zones, broken home/power buttons, muffled speakers, microphone failure, camera black screens.
- **Representative Query**: *"Half of my screen has green lines and doesn't respond to touch."*
- **Disambiguation**: Distinguish software display freezes (resolved by force restart) from physical hardware defects (permanent lines, physical impact damage).

### 4. `ACCOUNT_APPLE_ID_ICLOUD`
- **Scope**: Locked Apple IDs, forgotten passwords, 2FA verification code delivery issues, Activation Lock ownership disputes, iCloud storage full notifications.
- **Representative Query**: *"My Apple ID has been locked for security reasons and the trusted number is an old SIM card."*
- **Disambiguation**: If an inquiry involves purchasing iCloud storage tiers, classify under `STORE_ORDER_BILLING`; if it involves managing existing quota or account login, classify under `ACCOUNT_APPLE_ID_ICLOUD`.

### 5. `STORE_ORDER_BILLING`
- **Scope**: Unexpected App Store charges, duplicate subscription debits, refund requests, delivery delays, trade-in kit inquiries, AppleCare purchase questions.
- **Representative Query**: *"I was charged $9.99 for a subscription I canceled two weeks ago. How do I get a refund?"*
- **Disambiguation**: Routine questions about the standard $0.99 iCloud storage plan belong here but are `AUTO_HANDLE`; disputed or unauthorized transactions are `ESCALATE`.

### 6. `CONNECTIVITY_SYNC`
- **Scope**: Wi-Fi dropping or greyed out, Bluetooth car audio disconnects, cellular 'No Service' or 'Searching' errors, AirDrop failures, Apple Watch pairing errors.
- **Representative Query**: *"My iPhone won't connect to my home Wi-Fi after restarting my router."*
- **Disambiguation**: If connectivity loss occurred after a firmware flash, classify under `CONNECTIVITY_SYNC` if network troubleshooting (`Settings > General > Reset > Reset Network Settings`) is the primary resolution path.

### 7. `THIRD_PARTY_APP_ISSUES`
- **Scope**: Crashes, glitches, or account issues confined to non-Apple third-party applications (Spotify, WhatsApp, YouTube, Netflix, Instagram).
- **Representative Query**: *"Spotify keeps crashing every time I try to open a playlist on iOS 11."*
- **Disambiguation**: If the user cannot download *any* app from the App Store, classify under `STORE_ORDER_BILLING` or `SOFTWARE_UPDATE_OS`.

### 8. `GENERAL_FEEDBACK_RANT`
- **Scope**: Emotional venting, sarcasm, brand praise, philosophical comments, media inquiries, or greetings containing no actionable technical problem.
- **Representative Query**: *"Apple is the worst company ever. You ruined my life with this update."*
- **Disambiguation**: If an emotional rant also contains a specific diagnostic problem (*"Apple sucks, my camera is black"*), classify by the underlying technical issue (`HARDWARE_AUDIO_DISPLAY`).

---

## 4. Escalation Decision Rubric: "Safe Automated System" Rule

In historical Twitter support data, human agents frequently redirected customers to Direct Messages (DM) early to exchange serial numbers. **A competent automated agent should not mimic historical DM redirection indiscriminately.**

### Operational Escalation Triggers (`ESCALATE`):
Mark `ESCALATE` if the query involves any of the following 6 operational criteria:
1. **Physical Safety Hazards**: Thermal swelling, smoke, sparks, melting cables, electrical shocks.
2. **Account Security & Identity**: Compromised Apple ID, ransomware notes in Lost Mode, unrecoverable 2FA lockouts, Activation Lock disputes.
3. **Financial & Transaction Disputes**: Unauthorized credit card charges, disputed subscription debits, missing or stolen shipment parcels.
4. **Hardware Failures Beyond Software Triage**: Broken glass, permanent screen lines, failed internal solder/hardware components.
5. **Brand, Legal, or Media Exposure**: Threats of litigation, formal press inquiries, extreme multi-tweet hostility.
6. **Direct Customer Demand**: Explicit customer request to speak to a human representative (*"give me a human"*, *"stop bot"*).

### Auto-Handling Criteria (`AUTO_HANDLE`):
Mark `AUTO_HANDLE` if the inquiry can be safely addressed via:
- Public navigation steps (e.g. `Settings > General > iPhone Storage`).
- Device force restart sequences.
- Informational links to public Apple Support articles.
- Reassurance and polite acknowledgment for non-actionable feedback.

---

## 5. Difficulty Tier Definitions

- **Easy**: Clear, single-intent query with standard Apple vocabulary and straightforward resolution.
- **Medium**: Multi-sentence query, compound questions, or mild vocabulary ambiguity.
- **Hard**: Heavy slang, idiomatic expressions, sarcasm, or complex interactions across OS, battery, and hardware.
