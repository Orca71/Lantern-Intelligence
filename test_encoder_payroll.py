import torch
from transformers import AutoTokenizer, AutoModel

ENCODER_PATH = "models/PAY/encoder"

print("="*60)
print("Loading PAY Encoder...")
print("="*60)

tokenizer = AutoTokenizer.from_pretrained(ENCODER_PATH)
model = AutoModel.from_pretrained(
    ENCODER_PATH,
    device_map="auto",
    torch_dtype=torch.float16
)

print("PAY Encoder Loaded Successfully!")

text = "run payroll for staff"
inputs = tokenizer(text, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model(**inputs)

hidden = outputs.last_hidden_state

print("\n=== PAY Encoder Test Output ===")
print("Device:", model.device)
print("Hidden state shape:", hidden.shape)
print("Sample hidden vector:", hidden[0, 0, :10])
print("="*60)
