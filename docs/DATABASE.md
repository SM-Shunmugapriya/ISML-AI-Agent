\# ISML AI Agent - Database Documentation



\## 1. Database Overview



The ISML AI Agent uses PostgreSQL as the primary database.



SQLAlchemy is used as the ORM (Object Relational Mapper) to communicate with the PostgreSQL database.



The project also uses the `pgvector` extension to store and work with vector embeddings for semantic similarity search.



\---



\## 2. Database Files



The database implementation is located inside:



```text

app/database/

```



Main database files:



| File          | Purpose                                                      |

| ------------- | ------------------------------------------------------------ |

| `database.py` | Creates the database connection and SQLAlchemy configuration |

| `models.py`   | Defines database tables and columns                          |

| `init\_db.py`  | Creates database tables                                      |



\---



\## 3. Database Connection



\### File



`app/database/database.py`



The application loads database configuration from the `.env` file using `python-dotenv`.



The following environment variables are used:



\* `POSTGRES\_USER`

\* `POSTGRES\_PASSWORD`

\* `POSTGRES\_HOST`

\* `POSTGRES\_PORT`

\* `POSTGRES\_DB`



The database URL follows this format:



```text

postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE

```



SQLAlchemy creates the database engine using this connection URL.



\---



\## 4. SQLAlchemy Configuration



The project creates an SQLAlchemy engine:



```python

engine = create\_engine(DATABASE\_URL)

```



A session factory is created using:



```python

SessionLocal = sessionmaker(

&#x20;   autocommit=False,

&#x20;   autoflush=False,

&#x20;   bind=engine

)

```



The project also creates a declarative base:



```python

Base = declarative\_base()

```



All database models inherit from this `Base`.



\---



\## 5. Resource Table



\### Table Name



`resources`



The main database table is represented by the `Resource` model.



File:



`app/database/models.py`



The model inherits from SQLAlchemy's `Base`.



```python

class Resource(Base):

&#x20;   \_\_tablename\_\_ = "resources"

```



\---



\## 6. Resource Table Columns



| Column                   | Type         | Description                               |

| ------------------------ | ------------ | ----------------------------------------- |

| `id`                     | Integer      | Primary key and indexed identifier        |

| `title`                  | String(500)  | Title of the learning resource            |

| `url`                    | String(1000) | Resource URL; must be unique              |

| `resource\_type`          | String(50)   | Type of resource                          |

| `source`                 | String(100)  | Resource source                           |

| `description`            | Text         | Optional resource description             |

| `content`                | Text         | Optional resource content                 |

| `relevance\_score`        | Float        | Relevance score of the resource           |

| `educational\_quality`    | Float        | Educational quality score                 |

| `credibility`            | Float        | Credibility score                         |

| `learning\_effectiveness` | Float        | Learning effectiveness score              |

| `overall\_score`          | Float        | Overall resource score                    |

| `embedding`              | Vector(3072) | Vector embedding used for semantic search |

| `created\_at`             | DateTime     | Resource creation timestamp               |



\---



\## 7. Primary Key and Constraints



The `id` column is the primary key.



```python

id: Mapped\[int] = mapped\_column(

&#x20;   Integer,

&#x20;   primary\_key=True,

&#x20;   index=True

)

```



The `url` column is unique to prevent duplicate resource URLs.



```python

url: Mapped\[str] = mapped\_column(

&#x20;   String(1000),

&#x20;   nullable=False,

&#x20;   unique=True

)

```



Required fields use `nullable=False`.



Optional fields such as `description`, `content`, and scoring fields allow null values.



\---



\## 8. Resource Scoring



The database stores multiple evaluation scores for each learning resource.



These include:



\* `relevance\_score`

\* `educational\_quality`

\* `credibility`

\* `learning\_effectiveness`

\* `overall\_score`



These values allow the application to evaluate and rank discovered learning resources.



\---



\## 9. Vector Embeddings



The `embedding` column uses `pgvector`.



```python

embedding: Mapped\[list\[float] | None] = mapped\_column(

&#x20;   Vector(3072),

&#x20;   nullable=True

)

```



The vector dimension is:



```text

3072

```



These embeddings are used for semantic similarity search.



This allows the system to compare the meaning of a user's query with stored learning resources rather than relying only on exact keyword matching.



\---



\## 10. Timestamp



The `created\_at` column stores the creation time of each resource.



```python

created\_at: Mapped\[datetime] = mapped\_column(

&#x20;   DateTime,

&#x20;   default=datetime.utcnow,

&#x20;   nullable=False

)

```



If a value is not provided, the current UTC time is automatically assigned.



\---



\## 11. Database Initialization



\### File



`app/database/init\_db.py`



The database tables are created using:



```python

Base.metadata.create\_all(bind=engine)

```



The `Resource` model is imported before creating the tables so SQLAlchemy can register the model metadata.



The initialization function is:



```python

def init\_db():

&#x20;   Base.metadata.create\_all(bind=engine)

&#x20;   print("Database tables created successfully.")

```



The file can also be executed directly:



```python

if \_\_name\_\_ == "\_\_main\_\_":

&#x20;   init\_db()

```



\---



\## 12. Database Flow



The current database flow is:



```text

.env

&#x20; ↓

Database Configuration

&#x20; ↓

SQLAlchemy Engine

&#x20; ↓

SessionLocal

&#x20; ↓

Base Model

&#x20; ↓

Resource Model

&#x20; ↓

resources Table

&#x20; ↓

Resource Evaluation + Embeddings

```



\---



\## 13. Database Role in the AI Agent



The database provides persistent storage for discovered learning resources.



The stored information can be used for:



\* Resource management

\* Resource evaluation

\* Resource ranking

\* Semantic similarity search

\* Embedding-based retrieval

\* Avoiding duplicate URLs



The database therefore acts as the persistent storage layer of the ISML AI Agent.



\---



\## 14. Current Database Summary



The current implementation provides:



\* PostgreSQL database integration

\* SQLAlchemy ORM configuration

\* Resource data persistence

\* Resource scoring storage

\* pgvector embedding storage

\* Unique resource URL constraint

\* Automatic creation timestamps

\* Database table initialization



The database layer provides the foundation for storing and retrieving academic learning resources in the ISML AI Agent.



