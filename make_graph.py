import os

if __name__ == "__main__":
    classes = ['가수', '강', '과학자', '국가', '군인', '기업', '기차역', '대도시', '대학', '산맥', '스포츠팀', '영화', '올림픽', '전쟁', '창작자', '캐릭터']
    graph = open('extracted_graph.tsv', 'w', encoding='utf8')
    for i_class in classes :
        path = 'Data/'+i_class+'/'
        filenames = os.listdir(path)
        for filename in filenames:
            with open(path+filename, 'r', encoding='utf8') as f:
                while True:
                    line = f.readline()
                    if not line : break
                    if line[:7] == 'http://' : 
                        triple = line.strip().split()
                        s = triple[0].replace('http://ko.dbpedia.org/resource/', '')
                        p = triple[1]
                        o = triple[2].replace('http://ko.dbpedia.org/resource/', '')
                        graph.write(s+'\t'+p+'\t'+o+'\n')
    graph.close()
                    
                    