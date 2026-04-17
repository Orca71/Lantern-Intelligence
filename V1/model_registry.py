# pipeline/model_registry.py

BASE_MODELS_DIR = "models"

ROUTER_PATH = f"{BASE_MODELS_DIR}/router"

EXTRACTOR_PATHS = {
    "AP": "models/AP/decoder",
    "AR": "models/AR/decoder",
    "OPS": "models/OPS/decoder",
    "PAYROLL": "models/PAY/decoder",
}


# Encoders are defined here in case we want to use them later
ENCODER_PATHS = {
    "AP":  f"{BASE_MODELS_DIR}/AP/encoder",
    "AR":  f"{BASE_MODELS_DIR}/AR/encoder",
    "OPS": f"{BASE_MODELS_DIR}/OPS/encoder",
    "PAY": f"{BASE_MODELS_DIR}/PAY/encoder",
}
