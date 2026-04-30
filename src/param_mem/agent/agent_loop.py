import logging
from typing import List, Dict, Any
from param_mem.memory.parametric import ParametricMemory
from param_mem.memory.retrieval import CrossSampleMemory

logger = logging.getLogger(__name__)

class ParamAgent:
    """
    ParamMem Agent Loop
    Unifies episodic memory, cross-sample trajectory banks (ParamAgent-plus),
    and parametric memory for iterative task solving.
    """
    def __init__(self, memory_module: ParametricMemory, retrieval_module: CrossSampleMemory = None):
        self.memory_module = memory_module
        self.retrieval_module = retrieval_module
        
    def solve_task(self, problem: str, max_iterations: int = 3) -> Dict[str, Any]:
        """
        Executes the iterative reasoning loop.
        """
        episodic_memory = []
        current_solution = None
        
        # 1. Retrieve cross-sample patterns if ParamAgent-plus
        cross_sample_context = ""
        if self.retrieval_module:
            patterns = self.retrieval_module.retrieve_similar_patterns(problem)
            if patterns:
                cross_sample_context = "Helpful reasoning patterns from past experiences:\n"
                for p in patterns:
                    cross_sample_context += f"- {p.get('reflection', '')}\n"
                    
        for iteration in range(max_iterations):
            logger.info(f"Starting iteration {iteration + 1}/{max_iterations}")
            
            # Step 1: Propose Solution
            prompt = self._build_prompt(problem, cross_sample_context, episodic_memory)
            
            # Use abstracted generation method
            current_solution = self.memory_module.generate_solution(
                prompt, 
                max_new_tokens=256, 
                temperature=0.2
            )
            
            # Step 2: Evaluate (mock evaluation for this deployable scaffold)
            is_correct, error_signal = self._mock_evaluate(current_solution)
            
            if is_correct:
                logger.info("Solution is correct!")
                if self.retrieval_module:
                    self.retrieval_module.add_trajectory(
                        trajectory_id=f"traj_{hash(problem)}",
                        problem_description=problem,
                        final_reflection=f"Successfully solved by: {current_solution}"
                    )
                return {
                    "success": True, 
                    "solution": current_solution, 
                    "iterations": iteration + 1,
                    "history": episodic_memory
                }
                
            # Step 3: Reflect (Using Parametric Memory)
            temp = min(0.7 + (iteration * 0.1), 1.0)
            reflection = self.memory_module.generate_reflection(
                context=current_solution,
                error_signal=error_signal,
                temperature=temp
            )
            
            episodic_memory.append({
                "attempt": current_solution,
                "error": error_signal,
                "reflection": reflection
            })
            
            logger.info(f"Reflection generated: {reflection}")
            
        return {
            "success": False, 
            "solution": current_solution, 
            "iterations": max_iterations, 
            "history": episodic_memory
        }
        
    def _build_prompt(self, problem: str, cross_sample_context: str, episodic_memory: List[Dict]) -> str:
        prompt = f"Problem: {problem}\n"
        if cross_sample_context:
            prompt += f"{cross_sample_context}\n"
        
        if episodic_memory:
            prompt += "Previous Attempts and Reflections:\n"
            for i, mem in enumerate(episodic_memory):
                prompt += f"Attempt {i+1}: {mem['attempt']}\n"
                prompt += f"Error: {mem['error']}\n"
                prompt += f"Reflection: {mem['reflection']}\n"
                
        prompt += "\nProvide the best solution to the problem based on the above context:\n"
        return prompt
        
    def _mock_evaluate(self, solution: str):
        # Always fails once to demonstrate reflection loop, then succeeds if 'mock_success' is mentioned
        # Or just simulate a success on iteration 2
        if "correctly" in solution or "fixed" in solution:
             return True, ""
        
        # Default mock behavior
        if "def " in solution and "return" in solution:
            return False, "AssertionError: Expected output 5, got 3. Check your logic."
        return False, "SyntaxError: invalid syntax"
