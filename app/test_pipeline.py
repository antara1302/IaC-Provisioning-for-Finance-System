from core.triage_agent import run_triage

result = run_triage("URGENT: My account ACC-992841 has been compromised with unauthorized transfers of $45,000.")

print("Status:", result["status"])
print("Urgency:", result["urgency"])
print("\nPipeline steps:")
for step, data in result["pipeline"].items():
    status = data["status"]
    print(f"  {step}: {status}")
    if status == "error":
        print(f"    ERROR: {data['error']}")

print("\nDraft subject:", result["draft_response"]["subject"])
print("\nDraft body:")
print(result["draft_response"]["body"])