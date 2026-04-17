import torch
from transformers import AutoTokenizer, AutoModel

ENCODER_PATH = "models/OPS/encoder"

print("="*60)
print("Loading OPS Encoder...")
print("="*60)

tokenizer = AutoTokenizer.from_pretrained(ENCODER_PATH)
model = AutoModel.from_pretrained(
    ENCODER_PATH,
    device_map="auto",
    torch_dtype=torch.float16
)

print("OPS Encoder Loaded Successfully!")

text = "get profit and loss report for last month"
inputs = tokenizer(text, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model(**inputs)

hidden = outputs.last_hidden_state

print("\n=== OPS Encoder Test Output ===")
print("Device:", model.device)
print("Hidden state shape:", hidden.shape)
print("Sample hidden vector:", hidden[0, 0, :10])
print("="*60)
