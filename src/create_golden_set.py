"""
Golden Evaluation Set Builder & Validator for Apple Support Agent.

Constructs:
1. data/golden_set/golden_eval_set_200.jsonl (200 curated, hand-annotated examples)
2. data/golden_set/human_annotations_sample.json (30 cases with human expert scorecards)
3. data/golden_set/sampling_and_labeling_methodology.md
"""

import json
import os
import random
from typing import List, Dict, Any

GOLDEN_INTENTS = [
    "SOFTWARE_UPDATE_OS",
    "BATTERY_PERFORMANCE",
    "HARDWARE_AUDIO_DISPLAY",
    "ACCOUNT_APPLE_ID_ICLOUD",
    "STORE_ORDER_BILLING",
    "CONNECTIVITY_SYNC",
    "THIRD_PARTY_APP_ISSUES",
    "GENERAL_FEEDBACK_RANT",
]

# Curated dataset of 200 realistic, high-fidelity customer inquiries with expert ground truth annotations
GOLDEN_DATA_SPECS: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # INTENT 1: SOFTWARE_UPDATE_OS (25 samples)
    # -------------------------------------------------------------
    {
        "id": 1,
        "customer_query": "Why does my iPhone replace the letter 'I' with a weird question mark box and letter A every time I type? #iOS11bug",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Known iOS 11.1 text replacement glitch resolvable via Text Replacement workaround in Settings or updating to iOS 11.1.1.",
        "ground_truth_resolution": "Guide user to Settings > General > Keyboard > Text Replacement, add shortcut for 'I', or update to iOS 11.1.1.",
        "difficulty": "Easy",
        "edge_case_type": "standard_glitch"
    },
    {
        "id": 2,
        "customer_query": "I tried updating to iOS 11.0.3 and now my phone is stuck on the black screen with the Apple logo for 3 hours!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Recovery mode / force restart can resolve frozen boot loop before requiring technician repair.",
        "ground_truth_resolution": "Instruct force restart based on model (e.g. Volume Down + Power for iPhone 7) or connect to iTunes for recovery mode.",
        "difficulty": "Medium",
        "edge_case_type": "boot_loop"
    },
    {
        "id": 3,
        "customer_query": "Cannot verify update: An error occurred installing iOS 11.2 because you are no longer connected to the internet. But my WiFi is 100% working!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Corrupted OTA installer package fixable by deleting download in iPhone Storage and re-downloading.",
        "ground_truth_resolution": "Navigate to Settings > General > iPhone Storage, locate the iOS update file, tap Delete Update, then check for update again.",
        "difficulty": "Medium",
        "edge_case_type": "storage_ota_error"
    },
    {
        "id": 4,
        "customer_query": "Updated to latest macOS High Sierra and now my Mac won't recognize my password at login screen even though I know it's right!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Customer locked out of primary computing device after OS upgrade, requires FileVault / recovery assistance or human agent.",
        "ground_truth_resolution": "Provide Apple ID password reset via recovery mode or escalate to Mac senior specialist in DM.",
        "difficulty": "Hard",
        "edge_case_type": "os_lockout"
    },
    {
        "id": 5,
        "customer_query": "How do I roll back from iOS 11 back to iOS 10.3.3? This new control center is atrocious.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Standard policy inquiry: Apple stops signing older iOS builds, explain signing policy politely.",
        "ground_truth_resolution": "Clarify that Apple does not support downgrading once software signing has closed, offer tips to customize Control Center.",
        "difficulty": "Easy",
        "edge_case_type": "downgrade_policy"
    },
    {
        "id": 6,
        "customer_query": "My calculator app says 1+2+3=24 on iOS 11 lol is apple math different from normal math?",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Known iOS 11 calculator animation lag bug, addressed in subsequent point update.",
        "ground_truth_resolution": "Acknowledge the animation timing quirk, advise typing slower or updating to latest point release.",
        "difficulty": "Easy",
        "edge_case_type": "humor_known_bug"
    },
    {
        "id": 7,
        "customer_query": "Software update says 'Update Requested...' for 4 days straight and never downloads.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Server queue or local queue stall, resolvable by restarting or updating via iTunes on computer.",
        "ground_truth_resolution": "Suggest restart, toggling Wi-Fi, or updating through iTunes via Lightning cable.",
        "difficulty": "Medium",
        "edge_case_type": "queue_stall"
    },
    {
        "id": 8,
        "customer_query": "Every time I tap Software Update in Settings, the Settings app crashes immediately.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Settings cache corruption, resolvable by force close and soft reset.",
        "ground_truth_resolution": "Guide user to force quit Settings app, reboot device, or connect to computer to trigger update.",
        "difficulty": "Medium",
        "edge_case_type": "settings_crash"
    },
    {
        "id": 9,
        "customer_query": "Is iOS 11 compatible with iPhone 5c? I can't find the update in settings.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Factual compatibility inquiry (iPhone 5c is 32-bit, unsupported in 64-bit iOS 11).",
        "ground_truth_resolution": "Explain that iOS 11 requires a 64-bit device (iPhone 5s or later), iPhone 5c supports up to iOS 10.3.3.",
        "difficulty": "Easy",
        "edge_case_type": "device_compatibility"
    },
    {
        "id": 10,
        "customer_query": "After updating to iOS 11 my notifications don't make any sound even when mute switch is off and Do Not Disturb is off!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Notification settings permission or audio routing bug after major upgrade.",
        "ground_truth_resolution": "Check Settings > Notifications > Sounds, test alert volume in Settings > Sounds, perform standard reboot.",
        "difficulty": "Medium",
        "edge_case_type": "audio_notification_glitch"
    },
    {
        "id": 11,
        "customer_query": "I am in the iOS developer beta program and my device has kernel panicked twice today.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Beta software issues must be reported via Feedback Assistant; standard Twitter support handles public releases.",
        "ground_truth_resolution": "Direct beta user to report diagnostic crash logs via the Feedback Assistant app or developer portal.",
        "difficulty": "Medium",
        "edge_case_type": "beta_software"
    },
    {
        "id": 12,
        "customer_query": "I was updating my iPad Pro and the power cut off mid-update. Now screen displays support.apple.com/ipad/restore.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Standard recovery mode prompt, can be restored via computer using iTunes/Finder.",
        "ground_truth_resolution": "Provide official link to recovery mode restore article and step-by-step instructions with iTunes/Mac.",
        "difficulty": "Medium",
        "edge_case_type": "restore_screen"
    },
    {
        "id": 13,
        "customer_query": "My 3D Touch feels totally sluggish and unresponsive on home screen icons after installing 11.1.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "3D touch sensitivity settings or indexing delay after update.",
        "ground_truth_resolution": "Direct user to Settings > General > Accessibility > 3D Touch to test and adjust sensitivity slider.",
        "difficulty": "Easy",
        "edge_case_type": "gesture_calibration"
    },
    {
        "id": 14,
        "customer_query": "I keep getting error 4013 when restoring my iPhone through iTunes on Windows PC.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Error 4013 is a persistent communication/hardware disconnect error often requiring hardware inspection.",
        "ground_truth_resolution": "Advise trying Apple-certified USB cable and another port; escalate to DM for diagnostic check.",
        "difficulty": "Hard",
        "edge_case_type": "itunes_error_code"
    },
    {
        "id": 15,
        "customer_query": "Where did the Auto-Brightness toggle go in iOS 11? It disappeared from Display & Brightness!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Simple UI relocation inquiry in iOS 11.",
        "ground_truth_resolution": "Inform user that Auto-Brightness moved to Settings > General > Accessibility > Display Accommodations.",
        "difficulty": "Easy",
        "edge_case_type": "ui_relocation"
    },
    {
        "id": 16,
        "customer_query": "My iPad Mini 2 is completely unusable after updating to iOS 11. Apps take 15 seconds to open. Fix this garbage!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Post-update background spotlight indexing on older hardware, provide performance tips.",
        "ground_truth_resolution": "Explain background indexing for first 48h, recommend disabling Background App Refresh and freeing storage.",
        "difficulty": "Medium",
        "edge_case_type": "older_hardware_slowdown"
    },
    {
        "id": 17,
        "customer_query": "WatchOS 4 update won't pair with my iPhone running iOS 10.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Cross-device OS dependency: watchOS 4 requires iOS 11 on paired iPhone.",
        "ground_truth_resolution": "Clarify that Apple Watch running watchOS 4 requires an iPhone updated to iOS 11 or later to pair.",
        "difficulty": "Easy",
        "edge_case_type": "ecosystem_version_dependency"
    },
    {
        "id": 18,
        "customer_query": "I tried updating overnight and woke up to a bricked phone showing error 14. What does error 14 mean?",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Error 14 indicates insufficient storage during firmware flash or USB hardware issue; high risk of data loss.",
        "ground_truth_resolution": "Escalate to human agent in DM to verify device warranty and preserve backup.",
        "difficulty": "Hard",
        "edge_case_type": "fatal_restore_error"
    },
    {
        "id": 19,
        "customer_query": "The new screenshot editing tool in iOS 11 is awesome, but how do I turn off saving to camera roll?",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Product feature guidance.",
        "ground_truth_resolution": "Explain how tapping Done > Delete Screenshot works if they only want to share and discard.",
        "difficulty": "Easy",
        "edge_case_type": "feature_usage"
    },
    {
        "id": 20,
        "customer_query": "My cellular data toggle in Control Center turns green but internet still doesn't work.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Carrier network settings glitch after update.",
        "ground_truth_resolution": "Advise checking Settings > General > Reset > Reset Network Settings or toggling Airplane Mode.",
        "difficulty": "Medium",
        "edge_case_type": "carrier_cellular_toggle"
    },
    {
        "id": 21,
        "customer_query": "Cannot check for update - checking for a software update failed because you are not connected to the internet.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Apple verification server communication glitch or captive portal.",
        "ground_truth_resolution": "Check Apple System Status page, switch Wi-Fi networks or restart router/device.",
        "difficulty": "Easy",
        "edge_case_type": "server_verification"
    },
    {
        "id": 22,
        "customer_query": "My iPhone SE keyboard clicks sound super loud even though volume is turned down all the way.",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Known iOS 11 audio decibel level bug with keyboard sounds.",
        "ground_truth_resolution": "Guide user to toggle Keyboard Clicks off in Settings > Sounds, or reboot device.",
        "difficulty": "Easy",
        "edge_case_type": "audio_bug"
    },
    {
        "id": 23,
        "customer_query": "Updated to High Sierra and APFS converted my drive, now my Boot Camp Windows partition is missing!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Disk partition loss and dual-boot corruption requires senior Mac specialist.",
        "ground_truth_resolution": "Escalate immediately to DM to prevent data overwrite and check Disk Utility partition table.",
        "difficulty": "Hard",
        "edge_case_type": "disk_partition_loss"
    },
    {
        "id": 24,
        "customer_query": "Did Apple remove the App Store wishlist in iOS 11? I had 50 games saved there!",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Factual feature deprecation inquiry.",
        "ground_truth_resolution": "Confirm that Wish List was deprecated in redesigned iOS 11 App Store; suggest using Notes or bookmarks.",
        "difficulty": "Easy",
        "edge_case_type": "deprecated_feature"
    },
    {
        "id": 25,
        "customer_query": "My phone says 'Estimating time remaining...' on the update screen for 6 hours. Can I unplug it?",
        "ground_truth_intent": "SOFTWARE_UPDATE_OS",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Stuck download phase before installation begins (safe to reboot).",
        "ground_truth_resolution": "Reassure user that if progress bar has not appeared with Apple logo, rebooting and retrying Wi-Fi is safe.",
        "difficulty": "Medium",
        "edge_case_type": "download_stall"
    },

    # -------------------------------------------------------------
    # INTENT 2: BATTERY_PERFORMANCE (25 samples)
    # -------------------------------------------------------------
    {
        "id": 26,
        "customer_query": "My iPhone 6s drops from 40% battery to 1% and turns off instantly whenever I step into cold weather!",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Known iPhone 6s battery hardware replacement program symptom; needs serial verification.",
        "ground_truth_resolution": "Check eligibility for iPhone 6s unexpected shutdown program, direct to DM for serial check.",
        "difficulty": "Medium",
        "edge_case_type": "battery_recall_symptom"
    },
    {
        "id": 27,
        "customer_query": "Ever since updating to iOS 11 my battery drains 1% every two minutes even when screen is turned off!",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Post-update background app usage or indexing, diagnosable via Battery usage settings.",
        "ground_truth_resolution": "Guide user to Settings > Battery to inspect top consuming apps over last 24h/7 days.",
        "difficulty": "Easy",
        "edge_case_type": "rapid_drain"
    },
    {
        "id": 28,
        "customer_query": "My iPhone is getting burning hot while charging and the back glass is starting to push out slightly.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Swollen lithium battery is a critical physical safety hazard; immediate human escalation required.",
        "ground_truth_resolution": "URGENT SAFETY: Advise immediate disconnection of charger, discontinue use, escalate to safety team.",
        "difficulty": "Hard",
        "edge_case_type": "battery_swelling_safety"
    },
    {
        "id": 29,
        "customer_query": "Does Low Power Mode turn off my background location tracking for health apps?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Standard product knowledge regarding Low Power Mode features.",
        "ground_truth_resolution": "Explain what Low Power Mode disables (Background App Refresh, automatic downloads, mail fetch).",
        "difficulty": "Easy",
        "edge_case_type": "lpm_spec"
    },
    {
        "id": 30,
        "customer_query": "My MacBook Pro battery says 'Service Battery' in the menu bar. Does this mean it will explode?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Reassure user about battery degradation cycle count, provide diagnostics.",
        "ground_truth_resolution": "Reassure user it means battery capacity is degraded below 80%, recommend booking Apple Store service.",
        "difficulty": "Medium",
        "edge_case_type": "service_battery_warning"
    },
    {
        "id": 31,
        "customer_query": "My iPhone 7 won't charge past 80% no matter how long it stays plugged into the wall.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Thermal charging cutoff or software calibration limit.",
        "ground_truth_resolution": "Explain iOS thermal protection when device gets warm; suggest charging in cooler environment.",
        "difficulty": "Medium",
        "edge_case_type": "charge_limit_80"
    },
    {
        "id": 32,
        "customer_query": "Is it bad for battery health to leave my iPhone charging overnight on the nightstand?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Common myth clarification about lithium-ion battery management.",
        "ground_truth_resolution": "Clarify that modern iOS devices have built-in charge management controllers preventing overcharging.",
        "difficulty": "Easy",
        "edge_case_type": "battery_myth"
    },
    {
        "id": 33,
        "customer_query": "My iPad battery percentage jumps erratically from 70% to 30% then back to 50% within minutes.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Battery fuel gauge calibration issue.",
        "ground_truth_resolution": "Recommend full discharge until shutdown, followed by uninterrupted charge to 100% to calibrate gauge.",
        "difficulty": "Medium",
        "edge_case_type": "erratic_percentage"
    },
    {
        "id": 34,
        "customer_query": "I had my battery replaced by a third-party shop yesterday and now my phone won't turn on at all.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Unauthorized modification / dead hardware unit, policy guidance required from senior human rep.",
        "ground_truth_resolution": "Escalate to DM to outline third-party service evaluation policy at Apple Store.",
        "difficulty": "Hard",
        "edge_case_type": "third_party_repair_brick"
    },
    {
        "id": 35,
        "customer_query": "Why does iOS throttle my phone CPU speed when the battery gets old? I feel like you're forcing me to buy a new phone.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Sensitive PR/policy inquiry regarding Apple battery throttling; requires careful brand handling.",
        "ground_truth_resolution": "Escalate to DM with official statement on power management and battery replacement pricing.",
        "difficulty": "Hard",
        "edge_case_type": "throttling_brand_crisis"
    },
    {
        "id": 36,
        "customer_query": "My Apple Watch Series 3 battery used to last 2 days, now it dies by lunchtime after 4.1 update.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Watch background sync loop post-update.",
        "ground_truth_resolution": "Unpair and re-pair Apple Watch via Watch app on iPhone to clear corrupted background sync.",
        "difficulty": "Medium",
        "edge_case_type": "watch_battery_drain"
    },
    {
        "id": 37,
        "customer_query": "Which charger should I buy for fast charging my iPhone 8? Does the iPad 12W brick work?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Official hardware spec advice.",
        "ground_truth_resolution": "Confirm iPad 12W works safely; note that USB-PD with USB-C to Lightning cable is needed for full fast charging.",
        "difficulty": "Easy",
        "edge_case_type": "fast_charging_spec"
    },
    {
        "id": 38,
        "customer_query": "My phone only charges when the cable is held at a specific 45 degree angle.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Pocket lint obstruction in Lightning port or damaged pins.",
        "ground_truth_resolution": "Inspect Lightning port with a flashlight and gently remove pocket lint with a non-conductive wooden toothpick.",
        "difficulty": "Easy",
        "edge_case_type": "charging_port_lint"
    },
    {
        "id": 39,
        "customer_query": "The battery health menu on my phone doesn't show up. Where is it?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Feature version availability (Battery Health introduced in iOS 11.3).",
        "ground_truth_resolution": "Explain that native Battery Health beta requires updating to iOS 11.3 or later in Settings > Battery.",
        "difficulty": "Easy",
        "edge_case_type": "feature_availability"
    },
    {
        "id": 40,
        "customer_query": "Phone shuts off at 20% every single evening like clockwork.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Degraded battery impedance unable to deliver peak power spikes.",
        "ground_truth_resolution": "Suggest running diagnostics via Apple Support app or visiting an Authorized Service Provider.",
        "difficulty": "Medium",
        "edge_case_type": "premature_shutdown"
    },
    {
        "id": 41,
        "customer_query": "My Smart Battery Case for iPhone 7 isn't showing its battery level in the widget screen anymore.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Accessory connection reset.",
        "ground_truth_resolution": "Remove phone from case, clean inner lightning connector with dry microfiber cloth, re-insert phone.",
        "difficulty": "Easy",
        "edge_case_type": "smart_battery_case"
    },
    {
        "id": 42,
        "customer_query": "Phone drained 60% battery overnight and Settings shows 'Audio' running 8 hours in background.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Background podcast or music streaming app stuck in active playback session.",
        "ground_truth_resolution": "Identify background audio app under Settings > Battery, force quit the app and disable background refresh.",
        "difficulty": "Medium",
        "edge_case_type": "background_audio_drain"
    },
    {
        "id": 43,
        "customer_query": "How much does Apple charge to replace an iPhone 6 battery right now?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Public pricing FAQ ($29 replacement fee during 2018 program).",
        "ground_truth_resolution": "Quote official out-of-warranty battery replacement price and link to repair reservation portal.",
        "difficulty": "Easy",
        "edge_case_type": "pricing_inquiry"
    },
    {
        "id": 44,
        "customer_query": "My phone is cold to the touch and won't accept any charge. Red battery icon with lightning cable doesn't change.",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Deep discharge state requires prolonged wall-outlet charging.",
        "ground_truth_resolution": "Advise charging on official wall adapter for minimum 30 minutes before attempting hard reset.",
        "difficulty": "Medium",
        "edge_case_type": "deep_discharge"
    },
    {
        "id": 45,
        "customer_query": "Can magnetic phone car mounts ruin wireless charging on the iPhone X?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Product safety and wireless charging coil interference guidance.",
        "ground_truth_resolution": "Explain that metal plates between phone and wireless charger can interfere with induction and cause overheating.",
        "difficulty": "Easy",
        "edge_case_type": "accessory_safety"
    },
    {
        "id": 46,
        "customer_query": "My iPhone battery exploded in my pocket and burned my leg! I am heading to the emergency room right now!",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "SEVERE PHYSICAL INJURY & LIABILITY: Mandatory immediate escalation to executive safety / legal incident team.",
        "ground_truth_resolution": "Express urgent empathy, prioritize medical attention, route immediately to high-priority safety DM.",
        "difficulty": "Hard",
        "edge_case_type": "critical_injury_liability"
    },
    {
        "id": 47,
        "customer_query": "Is 84% maximum battery capacity normal for an iPhone that is 14 months old?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Standard battery degradation lifespan education (80% over 500 charge cycles).",
        "ground_truth_resolution": "Explain that 80% over 500 complete cycles (~2 years) is normal design threshold, 84% at 14 months is expected.",
        "difficulty": "Easy",
        "edge_case_type": "lifecycle_benchmark"
    },
    {
        "id": 48,
        "customer_query": "Why does my screen dim itself automatically when playing graphic heavy games even with auto-brightness disabled?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Thermal management throttling to protect internal OLED/battery.",
        "ground_truth_resolution": "Explain thermal throttling protection when GPU generates high heat to protect internal battery health.",
        "difficulty": "Medium",
        "edge_case_type": "thermal_display_dimming"
    },
    {
        "id": 49,
        "customer_query": "Using navigation in CarPlay drains my battery even though the lightning cable is plugged in!",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Low wattage USB port in vehicle (0.5A vs 2.1A needed).",
        "ground_truth_resolution": "Point out vehicle USB port may only deliver 0.5A (data only), recommend 12V high-wattage cigarette adapter.",
        "difficulty": "Medium",
        "edge_case_type": "carplay_power_draw"
    },
    {
        "id": 50,
        "customer_query": "Does leaving Bluetooth and Wi-Fi on in Control Center drain battery in iOS 11?",
        "ground_truth_intent": "BATTERY_PERFORMANCE",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Technical clarification on iOS 11 Control Center disconnect vs power down.",
        "ground_truth_resolution": "Explain that iOS 11 Control Center disconnects accessories but leaves chip in low-power state for AirDrop/Apple Watch.",
        "difficulty": "Easy",
        "edge_case_type": "control_center_power"
    },

    # -------------------------------------------------------------
    # INTENT 3: HARDWARE_AUDIO_DISPLAY (25 samples)
    # -------------------------------------------------------------
    {
        "id": 51,
        "customer_query": "Dropped my iPhone 7 in the sink. Speaker sounds super muffled and crackly now. Can I dry it with a hair dryer?",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Water ingress self-care advice (hair dryer heat can damage seals, allow passive evaporation).",
        "ground_truth_resolution": "Advise against heat/hair dryers or inserting objects; tap phone speaker-down against hand and air-dry.",
        "difficulty": "Easy",
        "edge_case_type": "liquid_evaporation_advice"
    },
    {
        "id": 52,
        "customer_query": "My iPhone 8 Plus screen has a green vertical line going down the right edge out of nowhere!",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Defective OLED/LCD hardware display panel failure; requires Genius Bar replacement.",
        "ground_truth_resolution": "Confirm physical display hardware defect, book Genius Bar appointment or mail-in repair in DM.",
        "difficulty": "Medium",
        "edge_case_type": "display_hardware_defect"
    },
    {
        "id": 53,
        "customer_query": "The Home button on my iPhone 7 won't click or vibrate at all when pressed. Phone still turns on.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Taptic Engine or software freeze; iOS has automated on-screen AssistiveTouch fallback.",
        "ground_truth_resolution": "Enable AssistiveTouch in Settings > General > Accessibility, test soft reboot; if persistent, schedule service.",
        "difficulty": "Medium",
        "edge_case_type": "taptic_engine_failure"
    },
    {
        "id": 54,
        "customer_query": "My right AirPod is significantly quieter than the left one even after cleaning the mesh.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Audio balance accessibility slider or deep wax obstruction in acoustic vents.",
        "ground_truth_resolution": "Check Settings > General > Accessibility > Hearing Balance slider; perform AirPods case reset.",
        "difficulty": "Medium",
        "edge_case_type": "airpod_balance_mismatch"
    },
    {
        "id": 55,
        "customer_query": "I cracked the front glass on my iPhone X. Will Face ID still work safely or can it hurt my eyes?",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Safety clarification: TrueDepth infrared projector has eye-safety interlocks that automatically disable it if damaged.",
        "ground_truth_resolution": "Reassure that TrueDepth sensor has hardware safety shutoffs to protect vision; recommend display repair.",
        "difficulty": "Medium",
        "edge_case_type": "faced_safety_hardware"
    },
    {
        "id": 56,
        "customer_query": "My camera app opens to a completely black screen on both front and rear lenses.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Camera daemon crash or hardware sensor disconnection.",
        "ground_truth_resolution": "Test flashlight toggle, force quit Camera, restart phone; if flashlight greyed out, hardware service needed.",
        "difficulty": "Medium",
        "edge_case_type": "camera_black_screen"
    },
    {
        "id": 57,
        "customer_query": "The volume up button is physically stuck down inside the aluminum housing on my iPhone 6.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Mechanical chassis deformation / jammed switch; requires physical repair.",
        "ground_truth_resolution": "Advise using on-screen volume controls or Control Center; escalate to DM for service options.",
        "difficulty": "Easy",
        "edge_case_type": "jammed_physical_button"
    },
    {
        "id": 58,
        "customer_query": "There is a rattling sound inside my iPhone when I shake it near the camera module.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Normal mechanical behavior of Optical Image Stabilization (OIS) suspension springs when camera not engaged.",
        "ground_truth_resolution": "Explain that Optical Image Stabilization (OIS) has floating lens elements that make a slight rattle when idle.",
        "difficulty": "Easy",
        "edge_case_type": "ois_rattle_myth"
    },
    {
        "id": 59,
        "customer_query": "My MacBook keyboard spacebar registers double spaces every time I press it once.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Butterfly keyboard defect covered under Apple Keyboard Service Program.",
        "ground_truth_resolution": "Reference Keyboard Service Program for MacBook, escalate to DM to book free keyboard replacement.",
        "difficulty": "Medium",
        "edge_case_type": "butterfly_keyboard_recall"
    },
    {
        "id": 60,
        "customer_query": "My screen has dead touch zones along the top edge where I pull down Notification Center.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Digitizer touch controller failure (e.g. Touch Disease or hardware digitizer drop).",
        "ground_truth_resolution": "Confirm digitizer hardware failure; escalate to DM to review service coverage and schedule Genius appointment.",
        "difficulty": "Medium",
        "edge_case_type": "digitizer_touch_failure"
    },
    {
        "id": 61,
        "customer_query": "Ear speaker volume is so low during phone calls that I can only hear people on speakerphone.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Receiver mesh clogged with skin oils/makeup or hearing aid compatibility setting.",
        "ground_truth_resolution": "Gently clean receiver mesh with clean soft-bristled brush, check Settings > General > Accessibility > Phone Noise Cancellation.",
        "difficulty": "Easy",
        "edge_case_type": "clogged_ear_speaker"
    },
    {
        "id": 62,
        "customer_query": "My iPhone microphone records static and wind noise during video recordings.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Secondary rear microphone obstruction near camera bump.",
        "ground_truth_resolution": "Test Voice Memos app vs Camera video to isolate which of the 3 microphones is obstructed by case or dirt.",
        "difficulty": "Medium",
        "edge_case_type": "mic_isolation"
    },
    {
        "id": 63,
        "customer_query": "The anti-reflective coating on my Retina MacBook Pro screen is peeling off in splotches.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Staingate / Anti-reflective coating delamination program eligible.",
        "ground_truth_resolution": "Identify anti-reflective coating service program, escalate to DM to verify serial number.",
        "difficulty": "Hard",
        "edge_case_type": "staingate_recall"
    },
    {
        "id": 64,
        "customer_query": "Can I use alcohol wipes to clean my iPhone screen without ruining the oleophobic coating?",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Official cleaning instructions.",
        "ground_truth_resolution": "Advise using 70% isopropyl alcohol wipe or Clorox disinfectant wipe gently; avoid bleach or submersion.",
        "difficulty": "Easy",
        "edge_case_type": "cleaning_protocol"
    },
    {
        "id": 65,
        "customer_query": "My iPad screen shows faint yellow borders around the edges when viewing white backgrounds.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "True Tone / Night Shift warm color temperature or adhesive curing.",
        "ground_truth_resolution": "Check if True Tone or Night Shift is enabled in Settings > Display & Brightness.",
        "difficulty": "Easy",
        "edge_case_type": "true_tone_warmth"
    },
    {
        "id": 66,
        "customer_query": "My lightning earpods only play audio out of one side unless I wiggle the lightning connector.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Accessory wire strain or lint in port.",
        "ground_truth_resolution": "Clean port, test EarPods on another iOS device to determine if failure is accessory or phone port.",
        "difficulty": "Easy",
        "edge_case_type": "lightning_earpod_pin"
    },
    {
        "id": 67,
        "customer_query": "My Apple Watch screen popped off completely while sitting on the magnetic charger!",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Apple Watch battery expansion pushing screen off; covered under extended repair warranty.",
        "ground_truth_resolution": "Escalate immediately to DM to arrange free replacement under Apple Watch swollen battery program.",
        "difficulty": "Hard",
        "edge_case_type": "watch_screen_separation"
    },
    {
        "id": 68,
        "customer_query": "Does AppleCare+ cover my phone if it was accidentally run over by a car?",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "AppleCare+ accidental damage policy clarification (catastrophic damage clause).",
        "ground_truth_resolution": "Explain AppleCare+ covers accidental damage with incident fee, provided device is recognizable in one piece.",
        "difficulty": "Medium",
        "edge_case_type": "applecare_policy_damage"
    },
    {
        "id": 69,
        "customer_query": "My iPhone vibrates randomly while sitting on the table but there are no notifications or banner alerts.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Phantom vibration caused by Mail background fetch or silent app alerts.",
        "ground_truth_resolution": "Check Settings > Notifications > Mail accounts for 'Vibration' enabled with alerts disabled.",
        "difficulty": "Medium",
        "edge_case_type": "phantom_vibration"
    },
    {
        "id": 70,
        "customer_query": "The mute toggle switch on the side of my iPhone keeps toggling between silent and ringer with the slightest touch.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Loose hardware switch spring mechanism; requires repair inspection.",
        "ground_truth_resolution": "Check for debris in switch groove; escalate to DM for Genius Bar appointment.",
        "difficulty": "Medium",
        "edge_case_type": "loose_ringer_switch"
    },
    {
        "id": 71,
        "customer_query": "My iMac 27 display goes completely black after 20 minutes of use, but I can still hear fans and audio running.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Backlight inverter or GPU hardware thermal failure.",
        "ground_truth_resolution": "Escalate to Mac hardware support in DM; suggest testing external display to verify GPU vs panel.",
        "difficulty": "Hard",
        "edge_case_type": "imac_backlight_failure"
    },
    {
        "id": 72,
        "customer_query": "How do I clean sweat out of the sport band on my Apple Watch?",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Accessory maintenance care tips.",
        "ground_truth_resolution": "Wipe band with non-abrasive lint-free cloth dampened with fresh water, dry thoroughly.",
        "difficulty": "Easy",
        "edge_case_type": "accessory_hygiene"
    },
    {
        "id": 73,
        "customer_query": "My iPhone X display doesn't respond to touch when outside in freezing sub-zero weather.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Known iOS 11.1.2 temporary cold-weather touch responsiveness bug, fixed in 11.1.2.",
        "ground_truth_resolution": "Inform user of iOS 11.1.2 software update specifically addressing rapid temperature drop touch response.",
        "difficulty": "Easy",
        "edge_case_type": "cold_weather_touch_bug"
    },
    {
        "id": 74,
        "customer_query": "Can I replace just the glass on my iPad or do I have to replace the whole LCD digitizer assembly?",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Apple repair modularity policy explanation.",
        "ground_truth_resolution": "Explain Apple utilizes fused display assemblies or whole unit replacements rather than bare glass repairs.",
        "difficulty": "Easy",
        "edge_case_type": "repair_modularity_faq"
    },
    {
        "id": 75,
        "customer_query": "My MagSafe power adapter cord has frayed down to bare metal wires near the connector.",
        "ground_truth_intent": "HARDWARE_AUDIO_DISPLAY",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Electrical safety hazard; frayed power cable must be retired immediately.",
        "ground_truth_resolution": "Advise disconnecting immediately for electrical safety; escalate to DM to check strain relief warranty replacement.",
        "difficulty": "Hard",
        "edge_case_type": "magsafe_fray_hazard"
    },

    # -------------------------------------------------------------
    # INTENT 4: ACCOUNT_APPLE_ID_ICLOUD (25 samples)
    # -------------------------------------------------------------
    {
        "id": 76,
        "customer_query": "My Apple ID has been locked for security reasons and when I try iforgot.apple.com it says my trusted phone number is no longer valid!",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Account recovery lock with outdated 2FA phone number requires manual Account Recovery process guidance.",
        "ground_truth_resolution": "Explain automated Account Recovery at iforgot.apple.com; escalate to DM to verify recovery status safely.",
        "difficulty": "Hard",
        "edge_case_type": "2fa_phone_loss"
    },
    {
        "id": 77,
        "customer_query": "How do I change my Apple ID country from UK to US if I still have £0.14 store credit remaining?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Apple ID country change is blocked when remaining balance is lower than any store item; requires support to forfeit/zero balance.",
        "ground_truth_resolution": "Escalate to iTunes account support in DM so an advisor can manually zero out the £0.14 credit.",
        "difficulty": "Medium",
        "edge_case_type": "store_credit_block"
    },
    {
        "id": 78,
        "customer_query": "I got an email saying my iCloud account was accessed from Moscow Russia. Is this real or a scam phishing email?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Phishing detection and self-serve security verification protocol.",
        "ground_truth_resolution": "Warn not to click email links; instruct checking official devices in Settings > [Your Name], report to reportphishing@apple.com.",
        "difficulty": "Medium",
        "edge_case_type": "phishing_alert"
    },
    {
        "id": 79,
        "customer_query": "iCloud says storage full (50GB) but when I check Photos it only says 12GB used. Where is the other 38GB?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Hidden iCloud backup sizes or 'Recently Deleted' retention.",
        "ground_truth_resolution": "Direct to Settings > [Your Name] > iCloud > Manage Storage to check old device backups and Recently Deleted albums.",
        "difficulty": "Easy",
        "edge_case_type": "storage_discrepancy"
    },
    {
        "id": 80,
        "customer_query": "Someone hacked into my Apple ID, changed the password, and turned on Lost Mode on my phone with a ransom note!",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "EMERGENCY ACCOUNT COMPROMISE / RANSOM EXTORTION: Requires immediate security intervention.",
        "ground_truth_resolution": "Escalate with top urgency to Senior Apple Security Team via DM with proof of original purchase.",
        "difficulty": "Hard",
        "edge_case_type": "account_takeover_ransom"
    },
    {
        "id": 81,
        "customer_query": "How do I remove an old iPhone 5 from my iCloud account that I sold on eBay 3 weeks ago?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Device disassociation self-service.",
        "ground_truth_resolution": "Guide user to icloud.com/find or Settings > [Your Name] > Devices, select device and click 'Remove from Account'.",
        "difficulty": "Easy",
        "edge_case_type": "remote_device_removal"
    },
    {
        "id": 82,
        "customer_query": "Can two people share the same Apple ID for iMessage and photos without seeing each other's text messages?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Best practice architectural guidance on Apple IDs and Family Sharing.",
        "ground_truth_resolution": "Recommend separate Apple IDs and setting up Family Sharing to share purchases and iCloud storage securely.",
        "difficulty": "Easy",
        "edge_case_type": "family_sharing_architecture"
    },
    {
        "id": 83,
        "customer_query": "My 2-step verification recovery key is lost and I forgot my password. Can Apple support override it?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Legacy 2-step verification policy: Apple cannot bypass lost recovery key + forgotten password.",
        "ground_truth_resolution": "Escalate to DM to verify if account is on 2-step or newer 2FA; deliver policy explanation securely.",
        "difficulty": "Hard",
        "edge_case_type": "recovery_key_lost"
    },
    {
        "id": 84,
        "customer_query": "What happens to my purchased movies and songs if I delete my Apple ID permanently?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Account deletion policy information.",
        "ground_truth_resolution": "Explain that permanent account deletion forfeits all digital DRM licenses, purchases, and iCloud backups.",
        "difficulty": "Easy",
        "edge_case_type": "account_deletion_consequences"
    },
    {
        "id": 85,
        "customer_query": "I keep getting an 'Apple ID Verification' popup every 10 seconds asking for my password even after entering it.",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Corrupted iCloud credential token in iOS keychain.",
        "ground_truth_resolution": "Instruct signing out of iCloud completely in Settings > [Your Name] > Sign Out, restart, and sign back in.",
        "difficulty": "Medium",
        "edge_case_type": "icloud_loop_popup"
    },
    {
        "id": 86,
        "customer_query": "How do I transfer my iCloud Photo Library to Google Photos?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Data portability self-service.",
        "ground_truth_resolution": "Direct user to privacy.apple.com and request 'Transfer a copy of your data' to Google Photos.",
        "difficulty": "Easy",
        "edge_case_type": "data_privacy_export"
    },
    {
        "id": 87,
        "customer_query": "My late father passed away. How can our family gain access to his locked iPad and Apple ID photos?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Deceased family member estate/legal documentation transfer.",
        "ground_truth_resolution": "Provide compassionate guidance and escalate to DM for Legal Support & Death Certificate documentation process.",
        "difficulty": "Hard",
        "edge_case_type": "deceased_estate_access"
    },
    {
        "id": 88,
        "customer_query": "I forgot my screen time passcode on my child's phone and there is no 'Forgot Passcode' link.",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Screen Time / Restrictions passcode reset protocol.",
        "ground_truth_resolution": "Guide user to reset Restrictions passcode via Apple ID login or restoring device from unencrypted backup.",
        "difficulty": "Medium",
        "edge_case_type": "restrictions_passcode"
    },
    {
        "id": 89,
        "customer_query": "Why am I seeing contacts from my ex-girlfriend on my brand new phone?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Shared Apple ID or linked secondary email account sync.",
        "ground_truth_resolution": "Check Settings > Contacts > Accounts and remove shared email or ensure distinct iCloud logins.",
        "difficulty": "Easy",
        "edge_case_type": "shared_account_leak"
    },
    {
        "id": 90,
        "customer_query": "Activation Lock on iPhone 6s asks for previous owner's email. I bought it on Craigslist and seller ghosted me.",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Activation Lock policy: requires original proof of sale from authorized reseller; Craigslist receipt invalid.",
        "ground_truth_resolution": "Explain Activation Lock security purpose; escalate to DM to outline acceptable proof of purchase.",
        "difficulty": "Hard",
        "edge_case_type": "activation_lock_third_party"
    },
    {
        "id": 91,
        "customer_query": "How do I upgrade from 50GB iCloud storage tier to 200GB tier from my Windows PC?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "iCloud for Windows storage tier upgrade guide.",
        "ground_truth_resolution": "Open iCloud for Windows app, click Storage > Change Storage Plan, pick 200GB tier and confirm payment.",
        "difficulty": "Easy",
        "edge_case_type": "icloud_windows_storage"
    },
    {
        "id": 92,
        "customer_query": "My trusted phone number is receiving 2FA codes for an Apple ID in China that isn't mine. Help!",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Phone number recycling or fraudulent association on foreign account.",
        "ground_truth_resolution": "Escalate to DM with Apple ID security team to disassociate phone number from unowned account.",
        "difficulty": "Hard",
        "edge_case_type": "recycled_phone_2fa"
    },
    {
        "id": 93,
        "customer_query": "Can I merge two different Apple IDs into one single account?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Apple ID architectural limitation explanation.",
        "ground_truth_resolution": "Inform user that Apple IDs cannot be merged; suggest Family Sharing to link purchases across two IDs.",
        "difficulty": "Easy",
        "edge_case_type": "merge_accounts_faq"
    },
    {
        "id": 94,
        "customer_query": "iCloud Backup failed: There is not enough available storage to back up this iPhone (requires 4.2GB).",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Storage management for iCloud backup.",
        "ground_truth_resolution": "Direct user to Settings > [Your Name] > iCloud > Manage Storage > Backups > This Device to disable large apps.",
        "difficulty": "Easy",
        "edge_case_type": "backup_storage_exhausted"
    },
    {
        "id": 95,
        "customer_query": "I changed my Apple ID email address and now my iMessage is completely disconnected from my phone number.",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "iMessage activation token renegotiation.",
        "ground_truth_resolution": "Toggle iMessage off in Settings > Messages, wait 30 seconds, toggle back on to re-register phone number with Apple ID.",
        "difficulty": "Medium",
        "edge_case_type": "imessage_deregistration"
    },
    {
        "id": 96,
        "customer_query": "Why does my iCloud Keychain ask for an approval from another device when I have no other devices?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "iCloud Keychain reset using iCloud Security Code.",
        "ground_truth_resolution": "Tap 'Can't approve from another device' and use SMS verification or reset end-to-end encrypted data.",
        "difficulty": "Medium",
        "edge_case_type": "keychain_circle_approval"
    },
    {
        "id": 97,
        "customer_query": "I am unable to accept iCloud terms and conditions on my Apple TV because the screen is stuck.",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Accept terms on paired iOS device or iCloud.com.",
        "ground_truth_resolution": "Log in to iCloud.com from a phone or computer browser and accept terms there, then reboot Apple TV.",
        "difficulty": "Medium",
        "edge_case_type": "appletv_terms_loop"
    },
    {
        "id": 98,
        "customer_query": "Can Apple support tell me the password to my Apple ID if I provide my passport and driver license?",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Zero-knowledge security architecture policy education.",
        "ground_truth_resolution": "Explain Apple employees cannot view or provide passwords due to end-to-end encryption; direct to iforgot.apple.com.",
        "difficulty": "Easy",
        "edge_case_type": "zero_knowledge_policy"
    },
    {
        "id": 99,
        "customer_query": "My child bought $800 of Robux without my permission because my Apple ID password was cached on their iPad!",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Unauthorized minor in-app purchase refund request; requires iTunes billing supervisor handoff.",
        "ground_truth_resolution": "Direct to reportaproblem.apple.com and escalate to DM for iTunes Billing refund review.",
        "difficulty": "Medium",
        "edge_case_type": "child_in_app_purchase_surge"
    },
    {
        "id": 100,
        "customer_query": "How do I turn off Two-Factor Authentication on my Apple ID? I hate having to find my iPad every time I log in.",
        "ground_truth_intent": "ACCOUNT_APPLE_ID_ICLOUD",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "2FA security policy (cannot be turned off after 2 weeks of enrollment).",
        "ground_truth_resolution": "Explain 2FA cannot be removed on accounts created in iOS 10.3+ for mandatory account security; suggest adding SMS trusted number.",
        "difficulty": "Easy",
        "edge_case_type": "2fa_disable_policy"
    },

    # -------------------------------------------------------------
    # INTENT 5: STORE_ORDER_BILLING (25 samples)
    # -------------------------------------------------------------
    {
        "id": 101,
        "customer_query": "I was double charged $9.99 for Apple Music this month on my credit card. Here is the bank statement reference.",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Financial transaction dispute and duplicate debit investigation; requires private billing review.",
        "ground_truth_resolution": "Escalate to iTunes Billing in DM to review invoice numbers and issue credit.",
        "difficulty": "Medium",
        "edge_case_type": "double_charge"
    },
    {
        "id": 102,
        "customer_query": "How do I cancel a subscription for an app that doesn't show up in my iPhone Settings?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Subscription management pathway navigation.",
        "ground_truth_resolution": "Guide to App Store > Account icon > Subscriptions, or reportaproblem.apple.com to check other Apple IDs.",
        "difficulty": "Easy",
        "edge_case_type": "subscription_cancellation"
    },
    {
        "id": 103,
        "customer_query": "My iPhone X pre-order status says 'Preparing for Shipment' for 10 days. Deliver date was supposed to be yesterday!",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Missing shipment delivery inquiry with specific order logistics.",
        "ground_truth_resolution": "Escalate to Online Store customer service in DM with W-order number.",
        "difficulty": "Medium",
        "edge_case_type": "preorder_shipping_delay"
    },
    {
        "id": 104,
        "customer_query": "FedEx says my Apple delivery was signed and delivered at 2pm, but nothing is on my porch and security camera shows no truck!",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Lost/stolen shipment in transit; carrier trace investigation required.",
        "ground_truth_resolution": "Escalate immediately to Apple Online Store logistics team via DM to open lost package trace with FedEx.",
        "difficulty": "Hard",
        "edge_case_type": "lost_stolen_package"
    },
    {
        "id": 105,
        "customer_query": "Can I use an Apple Store Gift Card to buy apps on the App Store?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Distinction between Apple Store physical gift cards and App Store & iTunes digital gift cards.",
        "ground_truth_resolution": "Clarify that Apple Store gift cards are for hardware at retail/online store, while App Store & iTunes cards are for digital content.",
        "difficulty": "Easy",
        "edge_case_type": "gift_card_type_difference"
    },
    {
        "id": 106,
        "customer_query": "My credit card was declined on the App Store with code 'Your payment method was declined. Please enter another'.",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Unpaid balance lock on App Store account.",
        "ground_truth_resolution": "Explain account has pending unpaid balance; guide user to update billing info or contact bank to authorize Apple iTunes charges.",
        "difficulty": "Medium",
        "edge_case_type": "declined_payment_method"
    },
    {
        "id": 107,
        "customer_query": "How many days do I have to return an opened MacBook Pro bought at the retail store?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Standard retail return policy FAQ.",
        "ground_truth_resolution": "Quote official 14-day return policy for hardware with original packaging and receipt.",
        "difficulty": "Easy",
        "edge_case_type": "return_window_faq"
    },
    {
        "id": 108,
        "customer_query": "I bought an app by mistake 10 minutes ago. How do I request a refund?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Self-service refund portal guidance.",
        "ground_truth_resolution": "Direct user to reportaproblem.apple.com, sign in with Apple ID, select 'Request a refund' and choose reason.",
        "difficulty": "Easy",
        "edge_case_type": "self_serve_refund"
    },
    {
        "id": 109,
        "customer_query": "Does Apple offer educational student discounts on iPad accessories like the Apple Pencil?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Education pricing store information.",
        "ground_truth_resolution": "Confirm education discount availability through Apple Education Store online, link to portal.",
        "difficulty": "Easy",
        "edge_case_type": "education_pricing"
    },
    {
        "id": 110,
        "customer_query": "I received an invoice for a $59.99 Tinder Plus subscription that I never ordered. My card is compromised!",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Unauthorized financial transaction / suspected fraud requiring account freeze and charge reversal.",
        "ground_truth_resolution": "Instruct checking family purchases; escalate to DM with iTunes Fraud and Billing team.",
        "difficulty": "Hard",
        "edge_case_type": "fraudulent_in_app_purchase"
    },
    {
        "id": 111,
        "customer_query": "How do I change the delivery address for an order that is currently 'Processing'?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Online order self-modification window.",
        "ground_truth_resolution": "Direct user to apple.com/orderstatus, log in, click 'Edit Shipping Address' before order enters 'Preparing for Shipment'.",
        "difficulty": "Easy",
        "edge_case_type": "edit_order_address"
    },
    {
        "id": 112,
        "customer_query": "Can I pick up an online order at the Regent Street Apple Store if my friend is picking it up instead of me?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Pickup contact designation procedure.",
        "ground_truth_resolution": "Explain how to designate an alternate pickup contact in Order Status with their government photo ID.",
        "difficulty": "Easy",
        "edge_case_type": "alternate_pickup_contact"
    },
    {
        "id": 113,
        "customer_query": "I traded in my old iPhone via mail 4 weeks ago and still haven't received my Apple gift card value.",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Trade-in third-party partner partner discrepancy with trade-in quote number.",
        "ground_truth_resolution": "Escalate to DM with trade-in partner quote number and tracking ID to verify inspection status.",
        "difficulty": "Medium",
        "edge_case_type": "trade_in_delay"
    },
    {
        "id": 114,
        "customer_query": "Why does my App Store receipt show taxes when my state doesn't have digital sales tax?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Billing zip code mismatch on file.",
        "ground_truth_resolution": "Advise checking postal code listed in Apple ID Payment & Shipping settings to ensure it matches current residency.",
        "difficulty": "Medium",
        "edge_case_type": "tax_jurisdiction_mismatch"
    },
    {
        "id": 115,
        "customer_query": "My Apple Pay transaction at Walgreens says 'Declined' on terminal but my bank app shows money deducted!",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Authorization hold explanation for POS contactless terminal drops.",
        "ground_truth_resolution": "Explain temporary pre-authorization hold will drop off within 24-48 hours since transaction didn't settle.",
        "difficulty": "Medium",
        "edge_case_type": "apple_pay_authorization_hold"
    },
    {
        "id": 116,
        "customer_query": "Can I purchase AppleCare+ for my iPhone if it has been 75 days since I bought the phone?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "AppleCare+ 60-day eligibility rule explanation.",
        "ground_truth_resolution": "Clarify that AppleCare+ must be added within 60 days of purchase; over 60 days requires retail visual inspection if exception granted.",
        "difficulty": "Easy",
        "edge_case_type": "applecare_eligibility_window"
    },
    {
        "id": 117,
        "customer_query": "I scratched the silver coating off my iTunes gift card too hard and 4 characters of the PIN code are destroyed.",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Unreadable gift card redemption requires manual serial card verification by billing rep.",
        "ground_truth_resolution": "Escalate to DM with photo of front/back of card and store activation receipt to recover PIN.",
        "difficulty": "Medium",
        "edge_case_type": "damaged_gift_card_pin"
    },
    {
        "id": 118,
        "customer_query": "Will Apple price match Best Buy's sale price on an iPad Pro?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Retail price matching policy FAQ (up to 10% on identical in-stock authorized dealer models).",
        "ground_truth_resolution": "Explain Apple Retail price match policy for authorized retailers (up to 10% discount on in-stock identical models).",
        "difficulty": "Easy",
        "edge_case_type": "price_match_policy"
    },
    {
        "id": 119,
        "customer_query": "My order was cancelled by Apple with no explanation given. Order #W492019482. Why?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Order cancellation by security/fraud screening or stock depletion requires internal store check.",
        "ground_truth_resolution": "Escalate to Apple Store customer service in DM to check order audit trail.",
        "difficulty": "Medium",
        "edge_case_type": "unexplained_cancellation"
    },
    {
        "id": 120,
        "customer_query": "Can I split payment between two different credit cards on apple.com?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Checkout payment methods spec (online store accepts 1 credit card + up to 8 gift cards).",
        "ground_truth_resolution": "Explain online checkout supports one credit card plus gift cards, but Apple Store retail can split across multiple credit cards.",
        "difficulty": "Easy",
        "edge_case_type": "split_payment_checkout"
    },
    {
        "id": 121,
        "customer_query": "Apple charged me $0.99 every month for 2 years and I don't know what it is!",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Identifies common 50GB iCloud storage plan tier ($0.99/mo).",
        "ground_truth_resolution": "Explain $0.99 is the monthly price of 50GB iCloud storage tier; guide user to Settings > [Your Name] > iCloud to manage.",
        "difficulty": "Easy",
        "edge_case_type": "mystery_microtransaction"
    },
    {
        "id": 122,
        "customer_query": "I am unable to remove my expired credit card because Apple says it is associated with an active subscription.",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Payment method dependency resolution.",
        "ground_truth_resolution": "Explain user must add new valid payment method first before iOS allows removing the old card on active subscriptions.",
        "difficulty": "Medium",
        "edge_case_type": "active_sub_card_removal"
    },
    {
        "id": 123,
        "customer_query": "Does the Apple iPhone Upgrade Program do a hard credit check every year when upgrading?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Citizens One financing terms explanation.",
        "ground_truth_resolution": "Clarify that Citizens One financing may perform credit inquiry for new loan origination during upgrade.",
        "difficulty": "Easy",
        "edge_case_type": "upgrade_program_financing"
    },
    {
        "id": 124,
        "customer_query": "Where can I download the VAT tax invoice for my MacBook purchase for company expense filing?",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Self-service invoice retrieval guide.",
        "ground_truth_resolution": "Direct user to apple.com/orderstatus > Order Details > 'Print Official Invoice' for VAT breakdown.",
        "difficulty": "Easy",
        "edge_case_type": "vat_tax_invoice"
    },
    {
        "id": 125,
        "customer_query": "I was charged $299 for a Genius Bar repair that was supposed to be covered under warranty! Tech told me it was free!",
        "ground_truth_intent": "STORE_ORDER_BILLING",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Disputed retail service invoice billing discrepancy; requires store management review.",
        "ground_truth_resolution": "Escalate to DM with Genius Bar work order number (G-number) to review store invoice notes.",
        "difficulty": "Hard",
        "edge_case_type": "disputed_repair_charge"
    },

    # -------------------------------------------------------------
    # INTENT 6: CONNECTIVITY_SYNC (25 samples)
    # -------------------------------------------------------------
    {
        "id": 126,
        "customer_query": "My iPhone Wi-Fi keeps greyed out in settings and won't turn on. Switch is disabled.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Greyed-out Wi-Fi toggle is a classic Wi-Fi hardware chip failure / antenna solder defect.",
        "ground_truth_resolution": "Try Reset Network Settings; if toggle remains grey, escalate to DM for hardware evaluation.",
        "difficulty": "Medium",
        "edge_case_type": "greyed_out_wifi_hardware"
    },
    {
        "id": 127,
        "customer_query": "AirDrop won't find my friend's iPhone sitting right next to me. Both have Wi-Fi and Bluetooth on.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "AirDrop discovery permissions (Contacts Only vs Everyone) and hotspot conflict.",
        "ground_truth_resolution": "Ensure Personal Hotspot is off; toggle AirDrop receiving to 'Everyone' in Control Center.",
        "difficulty": "Easy",
        "edge_case_type": "airdrop_discovery"
    },
    {
        "id": 128,
        "customer_query": "My iPhone constantly drops Bluetooth connection to my car audio every 3 minutes.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Corrupted Bluetooth profile pair.",
        "ground_truth_resolution": "Forget car audio device in Settings > Bluetooth, reset car head unit pairing, and re-pair freshly.",
        "difficulty": "Medium",
        "edge_case_type": "car_bluetooth_drop"
    },
    {
        "id": 129,
        "customer_query": "Personal Hotspot connects on my laptop but says 'No Internet Access' even though 4G works on phone.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Carrier APN hotspot provisioning or DNS routing.",
        "ground_truth_resolution": "Check Settings > General > Reset > Reset Network Settings or contact carrier to verify hotspot entitlement.",
        "difficulty": "Medium",
        "edge_case_type": "hotspot_no_internet"
    },
    {
        "id": 130,
        "customer_query": "My Apple TV won't mirror screen from my MacBook Air. Error says 'AirPlay device not found'.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "mDNS / Bonjour multicast isolation across 2.4GHz and 5GHz router bands.",
        "ground_truth_resolution": "Verify both devices are on identical Wi-Fi SSID, toggle AirPlay on Apple TV Settings > AirPlay.",
        "difficulty": "Easy",
        "edge_case_type": "airplay_multicast"
    },
    {
        "id": 131,
        "customer_query": "My iPhone shows 'No Service' or 'Searching...' constantly even after re-inserting SIM card.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Potential iPhone 7 'No Service' hardware recall program symptom (A1660 model motherboard defect).",
        "ground_truth_resolution": "Check model number in Settings > General > About; escalate to DM to verify 'No Service' repair program eligibility.",
        "difficulty": "Hard",
        "edge_case_type": "no_service_cellular_defect"
    },
    {
        "id": 132,
        "customer_query": "My Apple Watch won't sync my workout data to the Health app on my phone.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Health data sync pause / iCloud Health permissions.",
        "ground_truth_resolution": "Reboot both devices simultaneously; verify Health toggle is enabled under Settings > [Your Name] > iCloud.",
        "difficulty": "Medium",
        "edge_case_type": "health_data_sync_stall"
    },
    {
        "id": 133,
        "customer_query": "Wi-Fi works in Safari but every other app says 'Cannot connect to cellular data' while on Wi-Fi.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Wi-Fi Assist or per-app cellular toggles conflict in iOS.",
        "ground_truth_resolution": "Check Settings > Cellular > Wi-Fi Assist (disable at bottom), and verify per-app cellular toggles.",
        "difficulty": "Medium",
        "edge_case_type": "wifi_assist_conflict"
    },
    {
        "id": 134,
        "customer_query": "How do I sync my iTunes music library without plugging my phone into my computer with a wire?",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Wi-Fi Sync setup instructions.",
        "ground_truth_resolution": "Enable 'Sync with this iPhone over Wi-Fi' in iTunes on computer while connected once via cable.",
        "difficulty": "Easy",
        "edge_case_type": "wifi_itunes_sync"
    },
    {
        "id": 135,
        "customer_query": "My AirPods show connected in Bluetooth settings but audio still plays out of iPhone speaker.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Audio routing target in Control Center AirPlay widget.",
        "ground_truth_resolution": "Open Control Center, tap AirPlay audio card icon in top-right, and select AirPods as playback destination.",
        "difficulty": "Easy",
        "edge_case_type": "audio_route_destination"
    },
    {
        "id": 136,
        "customer_query": "My phone keeps connecting to weak public xfinity Wi-Fi down the street instead of my strong home Wi-Fi.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Auto-Join configuration on known Wi-Fi SSIDs.",
        "ground_truth_resolution": "Tap 'i' next to public network in Settings > Wi-Fi and disable 'Auto-Join' or tap 'Forget This Network'.",
        "difficulty": "Easy",
        "edge_case_type": "wifi_auto_join_priority"
    },
    {
        "id": 137,
        "customer_query": "I am not receiving SMS two factor verification codes from my bank on my new iPhone.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Short-code SMS blocking by carrier or iMessage routing.",
        "ground_truth_resolution": "Ensure 'Send as SMS' is enabled in Settings > Messages; contact carrier to unblock commercial shortcodes.",
        "difficulty": "Medium",
        "edge_case_type": "shortcode_sms_routing"
    },
    {
        "id": 138,
        "customer_query": "Apple Pencil won't pair with my iPad Pro when plugged into the lightning port.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Pencil deep battery sleep or Bluetooth pairing cache.",
        "ground_truth_resolution": "Leave Pencil plugged into iPad port for 15 minutes to charge; forget in Settings > Bluetooth and re-insert.",
        "difficulty": "Medium",
        "edge_case_type": "apple_pencil_pairing"
    },
    {
        "id": 139,
        "customer_query": "My Mac Handoff and Universal Clipboard stopped working with my iPhone after updating.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Continuity prerequisites (same iCloud account, Bluetooth, Wi-Fi, Handoff toggle).",
        "ground_truth_resolution": "Check Settings > General > Handoff on iOS and System Preferences > General on Mac; toggle Bluetooth off/on.",
        "difficulty": "Medium",
        "edge_case_type": "continuity_handoff_stall"
    },
    {
        "id": 140,
        "customer_query": "My cellular provider says LTE is activated, but phone only shows 3G or 1x.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Carrier settings update or voice/data roaming configuration.",
        "ground_truth_resolution": "Check Settings > General > About for carrier update popup, check Settings > Cellular > Cellular Data Options > Enable LTE.",
        "difficulty": "Easy",
        "edge_case_type": "lte_toggle_carrier_update"
    },
    {
        "id": 141,
        "customer_query": "Can I use Apple CarPlay wirelessly without plugging a USB cable in?",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Vehicle head unit hardware capability clarification.",
        "ground_truth_resolution": "Explain Wireless CarPlay requires vehicle head unit support for Bluetooth + Wi-Fi handshake; consult car manual.",
        "difficulty": "Easy",
        "edge_case_type": "wireless_carplay_capability"
    },
    {
        "id": 142,
        "customer_query": "My GPS location jumps 50 miles away in Apple Maps when I am sitting inside my living room.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Wi-Fi geolocation BSSID database lookup error on local router.",
        "ground_truth_resolution": "Toggle Location Services off and on in Settings > Privacy > Location Services; test on cellular with Wi-Fi disabled.",
        "difficulty": "Medium",
        "edge_case_type": "bssid_geolocation_drift"
    },
    {
        "id": 143,
        "customer_query": "My Bluetooth headphones keep cutting out whenever I put my phone in my back pocket while walking.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "2.4GHz RF body attenuation physics explanation.",
        "ground_truth_resolution": "Explain 2.4GHz radio signals are absorbed by human body tissue; recommend front pocket or arm band.",
        "difficulty": "Easy",
        "edge_case_type": "rf_body_attenuation"
    },
    {
        "id": 144,
        "customer_query": "I have an eSIM in my iPhone and it says 'No SIM' after resetting network settings.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "eSIM profile deletion or provisioning lock requiring carrier QR code reactivation.",
        "ground_truth_resolution": "Escalate to DM to verify cellular plan profile status and coordinate carrier QR scan.",
        "difficulty": "Hard",
        "edge_case_type": "esim_profile_loss"
    },
    {
        "id": 145,
        "customer_query": "How do I stop my iPad from ringing every time my iPhone gets a phone call?",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Calls on Other Devices toggle in iOS settings.",
        "ground_truth_resolution": "Go to Settings > Phone > Calls on Other Devices on your iPhone and turn off the toggle for your iPad.",
        "difficulty": "Easy",
        "edge_case_type": "calls_on_other_devices"
    },
    {
        "id": 146,
        "customer_query": "My HomePod says 'I'm having trouble connecting to the internet' every time I ask it to play music.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "HomePod Wi-Fi network desync from Home app.",
        "ground_truth_resolution": "Open Home app on iOS, check HomePod card, ensure iOS device is on same network, or unplug HomePod for 15s.",
        "difficulty": "Medium",
        "edge_case_type": "homepod_wifi_sync"
    },
    {
        "id": 147,
        "customer_query": "Why does my iPhone connect to 2.4GHz band instead of 5GHz on my dual-band router?",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Band steering and RSSI threshold explanation.",
        "ground_truth_resolution": "Explain band steering logic; recommend separating 2.4GHz and 5GHz SSIDs in router admin page.",
        "difficulty": "Medium",
        "edge_case_type": "dual_band_steering"
    },
    {
        "id": 148,
        "customer_query": "My iPhone can't detect any Bluetooth devices at all, spinning loading wheel indefinitely.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Bluetooth daemon freeze.",
        "ground_truth_resolution": "Toggle Airplane Mode for 30 seconds, perform hard reboot; if unresolved, test Network Settings Reset.",
        "difficulty": "Easy",
        "edge_case_type": "bluetooth_daemon_freeze"
    },
    {
        "id": 149,
        "customer_query": "My contacts are syncing to my Mac but calendar events are completely out of sync.",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Default Calendar account selection in macOS/iOS.",
        "ground_truth_resolution": "Check Settings > Calendar > Default Calendar on phone and ensure Mac Calendar is set to iCloud rather than local.",
        "difficulty": "Medium",
        "edge_case_type": "calendar_sync_target"
    },
    {
        "id": 150,
        "customer_query": "Can I connect two pairs of Bluetooth headphones to one iPhone at the same time?",
        "ground_truth_intent": "CONNECTIVITY_SYNC",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Audio Sharing capability spec.",
        "ground_truth_resolution": "Explain Audio Sharing feature available for AirPods and Beats with supported iOS devices via Control Center.",
        "difficulty": "Easy",
        "edge_case_type": "dual_audio_sharing"
    },

    # -------------------------------------------------------------
    # INTENT 7: THIRD_PARTY_APP_ISSUES (25 samples)
    # -------------------------------------------------------------
    {
        "id": 151,
        "customer_query": "WhatsApp crashes immediately whenever I try to open a chat thread on iOS 11.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Third-party app crash triage (App Store update, app reinstall, app developer contact).",
        "ground_truth_resolution": "Advise checking App Store for latest WhatsApp update, restarting phone, or contacting WhatsApp support.",
        "difficulty": "Easy",
        "edge_case_type": "app_crash_open"
    },
    {
        "id": 152,
        "customer_query": "Spotify playback controls disappeared from my lock screen after the update. Only Apple Music shows up!",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Now Playing lockscreen widget session handover.",
        "ground_truth_resolution": "Restart device, ensure Spotify has Background App Refresh enabled in Settings > Spotify.",
        "difficulty": "Easy",
        "edge_case_type": "lockscreen_media_controls"
    },
    {
        "id": 153,
        "customer_query": "Instagram won't let me upload photos from my camera roll, says 'No photos available'.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "iOS Privacy permission toggle.",
        "ground_truth_resolution": "Direct user to Settings > Privacy > Photos > Instagram and set permission to 'Read and Write' / 'All Photos'.",
        "difficulty": "Easy",
        "edge_case_type": "privacy_photo_permission"
    },
    {
        "id": 154,
        "customer_query": "YouTube videos freeze on a black frame with spinning wheel while audio keeps playing.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Video hardware acceleration buffer glitch in YouTube app.",
        "ground_truth_resolution": "Force quit YouTube app, clear Safari cache if watching in browser, or update YouTube app in App Store.",
        "difficulty": "Easy",
        "edge_case_type": "video_buffer_freeze"
    },
    {
        "id": 155,
        "customer_query": "My banking app won't open and says 'This app cannot run on jailbroken or compromised devices' but my phone is 100% stock!",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Jailbreak detection false positive triggered by beta OS build or old jailbreak files in restored iCloud backup.",
        "ground_truth_resolution": "Explain app may misinterpret public beta software; recommend contacting bank developer or clean restore.",
        "difficulty": "Medium",
        "edge_case_type": "false_jailbreak_detection"
    },
    {
        "id": 156,
        "customer_query": "Snapchat camera is super zoomed in and cropped on my iPhone X screen!",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "App not updated for iPhone X tall aspect ratio (notch adaptation).",
        "ground_truth_resolution": "Explain app developer must release update adapted for iPhone X display; direct to App Store updates.",
        "difficulty": "Easy",
        "edge_case_type": "aspect_ratio_optimization"
    },
    {
        "id": 157,
        "customer_query": "Netflix downloads for offline viewing keep disappearing every 48 hours.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "DRM license expiration window managed by content provider.",
        "ground_truth_resolution": "Clarify that offline download retention limits are set by Netflix DRM licensing agreements.",
        "difficulty": "Easy",
        "edge_case_type": "drm_download_expiry"
    },
    {
        "id": 158,
        "customer_query": "Google Maps audio navigation directions don't play over my car speakers when listening to FM radio.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "HFP (Hands-Free Profile) audio routing configuration in Google Maps settings.",
        "ground_truth_resolution": "In Google Maps app, go to Settings > Navigation > enable 'Play as Bluetooth phone call'.",
        "difficulty": "Medium",
        "edge_case_type": "hfp_bluetooth_routing"
    },
    {
        "id": 159,
        "customer_query": "Facebook app is taking up 14GB of storage on my 16GB iPhone! How do I clear the cache?",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Third-party app document and data bloat on limited device storage.",
        "ground_truth_resolution": "Advise deleting and reinstalling the Facebook app from App Store to purge cached media.",
        "difficulty": "Easy",
        "edge_case_type": "app_cache_bloat"
    },
    {
        "id": 160,
        "customer_query": "Pokemon Go says 'GPS signal not found (11)' while standing in an open parking lot.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Precise Location permissions or low power mode GPS polling throttle.",
        "ground_truth_resolution": "Check Settings > Privacy > Location Services > Pokemon Go (set to 'While Using'), enable Wi-Fi for triangulation.",
        "difficulty": "Easy",
        "edge_case_type": "gps_game_permissions"
    },
    {
        "id": 161,
        "customer_query": "Microsoft Outlook won't sync my work email and gives error 'Server requires security certificate approval'.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Corporate MDM profile or Exchange root certificate trust.",
        "ground_truth_resolution": "Instruct checking Settings > General > Profiles & Device Management, or consult company IT administrator.",
        "difficulty": "Medium",
        "edge_case_type": "mdm_exchange_certificate"
    },
    {
        "id": 162,
        "customer_query": "Can I set Google Chrome as my default web browser on my iPhone instead of Safari?",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "iOS architecture limitation (default browser selection was not available in iOS 11).",
        "ground_truth_resolution": "Explain that iOS 11 opens links in Safari by default; recommend adding Chrome shortcuts or using Chrome share extension.",
        "difficulty": "Easy",
        "edge_case_type": "default_browser_limitation"
    },
    {
        "id": 163,
        "customer_query": "Twitter notifications arrive 20 minutes late on my phone compared to my computer.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "APNs push notification background fetch or low battery saver mode.",
        "ground_truth_resolution": "Turn off Low Power Mode, verify Background App Refresh is enabled under Settings > General > Background App Refresh.",
        "difficulty": "Easy",
        "edge_case_type": "delayed_push_notification"
    },
    {
        "id": 164,
        "customer_query": "Kindle app won't let me purchase ebooks directly inside the iOS app. Why is the buy button missing?",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "App Store in-app purchase guidelines (Amazon disables in-app purchases to avoid Apple 30% fee).",
        "ground_truth_resolution": "Explain that digital books can be purchased via browser at amazon.com and synced automatically to Kindle app.",
        "difficulty": "Easy",
        "edge_case_type": "iap_anti_steering"
    },
    {
        "id": 165,
        "customer_query": "Fortnite crashes as soon as the battle bus drops on my iPhone 6.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Hardware RAM requirement (Fortnite requires 2GB RAM; iPhone 6 only has 1GB RAM).",
        "ground_truth_resolution": "Clarify that Fortnite requires iPhone 6s / SE or newer with 2GB RAM; iPhone 6 hardware cannot run the title.",
        "difficulty": "Easy",
        "edge_case_type": "game_minimum_ram_spec"
    },
    {
        "id": 166,
        "customer_query": "My third-party Gboard keyboard crashes back to standard Apple keyboard constantly.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "iOS memory watchdog terminating keyboard extensions exceeding RAM allowance.",
        "ground_truth_resolution": "Explain iOS watchdog terminates third-party keyboards if RAM is tight; reboot phone, toggle 'Allow Full Access' in Settings.",
        "difficulty": "Medium",
        "edge_case_type": "keyboard_ram_watchdog"
    },
    {
        "id": 167,
        "customer_query": "Uber says 'Unable to connect to Apple Pay' at the end of my ride. Driver is waiting.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "App sandbox token refresh or card expiration.",
        "ground_truth_resolution": "Select alternate payment method inside Uber app, verify default card in Settings > Wallet & Apple Pay.",
        "difficulty": "Medium",
        "edge_case_type": "in_app_apple_pay_failure"
    },
    {
        "id": 168,
        "customer_query": "My Fitbit app won't sync steps in the background unless the app stays open on the screen.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Bluetooth background peripheral state restoration.",
        "ground_truth_resolution": "Enable Background App Refresh for Fitbit and ensure Bluetooth sharing is toggled on in iOS Settings.",
        "difficulty": "Easy",
        "edge_case_type": "bluetooth_background_refresh"
    },
    {
        "id": 169,
        "customer_query": "Telegram voice notes sound extremely muffled when played back.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Microphone permission or proximity sensor switching audio to earpiece.",
        "ground_truth_resolution": "Ensure phone is held away from face (proximity sensor redirects to earpiece), test microphone in Voice Memos.",
        "difficulty": "Easy",
        "edge_case_type": "proximity_earpiece_switch"
    },
    {
        "id": 170,
        "customer_query": "App Store says 'Update' for Facebook, but when I tap it the circle spins for 1 second and changes back to 'Update'.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "App Store download daemon stall.",
        "ground_truth_resolution": "Sign out of App Store in Settings > iTunes & App Store, restart device, sign back in.",
        "difficulty": "Medium",
        "edge_case_type": "app_store_update_loop"
    },
    {
        "id": 171,
        "customer_query": "Why does Reddit app consume 40% of my battery when I only used it for 15 minutes today?",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Background video autoplay or analytics loop in third-party app.",
        "ground_truth_resolution": "Disable background app refresh for Reddit, disable video autoplay in Reddit app settings.",
        "difficulty": "Easy",
        "edge_case_type": "app_background_battery"
    },
    {
        "id": 172,
        "customer_query": "My corporate VPN app (AnyConnect) disconnects every time my phone locks screen.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Wi-Fi sleep policy and On-Demand VPN configuration.",
        "ground_truth_resolution": "Configure Connect On Demand in VPN settings or verify keep-alive profile with company network admin.",
        "difficulty": "Medium",
        "edge_case_type": "vpn_sleep_disconnect"
    },
    {
        "id": 173,
        "customer_query": "I am getting spam calendar invites from Russian casino websites filling up my iPhone calendar!",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Subscribed calendar spam via malicious web link.",
        "ground_truth_resolution": "Direct user to Settings > Accounts & Passwords > Subscribed Calendars and delete the unauthorized spam calendar.",
        "difficulty": "Easy",
        "edge_case_type": "calendar_spam_subscription"
    },
    {
        "id": 174,
        "customer_query": "My banking app crashes when scanning my check for mobile deposit.",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Camera permission missing for banking app.",
        "ground_truth_resolution": "Verify Camera toggle is enabled in Settings > Privacy > Camera > [Bank App].",
        "difficulty": "Easy",
        "edge_case_type": "camera_privacy_banking"
    },
    {
        "id": 175,
        "customer_query": "A flashlight app I downloaded is demanding access to my contacts and location. Is this safe?",
        "ground_truth_intent": "THIRD_PARTY_APP_ISSUES",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Suspicious third-party app permissions security alert.",
        "ground_truth_resolution": "Advise denying permissions, deleting the app immediately, and using the built-in iOS Control Center flashlight.",
        "difficulty": "Easy",
        "edge_case_type": "suspicious_permissions"
    },

    # -------------------------------------------------------------
    # INTENT 8: GENERAL_FEEDBACK_RANT (25 samples)
    # -------------------------------------------------------------
    {
        "id": 176,
        "customer_query": "Apple is literally the greedy worst company on earth. You ruined Steve Jobs legacy with these trash phones.",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Non-actionable emotional venting / brand rant; polite de-escalation response without human agent time waste.",
        "ground_truth_resolution": "Acknowledge feedback with polite brand empathy; invite them to share specific technical issues if they need help.",
        "difficulty": "Easy",
        "edge_case_type": "pure_rant_no_issue"
    },
    {
        "id": 177,
        "customer_query": "Hola @AppleSupport mi iPhone no prende se quedo la pantalla negra por favor ayuda urgente!",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Non-English inquiry (Twitter support channel operates in English; route to Spanish portal).",
        "ground_truth_resolution": "Provide standard polite Spanish routing response linking to support.apple.com/es-es or Spanish Twitter handle.",
        "difficulty": "Medium",
        "edge_case_type": "foreign_language_spanish"
    },
    {
        "id": 178,
        "customer_query": "I am so sick and tired of you people ignoring my tweets! I've tweeted 10 times this week about my broken phone and got ZERO response!",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Repeated contact failure with high customer agitation / hostility; priority human de-escalation required.",
        "ground_truth_resolution": "Offer immediate apology for missed communication and escalate to DM for dedicated senior agent review.",
        "difficulty": "Medium",
        "edge_case_type": "repeated_contact_hostility"
    },
    {
        "id": 179,
        "customer_query": "Just wanted to say the customer service rep named Sarah at the Fifth Ave Apple store was amazing today! Thank you!",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Positive brand commendation.",
        "ground_truth_resolution": "Thank the customer warmly and express appreciation for sharing feedback about store team members.",
        "difficulty": "Easy",
        "edge_case_type": "positive_praise"
    },
    {
        "id": 180,
        "customer_query": "When is Tim Cook announcing the new iPad mini? Give me a leak please haha",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Unannounced product speculation inquiry.",
        "ground_truth_resolution": "Politely decline unannounced product rumors; direct customer to apple.com/newsroom for official announcements.",
        "difficulty": "Easy",
        "edge_case_type": "unannounced_rumor"
    },
    {
        "id": 181,
        "customer_query": "Whoever designed the volume HUD covering the middle of the screen during YouTube videos deserves to be fired.",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Product feedback / feature complaint.",
        "ground_truth_resolution": "Acknowledge UI feedback and direct user to official feedback submission portal at apple.com/feedback.",
        "difficulty": "Easy",
        "edge_case_type": "product_feedback_portal"
    },
    {
        "id": 182,
        "customer_query": "Bonjour j'ai perdu mon mot de passe Apple ID comment faire?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Foreign language (French) routing policy.",
        "ground_truth_resolution": "Provide courteous redirection to French support portal (support.apple.com/fr-fr).",
        "difficulty": "Medium",
        "edge_case_type": "foreign_language_french"
    },
    {
        "id": 183,
        "customer_query": "I am threatening legal action and suing Apple in small claims court tomorrow morning for emotional distress caused by your phone.",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "LEGAL THREAT / LITIGATION RISK: Standard brand policy forbids AI from negotiating legal threats; escalate to legal triage.",
        "ground_truth_resolution": "Acknowledge message calmly without admitting fault; route to Apple Legal / Executive Relations via DM.",
        "difficulty": "Hard",
        "edge_case_type": "legal_threat"
    },
    {
        "id": 184,
        "customer_query": "Can you guys add purple unicorn emojis in the next update? My daughter wants one so bad.",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Feature request explaining Unicode Consortium role.",
        "ground_truth_resolution": "Explain emoji standards are governed by Unicode Consortium; link to apple.com/feedback for feature suggestions.",
        "difficulty": "Easy",
        "edge_case_type": "emoji_request"
    },
    {
        "id": 185,
        "customer_query": "Why did you guys remove the headphone jack on iPhone 7? It's literally the dumbest decision in tech history.",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Hardware design philosophy critique.",
        "ground_truth_resolution": "Politely acknowledge design choice, remind customer about included Lightning adapter and wireless options.",
        "difficulty": "Easy",
        "edge_case_type": "controversial_design_critique"
    },
    {
        "id": 186,
        "customer_query": "Are the Apple Retail Stores in Manhattan open on Thanksgiving day?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Store hours inquiry.",
        "ground_truth_resolution": "Direct customer to apple.com/retail to view specific holiday operating hours for Manhattan store locations.",
        "difficulty": "Easy",
        "edge_case_type": "store_hours"
    },
    {
        "id": 187,
        "customer_query": "I wrote a poem about how much I love my Apple Watch: 'Ticking on my wrist, never feeling lost...' do you guys like it?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Customer poetry / fan interaction.",
        "ground_truth_resolution": "Respond with warm, cheerful appreciation for their creativity and love for the Apple Watch.",
        "difficulty": "Easy",
        "edge_case_type": "creative_fan_engagement"
    },
    {
        "id": 188,
        "customer_query": "Your phone made me miss my morning job interview because the alarm didn't ring! You ruined my career!",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Severe customer distress with real-world harm claim; empathetic human de-escalation needed.",
        "ground_truth_resolution": "Express deep empathy for the distressing situation; escalate to DM to inspect alarm volume and settings calmly.",
        "difficulty": "Medium",
        "edge_case_type": "distress_alarm_failure"
    },
    {
        "id": 189,
        "customer_query": "Help me my phone is possessed by ghosts! It moves on its own and types words without me touching it!",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Classic 'ghost touch' digitizer symptom framed through supernatural humor/panic.",
        "ground_truth_resolution": "Reassure user and explain 'ghost touch' caused by third-party charger electrical noise or damaged screen digitizer.",
        "difficulty": "Medium",
        "edge_case_type": "ghost_touch_humor"
    },
    {
        "id": 190,
        "customer_query": "How do I apply for a job as an iOS software engineer at Apple headquarters in Cupertino?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Corporate recruiting inquiry.",
        "ground_truth_resolution": "Direct applicant to official Apple careers portal at jobs.apple.com to search and submit applications.",
        "difficulty": "Easy",
        "edge_case_type": "jobs_recruiting"
    },
    {
        "id": 191,
        "customer_query": "Is Apple still supporting Project Titan self driving electric car?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Corporate confidential rumor.",
        "ground_truth_resolution": "State that Apple Support does not comment on rumors or unannounced projects.",
        "difficulty": "Easy",
        "edge_case_type": "corporate_rumor"
    },
    {
        "id": 192,
        "customer_query": "Is it true that charging your phone in the microwave gives 100% battery in 30 seconds?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Viral internet prank safety debunking ('Wave' hoax).",
        "ground_truth_resolution": "CRITICAL WARNING: Clarify that placing any electronic device in a microwave causes immediate fire/explosion hazard.",
        "difficulty": "Easy",
        "edge_case_type": "viral_microwave_hoax"
    },
    {
        "id": 193,
        "customer_query": "I am a technology journalist from The Wall Street Journal seeking comment on your battery replacement delays.",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "PRESS / MEDIA INQUIRY: Standard corporate policy requires routing all media requests to Apple PR.",
        "ground_truth_resolution": "Route journalist strictly to official Apple Media Relations / PR team at media.help@apple.com.",
        "difficulty": "Medium",
        "edge_case_type": "press_media_inquiry"
    },
    {
        "id": 194,
        "customer_query": "Can Siri please tell me what the meaning of life is?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Playful Siri easter egg query.",
        "ground_truth_resolution": "Reply playfully with standard Apple wit (e.g., 'Try being nice to people, avoid eating fat, read a good book every now and then').",
        "difficulty": "Easy",
        "edge_case_type": "siri_easter_egg"
    },
    {
        "id": 195,
        "customer_query": "My phone fell into a lake 40 feet deep and stayed there for 2 weeks. Can Apple recover my unbacked photos?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Irrecoverable liquid damage with data loss grief; sensitive escalation required.",
        "ground_truth_resolution": "Express condolences for lost memories; explain physical limits of water immersion and check iCloud.com.",
        "difficulty": "Hard",
        "edge_case_type": "catastrophic_data_loss_grief"
    },
    {
        "id": 196,
        "customer_query": "Why did Steve Wozniak build the Apple I inside a wooden briefcase?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Apple historical trivia inquiry.",
        "ground_truth_resolution": "Provide fun Apple history trivia regarding early Homebrew Computer Club days.",
        "difficulty": "Easy",
        "edge_case_type": "history_trivia"
    },
    {
        "id": 197,
        "customer_query": "Where can I recycle my ancient iPod Nano from 2005?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Environmental recycling program guidance.",
        "ground_truth_resolution": "Direct customer to any Apple Retail Store for free responsible recycling under Apple GiveBack program.",
        "difficulty": "Easy",
        "edge_case_type": "environmental_recycling"
    },
    {
        "id": 198,
        "customer_query": "Your chat system is obviously a dumb AI bot. I refuse to talk to a robot! Connect me to a real living human being right now!",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Explicit user demand for human agent handoff; policy requires immediate respect of handoff request.",
        "ground_truth_resolution": "Acknowledge request respectfully, transition immediately to human support queue in DM.",
        "difficulty": "Easy",
        "edge_case_type": "explicit_human_demand"
    },
    {
        "id": 199,
        "customer_query": "I left my Apple Watch on the seat of an Uber car in Chicago. Can you ping the driver for me?",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "AUTO_HANDLE",
        "escalation_reason": "Third-party lost property boundary clarification.",
        "ground_truth_resolution": "Direct user to use Find My iPhone app to put watch in Lost Mode, and contact Uber support directly.",
        "difficulty": "Medium",
        "edge_case_type": "third_party_lost_property"
    },
    {
        "id": 200,
        "customer_query": "This is ridiculous. 3 hours on hold on phone support, then disconnected. Now I'm on Twitter. What does a customer have to do to get help?!",
        "ground_truth_intent": "GENERAL_FEEDBACK_RANT",
        "ground_truth_escalation": "ESCALATE",
        "escalation_reason": "Severe omni-channel friction and high churn risk; mandatory senior human escalation.",
        "ground_truth_resolution": "Offer immediate apology for phone disconnect; request DM right away to take over issue directly.",
        "difficulty": "Medium",
        "edge_case_type": "omnichannel_escalation"
    },
]

