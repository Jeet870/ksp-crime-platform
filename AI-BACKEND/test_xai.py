# test_xai.py
from xai_builder import build_xai_trace

result = build_xai_trace(
    fir_id=1,
    similar_firs=[
        {"fir_number":"FIR-2023-BTM-015","crime_type":"burglary","similarity_score":0.87,"date_filed":"2023-03-12"},
        {"fir_number":"FIR-2023-MG-044","crime_type":"burglary","similarity_score":0.72,"date_filed":"2023-05-20"},
    ],
)

print(f"Risk Level: {result['risk_level']}")
print(f"Risk Score: {result['risk_score']}/100")
print(f"Reasons:")
for r in result['reasons']:
    print(f"  - {r}")
print(f"Disclaimer: {result['disclaimer']}")