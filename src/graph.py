from langgraph.graph import StateGraph, END
from src.state import PostGeneratorState
from src.nodes.planner import planner_node
from src.nodes.content import content_node
from src.nodes.design import design_prompt_node
from src.nodes.logo import logo_node
from src.nodes.guardrails import guardrails_node
from src.nodes.qa import qa_node
from src.nodes.prompt_merger import prompt_merger_node
from src.nodes.image_generator import image_generator_node
from src.storage import storage_node

def after_guardrails(state: PostGeneratorState):
    if state.get("guardrail_issues") and len(state["guardrail_issues"]) > 0:
        print(">> Guardrails failed, looping back to Design Prompt.")
        return "design"
    return "qa"

def check_qa(state: PostGeneratorState):
    if not state.get("qa_passed", True):
        print(">> QA failed, looping back to Design Prompt.")
        return "design"
    return "prompt_merger"

def build_graph():
    workflow = StateGraph(PostGeneratorState)
    
    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("content", content_node)
    workflow.add_node("design", design_prompt_node)
    workflow.add_node("logo", logo_node)
    workflow.add_node("guardrails", guardrails_node)
    workflow.add_node("qa", qa_node)
    workflow.add_node("prompt_merger", prompt_merger_node)
    workflow.add_node("image", image_generator_node)
    workflow.add_node("storage", storage_node)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add Edges
    workflow.add_edge("planner", "content")
    workflow.add_edge("content", "design")
    workflow.add_edge("design", "logo")
    workflow.add_edge("logo", "guardrails")
    
    # Conditional Edges
    workflow.add_conditional_edges(
        "guardrails",
        after_guardrails,
        {
            "design": "design",
            "qa": "qa"
        }
    )
    
    workflow.add_conditional_edges(
        "qa",
        check_qa,
        {
            "design": "design",
            "prompt_merger": "prompt_merger"
        }
    )
    
    workflow.add_edge("prompt_merger", "image")
    workflow.add_edge("image", "storage")
    workflow.add_edge("storage", END)
    
    # Compile
    app = workflow.compile()
    return app

def run_workflow(input_data):
    app = build_graph()
    
    initial_state = {
        "input_data": input_data,
        "plan": None,
        "content": None,
        "design_prompt": None,
        "logo_prompt": None,
        "final_prompt": None,
        "guardrail_issues": [],
        "qa_feedback": None,
        "qa_passed": True,
        "image_url": None
    }
    
    # Stream the output for better visibility
    final_state = None
    for output in app.stream(initial_state):
        for key, value in output.items():
            final_state = value
            print(f"Completed node: {key}")
            
    return final_state
