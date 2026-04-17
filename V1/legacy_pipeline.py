from .router import CoarseRouter
from .extractors import ExtractorManager


class LanternPipeline:
    """
    Full pipeline:
      1. Coarse router → AP/AR/OPS/PAYROLL
      2. Fine extractor → JSON fields
    """

    def __init__(self):
        print("[Pipeline] Initializing pipeline...")

        self.router = CoarseRouter()
        self.extractors = ExtractorManager()

        print("[Pipeline] Ready.\n")

    def run(self, text: str):
        """
        Returns the unified extraction result including both steps.
        """

        # -------------------------------
        # Step 1: Coarse routing
        # -------------------------------
        route = self.router.predict(text)
        domain = route["coarse_intent"]

        if domain in ["UNKNOWN", "AMBIGUOUS"]:
            return {
                "ok": False,
                "step": "routing",
                "router": route,
                "error": f"Could not classify: {domain}",
            }

        # -------------------------------
        # Step 2: Fine extraction
        # -------------------------------
        finer = self.extractors.run(domain, text)

        return {
            "ok": finer["ok"],
            "domain": domain,
            "router": route,
            "extractor": finer,
        }
