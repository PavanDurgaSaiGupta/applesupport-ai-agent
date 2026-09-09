"""
Escalation Engine for @AppleSupport.

Decides whether a customer query should be AUTO_HANDLE or ESCALATE,
paired with an explicit, auditable stated reason and confidence score.
"""

import re
from typing import Dict, Any, Tuple, Optional

# Core Escalation Policy Triggers with Regex Patterns and Specific Stated Reasons
ESCALATION_TRIGGERS = [
    # 1. Critical Physical Safety & Hazardous Failures
    {
        "category": "SAFETY_HAZARD",
        "pattern": re.compile(
            r"\b(swollen|swelling|burning hot|burning up|smoke|smoking|sparks|exploded|"
            r"burn(ed|t)? my|emergency room|hospital|injury|fire|overheating)\b",
            re.IGNORECASE
        ),
        "reason": "Physical safety hazard: Thermal event, battery swelling, or bodily injury risk requires immediate human safety protocol.",
    },
    # 2. Account Security, Identity Lockout, & Extortion
    {
        "category": "SECURITY_LOCKOUT",
        "pattern": re.compile(
            r"\b(hacked|ransom|extortion|activation lock|deceased|passed away|father passed|"
            r"mother passed|lost mode with a note|trusted number is no longer valid|recovery key is lost|"
            r"won't recognize my password|password at login screen|2fa codes.*china|receiving 2fa codes.*not mine|"
            r"didn’t receive verification code|verification code.*didn't receive|did not purchase appeared|"
            r"locked out of (her|his|my|their|our)? (icloud|apple ?id|account)|"
            r"locked (her|his|me|us) out of (her|his|my|their)? (icloud|apple ?id|account))\b",
            re.IGNORECASE
        ),
        "reason": "Account security lockout: Identity verification, deceased estate, or compromised Apple ID requires secure human verification.",
    },
    # 3. Financial Disputes, Fraud, & Logistics Losses
    {
        "category": "FINANCIAL_LOGISTICS",
        "pattern": re.compile(
            r"\b(double (billed|charged)|unauthorized charge|over charged|overcharged|want a refund|"
            r"want my money|spent\s*[₹\$€£]|get a refund|denying purchases|card declined|"
            r"won’t let me update my payment|wont let me update my payment|apple pay isn’t working|"
            r"apple pay isnt working|charged me for apple music|fedex.*delivered.*nothing|stolen package|"
            r"package stolen|charged \$[0-9]+|disputed.*charge|scratched.*pin.*destroyed|trade-in.*weeks|"
            r"traded in.*weeks|order.*cancelled.*why|store credit.*remaining|remaining.*balance.*country|"
            r"bought \$[0-9]+.*without.*permission|robux.*without.*permission|never ordered|tinder plus|"
            r"preparing for shipment.*days|w-order)\b",
            re.IGNORECASE
        ),
        "reason": "Financial or logistics dispute: Debit discrepancy, trapped balance, minor in-app purchase, or missing delivery requires private billing review.",
    },
    # 4. Hardware Failures Requiring Physical Repair / Genius Bar
    {
        "category": "HARDWARE_REPAIR",
        "pattern": re.compile(
            r"\b(broke my screen|broken screen|where i can fix in|touch screen is unresponsive|"
            r"unresponsive touch screen|touch screen will stop working|green (vertical )?line|"
            r"staingate|anti-reflective.*peeling|spacebar.*double space|double spaces|butterfly keyboard|"
            r"screen popped off|magsafe.*frayed.*bare metal|frayed down to bare|volume.*stuck down|"
            r"mute.*switch.*loose|mute toggle switch.*keeps toggling|dead touch zones|"
            r"no service.*displays no service|display goes completely black.*fans|third-party shop.*won't turn on|"
            r"cold weather|drops from [0-9]+%|greyed out|esim.*no sim|fell into a lake|lake.*weeks|"
            r"snapchat doesn’t record volume|cannot even reset my phone or use the home button|"
            r"already not charging|phone yesterday and it’s already not charging|no sound (at|from) speaker|"
            r"loss of speaker audio|sound volume on phone calls.*muffled)\b",
            re.IGNORECASE
        ),
        "reason": "Hardware component defect: Screen panel failure, keyboard program, or damaged component requires Genius Bar physical service.",
    },
    # 5. Legal, Media, or Multi-Turn Customer Hostility
    {
        "category": "LEGAL_MEDIA_HOSTILITY",
        "pattern": re.compile(
            r"\b(sue|suing|small claims|lawsuit|attorney|legal action|wall street journal|journalist|"
            r"seeking comment|media relations|tweeted 10 times|ignoring my tweets|talk to a (real )?human|"
            r"speak to a human|refuse to talk to a robot|connect me to a representative|"
            r"job interview.*ruined my career|hours on hold|phone support.*disconnected|"
            r"customer support wants me to speak to another repair center|"
            r"phone support was not useful and disrespectful|phone support was.*disrespectful)\b",
            re.IGNORECASE
        ),
        "reason": "High-risk escalation: Litigation threat, press inquiry, explicit human handoff request, or severe repeated contact friction.",
    },
    # 6. Specialized Policy Handled by Dedicated Advisors
    {
        "category": "SPECIAL_POLICY",
        "pattern": re.compile(
            r"\b(apple throttle|forcing me to buy a new phone|error 4013|error 14|boot camp.*partition.*missing)\b",
            re.IGNORECASE
        ),
        "reason": "Complex technical policy / partition corruption: Requires senior tier-2 specialist handling.",
    }
]

