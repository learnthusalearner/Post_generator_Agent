import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.state import PostGeneratorState
import os

def design_prompt_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- DESIGN PROMPT GENERATOR ---")
    content = state["content"]
    input_data = state["input_data"]
    
    # Check if we have feedback from Guardrails or QA
    feedback = ""
    if state.get("guardrail_issues"):
        feedback += f"Fix Guardrail Issues: {', '.join(state['guardrail_issues'])}\n"
    if state.get("qa_feedback") and not state.get("qa_passed", True):
        feedback += f"Fix QA Issues: {state['qa_feedback']}\n"
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        prompt_str = (
            "You are an expert design director. Create a detailed image generation prompt "
            "based on the structured content.\n"
            "Content: {content}\n"
            "Constraints: {constraints}\n"
        )
        if feedback:
            prompt_str += f"\nCRITICAL FEEDBACK TO INCORPORATE:\n{feedback}\n"
            
        prompt_str += "Return just the narrative prompt text as a string."
        
        prompt = PromptTemplate.from_template(prompt_str)
        chain = prompt | llm
        try:
            result = chain.invoke({
                "content": json.dumps(content),
                "constraints": json.dumps(input_data.get("constraints", []))
            })
            design_prompt = result.content.strip()
        except Exception as e:
            print(f"Failed to call LLM: {e}")
            design_prompt = (
                f"Create a professional {input_data.get('platform', 'social')} infographic. "
                f"Constraints: {', '.join(input_data.get('constraints', []))}. "
                f"Content hook: {content.get('hook', '')}. "
                "Clean layout, sans-serif typography, central visual element."
            )
            if feedback:
                design_prompt += f" (Adjusted for feedback: {feedback})"
    else:
        print("[MOCK] Running mocked design prompt generator")
        design_prompt = (
            f"Create a professional {input_data.get('platform', 'social')} infographic. "
            f"Constraints: {', '.join(input_data.get('constraints', []))}. "
            f"Content hook: {content.get('hook', '')}. "
            "Clean layout, sans-serif typography, central visual element."
        )
        if feedback:
            design_prompt += f" (Adjusted for feedback: {feedback})"
            
    state["design_prompt"] = design_prompt
    
    # Clear issues for the next iteration if any
    state["guardrail_issues"] = []
    
    return state
