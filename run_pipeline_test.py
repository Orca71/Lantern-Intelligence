# run_pipeline_test.py

import json
from pipeline.controller import run_pipeline   # ✅ USE CONTROLLER ONLY

def pretty_print_result(result):
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=4))
    else:
        print(result)

if __name__ == "__main__":
    tests = [
        "create a bill for Verizon for $220",
    ]

    for t in tests:
        print("\n" + "=" * 80)
        print("INPUT:", t)

        try:
            result = run_pipeline(t)
        except Exception as e:
            print("❌ Pipeline crashed:", repr(e))
            continue

        print("\n--- Pipeline Output ---")
        pretty_print_result(result)

        print("=" * 80)
        print()
