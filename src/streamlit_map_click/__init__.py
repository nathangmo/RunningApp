import os
import streamlit.components.v1 as components

_component = components.declare_component(
    "map_click_component",
    path=os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend")),
)

def map_click(deck_json, key=None):
    return _component(deck_json=deck_json, default=None, key=key)
