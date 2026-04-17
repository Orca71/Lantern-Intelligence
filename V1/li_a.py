# pipeline/li_a.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re

class LIAgent:

    def __init__(self):
        print("[LI-A] Loading conversational brain (LIA)...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "models/LIA",
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            "models/LIA",
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True,
        )
        print("[LI-A] Ready ✓\n")

    def run(self, pipeline_result: dict) -> str:
        prompt = f"""
You are Lantern Intelligence, a professional accounting assistant.

You must read only the structured data below and produce a short,
business-friendly conversational response.

======================
PIPELINE RESULT (JSON):
{pipeline_result}
======================

Your Rules:
1. You MUST NOT re-parse or extract anything from natural language.
2. You MUST rely ONLY on the structured fields in pipeline_result.
3. If pipeline_result["status"] == "missing_fields":
       → Ask ONLY for the missing fields.
4. If pipeline_result contains "action_result" with an "error":
       → Explain briefly what failed and suggest next steps.
5. If pipeline_result contains "action_result" with QuickBooks JSON:
       → Summarize what was successfully recorded (bill, payment, etc.).
6. If no action was created:
       → Tell the user nothing actionable was detected.
7. Keep responses friendly, concise, and professional.
8. NEVER output JSON—only natural language.
9. Respond as a single short message. Do NOT continue a multi-turn dialogue.

Now write your single, final answer for the user:
"""

        encoded = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        out = self.model.generate(
            **encoded,
            max_new_tokens=200,
            do_sample=False,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        text = self.tokenizer.decode(out[0], skip_special_tokens=True)

        # Safety: if it hallucinated "User:" later, cut at the first such marker
        cut = re.split(r"\bUser:\b", text, maxsplit=1)[0]

        # Return only the part after the prompt
        return cut.strip()
