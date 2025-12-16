from transformers import AutoTokenizer, AutoModel
import torch

ENCODER_PATH = "models/AP/encoder"

print("Loading AP encoder...")
tokenizer = AutoTokenizer.from_pretrained(ENCODER_PATH)
model = AutoModel.from_pretrained(ENCODER_PATH)

print("Loaded successfully!")

text = "pay Verizon broadband invoice"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    out = model(**inputs)

print("Encoder output shape:", out.last_hidden_state.shape)
