import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.state import PostGeneratorState
import os

def content_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- CONTENT GENERATION AGENT ---")
    plan = state["plan"]
    input_data = state["input_data"]
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        prompt = PromptTemplate.from_template(
            "You are an expert copywriter. Refine the following structured plan into crisp copy, hooks, and stats.\n"
            "Plan: {plan}\n"
            "Platform: {platform}\n\n"
            "Return JSON only with keys: 'hook', 'body' (refined sections), 'stats' (list of facts), 'cta_refined'."
        )
        chain = prompt | llm
        
        try:
            result = chain.invoke({"plan": json.dumps(plan), "platform": input_data.get("platform")})
            content = result.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            refined_content = json.loads(content)
        except Exception as e:
            print(f"Failed to call LLM or parse output: {e}")
            refined_content = {
                "hook": f"Stop scrolling! Here's why {input_data.get('topic')} is changing the game.",
                "body": plan.get("sections", []),
                "stats": ["90% of people miss this."],
                "cta_refined": plan.get("cta", "")
            }
    else:
        print("[MOCK] Running mocked content generator due to missing API key")
        refined_content = {
            "hook": f"Stop scrolling! Here's why {input_data.get('topic', 'Topic')} is changing the game.",
            "body": plan.get("sections", []),
            "stats": ["90% of people miss this."],
            "cta_refined": plan.get("cta", "Follow us!")
        }
        
    state["content"] = refined_content
    return state
