\# ISML AI Agent - API Documentation



\## 1. API Overview



The ISML AI Agent provides a REST API built using FastAPI.



The API is responsible for:



\* Checking application health

\* Creating learning resources

\* Retrieving learning resources

\* Retrieving a resource by ID

\* Deleting resources

\* Performing semantic resource search



\### Application Details



| Property         | Value                                |

| ---------------- | ------------------------------------ |

| Framework        | FastAPI                              |

| Application Name | ISML AI Agent                        |

| Version          | 1.0.0                                |

| Description      | Academic Resource Intelligence Agent |

| Database         | PostgreSQL                           |

| ORM              | SQLAlchemy                           |

| Vector Search    | pgvector                             |



\---



\## 2. API Base



The API runs through the FastAPI application defined in:



```text id="tq8vpr"

app/main.py

```



FastAPI automatically provides interactive API documentation through its documentation interfaces when the application is running.



\---



\## 3. Root Endpoint



\### `GET /`



Checks whether the ISML AI Agent application is running.



\### Response



```json id="8kghhf"

{

&#x20; "message": "ISML AI Agent is running"

}

```



\---



\## 4. Health Check Endpoint



\### `GET /health`



Checks the health status of the application.



\### Response



```json id="t4vqqr"

{

&#x20; "status": "healthy",

&#x20; "service": "ISML AI Agent"

}

```



\---



\## 5. Create Resource



\### `POST /resources`



Creates a new academic learning resource.



\### Request Body



The request uses the `ResourceCreate` Pydantic model.



| Field                    | Type   | Required | Description                  |

| ------------------------ | ------ | -------- | ---------------------------- |

| `title`                  | string | Yes      | Resource title               |

| `url`                    | string | Yes      | Resource URL                 |

| `resource\_type`          | string | Yes      | Type of learning resource    |

| `source`                 | string | Yes      | Resource source              |

| `description`            | string | No       | Resource description         |

| `content`                | string | No       | Resource content             |

| `relevance\_score`        | float  | No       | Relevance score              |

| `educational\_quality`    | float  | No       | Educational quality score    |

| `credibility`            | float  | No       | Credibility score            |

| `learning\_effectiveness` | float  | No       | Learning effectiveness score |

| `overall\_score`          | float  | No       | Overall resource score       |



\### Example Request



```json id="h5q9bc"

{

&#x20; "title": "Introduction to Python",

&#x20; "url": "https://example.com/python",

&#x20; "resource\_type": "article",

&#x20; "source": "Example",

&#x20; "description": "Python programming basics",

&#x20; "content": "Introduction to Python programming",

&#x20; "relevance\_score": 0.9,

&#x20; "educational\_quality": 0.85,

&#x20; "credibility": 0.9,

&#x20; "learning\_effectiveness": 0.88,

&#x20; "overall\_score": 0.88

}

```



\### Response



```json id="b0d5ut"

{

&#x20; "message": "Resource created successfully",

&#x20; "id": 1,

&#x20; "title": "Introduction to Python",

&#x20; "url": "https://example.com/python",

&#x20; "overall\_score": 0.88

}

```



\---



\## 6. Get All Resources



\### `GET /resources`



Retrieves all stored learning resources.



\### Response



The endpoint returns a list of resources.



```json id="9x7q1a"

\[

&#x20; {

&#x20;   "id": 1,

&#x20;   "title": "Introduction to Python",

&#x20;   "url": "https://example.com/python",

&#x20;   "resource\_type": "article",

&#x20;   "source": "Example",

&#x20;   "description": "Python programming basics",

&#x20;   "overall\_score": 0.88

&#x20; }

]

```



\---



\## 7. Get Resource by ID



\### `GET /resources/{resource\_id}`



Retrieves a specific learning resource using its ID.



\### Path Parameter



| Parameter     | Type    | Description        |

| ------------- | ------- | ------------------ |

| `resource\_id` | integer | Unique resource ID |



\### Example



```text id="u4p2jz"

GET /resources/1

```



\### Response



```json id="8ldvgu"

{

&#x20; "id": 1,

&#x20; "title": "Introduction to Python",

&#x20; "url": "https://example.com/python",

&#x20; "resource\_type": "article",

&#x20; "source": "Example",

&#x20; "description": "Python programming basics",

&#x20; "content": "Introduction to Python programming",

&#x20; "relevance\_score": 0.9,

&#x20; "educational\_quality": 0.85,

&#x20; "credibility": 0.9,

&#x20; "learning\_effectiveness": 0.88,

&#x20; "overall\_score": 0.88,

&#x20; "created\_at": "2026-08-19T10:00:00"

}

```



\### Error Response



If the resource does not exist:



