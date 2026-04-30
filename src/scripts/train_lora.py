import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from trl import SFTTrainer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_lora(
    base_model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    dataset_path: str = "./data/reflective_feedback.jsonl",
    output_dir: str = "./param_mem_lora",
    epochs: int = 3,
    batch_size: int = 4
):
    """
    Fine-tunes the base language model using Low-Rank Adaptation (LoRA)
    on a curated dataset of reflective feedback.
    """
    logger.info("Initializing LoRA Training Pipeline for Parametric Memory...")

    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Setup Quantization for local laptop environment
    logger.info("Loading base model in 4-bit...")
    
    # In a real deployment, paths should be injected via environment variables
    # We default to the local mock base model setup
    base_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=quantization_config,
        device_map="auto"
    )
    
    # Prepare model for PEFT
    model = prepare_model_for_kbit_training(model)

    # Define LoRA Config
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"]
    )
    
    # model = get_peft_model(model, peft_config) # Removed to let SFTTrainer handle it

    # Load Dataset
    # Assuming the dataset has a "text" field with the formatted reflective prompt
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset not found at {dataset_path}. Please generate dummy data first.")
        return
        
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    # Define Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        optim="paged_adamw_32bit",
        save_steps=100,
        logging_steps=10,
        learning_rate=2e-4,
        weight_decay=0.001,
        fp16=True,
        bf16=False,
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        lr_scheduler_type="constant"
    )

    # Initialize SFTTrainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        formatting_func=lambda x: x["text"],
        args=training_args,
    )

    # Train
    logger.info("Starting Training...")
    trainer.train()

    # Save
    logger.info(f"Saving LoRA adapter to {output_dir}")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("Training complete.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="meta-llama/Meta-Llama-3-8B-Instruct")
    parser.add_argument("--dataset", type=str, default="./data/reflective_feedback.jsonl")
    parser.add_argument("--output", type=str, default="./param_mem_lora")
    args = parser.parse_args()
    
    train_lora(args.model, args.dataset, args.output)
