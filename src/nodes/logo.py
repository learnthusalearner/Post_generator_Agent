import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.state import PostGeneratorState
import random

LOGO_AGENT_PROMPT = """You are a brand-aware logo generator for influight.

BRAND CONSTANTS (never change):
- Brand name: influight (all lowercase, rounded bold sans-serif)
- Core palette: Red #E63946 · Orange #F4841A · Yellow #F5C518 · Green #2A9D5C · Teal #1BA89A
- Canvas: dark navy #0D1B2A
- Wordmark: white text, always legible
- Signature element: 5 pill/bar shapes using the 5 brand colors, always present

CONTEXT-TO-DESIGN MAPPING:
- Social / viral context  -> waveform icon · arc spread bars · vibrant saturated palette
- Data / analytics context -> bar-chart icon · stacked bars · precise grid alignment  
- Creator / influence context -> broadcast icon · diagonal cascade · dynamic angles
- Enterprise / formal context -> paper-plane icon · horizontal row · clean whitespace
- Community / culture context -> constellation dots · orbit arrangement · softer glow

GENERATION RULES:
1. Combine the correct ICON_STYLE + BAR_ARRANGEMENT based on the CONTEXT_HINT.
2. All 5 brand colors must appear in every logo — order may vary.
3. The word influight must always be clearly readable.
4. Maintain dark navy background.
5. Output just the specific logo generation prompt exactly in the format below.

Output Format Example:
Generate a logo for influight.

Layout: [Choose one: landscape-banner, square-badge, vertical-stacked, icon-only, icon-left-wordmark-right, wordmark-above-icon]
Icon: [Selected icon] (using brand colors)
Bar arrangement: [Selected arrangement]
Context mood: [Context mood derived from context]

Colors: R #E63946 · O #F4841A · Y #F5C518 · G #2A9D5C · T #1BA89A
Background: dark navy #0D1B2A
Wordmark: "influight" in white rounded sans-serif, clearly legible
All 5 colored pill bars must appear.

Negative prompt: serif, gradient, blurry, missing text, wrong colors
Output: 1200x600px transparent-bg PNG + dark-bg PNG

---
CONTEXT_HINT: {context_hint}
"""

import glob

def load_used_combinations(storage_dir="storage/"):
    used = []
    if os.path.exists(storage_dir):
        for f in glob.glob(f"{storage_dir}*.json"):
            with open(f, encoding="utf-8") as fp:
                try:
                    data = json.load(fp)
                    combo = data.get("logo_combination_used")
                    if combo:
                        used.append(combo)
                except:
                    pass
    return used

def logo_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- LOGO AGENT ---")
    
    # We use the generated content or design prompt as context hint
    context_hint = "general"
    if state.get("content") and isinstance(state["content"], dict):
        context_hint = state["content"].get("hook", "general context")
    elif state.get("input_data") and isinstance(state["input_data"], dict):
        context_hint = state["input_data"].get("topic", "general context")

    used_combinations = load_used_combinations()
    exclusion_text = ""
    if used_combinations:
        exclusion_text = f"\nDo NOT use any of these logo combinations: {used_combinations}\n"

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
        prompt = PromptTemplate.from_template(LOGO_AGENT_PROMPT + exclusion_text)
        chain = prompt | llm
        
        try:
            result = chain.invoke({"context_hint": context_hint})
            logo_prompt = result.content.strip()
        except Exception as e:
            print(f"Failed to call LLM for Logo Agent: {e}")
            logo_prompt = _mock_logo_prompt(context_hint)
    else:
        print("[MOCK] Running mocked Logo Agent")
        logo_prompt = _mock_logo_prompt(context_hint)
        
    state["logo_prompt"] = logo_prompt
    return state

def _mock_logo_prompt(context_hint: str) -> str:
    icons = ["sound-waveform", "bar-chart-ascending", "paper-plane", "lightbulb", "upward-arrow", "signal-bars", "broadcast-lines", "constellation-dots"]
    layouts = ["landscape-banner", "square-badge", "vertical-stacked", "icon-left-wordmark-right"]
    arrangements = ["horizontal-pill-row", "stacked-left-to-right", "arc-spread", "diagonal-cascade"]
    
    return f"""Generate a logo for influight.

Layout: {random.choice(layouts)}
Icon: {random.choice(icons)} (using brand colors)
Bar arrangement: {random.choice(arrangements)}
Context mood: {context_hint[:30]}...

Colors: R #E63946 · O #F4841A · Y #F5C518 · G #2A9D5C · T #1BA89A
Background: dark navy #0D1B2A
Wordmark: "influight" in white rounded sans-serif, clearly legible
All 5 colored pill bars must appear.

Negative prompt: serif, gradient, blurry, missing text, wrong colors
Output: 1200x600px transparent-bg PNG + dark-bg PNG"""
