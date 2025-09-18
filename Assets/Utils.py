import re
from rdflib import Graph, URIRef

def load_graph(file_path):
    g = Graph()
    try:
        g.parse(file_path)
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
    return g

def get_local_name(uri):
    """Extracts the local part of a URI (after last # or /)"""
    if isinstance(uri, URIRef):
        return uri.split("#")[-1].split("/")[-1]
    return ""

def is_title_case(name):
    return bool(re.fullmatch(r"[A-Z][a-zA-Z0-9]*", name))

def is_lower_camel_case(name):
    return bool(re.fullmatch(r"[a-z]+(?:[A-Z][a-z0-9]*)*", name))