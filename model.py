import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

model_path = "modellamma"


model = AutoPeftModelForCausalLM.from_pretrained(
    model_path,
    load_in_4bit=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

inputs = tokenizer([r"<human>: allien building pc\n<bot>: "], return_tensors="pt").to(
    "cuda"
)

outputs = model.generate(
    **inputs, max_new_tokens=64, use_cache=True, repetition_penalty=1.15
)
tokenizer.batch_decode(outputs, skip_special_tokens=True)
