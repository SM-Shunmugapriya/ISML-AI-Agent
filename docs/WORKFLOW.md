\# ISML AI Agent - Workflow Documentation



\## 4. Topic Analysis Node



\### Function



`analyze\_topic`



\### Purpose



The topic analysis node processes the user's query and extracts useful information about the learning topic.



The `AgentState` supports information such as:



\* `user\_query`

\* `topic`

\* `subtopics`

\* `learning\_intent`



\---



\## 5. Search Strategy Node



\### Function



`generate\_search\_strategy`



\### Purpose



The search strategy node generates search queries based on the analyzed topic.



The generated search queries are stored in:



`search\_queries`



These queries can be used for discovering relevant academic learning resources.



\---



\## 6. Agent State



\### File



`agents/state.py`



The workflow uses a TypedDict called `AgentState`.



Current state fields:



| Field             | Type        | Purpose                         |

| ----------------- | ----------- | ------------------------------- |

| `user\_query`      | `str`       | Stores the original user query  |

| `topic`           | `str`       | Stores the analyzed topic       |

| `subtopics`       | `List\[str]` | Stores identified subtopics     |

| `learning\_intent` | `str`       | Stores the learning intent      |

| `search\_queries`  | `List\[str]` | Stores generated search queries |

| `search\_results`  | `List\[str]` | Stores search results           |

| `final\_answer`    | `str`       | Stores the final response       |



\---



\## 7. Workflow Connections



The workflow defines the following connections:



\### Start to Topic Analysis



```text

START → topic\_analysis

```



The workflow begins with topic analysis.



\### Topic Analysis to Search Strategy



```text

topic\_analysis → search\_strategy

```



After analyzing the topic, the workflow passes the state to the search strategy node.



\### Search Strategy to End



```text

search\_strategy → END

```



After generating the search strategy, the current workflow reaches the end.



\---



\## 8. Workflow Compilation



After defining the nodes and connections, the LangGraph workflow is compiled into an executable application.



```python

graph.compile()

```



The compiled application is stored as:



`app`



\---



\## 9. Error Handling and Logging



The workflow initialization is wrapped in a `try-except` block.



If the workflow is initialized successfully, an informational log is generated.



If initialization fails:



\* The error is logged.

\* The exception is raised again.



This provides visibility into workflow initialization problems.



\---



\## 10. Current Workflow Summary



The current implementation provides the foundation for the AI agent workflow.



The workflow currently focuses on:



\* Receiving a user query

\* Analyzing the topic

\* Generating a search strategy

\* Maintaining agent state

\* Compiling the LangGraph workflow



The state structure also contains fields for search results and the final answer, which can support further workflow stages as the project evolves.



