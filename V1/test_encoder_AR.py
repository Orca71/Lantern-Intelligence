import torch
from transformers import AutoTokenizer, AutoModel

ENCODER_PATH = "models/AR/encoder"

print("="*60)
print("Loading AR Encoder...")
print("="*60)

tokenizer = AutoTokenizer.from_pretrained(ENCODER_PATH)
model = AutoModel.from_pretrained(
    ENCODER_PATH,
    device_map="auto",
    torch_dtype=torch.float16
)

print("Model + tokenizer loaded successfully")

text = "get customer balance from AT&T"
inputs = tokenizer(text, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model(**inputs)

hidden = outputs.last_hidden_state

print("\n=== AR Encoder Test Output ===")
print("Device loaded on:", model.device)
print("Hidden state shape:", hidden.shape)
print("Attention mask:", inputs["attention_mask"].shape)
print("Sample hidden vector:", hidden[0, 0, :10])
print("="*60)
