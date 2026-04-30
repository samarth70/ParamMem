import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import logging
import os
from typing import Optional
from groq import Groq

logger = logging.getLogger(__name__)

class ParametricMemory:
    """
    Parametric Memory Module
    Replaces traditional retrieval-based memory with a lightweight
    parametric encoding using LoRA fine-tuning OR high-speed Groq API.
    """
    def __init__(
        self, 
        base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0", 
        lora_path: str = None, 
        provider: str = "local",
        api_key: Optional[str] = None,
        model_id: Optional[str] = None
    ):
        self.provider = provider
        self.base_model_name = base_model_name
        self.lora_path = lora_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if provider == "groq":
            if not api_key:
                raise ValueError("Groq API key must be provided for 'groq' provider.")
            self.client = Groq(api_key=api_key)
            self.model_id = model_id or "openai/gpt-oss-20b"
            logger.info(f"Initialized ParametricMemory via Groq (Model: {self.model_id})")
            # For compatibility with Agent loop that might check these
            self.tokenizer = None
            self.model = None
        else:
            # Local setup
            logger.info(f"Loading local base model: {base_model_name} on {self.device}")
            
            # Configure 4-bit quantization if CUDA
            quantization_config = None
            if torch.cuda.is_available():
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                
            self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=quantization_config,
                device_map="auto" if self.device == "cuda" else None,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            if lora_path and os.path.exists(lora_path):
                logger.info(f"Loading LoRA adapters from {lora_path}")
                self.model = PeftModel.from_pretrained(self.model, lora_path)
            
    def generate_solution(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.2) -> str:
        """
        Generates a solution attempt using the selected provider.
        """
        if self.provider == "groq":
            return self._generate_groq(prompt, max_new_tokens, temperature)
        else:
            return self._generate_local(prompt, max_new_tokens, temperature)

    def generate_reflection(self, context: str, error_signal: str, max_new_tokens: int = 256, temperature: float = 0.7) -> str:
        """
        Generates reflection using the selected provider.
        """
        prompt = f"""[System] You are a highly self-aware agent that reflects on its own errors.
[Context] {context}
[Error] {error_signal}
[Reflection] Analyze the error and provide a corrected reasoning path. Wrap your final answer/fix in a python code block if applicable.
"""
        return self.generate_solution(prompt, max_new_tokens, temperature)

    def _generate_groq(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            return f"Error generating via Groq: {e}"

    def _generate_local(self, prompt: str, max_new_tokens: int, temperature: float) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )
        response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        return response.strip()
