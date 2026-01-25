import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

EXTRACTOR_PATH = "models/PAY/decoder"

print("Loading Payroll extractor...")
tokenizer = AutoTokenizer.from_pretrained(EXTRACTOR_PATH)
model = AutoModelForCausalLM.from_pretrained(
    EXTRACTOR_PATH,
    device_map="auto",
    torch_dtype=torch.float16
)

print("Payroll Extractor Loaded!")

prompt = "run payroll for the kitchen staff today"

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    out = model.generate(
        **inputs,
        max_new_tokens=64,
        do_sample=False
    )

decoded = tokenizer.decode(out[0], skip_special_tokens=True)
print("\nExtractor output:")
print(decoded)
