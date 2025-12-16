# pipeline/router.py

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .model_registry import ROUTER_PATH


class CoarseRouter:
    """
    Wrapper for MiniLM coarse-intent classifier.
    """

    # 🔥 Official mapping from your model
    ID2LABEL = {
        0: "AMBIGUOUS",
        1: "AP",
        2: "AR",
        3: "OPS",
        4: "PAYROLL",
        5: "UNKNOWN",
    }

    def __init__(self):
        print("[Router] Loading coarse intent router...")
        self.tokenizer = AutoTokenizer.from_pretrained(ROUTER_PATH)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            ROUTER_PATH,
            device_map="auto",
            torch_dtype=torch.float16
        )

        print("[Router] Loaded successfully.")
        print("[Router] Labels:", self.ID2LABEL)

    def predict(self, text: str):
        """
        Classifies user text into a coarse business intent.

        Returns a dict:
        {
            "coarse_intent": str,
            "confidence": float,
            "logits": list
        }
        """

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            logits = self.model(**inputs).logits[0]
            probs = F.softmax(logits, dim=-1)

        top_id = torch.argmax(probs).item()
        label = self.ID2LABEL.get(top_id, "UNKNOWN")

        return {
            "coarse_intent": label,
            "confidence": float(probs[top_id]),
            "logits": logits.cpu().tolist(),
        }
