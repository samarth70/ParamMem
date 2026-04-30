import logging
import json
from param_mem.memory.parametric import ParametricMemory
from param_mem.agent.agent_loop import ParamAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_evaluation(model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", lora_path: str = None, domain: str = "humaneval"):
    """
    Evaluates the ParamMem agent dynamically on a given benchmark domain.
    Domains supported (mock implementation): humaneval, gsm8k, hotpotqa
    """
    logger.info(f"Starting Evaluation on {domain.upper()} domain...")
    
    memory = ParametricMemory(base_model_name=model_name, lora_path=lora_path)
    agent = ParamAgent(memory_module=memory)
    
    # Mock dataset for demonstration
    mock_datasets = {
        "humaneval": ["def add(a, b):", "def is_prime(n):"],
        "gsm8k": ["John has 5 apples, gives 2 to Mary. How many?", "A train travels 60mph for 2 hours."],
        "hotpotqa": ["Who was the director of the movie starring Tom Hanks in 1994?"]
    }
    
    dataset = mock_datasets.get(domain, [])
    results = []
    
    for problem in dataset:
        logger.info(f"Evaluating Problem: {problem}")
        result = agent.solve_task(problem, max_iterations=3)
        results.append({
            "problem": problem,
            "success": result["success"],
            "iterations": result["iterations"]
        })
        
    success_rate = sum([1 for r in results if r["success"]]) / len(results) if results else 0
    logger.info(f"Evaluation Complete. Success Rate: {success_rate * 100:.2f}%")
    
    with open(f"./data/eval_results_{domain}.json", "w") as f:
        json.dump(results, f, indent=4)
        
    return success_rate

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct")
    parser.add_argument("--lora", type=str, default=None)
    parser.add_argument("--domain", type=str, choices=["humaneval", "gsm8k", "hotpotqa"], default="humaneval")
    args = parser.parse_args()
    
    run_evaluation(args.model, args.lora, args.domain)
