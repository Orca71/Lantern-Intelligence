from transformers import AutoTokenizer, AutoModelForSequenceClassification

router_path = "models/router"

tokenizer = AutoTokenizer.from_pretrained(router_path)
model = AutoModelForSequenceClassification.from_pretrained(router_path)

text = "create bill for Verizon"

inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

print("Router loaded successfully!")
print("logits:", outputs.logits)
