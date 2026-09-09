"""
Grounded Reply Generator for @AppleSupport.

Drafts brand-aligned customer support responses grounded in historical
resolutions retrieved from the knowledge base, calibrated for Twitter character limits.
"""

import os
import re
from typing import List, Dict, Any, Optional

# Standard Apple Support DM handoff link
APPLE_DM_LINK = "https://t.co/GDrqU22YpT"

# Canonical Apple resolution knowledge cards for key technical scenarios
CANONICAL_RESOLUTIONS = {
    "SOFTWARE_UPDATE_OS": {
        "text_bug": "We'd like to help with your keyboard. You can resolve this by adding a text replacement shortcut under Settings > General > Keyboard > Text Replacement, or updating to the latest iOS 11 point release.",
        "storage_ota": "We can help with that update error. Try going to Settings > General > iPhone Storage, find the iOS update download, tap Delete Update, then check for the update again in Settings > General > Software Update.",
        "boot_loop": "Let's help get your device back up and running. Try a force restart by pressing and holding the Power and Volume Down buttons (or Power and Home on older models) until the Apple logo appears.",
        "general": "We're here to help. To get started, let us know which device model you have and the exact version of iOS installed under Settings > General > About."
    },
    "BATTERY_PERFORMANCE": {
        "swollen": "Please disconnect your charger and stop using the device immediately for safety. We want to inspect this right away—join us in DM so we can prioritize your case: " + APPLE_DM_LINK,
        "drain": "We understand battery life is important. Head over to Settings > Battery to see which apps have been using the most power over the last 24 hours. Does anything stand out?",
        "shutdown": "We'd like to look into those unexpected shutdowns with you. What battery percentage does this usually happen at, and are you in a cold environment?",
        "general": "We'd be glad to look into your battery performance. Which device model do you have, and does this happen during specific tasks?"
    },
    "HARDWARE_AUDIO_DISPLAY": {
        "screen": "We want to help with your display. Let's meet in DM with your device serial number so we can check your repair options and schedule a Genius Bar appointment: " + APPLE_DM_LINK,
        "audio": "Let's look into your audio issue. Try testing the microphone in the Voice Memos app, and check that the speaker mesh is clean and unobstructed.",
        "general": "We're here to help with your device. Did this issue start following any recent drops or liquid exposure?"
    },
    "ACCOUNT_APPLE_ID_ICLOUD": {
        "locked": "Your security is our priority. You can initiate account recovery securely at iforgot.apple.com. If you need step-by-step assistance, join us in DM: " + APPLE_DM_LINK,
        "storage": "We can help you manage your storage. Head to Settings > [Your Name] > iCloud > Manage Storage to see what is taking up space and manage your backups.",
        "general": "We want to make sure your Apple ID is secure. Send us a DM so we can guide you through the next steps safely: " + APPLE_DM_LINK
    },
    "STORE_ORDER_BILLING": {
        "refund": "You can view your recent purchase history and request a refund directly at reportaproblem.apple.com. Let us know if you have questions about the process!",
        "unauthorized": "We understand this is concerning. To protect your financial security, please join us in DM with your order details so an advisor can review the charge: " + APPLE_DM_LINK,
        "general": "We'd be happy to check into your order details. Send us a DM with your order or invoice number: " + APPLE_DM_LINK
    },
    "CONNECTIVITY_SYNC": {
        "wifi": "Let's get your connection working. Try tapping Settings > General > Reset > Reset Network Settings (note: this will reset saved Wi-Fi passwords), then reconnect.",
        "airdrop": "To troubleshoot AirDrop, make sure both Wi-Fi and Bluetooth are turned on, Personal Hotspot is off, and AirDrop receiving is set to 'Everyone' in Control Center.",
        "general": "We can help with your connectivity. Have you tried toggling Airplane Mode on for 30 seconds or restarting your device?"
    },
    "THIRD_PARTY_APP_ISSUES": {
        "crash": "We'd like to help with your app. Have you checked the App Store for any pending updates for this app, or tried restarting your device?",
        "general": "Let's troubleshoot this app together. If restarting and updating doesn't help, try deleting and reinstalling the app from the App Store."
    },
    "GENERAL_FEEDBACK_RANT": {
        "foreign": "We offer support on Twitter in English. To get help in your preferred language, please visit support.apple.com or download the Apple Support app.",
        "rant": "We appreciate your feedback and are always here to help if you're experiencing a technical issue with your Apple device. Let us know what's going on!",
        "escalate": "We're here for you and want to give this the attention it deserves. Please send us a DM so a senior advisor can assist you directly: " + APPLE_DM_LINK
    }
}


