f = open('graph.tsv', 'r', encoding='utf-8')
of = open('modified_graph.tsv', 'w', encoding='utf-8')
while True:
    line = f.readline()
    if not line : break
    if line.find('http://dbpedia.org/ontology/wikiPageWikiLink') == -1 :
        of.write(line)