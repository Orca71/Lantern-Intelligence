import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

EXTRACTOR_PATH = "models/OPS/decoder"

print("Loading OPS extractor...")
tokenizer = AutoTokenizer.from_pretrained(EXTRACTOR_PATH)
model = AutoModelForCausalLM.from_pretrained(
    EXTRACTOR_PATH,
    device_map="auto",
    torch_dtype=torch.float16
)

print("OPS Extractor Loaded!")

prompt = "get balance sheet for Chase Bank"

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
