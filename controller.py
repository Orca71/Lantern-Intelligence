from pipeline.router import CoarseRouter
from pipeline.fine_router import FineRouterManager
from pipeline.extractors import ExtractorManager
from pipeline.action_builder import ActionBuilder
from pipeline.action_executor import ActionExecutor      # ✅
from pipeline.li_a import LIAgent

lia = LIAgent()
coarse = CoarseRouter()
fine = FineRouterManager()
extractors = ExtractorManager()
actions = ActionBuilder()
executor = ActionExecutor()                              # ✅


def run_pipeline(user_text: str):

    # 1. Coarse router
    coarse_result = coarse.predict(user_text)
    domain = coarse_result["coarse_intent"]

    if domain in ["UNKNOWN", "AMBIGUOUS"]:
        # fallback; or just return a simple message
        return lia.handle_no_action(user_text)

    # 2. Fine router
    fine_intent = fine.predict(domain, user_text)

    # 3. Extractor
    extractor_result = extractors.run(domain, user_text, fine_intent)

    # 4. Action Builder + QuickBooks execution
    action = actions.build_from_extractor(extractor_result)

    if action is not None:
        extractor_result["action"] = action.to_dict()

        try:
            print(f"[Controller] Executing action: {action.name}")
            qb_result = executor.execute(action)          # ✅ QuickBooks call
        except Exception as e:
            qb_result = {"error": str(e)}

        extractor_result["action_result"] = qb_result
    else:
        extractor_result["action"] = None
        extractor_result["action_result"] = None

    # Attach router metadata
    extractor_result["router"] = coarse_result
    extractor_result["resolved_fine_intent"] = fine_intent

    # 5. LI-A builds final reply
    return lia.run(extractor_result)
