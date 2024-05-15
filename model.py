import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer

model_path = "modellamma"


model = AutoPeftModelForCausalLM.from_pretrained(
    model_path,
    load_in_4bit=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_path)


model_input = tokenizer(r"<human>: allien building pc\n<bot>: ", return_tensors="pt").to("cuda")
model.eval()
with torch.no_grad():
    print(tokenizer.decode(model.generate(**model_input, max_new_tokens=60, repetition_penalty=1.15)[0], skip_special_tokens=True))

inputs = tokenizer(
[
    r"<human>: allien building pc\n<bot>: "
], return_tensors = "pt").to("cuda")

outputs = model.generate(**inputs, max_new_tokens = 64, use_cache = True)
tokenizer.batch_decode(outputs)