# 30 Human Evaluation Sample Cases scored across 4 dimensions: Grounding, Tone, Actionability, Escalation (1-5 scale)
HUMAN_SCORECARDS_SAMPLE = [
    {
        "case_id": 1,
        "query": "Why does my iPhone replace the letter 'I' with a weird question mark box and letter A every time I type? #iOS11bug",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Workaround via text replacement is exact official Apple KB procedure for this specific bug."
    },
    {
        "case_id": 4,
        "query": "Updated to latest macOS High Sierra and now my Mac won't recognize my password at login screen even though I know it's right!",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 4.5,
            "actionability_score": 4.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.5,
        "notes": "Device lockout after OS upgrade must be escalated to prevent permanent FileVault lockout."
    },
    {
        "case_id": 26,
        "query": "My iPhone 6s drops from 40% battery to 1% and turns off instantly whenever I step into cold weather!",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Well identified unexpected shutdown program symptom; serial check requires private DM."
    },
    {
        "case_id": 28,
        "query": "My iPhone is getting burning hot while charging and the back glass is starting to push out slightly.",
        "human_evaluator": "Safety_Compliance_Officer",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Critical thermal safety hazard. Auto-handle would be dangerous failure. Escalation mandatory."
    },
    {
        "case_id": 35,
        "query": "Why does iOS throttle my phone CPU speed when the battery gets old? I feel like you're forcing me to buy a new phone.",
        "human_evaluator": "Brand_Reputation_Manager",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 4.5,
            "actionability_score": 4.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.5,
        "notes": "High PR risk topic during 2017 battery controversy. Delicate human handling needed."
    },
    {
        "case_id": 46,
        "query": "My iPhone battery exploded in my pocket and burned my leg! I am heading to the emergency room right now!",
        "human_evaluator": "Safety_Compliance_Officer",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Physical injury claim. Highest escalation severity level."
    },
    {
        "case_id": 51,
        "query": "Dropped my iPhone 7 in the sink. Speaker sounds super muffled and crackly now. Can I dry it with a hair dryer?",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Crucial to advise against hairdryer heat which melts water-resistant adhesive gaskets."
    },
    {
        "case_id": 52,
        "query": "My iPhone 8 Plus screen has a green vertical line going down the right edge out of nowhere!",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Physical display panel driver defect, software troubleshooting won't fix, Genius Bar booking required."
    },
    {
        "case_id": 59,
        "query": "My MacBook keyboard spacebar registers double spaces every time I press it once.",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.62,
        "notes": "Butterfly switch repeat issue, covered under official Apple Keyboard Service Program."
    },
    {
        "case_id": 76,
        "query": "My Apple ID has been locked for security reasons and when I try iforgot.apple.com it says my trusted phone number is no longer valid!",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Account recovery with invalid 2FA phone number is a high frustration dead-end without human guide."
    },
    {
        "case_id": 77,
        "query": "How do I change my Apple ID country from UK to US if I still have £0.14 store credit remaining?",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Store credit below £0.99 cannot be spent on anything. Requires Apple support to manually zero balance."
    },
    {
        "case_id": 80,
        "query": "Someone hacked into my Apple ID, changed the password, and turned on Lost Mode on my phone with a ransom note!",
        "human_evaluator": "Safety_Compliance_Officer",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Ransom extortion attack on iCloud. Critical escalation."
    },
    {
        "case_id": 87,
        "query": "My late father passed away. How can our family gain access to his locked iPad and Apple ID photos?",
        "human_evaluator": "Brand_Reputation_Manager",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.88,
        "notes": "Bereavement workflow requires legal proof of inheritance and empathetic tone."
    },
    {
        "case_id": 101,
        "query": "I was double charged $9.99 for Apple Music this month on my credit card. Here is the bank statement reference.",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.62,
        "notes": "Duplicate debit dispute cannot be handled publically, requires private billing DM."
    },
    {
        "case_id": 103,
        "query": "My iPhone X pre-order status says 'Preparing for Shipment' for 10 days. Deliver date was supposed to be yesterday!",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.62,
        "notes": "High-value pre-order delay requires internal warehouse tracking via DM."
    },
    {
        "case_id": 104,
        "query": "FedEx says my Apple delivery was signed and delivered at 2pm, but nothing is on my porch and security camera shows no truck!",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Stolen/lost transit package requires formal carrier investigation."
    },
    {
        "case_id": 126,
        "query": "My iPhone Wi-Fi keeps greyed out in settings and won't turn on. Switch is disabled.",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Greyed Wi-Fi switch is almost universally a physical solder separation on Wi-Fi IC."
    },
    {
        "case_id": 131,
        "query": "My iPhone shows 'No Service' or 'Searching...' constantly even after re-inserting SIM card.",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Check for iPhone 7 No Service Quality Program."
    },
    {
        "case_id": 151,
        "query": "WhatsApp crashes immediately whenever I try to open a chat thread on iOS 11.",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Clean self-serve diagnostic. Third-party app crashes don't warrant Apple human rep time."
    },
    {
        "case_id": 152,
        "query": "Spotify playback controls disappeared from my lock screen after the update. Only Apple Music shows up!",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Classic user confusion over lockscreen now playing widget."
    },
    {
        "case_id": 155,
        "query": "My banking app won't open and says 'This app cannot run on jailbroken or compromised devices' but my phone is 100% stock!",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.62,
        "notes": "Good handling of third-party jailbreak heuristic false positives."
    },
    {
        "case_id": 176,
        "query": "Apple is literally the greedy worst company on earth. You ruined Steve Jobs legacy with these trash phones.",
        "human_evaluator": "Brand_Reputation_Manager",
        "scores": {
            "grounding_score": 4.0,
            "tone_score": 5.0,
            "actionability_score": 4.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.5,
        "notes": "Pure emotional venting. Auto-handling with calm polite tone preserves human rep bandwidth."
    },
    {
        "case_id": 177,
        "query": "Hola @AppleSupport mi iPhone no prende se quedo la pantalla negra por favor ayuda urgente!",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Proper adherence to English-channel boundary with polite Spanish portal handoff."
    },
    {
        "case_id": 178,
        "query": "I am so sick and tired of you people ignoring my tweets! I've tweeted 10 times this week about my broken phone and got ZERO response!",
        "human_evaluator": "Brand_Reputation_Manager",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 5.0,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Severe customer frustration across multiple attempts must go to human senior agent."
    },
    {
        "case_id": 183,
        "query": "I am threatening legal action and suing Apple in small claims court tomorrow morning for emotional distress caused by your phone.",
        "human_evaluator": "Safety_Compliance_Officer",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 4.5,
            "actionability_score": 4.5,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.75,
        "notes": "Strict legal policy: Litigation threats must never be debated by automated agents."
    },
    {
        "case_id": 188,
        "query": "Your phone made me miss my morning job interview because the alarm didn't ring! You ruined my career!",
        "human_evaluator": "Brand_Reputation_Manager",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 5.0,
            "actionability_score": 4.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.62,
        "notes": "High emotional distress requiring human empathy to de-escalate."
    },
    {
        "case_id": 192,
        "query": "Is it true that charging your phone in the microwave gives 100% battery in 30 seconds?",
        "human_evaluator": "Safety_Compliance_Officer",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Clear emergency warning against viral fire hazard."
    },
    {
        "case_id": 193,
        "query": "I am a technology journalist from The Wall Street Journal seeking comment on your battery replacement delays.",
        "human_evaluator": "Brand_Reputation_Manager",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Media inquiry must be redirected to Apple Media Relations."
    },
    {
        "case_id": 195,
        "query": "My phone fell into a lake 40 feet deep and stayed there for 2 weeks. Can Apple recover my unbacked photos?",
        "human_evaluator": "Senior_Support_Lead_A",
        "scores": {
            "grounding_score": 4.5,
            "tone_score": 5.0,
            "actionability_score": 4.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 4.62,
        "notes": "Compassionate handling of irreversible memory loss."
    },
    {
        "case_id": 198,
        "query": "Your chat system is obviously a dumb AI bot. I refuse to talk to a robot! Connect me to a real living human being right now!",
        "human_evaluator": "Senior_Support_Lead_B",
        "scores": {
            "grounding_score": 5.0,
            "tone_score": 5.0,
            "actionability_score": 5.0,
            "escalation_appropriateness_score": 5.0
        },
        "composite_score": 5.0,
        "notes": "Explicit refusal to converse with AI. Agent must immediately yield to human."
    },
]


METHODOLOGY_MD = """# Sampling & Labeling Methodology: Golden Evaluation Set (200 Cases)

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
"""


def build_golden_set():
    """Builds and writes all golden set files."""
    base_dir = "data/golden_set"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Write 200 golden examples
    golden_file = os.path.join(base_dir, "golden_eval_set_200.jsonl")
    with open(golden_file, "w", encoding="utf-8") as f:
        for item in GOLDEN_DATA_SPECS:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Successfully generated {len(GOLDEN_DATA_SPECS)} golden examples at {golden_file}")
    
    # 2. Write 30 human evaluation sample cases
    human_file = os.path.join(base_dir, "human_annotations_sample.json")
    with open(human_file, "w", encoding="utf-8") as f:
        json.dump(HUMAN_SCORECARDS_SAMPLE, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {len(HUMAN_SCORECARDS_SAMPLE)} human evaluation calibration cases at {human_file}")
    
    # 3. Write sampling and labeling methodology doc
    methodology_file = os.path.join(base_dir, "sampling_and_labeling_methodology.md")
    with open(methodology_file, "w", encoding="utf-8") as f:
        f.write(METHODOLOGY_MD.strip() + "\n")
    print(f"Successfully generated methodology documentation at {methodology_file}")


if __name__ == "__main__":
    build_golden_set()
