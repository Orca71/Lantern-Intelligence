import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

EXTRACTOR_PATH = "models/AR/decoder"

print("Loading AR extractor...")
tokenizer = AutoTokenizer.from_pretrained(EXTRACTOR_PATH)
model = AutoModelForCausalLM.from_pretrained(
    EXTRACTOR_PATH,
    device_map="auto",
    torch_dtype=torch.float16
)

print("Extractor loaded!")

prompt = "get customer balance for Verizon for $500"

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
