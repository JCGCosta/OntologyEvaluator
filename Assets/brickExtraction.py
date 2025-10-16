import brickschema as bs

g = bs.Graph(load_brick=True)

res = g.query("""SELECT ?s ?p ?o WHERE { ?s ?p ?o . }""")
for row in res:
    print(row)