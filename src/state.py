from typing import TypedDict, List, Dict, Any, Optional

class PostGeneratorState(TypedDict):
    # Input
    input_data: Dict[str, Any]
    
    # Outputs from different nodes
    plan: Optional[Dict[str, Any]]
    content: Optional[Dict[str, Any]]
    design_prompt: Optional[str]
    logo_prompt: Optional[str]
    final_prompt: Optional[str]
    guardrail_issues: List[str]
    qa_feedback: Optional[str]
    qa_passed: bool
    image_url: Optional[str]
    variant_scores: Optional[Dict[str, Any]]
    selection_reasoning: Optional[str]
    storage_path: Optional[str]
    logo_combination_used: Optional[str]