```json id="6e3qtp"

{

&#x20; "detail": "Resource not found"

}

```



HTTP status:



```text id="2c2l9j"

404 Not Found

```



\---



\## 8. Delete Resource



\### `DELETE /resources/{resource\_id}`



Deletes a learning resource using its ID.



\### Path Parameter



| Parameter     | Type    | Description        |

| ------------- | ------- | ------------------ |

| `resource\_id` | integer | Unique resource ID |



\### Example



```text id="d9b7m2"

DELETE /resources/1

```



\### Successful Response



```json id="x6f7av"

{

&#x20; "message": "Resource deleted successfully",

&#x20; "id": 1

}

```



\### Error Response



If the resource does not exist:



```json id="v1q3hx"

{

&#x20; "detail": "Resource not found"

}

```



HTTP status:



```text id="h7y0ps"

404 Not Found

```



\---



\## 9. Semantic Resource Search



\### `GET /resources/search`



Searches for learning resources using semantic similarity.



The endpoint converts the user's query into an embedding and compares it with stored resource embeddings.



\### Query Parameters



| Parameter | Type    | Required | Default | Description                 |

| --------- | ------- | -------- | ------- | --------------------------- |

| `query`   | string  | Yes      | -       | User's search query         |

| `limit`   | integer | No       | 5       | Number of results to return |



The allowed `limit` range is:



```text id="b7u0dy"

1 to 20

```



\### Example



```text id="9e6j2s"

GET /resources/search?query=python programming\&limit=5

```



\### Response



```json id="5d8w0k"

{

&#x20; "query": "python programming",

&#x20; "count": 2,

&#x20; "results": \[

&#x20;   {

&#x20;     "id": 1,

&#x20;     "title": "Introduction to Python",

&#x20;     "url": "https://example.com/python",

&#x20;     "resource\_type": "article",

&#x20;     "source": "Example",

&#x20;     "description": "Python programming basics",

&#x20;     "similarity\_distance": 0.1234

&#x20;   }

&#x20; ]

}

```



\### Validation Errors



If the query is empty:



```json id="0y4d6k"

{

&#x20; "detail": "Query cannot be empty"

}

```



HTTP status:



```text id="r1t4fm"

400 Bad Request

```



If the limit is outside the allowed range:



```json id="g9z6xq"

{

&#x20; "detail": "Limit must be between 1 and 20"

}

```



HTTP status:



```text id="w2h5cs"

400 Bad Request

```



\---



\## 10. Semantic Search Flow



The semantic search endpoint follows this process:



```text id="1x2n6c"

User Query

&#x20;   ↓

Generate Query Embedding

&#x20;   ↓

Compare with Resource Embeddings

&#x20;   ↓

Find Similar Resources

&#x20;   ↓

Apply Result Limit

&#x20;   ↓

Return Ranked Results

```



The query embedding is generated using the embedding service.



The database search is performed through:



`search\_similar\_resources`



\---



\## 11. Database Session Handling



Resource endpoints create a database session using:



```python id="r0l2kp"

db = SessionLocal()

```



After the database operation is completed, the session is closed:



```python id="a3f9ws"

finally:

&#x20;   db.close()

```



This ensures that database sessions are properly released.



\---



\## 12. CORS Configuration



The application enables CORS middleware.



The current configuration allows:



\* All origins

\* All HTTP methods

\* All headers



This is configured in `app/main.py` using FastAPI's `CORSMiddleware`.



The current configuration is suitable for development and testing.



For production deployment, the allowed origins should be restricted to trusted applications.



\---



\## 13. Logging



The API uses Python's built-in logging module.



The logging level is configured as:



```python id="j2c5nv"

logging.basicConfig(level=logging.INFO)

```



Important API operations such as the root endpoint and health check generate informational log messages.



\---



\## 14. API Endpoint Summary



| Method   | Endpoint                   | Purpose                          |

| -------- | -------------------------- | -------------------------------- |

| `GET`    | `/`                        | Check application availability   |

| `GET`    | `/health`                  | Check application health         |

| `POST`   | `/resources`               | Create a resource                |

| `GET`    | `/resources`               | Get all resources                |

| `GET`    | `/resources/{resource\_id}` | Get a resource by ID             |

| `DELETE` | `/resources/{resource\_id}` | Delete a resource                |

| `GET`    | `/resources/search`        | Perform semantic resource search |



\---



\## 15. Current API Summary



The FastAPI layer provides the main REST interface for the ISML AI Agent.



The current implementation supports:



\* Application health monitoring

\* Resource creation

\* Resource retrieval

\* Resource deletion

\* Semantic similarity search

\* Request validation

\* Database session management

\* API logging

\* CORS support



This API layer connects the application logic, database layer, and semantic search functionality into a single service interface.



