"""
Interactive CLI Demo for @AppleSupport AI Agent.

Allows real-time testing of customer queries with immediate triage,
escalation decision, stated reasoning, grounded reply, and latency.
"""

import sys
from src.agent import AppleSupportAgent


def main():
    print("=" * 75)
    print("  @AppleSupport AI Support Agent — Interactive Live Demo")
    print("=" * 75)
    print("Initializing agent and knowledge base (takes ~1.5s)...")
    agent = AppleSupportAgent()
    print("Ready! Type any customer tweet (or 'quit' / 'exit' to stop).\n")

    sample_queries = [
        "Why does my iPhone replace the letter 'I' with a question mark box?",
        "My battery is burning hot and swelling pushing out the screen glass!",
        "I was double charged $9.99 on my credit card for Apple Music this month.",
        "My right AirPod is much quieter than the left one. How do I fix it?",
        "I want to speak to a real human being right now, stop ignoring my tweets!"
    ]

    print("Sample queries you can try:")
    for i, sq in enumerate(sample_queries, 1):
        print(f"  {i}. {sq}")
    print("-" * 75)

    while True:
        try:
            user_input = input("\nEnter customer tweet > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Exiting interactive demo. Goodbye!")
                break

            result = agent.process(user_input)
            print("\n" + "-" * 75)
            print(f"🔹 PREDICTED INTENT:      {result['intent']} (confidence: {result['intent_confidence']*100:.1f}%)")
            print(f"🔹 ESCALATION DECISION:  {result['escalation_decision']} (confidence: {result['escalation_confidence']*100:.1f}%)")
            print(f"🔹 STATED REASON:        {result['escalation_reason']}")
            print(f"🔹 DRAFTED REPLY:        {result['drafted_reply']}")
            print(f"⏱️  LATENCY:              {result['latency_ms']} ms")
            if result["retrieved_contexts"]:
                top_hit = result["retrieved_contexts"][0]
                print(f"📚 TOP GROUNDING MATCH:   Similarity {top_hit['similarity_score']} | Historical Tweet: {top_hit['customer_text'][:60]}...")
            print("-" * 75)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break


if __name__ == "__main__":
    main()
