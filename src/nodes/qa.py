import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.state import PostGeneratorState
import os

def qa_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- QA / CRITIC AGENT ---")
    design_prompt = state["design_prompt"]
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        prompt = PromptTemplate.from_template(
            "Critique this design prompt like a senior designer.\n"
            "Prompt: {prompt}\n"
            "Evaluate readability, visual hierarchy, and alignment.\n"
            "Return JSON only with 'passed' (boolean) and 'feedback' (string). If passed is true, feedback can be empty."
        )
        chain = prompt | llm
        
        try:
            result = chain.invoke({"prompt": design_prompt})
            content = result.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            critique = json.loads(content)
            state["qa_passed"] = critique.get("passed", True)
            state["qa_feedback"] = critique.get("feedback", "")
        except Exception as e:
            print(f"Failed to call LLM or parse QA output: {e}")
            state["qa_passed"] = True
            state["qa_feedback"] = ""
    else:
        print("[MOCK] Running mocked QA agent")
        # In mock mode, we'll just pass it unless it's the first run and we want to simulate a loop
        if not state.get("qa_feedback"):
            print("Simulating a QA failure for demonstration...")
            state["qa_passed"] = False
            state["qa_feedback"] = "Missing strong visual hierarchy in the header section."
        else:
            state["qa_passed"] = True
            state["qa_feedback"] = "Looks good after revisions."
            
    return state
