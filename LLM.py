from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

llm = ChatNVIDIA(
    model='meta/llama-3.2-3b-instruct',
    base_url='https://integrate.api.nvidia.com/v1',
    temperature=0,
    api_key=''
)
template = ChatPromptTemplate.from_template("""
You are an expert JSON-only classifier for feedback about 
the Saudi Electricity Regulatory Authority.

Use the organizational structure below to determine the correct responsible department. Each department has a clear mandate:

1. Communication & Media — Manages internal/external communication, media relations, awareness campaigns, and all public-facing communication channels.

2. Governance, Risk & Compliance — Ensures proper governance practices, manages enterprise risks, monitors regulatory compliance, and strengthens transparency and integrity.

3. Strategy & Excellence — Develops strategic plans, monitors organizational performance, leads corporate initiatives, and applies best-practice frameworks to achieve operational excellence.

4. Sector Monitoring & Inspection — Conducts monitoring, auditing, and inspection activities across the electricity sector to ensure adherence to regulations, service standards, and operational requirements.

5. Shared Services — Provides centralized support functions such as HR, finance, procurement, IT, digital transformation, and facility services to enable smooth operations.

6. Legal Affairs & Regulations — Handles legal matters, drafts/reviews regulations, ensures regulatory alignment, provides legal guidance, and manages the development and enforcement of sector rules.

7. Technical Affairs — Oversees technical operations related to electrical systems, engineering standards, quality, safety, and crisis management to ensure reliable and safe electricity services.

8. Economic Affairs & Licensing — Responsible for market analysis, tariff & cost studies, economic regulation, and the management/issuance of operational licenses.

9. Consumer Affairs — Handles consumer care, service complaints, consumer experience, consumer protection, and transparent consumer relations.

Choose EXACTLY ONE responsible department.

Urgency classification rules:
- Critical → safety risk, outage, danger, emergency, severe service failure, or contractor negligence causing risk.
- High → major service interruption or significant operational impact.
- Medium → operational issue or inconvenience with no safety risk.
- Low → minor issue or suggestion.
- Positive → if the message is positive.

Follow these rules STRICTLY:
- DO NOT explain anything.
- DO NOT write code.
- DO NOT add notes.
- ONLY return valid JSON.

Your tasks:
1. Detect the language of the input.
2. If the text is Arabic, translate it to English while keeping the full meaning and context. Do NOT translate word by word.
3. Classify sentiment (positive/neutral/negative).
4. Classify EXACTLY ONE responsible department by its name.
5. Classify EXACTLY ONE urgency level.
6. Classify issue_category based on the English text.
7. Return ONLY JSON, nothing before or after.

Input text:
{text}

Return EXACTLY this JSON structure:

{{{{ 
 "english_text": "",
 "sentiment": "",
 "Responsible_Department": "",
 "urgency": "",
 "issue_category": ""
}}}}
""")


parser = StrOutputParser()

chain = template | llm | parser


raw_output = chain.batch([
    {"text": w} for w in word
])

result = []

for item in raw_output:
    # Each item is already a string from StrOutputParser
    cleaned = item.replace("{{", "{").replace("}}", "}")
    result = json.loads(cleaned)

print(result)

import pandas as pd
from datetime import datetime
import os

# Save each prediction to a CSV log
log_row = {
    "original_text": word.strip(),
    "english_text": result["english_text"],
    "sentiment": result["sentiment"],
    "responsible_department": result["Responsible_Department"],
    "urgency": result["urgency"],
    "issue_category": result["issue_category"],
    "date": datetime.now().strftime("%Y-%m-%d")
}

file_path = "feedback_log.csv"

if os.path.exists(file_path):
    df_log = pd.read_csv(file_path, encoding="utf-8-sig")
    df_log = pd.concat([df_log, pd.DataFrame([log_row])], ignore_index=True)
else:
    df_log = pd.DataFrame([log_row])

df_log.to_csv(file_path, index=False, encoding="utf-8-sig")
