import services.llm_service as llm_service


def fake_gemini(prompt):
    raise Exception("Simulated API failure")


llm_service.ask_gemini = fake_gemini


try:
    llm_service.ask_llm(
        "Test retry mechanism",
        provider="gemini"
    )
except Exception as e:
    print(f"Final error caught: {e}")