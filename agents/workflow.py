from langgraph.graph import StateGraph, START, END
from agents.state import AgentState
from agents.topic_analysis import analyze_topic
from agents.search_strategy import generate_search_strategy


graph = StateGraph(AgentState)

graph.add_node("topic_analysis", analyze_topic)
graph.add_node("search_strategy", generate_search_strategy)

graph.add_edge(START, "topic_analysis")
graph.add_edge("topic_analysis", "search_strategy")

graph.add_edge("search_strategy", END)
app = graph.compile()