from src.graph import run_workflow
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("Initializing Post Generator Agent Workflow...")
    
    # Input schema provided by user
    input_data = {
        "topic": "Influencer Marketing Pro's",
        "goal": "educational / promotional",
        "platform": "instagram",
        "format": "story · 9:16",
        "brand_id": "influight",
        "constraints": ["minimalist", "no copyright", "teal theme"]
    }
    
    print("\n[Input Layer] Received Trigger:")
    print(json.dumps(input_data, indent=2))
    print("\n============================================\n")
    
    # Run the graph
    final_state = run_workflow(input_data)
    
    print("\n============================================\n")
    print("Workflow Complete!")
    print(f"Generated Image URL: {final_state.get('image_url')}")
    print("\nFinal Design Prompt:")
    print(final_state.get("design_prompt"))
    
    if final_state.get("logo_prompt"):
        print("\nFinal Logo Prompt:")
        print(final_state.get("logo_prompt"))
