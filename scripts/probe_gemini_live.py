import os
import sys
sys.path.insert(0, os.path.abspath("."))
from backend.config import load_dotenv
load_dotenv()
from backend.extraction.gemini_provider import GeminiProvider

prov = GeminiProvider()
print("Provider:", prov.provider_name, "Model:", prov.model_name, "Fallback:", prov.fallback_model)

pdf_path = "data/demo/JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

print(f"Sending {len(pdf_bytes)} bytes of PDF to Gemini via generate_structured_from_pdf...")
resp = prov.generate_structured_from_pdf(
    pdf_bytes=pdf_bytes,
    prompt='Extract company name and return JSON: {"company_name": "..."}',
    system_prompt='You are a document analyzer. Respond only with JSON: {"company_name": "..."}',
)

print("Response error:", resp.error)
print("Response content:", resp.content)
print("Response model:", resp.model_name)
print("Latency ms:", resp.latency_ms)
