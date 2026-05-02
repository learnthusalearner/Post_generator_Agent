import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.state import PostGeneratorState
import os

def planner_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- PLANNER AGENT ---")
    input_data = state["input_data"]
    
    # In a real scenario, use ChatOpenAI. For now, we simulate if no API key is provided.
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        prompt = PromptTemplate.from_template(
            "You are a master content strategist. Create a structured content plan for a post.\n"
            "Topic: {topic}\n"
            "Goal: {goal}\n"
            "Platform: {platform}\n"
            "Brand ID: {brand_id}\n\n"
            "Return JSON only with keys: 'title', 'sections' (list of dicts with 'heading' and 'content'), 'insight', and 'cta'."
        )
        chain = prompt | llm
        
        try:
            result = chain.invoke(input_data)
            # Handle markdown json wrapping if any
            content = result.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            plan = json.loads(content)
        except Exception as e:
            print(f"Failed to call LLM or parse output: {e}")
            plan = {
                "title": f"The Ultimate Guide to {input_data.get('topic', 'Topic')}",
                "sections": [{"heading": "Introduction", "content": "Welcome to our post."}],
                "insight": "Here is an insight.",
                "cta": "Like and subscribe!"
            }
    else:
        print("[MOCK] Running mocked planner due to missing API key")
        plan = {
            "title": f"The Ultimate Guide to {input_data.get('topic', 'Topic')}",
            "sections": [
                {"heading": "Why it matters", "content": "Understanding this is crucial."},
                {"heading": "How to start", "content": "Step 1: Just do it."}
            ],
            "insight": "Action takes you further than reading.",
            "cta": "Follow for more!"
        }
        
    state["plan"] = plan
    return state