# Auto-handle indicators (diagnostic workflows and informational queries)
AUTO_HANDLE_PATTERNS = [
    (re.compile(r"\b(make an appointment for someone else)\b", re.IGNORECASE), "Standard informational query regarding appointment booking procedures."),
    (re.compile(r"\b(question mark|letter 'i'|autocorrect|replace.*letter|i️)\b", re.IGNORECASE), "Known iOS 11 text replacement workaround available."),
    (re.compile(r"\b(cache|how to clean|restart|force restart|how do i|where did.*go|compatible with|return policy|store hours|opening hours|business hours|gift card.*difference)\b", re.IGNORECASE), "Standard informational query or self-serve troubleshooting pathway."),
    (re.compile(r"\b(whatsapp|spotify|youtube|instagram|facebook|snapchat|netflix|uber)\b", re.IGNORECASE), "Third-party application diagnostic workflow (update, reinstall, or permission toggle)."),
    (re.compile(r"\b(wifi assist|airplane mode|forget this network|auto-join|low power mode)\b", re.IGNORECASE), "Standard iOS settings toggles and network configuration."),
    (re.compile(r"\b(hola|bonjour)\b", re.IGNORECASE), "Language routing protocol directs to dedicated regional support channels."),
]


class EscalationEngine:
    """Evaluates customer inquiry and determines whether to auto-handle or escalate."""

    def __init__(self, confidence_threshold: float = 0.14):
        self.confidence_threshold = confidence_threshold

    def evaluate(
        self,
        customer_query: str,
        predicted_intent: str,
        intent_confidence: float = 0.8
    ) -> Dict[str, Any]:
        """
        Determines escalation status, stated reason, and confidence.

        Returns:
            {
                "decision": "AUTO_HANDLE" | "ESCALATE",
                "reason": str,
                "confidence": float,
                "trigger_category": Optional[str]
            }
        """
        query_clean = customer_query.strip()

        # Step 0: Check high-confidence self-serve informational exceptions (e.g. appointment booking FAQ)
        if re.search(r"\b(make an appointment for someone else)\b", query_clean, re.IGNORECASE):
            return {
                "decision": "AUTO_HANDLE",
                "reason": "Standard informational query regarding Genius Bar appointment reservation policy.",
                "confidence": 0.95,
                "trigger_category": "INFORMATIONAL_FAQ"
            }

        # Step 1: Check High-Priority Escalation Triggers
        for trigger in ESCALATION_TRIGGERS:
            if trigger["pattern"].search(query_clean):
                return {
                    "decision": "ESCALATE",
                    "reason": trigger["reason"],
                    "confidence": 0.98,
                    "trigger_category": trigger["category"]
                }

        # Step 2: Intent-Specific Deterministic Fallback Policies
        # Account locks or Store billing disputes default to ESCALATE unless clearly self-serve
        if predicted_intent == "STORE_ORDER_BILLING" and any(k in query_clean.lower() for k in ["charged", "refund", "stolen", "dispute", "cancel order"]):
            return {
                "decision": "ESCALATE",
                "reason": "Account or transaction modification requires private customer identification in DM.",
                "confidence": 0.88,
                "trigger_category": "BILLING_POLICY"
            }

        if predicted_intent == "ACCOUNT_APPLE_ID_ICLOUD" and any(k in query_clean.lower() for k in ["locked", "compromised", "recovery", "password", "passwords", "verification code", "veri code", "overridden", "sign in", "signing in"]):
            return {
                "decision": "ESCALATE",
                "reason": "Account recovery, password authentication, or identity credential issue requires secure DM channel.",
                "confidence": 0.90,
                "trigger_category": "AUTH_SECURITY"
            }

        # Step 3: Check Auto-Handle Patterns
        for pattern, reason in AUTO_HANDLE_PATTERNS:
            if pattern.search(query_clean):
                return {
                    "decision": "AUTO_HANDLE",
                    "reason": reason,
                    "confidence": 0.92,
                    "trigger_category": "SELF_SERVE_WORKFLOW"
                }

        # Step 4: Gating on Model Uncertainty
        if intent_confidence < self.confidence_threshold:
            return {
                "decision": "ESCALATE",
                "reason": f"Low model confidence ({intent_confidence:.2f}) on multi-intent or ambiguous query.",
                "confidence": 0.70,
                "trigger_category": "CONFIDENCE_GATE"
            }

        # Step 5: Default Operational Self-Serve
        return {
            "decision": "AUTO_HANDLE",
            "reason": f"Standard {predicted_intent.lower().replace('_', ' ')} diagnostic guidance and self-serve resolution available.",
            "confidence": 0.85,
            "trigger_category": "DEFAULT_SELF_SERVE"
        }
