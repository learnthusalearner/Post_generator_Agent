# Post Generator Modular Agent

A powerful, multi-agent AI pipeline built with **LangGraph** that autonomously transforms a raw topic into a fully-fledged social media post. The pipeline generates structured content, a narrative design prompt, a context-aware brand logo, merges them seamlessly, and relies on self-refining feedback loops utilizing Guardrails and QA validation before final image generation.

## 🏗 System Architecture & Structure

The system is decoupled into highly specific, modular agents that pass state sequentially using a robust `PostGeneratorState` dictionary.

- `main.py` — The entry point that injects the initial user configuration.
- `src/state.py` — Defines `PostGeneratorState`, a `TypedDict` that tracks the payload as it morphs through the graph, including `logo_combination_used` and `variant_scores` to track historical performance.
- `src/graph.py` — Wires the LangGraph node executions and conditional loops.
- `src/storage.py` — Saves the completed generation lifecycle locally.
- **`src/nodes/` (The Agents)**:
  - `planner.py`: Transforms raw topics into structured JSON outlines.
  - `content.py`: Expands the plan into crisp copy, hooks, and stats.
  - `design.py`: Creates a rich, narrative design prompt targeting the content.
  - `logo.py`: Generates a dynamic, brand-compliant logo generation prompt tailored to the context.
  - `guardrails.py`: Validates the design rules against hard-coded constraints (e.g., copyright terms) and brand compliance.
  - `qa.py`: Critiques the visual layout. If it fails, LangGraph dynamically routes the workflow back to the `design` agent.
  - `prompt_merger.py`: (Node 7.5) Merges the design and logo prompts into a single, unified generation prompt using a strict template.
  - `image_generator.py`: The final execution layer that queries Ideogram v3 for variants and uses a Variant Selector Agent to score and pick the best image.

---

## 🚀 Steps to Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Open the `.env` file in the root directory and ensure your OpenAI API Key is valid:
   ```env
   OPENAI_API_KEY="sk-..."
   ```
   *(Note: The system features robust error handling. If your API key lacks quota, it will seamlessly fall back to mock generation so you can still test the pipeline execution!)*

3. **Execute the Graph**
   Trigger the multi-agent workflow by running:
   ```bash
   python main.py
   ```

---

## 🔄 Detailed End-to-End Execution Example

When you run `python main.py`, the `PostGeneratorState` dictionary is passed sequentially through the nodes. Each node acts upon the output of the previous nodes. Here is exactly how the data flows and transforms:

### 1. Input Layer (Trigger)
The `main.py` script initializes the state with the raw user input payload.
**State Added:** `state["input_data"]`
```json
{
  "topic": "Sales vs Influencer Marketing",
  "goal": "educational / promotional",
  "platform": "instagram",
  "format": "story · 9:16",
  "brand_id": "influight",
  "constraints": ["minimalist", "no copyright", "teal theme"]
}
```

### 2. Planner Agent (`planner.py`)
**Input:** `state["input_data"]`
**Process:** The LLM acts as a content strategist to break the raw topic into logical sections.
**State Added:** `state["plan"]`
```json
{
  "title": "The Ultimate Guide to Sales vs Influencer Marketing",
  "sections": [
    {"heading": "Why it matters", "content": "Understanding the difference drives ROI."}
  ],
  "insight": "Authenticity beats direct selling.",
  "cta": "Like and subscribe!"
}
```

### 3. Content Generation Agent (`content.py`)
**Input:** `state["plan"]` and `state["input_data"]["platform"]`
**Process:** The LLM acts as an expert copywriter, turning the dry skeleton into punchy, platform-ready copy.
**State Added:** `state["content"]`
```json
{
  "hook": "Stop scrolling! Here's why Sales vs Influencer Marketing is changing the game.",
  "body": [{"heading": "Why it matters", "content": "Understanding the difference drives ROI."}],
  "stats": ["90% of people miss this."],
  "cta_refined": "Like and subscribe!"
}
```

### 4. Design Prompt Generator (`design.py`)
**Input:** `state["content"]` and `state["input_data"]["constraints"]`
**Process:** The LLM acts as an art director, taking the copy and constraints to craft an image generation prompt.
**State Added:** `state["design_prompt"]`
> *"Create a professional instagram infographic. Constraints: minimalist, no copyright, teal theme. Content hook: Stop scrolling! Here's why Sales vs Influencer Marketing is changing the game. Clean layout, sans-serif typography, central visual element."*

