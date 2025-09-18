import os, owlready2
owlready2.reasoning.JAVA_MEMORY = 1000
from rdflib import Graph, RDF, RDFS, OWL, URIRef
from tempfile import NamedTemporaryFile
from Assets.Utils import get_local_name, is_title_case, is_lower_camel_case

class Metrics:
    def __init__(self, g: Graph, cur_filename: str = None):
        self.g = g
        self.entity = {
            "classes": set(g.subjects(RDF.type, OWL.Class)) | set(g.subjects(RDF.type, RDFS.Class)),
            "obj_props": set(g.subjects(RDF.type, OWL.ObjectProperty)),
            "data_props": set(g.subjects(RDF.type, OWL.DatatypeProperty)),
            "all_props": set(g.subjects(RDF.type, OWL.ObjectProperty)) | set(g.subjects(RDF.type, OWL.DatatypeProperty)),
            "total_properties": len(set(g.subjects(RDF.type, OWL.ObjectProperty))) + len(set(g.subjects(RDF.type, OWL.DatatypeProperty)))
        }
        self.cur_fn = cur_filename
        self.metrics = {}

    def save_classes_to_txt(self, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            for cls in sorted(self.entity["classes"]):
                if isinstance(cls, URIRef):
                    f.write(str(cls) + "\n")

    def structural_indicators(self):
        self.metrics["Number of Classes"] = len(self.entity["classes"])
        self.metrics["Number of Object Properties"] = len(self.entity["obj_props"])
        self.metrics["Number of Datatype Properties"] = len(self.entity["data_props"])
        self.metrics["Total Properties"] = self.entity["total_properties"]
        self.metrics["Relationship Richness"] = self.entity["total_properties"] / (
                    self.entity["total_properties"] + len(self.entity["classes"])) if (self.entity["total_properties"] + len(self.entity["classes"])) else 0

    def lexical_indicators(self):
        # Labeling Consistence
        documented_classes = sum(1 for c in self.entity["classes"] if (c, RDFS.label, None) in self.g or (c, RDFS.comment, None) in self.g)
        documented_props = sum(1 for p in self.entity["all_props"] if (p, RDFS.label, None) in self.g or (p, RDFS.comment, None) in self.g)
        self.metrics["Class Documentation Coverage"] = documented_classes / len(self.entity["classes"]) if self.entity["classes"] else 0
        self.metrics["Property Documentation Coverage"] = documented_props / len(self.entity["all_props"]) if self.entity["all_props"] else 0
        # Naming Convention
        class_names = [get_local_name(c) for c in self.entity["classes"]]
        prop_names = [get_local_name(p) for p in self.entity["all_props"]]
        title_case_classes = sum(1 for name in class_names if is_title_case(name))
        lower_camel_props = sum(1 for name in prop_names if is_lower_camel_case(name))
        self.metrics["Class Naming Consistency"] = title_case_classes / len(class_names) if class_names else 0
        self.metrics["Property Naming Consistency"] = lower_camel_props / len(prop_names) if prop_names else 0

    def logical_indicators(self):
        axiom_predicates = {
            RDF.type, RDFS.subClassOf, OWL.equivalentClass, OWL.disjointWith,
            RDFS.domain, RDFS.range, OWL.inverseOf, OWL.complementOf,
            OWL.intersectionOf, OWL.unionOf, OWL.sameAs,
            OWL.hasValue, OWL.allValuesFrom, OWL.someValuesFrom,
            OWL.minCardinality, OWL.maxCardinality, OWL.cardinality,
            OWL.minQualifiedCardinality, OWL.maxQualifiedCardinality, OWL.qualifiedCardinality
        }

        axiom_count = sum(1 for s, p, o in self.g if p in axiom_predicates)
        self.metrics["Axiom Richness"] = (
            axiom_count / (len(self.entity["classes"]) + len(self.entity["all_props"]))
            if (len(self.entity["classes"]) + len(self.entity["all_props"])) > 0
            else 0
        )

    def usability_reusability_indicators(self, ontologies_base_urls: dict):
        base_url = ontologies_base_urls[self.cur_fn.split(".")[0]]

        classes = self.entity["classes"]
        props = self.entity["all_props"]

        total_entities = len(classes) + len(props)

        reused_classes = [c for c in classes if not str(c).startswith(base_url)]
        reused_props = [p for p in props if not str(p).startswith(base_url)]
        reused_entities = len(reused_classes) + len(reused_props)

        self.metrics["Semantic Reuse Ratio"] = reused_entities / total_entities if total_entities else 0.0

    def constraint_indicators(self):
        card_preds = [
            OWL.minCardinality, OWL.maxCardinality, OWL.cardinality,
            OWL.minQualifiedCardinality, OWL.maxQualifiedCardinality, OWL.qualifiedCardinality
        ]
        self.metrics["Cardinality Restrictions"] = sum(1 for p in card_preds for _ in self.g.triples((None, p, None)))
        self.metrics["Properties with Domain"] = len(set(self.g.subjects(RDFS.domain, None)))
        self.metrics["Properties with Range"] = len(set(self.g.subjects(RDFS.range, None)))
        self.metrics["Disjoint Classes"] = len(list(self.g.triples((None, OWL.disjointWith, None))))
        self.metrics["Functional Properties"] = len(list(self.g.subjects(RDF.type, OWL.FunctionalProperty)))
        self.metrics["Inverse Functional Properties"] = len(list(self.g.subjects(RDF.type, OWL.InverseFunctionalProperty)))
        self.metrics["SomeValuesFrom Restrictions"] = len(list(self.g.triples((None, OWL.someValuesFrom, None))))
        self.metrics["AllValuesFrom Restrictions"] = len(list(self.g.triples((None, OWL.allValuesFrom, None))))

    def other_indicators(self):
        labeled_classes = sum(1 for c in self.entity["classes"] if (c, RDFS.label, None) in self.g)
        commented_classes = sum(1 for c in self.entity["classes"] if (c, RDFS.comment, None) in self.g)
        labeled_props = sum(1 for p in self.entity["all_props"] if (p, RDFS.label, None) in self.g)
        commented_props = sum(1 for p in self.entity["all_props"] if (p, RDFS.comment, None) in self.g)
        metrics["Class Label Coverage"] = labeled_classes / len(self.entity["classes"]) if self.entity["classes"] else 0
        metrics["Class Comment Coverage"] = commented_classes / len(self.entity["classes"]) if self.entity["classes"] else 0
        metrics["Property Label Coverage"] = labeled_props / len(self.entity["all_props"]) if self.entity["all_props"] else 0
        metrics["Property Comment Coverage"] = commented_props / len(self.entity["all_props"]) if self.entity["all_props"] else 0
        self.metrics["Domain Coverage (%)"] = len(set(self.g.subjects(RDFS.domain, None))) / self.entity["total_properties"] if self.entity["total_properties"] else 0
        self.metrics["Range Coverage (%)"] = len(set(self.g.subjects(RDFS.range, None))) / self.entity["total_properties"] if self.entity["total_properties"] else 0

    def run(self,
            structural_metrics: bool = True,
            lexical_metrics: bool = True,
            logical_indicators: bool = True,
            constraint_indicators: bool = True,
            add_other_indicators: bool = False,
            ontology_c_output: str = None,
            ontologies_base_urls: dict = None):
        if structural_metrics: self.structural_indicators()
        if lexical_metrics: self.lexical_indicators()
        if logical_indicators: self.logical_indicators()
        if constraint_indicators: self.constraint_indicators()
        if add_other_indicators: self.other_indicators()
        if ontology_c_output is not None: self.save_classes_to_txt(ontology_c_output)
        if ontologies_base_urls is not None: self.usability_reusability_indicators(ontologies_base_urls)
        return self.metrics