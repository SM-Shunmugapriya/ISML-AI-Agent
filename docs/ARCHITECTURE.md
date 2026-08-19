\# ISML AI Agent - System Architecture



\## 1. Project Overview



ISML AI Agent is an AI-powered academic resource intelligence system.



The main purpose of the system is to analyze a user's learning topic, discover relevant learning resources, evaluate those resources, rank them based on relevance, and provide useful resources to the user.



The system uses AI, web search, YouTube search, PDF discovery, embeddings, PostgreSQL, and pgvector.



\---



\## 2. System Architecture



The overall flow of the system is:



User Query

&#x20;   ↓

Topic Analysis

&#x20;   ↓

Search Strategy

&#x20;   ↓

Resource Discovery

&#x20;   ↓

Resource Evaluation

&#x20;   ↓

Resource Ranking

&#x20;   ↓

Semantic Similarity Search

&#x20;   ↓

Recommended Learning Resources



\---



\## 3. Main Components



\### 3.1 Agent Layer



The agent layer manages the overall workflow of the AI agent.



Main components:



\- `agents/state.py`

\- `agents/topic\_analysis.py`

\- `agents/search\_strategy.py`

\- `agents/workflow.py`



\### 3.2 Search Tools



The system uses different tools to discover learning resources.



Main tools:



\- `tools/web\_search.py`

\- `tools/youtube\_search.py`

\- `tools/pdf\_search.py`

\- `tools/metadata\_extractor.py`



These tools help discover resources from different sources.



\### 3.3 LLM Services



The project contains services for interacting with Large Language Models.



Main components:



\- `services/llm\_service.py`

\- `services/gemini\_service.py`

\- `services/deepseek\_service.py`

\- `services/json\_parser.py`



Gemini is used as the primary LLM service in the current implementation.



\### 3.4 Resource Evaluation



After discovering resources, the system evaluates their quality and relevance.



Main component:



\- `services/resource\_evaluator.py`



The evaluator helps determine how useful a resource is for the requested topic.



\### 3.5 Resource Ranking



Resources are ranked based on their relevance and evaluation results.



Main component:



\- `services/resource\_ranker.py`



This helps the system provide better resources first.



\### 3.6 Embedding and Semantic Search



The system uses embeddings to represent resources as vectors.



Main components:



\- `services/embedding\_service.py`

\- `services/generate\_resource\_embeddings.py`



The generated embeddings are stored in PostgreSQL using pgvector.



Semantic similarity search is used to find resources that are conceptually relevant to the user's query.



\---



\## 4. Database Architecture



The project uses PostgreSQL as the database.



The system also uses the pgvector extension for storing and searching vector embeddings.



Main database components:



\- `database/database.py`

\- `database/models.py`

\- `database/init\_db.py`



The database stores resource information along with embedding data.



\---



\## 5. Agent Workflow



The agent follows a structured workflow.



\### Step 1 - Topic Analysis



The user's learning query is analyzed to understand the topic and requirements.



\### Step 2 - Search Strategy



The system decides how the required resources should be discovered.



\### Step 3 - Resource Discovery



The system searches for relevant:



\- Web resources

\- YouTube videos

\- PDF resources



\### Step 4 - Resource Evaluation



The discovered resources are evaluated based on their relevance and quality.



\### Step 5 - Resource Ranking



The evaluated resources are ranked so that the most useful resources can be selected.



\### Step 6 - Semantic Search



Embeddings and vector similarity are used to identify semantically relevant resources.



\### Step 7 - Final Recommendation



The system provides the most relevant learning resources for the requested topic.



\---



\## 6. Performance and Reliability



The project includes several mechanisms for improving reliability and performance.



\### Logging



`services/logger.py`



Structured logging is used to track system activities and errors.



\### Retry Handling



The LLM request process includes retry logic to handle temporary failures.



\### Caching



`services/cache.py`



Caching is used to reduce unnecessary repeated operations and improve performance.



\---



\## 7. Testing



The project contains tests for the major resource processing components.



Important test files include:



\- `tests/test\_dataset.py`

\- `tests/test\_resource\_discovery.py`

\- `tests/test\_resource\_evaluator.py`

\- `tests/test\_resource\_ranker.py`



A comprehensive test dataset containing 60 topics was also created for testing.



\---



\## 8. Project Structure



```text

ISML-AI-Agent/

│

├── agents/

│   ├── state.py

│   ├── topic\_analysis.py

│   ├── search\_strategy.py

│   └── workflow.py

│

├── database/

│   ├── database.py

│   ├── models.py

│   └── init\_db.py

│

├── services/

│   ├── llm\_service.py

│   ├── gemini\_service.py

│   ├── deepseek\_service.py

│   ├── embedding\_service.py

│   ├── generate\_resource\_embeddings.py

│   ├── resource\_evaluator.py

│   ├── resource\_ranker.py

│   ├── cache.py

│   └── logger.py

│

├── tools/

│   ├── web\_search.py

│   ├── youtube\_search.py

│   ├── pdf\_search.py

│   └── metadata\_extractor.py

│

├── prompts/

│   ├── system\_prompt.py

│   └── task\_prompt.py

│

├── tests/

│   ├── test\_dataset.py

│   ├── test\_resource\_discovery.py

│   ├── test\_resource\_evaluator.py

│   └── test\_resource\_ranker.py

│

└── docs/

&#x20;   └── ARCHITECTURE.md

