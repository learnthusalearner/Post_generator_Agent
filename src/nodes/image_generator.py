import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from src.state import PostGeneratorState

VARIANT_SELECTOR_PROMPT = """You are the Influight Visual Performance Analyst.

Your job is to evaluate 3 generated image variants and select the ONE 
that will drive the highest engagement for Influight's brand and business goals.

INFLUIGHT'S COMPANY OBJECTIVES (your scoring must serve these):
- Primary: Drive creators and brands to discover Influight as their 
  influencer marketing intelligence platform
- Secondary: Position Influight as a thought-leader in the 
  creator economy / influencer marketing space
- Tertiary: Build brand recall through consistent visual identity 
  so audiences instantly recognize Influight content in their feed

PLATFORM CONTEXT:
- Platform: {platform}
- Format: {format}
- Goal: {goal}
- Topic Hook: {topic_hook}

YOU WILL RECEIVE 3 IMAGE VARIANTS:
- Variant A: {image_url_1}
- Variant B: {image_url_2}  
- Variant C: {image_url_3}

EVALUATE EACH VARIANT AGAINST THESE 6 CRITERIA.
Score each criterion from 1-10. Be ruthless — a 10 must be exceptional.

1. SCROLL-STOP POWER (weight: 30%)
   Does this image stop a fast-scrolling thumb within 1 second?
   Look for: bold contrast, visual tension, unexpected composition.
   A 10 = someone would stop mid-scroll involuntarily.

2. BRAND RECALL (weight: 20%)
   Is the Influight logo clearly visible and positioned correctly?
   Are the 5 brand colors (R/O/Y/G/T) present and dominant?
   A 10 = someone sees this 3x and forever associates it with Influight.

3. MESSAGE CLARITY (weight: 20%)
   Can the core message be understood in under 3 seconds?
   Is the headline readable without zooming?
   Is the visual hierarchy: logo → headline → stat → illustration?
   A 10 = message lands instantly with zero cognitive effort.

4. PLATFORM FIT (weight: 15%)
   Does the composition work for {platform} {format}?
   Check: safe zones respected, text not near edges, aspect ratio used well.
   A 10 = looks native, not repurposed from another format.

5. TRUST & AUTHORITY (weight: 10%)
   Does this look like content from a credible B2B intelligence platform?
   Not too playful, not too corporate. Premium but accessible.
   A 10 = a CMO would save this and share it internally.

6. CTA ENERGY (weight: 5%)
   Does the visual energy push the viewer toward action 
   (save, share, click, follow)?
   A 10 = viewer feels compelled to engage immediately.

SCORING FORMULA:
weighted_score = (score1 * 0.30) + (score2 * 0.20) + (score3 * 0.20) 
               + (score4 * 0.15) + (score5 * 0.10) + (score6 * 0.05)

OUTPUT FORMAT (strict JSON, nothing else):
{{
  "winner": "A" | "B" | "C",
  "winner_url": "[url of winning variant]",
  "winner_score": [final weighted score out of 10],
  "reasoning": "[2 sentences max — why this variant wins for Influight's goals]",
  "scores": {{
    "A": {{"scroll_stop": 0, "brand_recall": 0, "message_clarity": 0, 
          "platform_fit": 0, "trust_authority": 0, "cta_energy": 0, 
          "weighted_total": 0}},
    "B": {{"scroll_stop": 0, "brand_recall": 0, "message_clarity": 0, 
          "platform_fit": 0, "trust_authority": 0, "cta_energy": 0, 
          "weighted_total": 0}},
    "C": {{"scroll_stop": 0, "brand_recall": 0, "message_clarity": 0, 
          "platform_fit": 0, "trust_authority": 0, "cta_energy": 0, 
          "weighted_total": 0}}
  }},
  "disqualified": "[variant letter if any were disqualified, else null]",
  "disqualification_reason": "[reason if any, else null]"
}}

DISQUALIFICATION RULES (check before scoring):
If ANY variant has ANY of the following, disqualify it immediately 
and remove it from selection regardless of score:
- Influight logo missing or unreadable
- Headline text overlapping the logo
- Any competitor brand name visible
- Background is NOT dark navy
- Fewer than 5 brand color elements visible

TIEBREAKER:
If two variants are within 0.5 points of each other, 
select the one with the higher scroll_stop score.
Brand recall is the final tiebreaker if scroll_stop is also tied.
"""

def _mock_selector_output(variants):
    return {
        "winner": "B",
        "winner_url": variants[1]["url"],
        "winner_score": 8.5,
        "reasoning": "Variant B demonstrated exceptional brand recall and message clarity, ensuring immediate recognition while respecting the native platform safe zones. It effectively balances authority with high-energy composition.",
        "scores": {
            "A": {"scroll_stop": 7, "brand_recall": 6, "message_clarity": 8, "platform_fit": 8, "trust_authority": 7, "cta_energy": 6, "weighted_total": 7.1},
            "B": {"scroll_stop": 9, "brand_recall": 9, "message_clarity": 9, "platform_fit": 8, "trust_authority": 8, "cta_energy": 7, "weighted_total": 8.65},
            "C": {"scroll_stop": 6, "brand_recall": 5, "message_clarity": 6, "platform_fit": 7, "trust_authority": 6, "cta_energy": 5, "weighted_total": 5.9}
        },
        "disqualified": "C",
        "disqualification_reason": "Fewer than 5 brand color elements visible"
    }

def image_generator_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- IMAGE GENERATION TOOL ---")
    final_prompt = state.get("final_prompt", "")
    
    print("[MOCK EXECUTION] Calling Ideogram v3 API...")
    print(f" -> Input: {final_prompt[:100]}...")
    print(" -> Config: 1080x1920px · 3 variants · top-pick returned")
    
    # Mocking ideogram response returning 3 variants
    ideogram_response = {
        "images": [
            {"url": "https://ideogram.ai/api/mock/variant-A-123.png"},
            {"url": "https://ideogram.ai/api/mock/variant-B-456.png"},
            {"url": "https://ideogram.ai/api/mock/variant-C-789.png"}
        ]
    }
    
    variants = ideogram_response["images"]
    
    selector_input = {
        "image_url_1": variants[0]["url"],
        "image_url_2": variants[1]["url"],
        "image_url_3": variants[2]["url"],
        "platform": state.get("input_data", {}).get("platform", "instagram"),
        "format": state.get("input_data", {}).get("format", "story 9:16"),
        "goal": state.get("input_data", {}).get("goal", "educational"),
        "topic_hook": state.get("content", {}).get("hook", "")
    }

    print("--- VARIANT SELECTOR AGENT ---")
    api_key = os.getenv("OPENAI_API_KEY")
    selection = None
    
    if api_key:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
        prompt = PromptTemplate.from_template(VARIANT_SELECTOR_PROMPT)
        chain = prompt | llm
        
        try:
            result = chain.invoke(selector_input)
            raw_content = result.content.strip()
            # Try to extract JSON if enclosed in markdown blocks
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.endswith("```"):
                raw_content = raw_content[:-3]
                
            selection = json.loads(raw_content.strip())
        except Exception as e:
            print(f"Failed to call LLM or parse Variant Selector output: {e}")
            selection = _mock_selector_output(variants)
    else:
        selection = _mock_selector_output(variants)
        
    print(f"Agent selected Variant {selection['winner']} ({selection['winner_score']}/10)")
    
    state["image_url"] = selection["winner_url"]
    state["variant_scores"] = selection["scores"]
    state["selection_reasoning"] = selection["reasoning"]
    
    return state
