import pandas as pd
import os
from rdflib import Graph, RDF, RDFS, OWL
ONTO_EXTENSIONS = {'.ttl', '.rdf', '.owl'}
from Assets.Metrics import Metrics
from Assets.Utils import load_graph

def find_ontology_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in ONTO_EXTENSIONS):
                yield os.path.join(root, file)

def analyze_directory_as_one_ontology(directory_path):
    g = Graph()
    for file_path in find_ontology_files(directory_path):
        try:
            g.parse(file_path)
        except Exception as e:
            print(f"Warning: could not parse {file_path}: {e}")
    return g

class OntologyEvaluator:
    def __init__(self, root: str, ontologiesBaseURL: dict):
        self.root = root
        self.ontologiesBaseURL = ontologiesBaseURL
        self.results = None

    def process_work(self, add_other_indicators: bool = False, ontology_c_output: str = "./", try_import_external_ontologies: bool = False):
        all_metrics = []
        for entry in os.scandir(self.root):
            if entry.is_file() and any(entry.name.endswith(ext) for ext in ONTO_EXTENSIONS):
                print(f"Analyzing single ontology file: {entry.path}")
                txt_path = os.path.join(ontology_c_output, f"{entry.name}_classes.txt")
                g = load_graph(entry.path)
                if try_import_external_ontologies:
                    try:
                        for o in g.objects(predicate=OWL.imports):
                            print(f"Loading import: {o}")
                            g.parse(o)
                    except Exception as e:
                        print(f"Warning: could not parse {file_path}: {e}")
                metrics = Metrics(g, entry.name).run(add_other_indicators=add_other_indicators, ontology_c_output=txt_path, ontologies_base_urls=self.ontologiesBaseURL)
                metrics["Ontology Source"] = entry.name  # Use filename
                metrics["Source Type"] = "file"
                all_metrics.append(metrics)
            elif entry.is_dir():
                print(f"Analyzing combined ontology for subdirectory: {entry.path}")
                txt_path = os.path.join(ontology_c_output, f"{entry.name}_classes.txt")
                g = analyze_directory_as_one_ontology(entry.path)
                if try_import_external_ontologies:
                    try:
                        for o in g.objects(predicate=OWL.imports):
                            print(f"Loading import: {o}")
                            g.parse(o)
                    except Exception as e:
                        print(f"Warning: could not parse {file_path}: {e}")
                metrics = Metrics(g, entry.name).run(add_other_indicators=add_other_indicators, ontology_c_output=txt_path, ontologies_base_urls=self.ontologiesBaseURL)
                metrics["Ontology Source"] = os.path.basename(entry.path)  # Use folder name
                metrics["Source Type"] = "subdirectory"
                all_metrics.append(metrics)
        df = pd.DataFrame(all_metrics)
        source = df.pop("Ontology Source")
        df.insert(0, "Ontology Source", source)
        source_type = df.pop("Source Type")
        df.insert(1, "Source Type", source_type)
        self.results = df

    def process_file(self, add_other_indicators: bool = False):
        all_metrics = []
        for file_path in find_ontology_files(self.root):
            print(f"Analyzing: {file_path}")
            g = load_graph(file_path)
            metrics = Metrics(g).run(add_other_indicators=add_other_indicators)
            metrics["Ontology File"] = os.path.relpath(file_path, self.root)
            all_metrics.append(metrics)
        df = pd.DataFrame(all_metrics)
        ontology_files = df.pop("Ontology File")
        df.insert(0, "Ontology File", ontology_files)
        self.results = df

    def save_to_csv(self, output_csv: str):
        self.results.to_csv(output_csv, sep=";", index=False)
        print(f"\n✅ Metrics saved to: {output_csv}")