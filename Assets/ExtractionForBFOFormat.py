import requests
from bs4 import BeautifulSoup
import time
import csv

def parse_oeo_concept(url):
    """
    Given a URL of an OEO concept, return a dict with fields:
    - url
    - concept_id
    - label
    - definition
    - superclasses (a list of dicts with name + optional definition)
    """
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {url}: status {resp.status_code}")
        return None
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract concept_id from URL
    # e.g. .../oeo/OEO_00020408/, or maybe without trailing slash.
    concept_id = url.rstrip("/").split("/")[-1]

    # Label
    label_el = soup.find(lambda tag: tag.name in ["h#", "h1","h2","h3","h4","h5","h6"]
                         and "Label:" in tag.text)
    # alternative: find element with text "Label:" or a “#### Label:” etc.
    if label_el:
        # Label text might be "##### Label: sector coupling"
        label_text = label_el.text.strip()
        # remove "Label:" prefix if present
        label = label_text.split("Label:")[-1].strip()
    else:
        label = None

    # Definition: often a tag with “Definition:” prefix
    def_el = soup.find(lambda tag: tag.name in ["p","div","section"] and "Definition:" in tag.text)
    if def_el:
        def_text = def_el.text.strip()
        definition = def_text.split("Definition:")[-1].strip()
    else:
        definition = None

    # Superclasses
    superclasses = []
    # The superclasses are under “Back to the super classes:” – find that section
    # Then locate links or tags that represent the superclasses names, and under each, maybe definitions
    sc_section = None
    # find the heading that says “Back to the super classes:” maybe h4 or so
    for tag in soup.find_all():
        if "Back to the super classes" in tag.text:
            sc_section = tag
            break
    if sc_section:
        # after this tag, find the list (could be ul/li or links) of superclasses
        # simple approach: look at siblings
        for sib in sc_section.find_next_siblings():
            # stop if we reach another major section
            # e.g. if sib has “###### Definition:” again or a heading
            # Otherwise, collect link tags
            links = sib.find_all("a")
            if links:
                for a in links:
                    sc_name = a.text.strip()
                    sc_url = a.get("href")
                    # optionally fetch class definition of superclass inline if shown
                    # maybe after the link, there is a “Definition:” text
                    # The super‐class definition is shown in sample under “process”
                    # Find definition in sibling or within same container
                    # For simplicity, try to find in the same sib block
                    sc_def = None
                    text_after = sib.text
                    # crude: see if “Definition:” appears in the same block
                    if "Definition:" in text_after:
                        # everything after “Definition:” until maybe end or line break
                        sc_def = text_after.split("Definition:")[-1].strip()
                    superclasses.append({"name": sc_name, "url": sc_url, "definition": sc_def})
                # maybe break if we got enough
            # Optionally stop after capturing
    # Return dict
    return {
        "url": url,
        "concept_id": concept_id,
        "label": label,
        "definition": definition,
        "superclasses": superclasses
    }

def scrape_from_file(input_file, output_file, delay=1.0):
    """
    input_file: path to a txt file, each line one URL
    output_file: path to CSV or JSON
    """
    results = []

    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    for u in urls:
        print(f"Scraping {u}")
        r = parse_oeo_concept(u)
        if r:
            results.append(r)
        time.sleep(delay)  # be kind to the server / avoid rate limiting

    # Write out results
    # Example: CSV with concept_id, label, definition, superclasses (names joined by semicolon)
    with open(output_file, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["concept_id","label","definition","superclasses"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rec in results:
            sc_names = "; ".join([sc["name"] for sc in rec["superclasses"]])
            writer.writerow({
                "concept_id": rec["concept_id"],
                "label": rec["label"],
                "definition": rec["definition"],
                "superclasses": sc_names
            })

if __name__ == "__main__":
    # Example usage
    scrape_from_file("../OntologyClasses/OpenEnergyOntology_classes.txt", "../OntologyClasses/oeo_concepts.csv")