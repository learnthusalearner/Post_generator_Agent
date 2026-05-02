import json
from datetime import datetime
import os
import re
from src.state import PostGeneratorState

STORAGE_DIR = "storage"

def init_storage():
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

def storage_node(state: PostGeneratorState) -> PostGeneratorState:
    print("--- STORAGE LAYER ---")
    init_storage()
    
    topic = state.get("input_data", {}).get("topic", "untitled")
    slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
    record_id = datetime.now().strftime("%Y%m%d")
    
    filename = f"post_{record_id}_{slug}.json"
    filepath = os.path.join(STORAGE_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        
    state["storage_path"] = filepath
    print(f"Saved complete state to {filepath}")
    
    return state
