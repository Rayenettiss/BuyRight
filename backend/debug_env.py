import os
from dotenv import load_dotenv

load_dotenv()
print("--- ENV VARS START ---")
for k, v in os.environ.items():
    if any(pattern in k.upper() for pattern in ["QDRANT", "DATABASE", "VERTEX", "GOOGLE", "SECRET", "JWT"]):
        print(f"{k}: {v}")
print("--- ENV VARS END ---")

try:
    from config.settings import settings
    print("Settings loaded successfully")
except Exception as e:
    print(f"Error loading settings: {e}")
