import re
from src.state import PostGeneratorState

def prompt_merger_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- PROMPT MERGER ---")
    
    design_prompt = state.get("design_prompt", "")
    logo_prompt = state.get("logo_prompt", "")
    
    # Extract variables from logo_prompt using regex
    icon_style = "default-icon"
    bar_arrangement = "default-arrangement"
    layout_format = "default-layout"
    
    if logo_prompt:
        icon_match = re.search(r"Icon:\s*([^\n\(]+)", logo_prompt)
        if icon_match:
            icon_style = icon_match.group(1).strip()
            
        bar_match = re.search(r"Bar arrangement:\s*([^\n]+)", logo_prompt)
        if bar_match:
            bar_arrangement = bar_match.group(1).strip()
            
        layout_match = re.search(r"Layout:\s*([^\n]+)", logo_prompt)
        if layout_match:
            layout_format = layout_match.group(1).strip()
            
    state["logo_combination_used"] = f"{icon_style} + {bar_arrangement}"
    
    final_prompt = f"""{design_prompt}

LOGO INSTRUCTIONS (do not ignore):
- Place Influight logo TOP CENTER of canvas
- Logo style: {icon_style} icon · {bar_arrangement} bars · {layout_format} layout
- Wordmark: "influight" white rounded bold sans-serif
- Pill bars: Red #E63946 · Orange #F4841A · Yellow #F5C518 · Green #2A9D5C · Teal #1BA89A
- Reserve top 12% of canvas for logo. Must NOT overlap headline.
- Background behind logo: dark navy #0D1B2A

Negative: serif font, white background, missing wordmark, blurry text,
logo overlapping headline, wrong colors, stock photo watermark
"""

    state["final_prompt"] = final_prompt
    return state
