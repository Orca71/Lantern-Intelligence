# pipeline/fine_router.py

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .model_registry import ENCODER_PATHS


class FineRouterManager:

    def __init__(self):
        self.models = {}
        self.tokenizers = {}

        print("[FineRouter] Loading fine routers...")

        for domain, path in ENCODER_PATHS.items():
            domain = domain.upper()
            print(f"  - {domain} → {path}")

            self.tokenizers[domain] = AutoTokenizer.from_pretrained(path)
            self.models[domain] = AutoModelForSequenceClassification.from_pretrained(
                path,
                device_map="auto",
                torch_dtype=torch.float16
            )

        print("[FineRouter] Ready ✓\n")

    def predict(self, domain: str, text: str):
        domain = domain.upper()

        if domain not in self.models:
            raise ValueError(f"Missing fine router for {domain}")

        tokenizer = self.tokenizers[domain]
        model = self.models[domain]

        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            logits = model(**inputs).logits[0]
            probs = F.softmax(logits, dim=-1)

        top_id = torch.argmax(probs).item()
        label = model.config.id2label[top_id]

        return label
