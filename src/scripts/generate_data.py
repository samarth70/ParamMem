import json
import random

def generate_synthetic_data(output_path, num_samples=500):
    domains = ["programming", "mathematics", "logic"]
    error_types = [
        "Index out of bounds", "Type mismatch", "Logic error in loop", 
        "Incorrect math formula", "Off-by-one error", "Missing edge case",
        "Inefficient algorithm", "Syntax error"
    ]
    
    samples = []
    for i in range(num_samples):
        domain = random.choice(domains)
        error = random.choice(error_types)
        
        # Format consistent with src/param_mem/memory/parametric.py
        context = f"A {domain} task resulted in a {error}."
        error_signal = f"Error: {error} detected during execution."
        reflection = f"The error occurred because of a {error.lower()}. To fix this, we should re-examine the reasoning path and ensure that the constraints of the {domain} domain are respected."
        
        text = f"[System] You are a highly self-aware agent that reflects on its own errors.\n[Context] {context}\n[Error] {error_signal}\n[Reflection] {reflection}"
        
        samples.append({"text": text, "metadata": {"domain": domain, "error": error}})
        
    with open(output_path, "w") as f:
        for sample in samples:
            f.write(json.dumps(sample) + "\n")
            
    print(f"Generated {num_samples} synthetic samples at {output_path}")

if __name__ == "__main__":
    generate_synthetic_data("c:/Users/samar/OneDrive/Document/Projects/ParamMem/data/reflective_feedback.jsonl")
