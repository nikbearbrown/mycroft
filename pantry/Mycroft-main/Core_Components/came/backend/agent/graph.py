from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    event_normalizer,
    state_builder,
    pattern_engine,
    behavior_modeler,
    drift_detector,
    strategy_synthesizer,
)


def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    g.add_node("event_normalizer", event_normalizer)
    g.add_node("state_builder", state_builder)
    g.add_node("pattern_engine", pattern_engine)
    g.add_node("behavior_modeler", behavior_modeler)
    g.add_node("drift_detector", drift_detector)
    g.add_node("strategy_synthesizer", strategy_synthesizer)

    g.set_entry_point("event_normalizer")
    g.add_edge("event_normalizer", "state_builder")
    g.add_edge("state_builder", "pattern_engine")
    g.add_edge("pattern_engine", "behavior_modeler")
    g.add_edge("behavior_modeler", "drift_detector")
    g.add_edge("drift_detector", "strategy_synthesizer")
    g.add_edge("strategy_synthesizer", END)

    return g.compile()


came_graph = build_graph()
