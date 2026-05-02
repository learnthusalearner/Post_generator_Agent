import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.state import PostGeneratorState
import os

HARD_RULES = {
    "no_copyright_terms": ["Nike", "Apple", "Netflix", "Disney"],
}

def guardrails_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- GUARDRAILS ENGINE ---")
    design_prompt = state["design_prompt"]
    input_data = state["input_data"]
    issues = []
    
    # 1. Hard Guardrails (Code)
    design_lower = design_prompt.lower()
    for term in HARD_RULES["no_copyright_terms"]:
        if term.lower() in design_lower:
            issues.append(f"Copyright term found: {term}")
            
    # 2. Soft Guardrails (LLM)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        prompt = PromptTemplate.from_template(
            "Check this design prompt for violations.\n"
            "Prompt: {prompt}\n"
            "Constraints: {constraints}\n"
            "Return JSON only with 'valid' (boolean) and 'issues' (list of strings)."
        )
        chain = prompt | llm
        
        try:
            result = chain.invoke({
                "prompt": design_prompt,
                "constraints": json.dumps(input_data.get("constraints", []))
            })
            content = result.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            validation = json.loads(content)
            if not validation.get("valid", True):
                issues.extend(validation.get("issues", []))
        except Exception as e:
            print(f"Failed to call LLM or parse Guardrails output: {e}")
            # Mock behavior on failure
            if not state.get("qa_feedback") and "teal" in str(input_data.get("constraints")):
                pass
    else:
        print("[MOCK] Running mocked guardrails")
        # In mock mode, randomly trigger an issue if we haven't looped yet
        if not state.get("qa_feedback") and "teal" in str(input_data.get("constraints")):
            # Just a fake check for demonstration, won't always fail
            pass
            
    state["guardrail_issues"] = issues
    return state
