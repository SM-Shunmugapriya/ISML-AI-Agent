\# ENH-014: Testing Strategy



\## Test Pyramid



\### Unit Tests

Test topic analysis, metadata extraction, evaluation, ranking, categorization, deduplication, learning sequence, and embedding logic independently.



\### Integration Tests

Test LLM and embedding services, search, PostgreSQL, pgvector, cache, and review queue interactions. Mock external API calls when needed.



\### End-to-End Tests

Verify the complete resource-learning workflow from query processing through discovery, validation, ranking, persistence, and retrieval.



\### Regression Tests

Run the complete pytest suite on pushes and pull requests targeting `main`.



\## Coverage Requirement

Minimum overall coverage: 70%.



Run locally:



```powershell

.\\venv311\\Scripts\\python.exe -m pytest -q --cov=agents --cov=services --cov=app --cov-report=term-missing --cov-fail-under=70

```



\## CI Requirements

\- Python 3.11

\- PostgreSQL with pgvector

\- Database initialized before testing

\- Coverage report generated

\- All regression tests pass



\## Local Verification

\- 166 tests passed

\- Overall coverage: 75.32%

\- CI verification still required