### 5. Logo Agent (`logo.py`)
**Input:** `state["content"]["hook"]` (The Context Hint)
**Process:** A brand-aware agent that determines the exact visual configuration of the **influight** logo based on the context. It also reads all past JSON files from `/storage/` to extract `logo_combination_used` and instructs the LLM to strictly avoid generating duplicate layouts on future runs!
**State Added:** `state["logo_prompt"]`
```text
Layout: square-badge
Icon: broadcast-lines (using brand colors)
Bar arrangement: stacked-left-to-right
Context mood: Stop scrolling! Here's why Sales...
Colors: R #E63946 · O #F4841A · Y #F5C518 · G #2A9D5C · T #1BA89A
Background: dark navy #0D1B2A
Wordmark: "influight" in white rounded sans-serif, clearly legible
All 5 colored pill bars must appear.
Negative prompt: serif, gradient, blurry, missing text, wrong colors
Output: 1200x600px transparent-bg PNG + dark-bg PNG
```

### 6. Guardrails Engine (`guardrails.py`)
**Input:** `state["design_prompt"]` and Hardcoded Rules
**Process:** A hybrid Python + LLM node that checks for copyright infringement and brand violations.
**State Added:** `state["guardrail_issues"]` -> `[]` (Empty list if valid)
*(Note: If Guardrails fail, LangGraph dynamically intercepts the flow here and loops the state BACK to Step 4 (`design.py`). If they pass, it proceeds to Step 7 (`qa.py`))*

### 7. QA / Critic Agent (`qa.py`)
**Input:** `state["design_prompt"]`
**Process:** A senior designer LLM that critiques the prompt's visual hierarchy.
**State Added:** `state["qa_passed"]` -> `true`
*(Note: If QA fails, LangGraph intercepts the flow here and loops the state BACK to Step 4 (`design.py`) to regenerate the prompt! If it passes, it proceeds to Step 8)*

### 8. Prompt Merger (`prompt_merger.py`)
**Input:** `state["design_prompt"]` and `state["logo_prompt"]`
**Process:** Parses the dynamic variables (Icon style, Bar arrangement, Layout) from the logo prompt and strictly injects them along with the design prompt into a rigid, unified template.
**State Added:** `state["final_prompt"]`
```text
Create a professional instagram infographic. Constraints: minimalist, no copyright, teal theme. Content hook: Stop scrolling! Here's why Sales vs Influencer Marketing is changing the game. Clean layout, sans-serif typography, central visual element.

LOGO INSTRUCTIONS (do not ignore):
- Place Influight logo TOP CENTER of canvas
- Logo style: broadcast-lines icon · stacked-left-to-right bars · square-badge layout
- Wordmark: "influight" white rounded bold sans-serif
- Pill bars: Red #E63946 · Orange #F4841A · Yellow #F5C518 · Green #2A9D5C · Teal #1BA89A
- Reserve top 12% of canvas for logo. Must NOT overlap headline.
- Background behind logo: dark navy #0D1B2A

Negative: serif font, white background, missing wordmark, blurry text,
logo overlapping headline, wrong colors, stock photo watermark
```

### 9. Image Generation & Variant Selector (`image_generation.py`)
**Input:** `state["final_prompt"]` (only this, nothing else)
**Process:** The execution layer sends the single, unified prompt to the Ideogram v3 API requesting 3 variants (`1080x1920px`). The **Variant Selector Agent** then analyzes all 3 images against 6 strict visual performance metrics (Scroll-Stop Power, Brand Recall, Message Clarity, Platform Fit, Trust & Authority, CTA Energy) and explicitly picks the highest-scoring winner.
**State Added:** 
- `state["image_url"]` -> `"https://ideogram.ai/api/mock/variant-B-456.png"`
- `state["variant_scores"]` -> `{"A": {...}, "B": {...}, "C": {...}}`
- `state["selection_reasoning"]` -> `"Variant B demonstrated exceptional brand recall..."`

### 10. Storage (`storage.py`)
**Input:** entire `PostGeneratorState` object.
**Process:** Serializes the state and writes `post_YYYYMMDD_[topic-slug].json` to the `/storage/` directory. Must save the `state["logo_combination_used"]` representing the exact logo combination used so it feeds back to Node 5 (`logo.py`) as an exclusion list on the next run!
**State Added:** `state["storage_path"]` -> `"storage/post_20260502_sales-vs-influencer-marketing.json"`
