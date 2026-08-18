TEST_TOPICS = [
    "Python programming basics",
    "Python functions",
    "Python object oriented programming",
    "Python exception handling",
    "Python file handling",
    "Python modules and packages",
    "Python decorators",
    "Python generators",
    "Python data structures",
    "Python multithreading",

    "Java programming basics",
    "Java object oriented programming",
    "Java inheritance",
    "Java exception handling",
    "Java collections",
    "Java multithreading",
    "Java interfaces",
    "Java file handling",
    "Java JDBC",
    "Java streams",

    "C programming basics",
    "C pointers",
    "C arrays",
    "C structures",
    "C functions",
    "C file handling",
    "C memory management",
    "C recursion",

    "C++ programming basics",
    "C++ classes and objects",
    "C++ inheritance",
    "C++ polymorphism",
    "C++ templates",
    "C++ STL",
    "C++ exception handling",

    "Data structures",
    "Arrays and linked lists",
    "Stacks and queues",
    "Trees and binary trees",
    "Binary search trees",
    "Graphs",
    "Hash tables",
    "Sorting algorithms",
    "Searching algorithms",
    "Time complexity",

    "Database management systems",
    "SQL basics",
    "SQL joins",
    "Database normalization",
    "Transactions in DBMS",
    "PostgreSQL basics",

    "Machine learning basics",
    "Supervised learning",
    "Unsupervised learning",
    "Linear regression",
    "Logistic regression",
    "Decision trees",
    "Random forest",
    "Support vector machines",
    "K means clustering",
    "Feature engineering",

    "Deep learning",
    "Neural networks",
    "Convolutional neural networks",
    "Recurrent neural networks",
    "Natural language processing",
    "Generative AI",

    "Artificial intelligence basics",
    "AI agents",
    "LangChain",
    "LangGraph",
    "Vector databases",
    "Semantic search",
    "Retrieval augmented generation",

    "HTML basics",
    "CSS basics",
    "JavaScript basics",
    "React basics",
    "REST API",
    "FastAPI",
    "Web development",

    "Git basics",
    "GitHub basics",
    "Docker basics",
    "Cloud computing",
    "AWS basics",
    "Software testing",
    "Unit testing",
    "Pytest"
]


def test_dataset_contains_50_plus_topics():
    assert len(TEST_TOPICS) >= 50


def test_topics_are_not_empty():
    assert all(topic.strip() for topic in TEST_TOPICS)


def test_topics_are_unique():
    assert len(TEST_TOPICS) == len(set(TEST_TOPICS))