class ResponseGenerator:
    """Generates grounded Apple Support replies based on intent, escalation, and retrieved history."""

    def __init__(self):
        pass

    def generate_reply(
        self,
        customer_query: str,
        predicted_intent: str,
        escalation_decision: str,
        escalation_reason: str,
        retrieved_contexts: List[Dict[str, Any]]
    ) -> str:
        """
        Drafts an authentic, grounded Apple Support tweet response.
        """
        query_lower = customer_query.lower()

        # Handle ESCALATE cases
        if escalation_decision == "ESCALATE":
            if any(w in query_lower for w in ["swollen", "smoke", "sparks", "burn", "exploded", "hospital"]):
                return (
                    f"Please disconnect your charger and discontinue using the device immediately for safety. "
                    f"We take safety very seriously—send us a DM right now so we can assist: {APPLE_DM_LINK}"
                )
            if any(w in query_lower for w in ["lawsuit", "sue", "legal", "journalist", "media"]):
                return (
                    f"Thanks for reaching out. Please connect with our team directly in DM so we can direct you to "
                    f"the appropriate department: {APPLE_DM_LINK}"
                )
            if any(w in query_lower for w in ["charged", "refund", "stolen", "dispute", "bill"]):
                return (
                    f"We understand your concern regarding this charge and want to look into it with you safely. "
                    f"Join us in DM so we can review your account details: {APPLE_DM_LINK}"
                )
            if any(w in query_lower for w in ["locked", "compromised", "hacked", "activation lock"]):
                return (
                    f"We take account security very seriously. Send us a DM so we can guide you through the next steps "
                    f"securely: {APPLE_DM_LINK}"
                )
            # General Escalation handoff
            return (
                f"We're here to help and want to take a closer look into this with you. "
                f"Please join us in a DM with your device details so we can assist: {APPLE_DM_LINK}"
            )

        # Handle AUTO_HANDLE cases with Grounded Guidance
        canonical_group = CANONICAL_RESOLUTIONS.get(predicted_intent, CANONICAL_RESOLUTIONS["SOFTWARE_UPDATE_OS"])
        
        # Specific sub-issue matching
        if predicted_intent == "SOFTWARE_UPDATE_OS":
            if any(w in query_lower for w in ["'i'", "letter i", "question mark", "a [?]", "i️"]):
                return canonical_group["text_bug"]
            if any(w in query_lower for w in ["storage", "ota", "delete update", "not enough"]):
                return canonical_group["storage_ota"]
            if any(w in query_lower for w in ["frozen", "apple logo", "stuck", "boot"]):
                return canonical_group["boot_loop"]

        elif predicted_intent == "BATTERY_PERFORMANCE":
            if any(w in query_lower for w in ["drain", "battery life", "dying"]):
                return canonical_group["drain"]
            if any(w in query_lower for w in ["shut", "shutdown", "turning off"]):
                return canonical_group["shutdown"]

        elif predicted_intent == "CONNECTIVITY_SYNC":
            if any(w in query_lower for w in ["wifi", "wi-fi", "network"]):
                return canonical_group["wifi"]
            if any(w in query_lower for w in ["airdrop", "share"]):
                return canonical_group["airdrop"]

        elif predicted_intent == "STORE_ORDER_BILLING":
            if any(w in query_lower for w in ["cancel", "subscription", "refund"]):
                return canonical_group["refund"]

        elif predicted_intent == "GENERAL_FEEDBACK_RANT":
            if any(w in query_lower for w in ["hola", "bonjour", "gracias", "merci"]):
                return canonical_group["foreign"]
            return canonical_group["rant"]

        # Check if high-similarity historical reply exists
        if retrieved_contexts and retrieved_contexts[0]["similarity_score"] > 0.45:
            hist_reply = retrieved_contexts[0]["apple_reply"]
            if len(hist_reply) > 20 and not hist_reply.startswith("http"):
                # Clean any lingering user handles from historical reply
                clean_reply = re.sub(r"@[\w_]+", "", hist_reply).strip()
                if 20 <= len(clean_reply) <= 270:
                    return clean_reply

        # Default intent guidance
        return canonical_group.get("general", "We're here to help. What device model and software version are you running?")
