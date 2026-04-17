# pipeline/extractors.py

import json
import re
from typing import Dict, Any, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from .model_registry import EXTRACTOR_PATHS
from .required_fields import REQUIRED_FIELDS, get_missing_fields


# ----------------------------------------------------
# JSON extraction helper
# ----------------------------------------------------
def extract_last_json_block(text: str):
    """
    Extract the LAST top-level JSON object from the model output.

    Handles cases like:
        'pay bill for Verizon 300\n{...} {...}'
    by pulling only the final `{...}` block.
    """
    raw = text.strip()

    # Find all non-nested {...} blocks
    blocks = re.findall(r"\{[^{}]*\}", raw)
    if not blocks:
        return None, raw

    last = blocks[-1]

    # 1. try direct parse
    try:
        return json.loads(last), raw
    except Exception:
        pass

    # 2. attempt to fix malformed JSON
    fixed = last
    fixed = re.sub(r"}[^}]*$", "}", fixed)
    fixed = re.sub(r'"fine_intent[^"]*', '"fine_intent": null', fixed)
    fixed = fixed.replace("'", '"')
    fixed = re.sub(r",\s*}", "}", fixed)

    try:
        return json.loads(fixed), raw
    except Exception:
        return None, raw


# ----------------------------------------------------
# Unified extractor loader
# ----------------------------------------------------
class ExtractorManager:
    """Loads and runs AP/AR/OPS/PAYROLL extractors."""

    def __init__(self):
        self.models = {}
        self.tokenizers = {}

        print("[ExtractorManager] Loading fine extractors...")
        for domain, path in EXTRACTOR_PATHS.items():
            domain = domain.upper()
            print(f"  - {domain} → {path}")

            self.tokenizers[domain] = AutoTokenizer.from_pretrained(path)
            self.models[domain] = AutoModelForCausalLM.from_pretrained(
                path,
                device_map="auto",
                torch_dtype=torch.float16,
            )

        print("[ExtractorManager] Ready ✓\n")

    # ------------------------------------------------
    # Public extraction method
    # ------------------------------------------------
    def run(self, domain: str, text: str, fine_intent: str) -> Dict[str, Any]:
        domain = domain.upper()

        if domain not in self.models:
            return self._error_result(
                domain=domain,
                raw=None,
                msg=f"Unsupported extractor: {domain}",
            )

        model = self.models[domain]
        tokenizer = self.tokenizers[domain]

        # inference
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=128,
                do_sample=False,
                temperature=0.0,
            )

        decoded = tokenizer.decode(out[0], skip_special_tokens=True)
        parsed, raw = extract_last_json_block(decoded)

        if not parsed:
            return self._error_result(domain, raw, "Failed to parse JSON")

        # ------------------------------------------------
        # REQUIRED FIELDS CHECKING
        # ------------------------------------------------
        missing = get_missing_fields(domain, fine_intent, parsed)

        if missing:
            return {
                "status": "missing_fields",
                "domain": domain,
                "fine_intent": fine_intent,
                "missing": missing,
                "json": parsed,
                "raw_output": raw,
            }

        # ------------------------------------------------
        # COMPLETE extraction result
        # ------------------------------------------------
        return {
            "status": "complete",
            "domain": domain,
            "fine_intent": fine_intent,
            "json": parsed,
            "raw_output": raw,
        }

    # ------------------------------------------------
    # small utility
    # ------------------------------------------------
    def _error_result(self, domain, raw, msg):
        return {
            "domain": domain,
            "ok": False,
            "fine_intent": None,
            "missing_fields": [],
            "fields": None,
            "raw_output": raw,
            "error": msg,
        }
