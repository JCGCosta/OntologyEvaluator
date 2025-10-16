from Assets.Evaluation import OntologyEvaluator

ontologiesBaseUrl = {
  "aid-em": "http://www.mascem.gecad.isep.ipp.pt/ontologies/aid-em.owl",
  "call-for-proposal": "http://www.mascem.gecad.isep.ipp.pt/ontologies/call-for-proposal.owl",
  "DABGEO": "http://www.purl.org/dabgeo",
  "electricity-markets-results": "http://www.mascem.gecad.isep.ipp.pt/ontologies/electricity-markets-results.owl",
  "ElectricityMarkets": "http://www.mascem.gecad.isep.ipp.pt/ontologies/electricity-markets.owl",
  "em-kpi-1_1": "http://energy.linkeddata.es/em-kpi",
  "EpexOntology": "http://www.mascem.gecad.isep.ipp.pt/ontologies/epex.owl",
  "IEMS": "http://www.semanticweb.org/robertomonaco/ontologies",
  "IESO": "https://www.gecad.isep.ipp.pt/ieso/v1.0.0",
  "MibelOntology": "http://www.mascem.gecad.isep.ipp.pt/ontologies/mibel.owl",
  "NordPool": "http://www.mascem.gecad.isep.ipp.pt/ontologies/nordpool.owl",
  "OEMA": "http://www.purl.org/oema",
  "OpenEnergyOntology": "http://openenergy-platform.org/ontology",
  "saref4ener": "https://saref.etsi.org/saref4ener",
  "SARGON": "https://w3id.org/saref",
  "SEAS": "https://w3id.org/seas",
  "ThinkHome": "https://www.auto.tuwien.ac.at/downloads/thinkhome",
  "saref4grid": "https://saref.etsi.org/saref4grid/",
  "SEMANCO": "http://semanco02.hs-albsig.de/repository/ontology-releases/eu/semanco/ontology/SEMANCO/SEMANCO.owl#",
  "EEPSA": "https://w3id.org/eepsa/",
  "BOnSAI": "http://lpis.csd.auth.gr/ontologies/bonsai/BOnSAI.owl",
  "SmartHome": "http://www.owl-ontologies.com/smarthome",
  "brick": "https://brickschema.org/schema/Brick"
}

OE = OntologyEvaluator(root="Ontologies", ontologiesBaseURL=ontologiesBaseUrl)
OE.process_work(ontology_c_output="OntologyClasses", try_import_external_ontologies=False)
OE.save_to_csv("MetricsResults/Ontology Metrics Per Work.csv")
OE.process_file()
OE.save_to_csv("MetricsResults/Ontology Metrics Per File.csv")