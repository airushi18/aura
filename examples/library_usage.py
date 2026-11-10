"""Run with a configured CREATIVITY_MODEL and compatible model provider."""
from creative_intelligence import CreativeAgent

if __name__ == "__main__":
    brief = {
        "medium": "social_post",
        "goal": "Explain the benefit of an automotive coating",
        "audience": "Car owners",
        "content": "Premium coating is available now.",
    }
    result = CreativeAgent().evaluate(brief)
    print(f"Score: {result['score']}/100; Decision: {result['decision']}")
