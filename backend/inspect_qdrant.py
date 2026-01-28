from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig, ScalarType
import json

print("--- ScalarQuantization fields ---")
print(ScalarQuantization.model_fields.keys())

print("\n--- ScalarQuantizationConfig fields ---")
print(ScalarQuantizationConfig.model_fields.keys())

print("\n--- ScalarType values ---")
print([v.value for v in ScalarType])
