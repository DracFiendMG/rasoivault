import os
import asyncio
from dotenv import load_dotenv
from backboard import BackboardClient

load_dotenv()

async def test():
    api_key = os.getenv("BACKBOARD_API_KEY")
    client = BackboardClient(api_key=api_key)
    
    # Create test assistant and thread
    asst = await client.create_assistant(name="Test Runner")
    thread = await client.create_thread(asst.assistant_id)
    
    # Models to test: Gemma 3 12B first (for the Gemma prize), then other open weights
    candidates = [
        {"provider": "openrouter", "model": "google/gemma-3-12b-it"},
        {"provider": "openrouter", "model": "meta-llama/llama-3.1-8b-instruct"},
        {"provider": "openai", "model": "gpt-4o-mini"},
    ]
    
    for c in candidates:
        print(f"Testing {c['provider']} -> {c['model']}...")
        try:
            resp = await client.add_message(
                thread_id=thread.thread_id,
                content="Return strictly: {\"status\": \"ok\"}",
                llm_provider=c["provider"],
                model_name=c["model"],
                stream=False
            )
            text = resp.content or ""
            if "LLM Error" in text:
                print(f"❌ Failed: {text[:80]}")
            else:
                print(f"✅ SUCCESS with {c['model']}! Output: {text[:60]}")
                break
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test())