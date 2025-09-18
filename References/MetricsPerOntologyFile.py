import os
from rdflib import Graph, RDF, RDFS, OWL
from collections import defaultdict
import pandas as pd

ONTO_EXTENSIONS = {'.ttl', '.rdf', '.owl'}

def find_ontology_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in ONTO_EXTENSIONS):
                yield os.path.join(root, file)

def load_graph(file_path):
    g = Graph()
    try:
        g.parse(file_path)
    except Exception as e:
        print(f"Failed to parse {file_path}: {e}")
    return g

def analyze_graph(g):
    metrics = {}

    # === Structural metrics ===
    classes = set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class))
    obj_props = set(g.subjects(RDF.type, OWL.ObjectProperty))
    data_props = set(g.subjects(RDF.type, OWL.DatatypeProperty))
    all_props = obj_props | data_props

    # === Labeling Consistency ===
    labeled_classes = sum(1 for c in classes if (c, RDFS.label, None) in g)
    commented_classes = sum(1 for c in classes if (c, RDFS.comment, None) in g)

    labeled_props = sum(1 for p in all_props if (p, RDFS.label, None) in g)
    commented_props = sum(1 for p in all_props if (p, RDFS.comment, None) in g)

    subclass_rels = list(g.triples((None, RDFS.subClassOf, None)))
    subclass_map = defaultdict(list)
    for s, _, o in subclass_rels:
        subclass_map[o].append(s)

    def depth(node, visited=None):
        if visited is None:
            visited = set()
        visited.add(node)

        children = [child for child in subclass_map[node] if child not in visited]
        if not children:
            return 1
        try:
            return 1 + max(depth(child, visited.copy()) for child in children)
        except ValueError:
            return 1

    hierarchy_depths = [depth(cls) for cls in classes if cls in subclass_map]
    max_depth = max(hierarchy_depths) if hierarchy_depths else 0

    metrics["Number of Classes"] = len(classes)
    metrics["Number of Object Properties"] = len(obj_props)
    metrics["Number of Datatype Properties"] = len(data_props)
    metrics["Total Properties"] = len(obj_props) + len(data_props)
    metrics["Class/Property Ratio"] = len(classes) / metrics["Total Properties"] if metrics["Total Properties"] else 0
    metrics["Subclass Relationships"] = len(subclass_rels)
    metrics["Max Depth of Inheritance"] = max_depth
    metrics["Relationship Richness"] = metrics["Total Properties"] / (metrics["Total Properties"] + len(classes)) if (metrics["Total Properties"] + len(classes)) else 0

    metrics["Class Label Coverage"] = labeled_classes / len(classes) if classes else 0
    metrics["Class Comment Coverage"] = commented_classes / len(classes) if classes else 0
    metrics["Property Label Coverage"] = labeled_props / len(all_props) if all_props else 0
    metrics["Property Comment Coverage"] = commented_props / len(all_props) if all_props else 0

    documented_classes = sum(1 for c in classes if (c, RDFS.label, None) in g or (c, RDFS.comment, None) in g)
    documented_props = sum(1 for p in all_props if (p, RDFS.label, None) in g or (p, RDFS.comment, None) in g)

    metrics["Class Documentation Coverage"] = documented_classes / len(classes) if classes else 0
    metrics["Property Documentation Coverage"] = documented_props / len(all_props) if all_props else 0

    labeled_classes = sum(1 for c in classes if (c, RDFS.label, None) in g)
    labeled_props = sum(1 for p in obj_props | data_props if (p, RDFS.label, None) in g)
    metrics["Class Label Coverage"] = labeled_classes / len(classes) if classes else 0
    metrics["Property Label Coverage"] = labeled_props / metrics["Total Properties"] if metrics["Total Properties"] else 0

    # === Constraint metrics ===

    card_preds = [
        OWL.minCardinality, OWL.maxCardinality, OWL.cardinality,
        OWL.minQualifiedCardinality, OWL.maxQualifiedCardinality, OWL.qualifiedCardinality
    ]
    cardinality_count = sum(1 for p in card_preds for _ in g.triples((None, p, None)))

    domain_count = len(set(g.subjects(RDFS.domain, None)))
    range_count = len(set(g.subjects(RDFS.range, None)))

    disjoint_count = len(list(g.triples((None, OWL.disjointWith, None))))
    func_props_count = len(list(g.subjects(RDF.type, OWL.FunctionalProperty)))
    inv_func_props_count = len(list(g.subjects(RDF.type, OWL.InverseFunctionalProperty)))

    some_values_count = len(list(g.triples((None, OWL.someValuesFrom, None))))
    all_values_count = len(list(g.triples((None, OWL.allValuesFrom, None))))

    metrics["Cardinality Restrictions"] = cardinality_count
    metrics["Properties with Domain"] = domain_count
    metrics["Properties with Range"] = range_count
    metrics["Domain Coverage (%)"] = domain_count / metrics["Total Properties"] if metrics["Total Properties"] else 0
    metrics["Range Coverage (%)"] = range_count / metrics["Total Properties"] if metrics["Total Properties"] else 0
    metrics["Disjoint Classes"] = disjoint_count
    metrics["Functional Properties"] = func_props_count
    metrics["Inverse Functional Properties"] = inv_func_props_count
    metrics["SomeValuesFrom Restrictions"] = some_values_count
    metrics["AllValuesFrom Restrictions"] = all_values_count

    return metrics

def main(directory, output_csv="ontology_metrics_per_file.csv"):
    all_metrics = []

    for file_path in find_ontology_files(directory):
        print(f"Analyzing: {file_path}")
        g = load_graph(file_path)
        metrics = analyze_graph(g)
        metrics["Ontology File"] = os.path.relpath(file_path, directory)
        all_metrics.append(metrics)

    df = pd.DataFrame(all_metrics)
    # Insert "Ontology File" as the first column
    ontology_files = df.pop("Ontology File")
    df.insert(0, "Ontology File", ontology_files)

    df.to_csv(output_csv, sep=";", index=False)
    print(f"\n✅ Metrics saved to: {output_csv}")

if __name__ == "__main__":
    ontology_dir = "../Ontologies"  # Change to your folder
    main(ontology_dir)
