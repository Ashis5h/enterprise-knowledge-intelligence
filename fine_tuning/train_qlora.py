import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="QLoRA fine-tuning scaffold for enterprise instruction data.")
    parser.add_argument("--config", required=True, help="Path to QLoRA config JSON.")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    dataset_path = Path(config["dataset_path"])
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    try:
        from datasets import load_dataset
        from peft import LoraConfig
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
        from trl import SFTTrainer
    except ImportError as exc:
        raise SystemExit(
            "Missing training dependencies. Install transformers, datasets, peft, trl, accelerate, and bitsandbytes "
            "in a GPU environment before running this script."
        ) from exc

    tokenizer = AutoTokenizer.from_pretrained(config["base_model"], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=config["load_in_4bit"],
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="bfloat16",
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        config["base_model"],
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=True,
    )

    dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    dataset = dataset.map(lambda row: {"text": format_instruction(row)})

    lora_config = LoraConfig(
        r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=config["target_modules"],
    )

    training_args = TrainingArguments(
        output_dir=config["output_dir"],
        learning_rate=config["learning_rate"],
        num_train_epochs=config["num_train_epochs"],
        per_device_train_batch_size=config["per_device_train_batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation_steps"],
        warmup_ratio=config["warmup_ratio"],
        save_steps=config["save_steps"],
        logging_steps=config["logging_steps"],
        fp16=False,
        bf16=True,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        peft_config=lora_config,
        args=training_args,
        max_seq_length=config["max_seq_length"],
        dataset_text_field="text",
    )
    trainer.train()
    trainer.save_model(config["output_dir"])
    tokenizer.save_pretrained(config["output_dir"])


def format_instruction(row: dict) -> str:
    instruction = row["instruction"].strip()
    input_text = row.get("input", "").strip()
    output = row["output"].strip()

    if input_text:
        return f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"

    return f"### Instruction:\n{instruction}\n\n### Response:\n{output}"


if __name__ == "__main__":
    main()

