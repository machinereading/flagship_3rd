#-*- coding:utf-8 -*-
import os
import json
import re
import numpy as np
import operator
import urllib3
import random
import tossi
from gensim.models.wrappers import FastText
from contextlib import suppress

parse = re.compile('\(.*?\)')
types = json.load(open('types.json', 'r', encoding='utf-8'))
sentence_format = json.load(open("_merged.json", 'r', encoding='utf8'))
classes = ['가수', '강', '과학자', '국가', '군인', '기업', '기차역', '대도시', '대학', '산맥', '스포츠팀', '영화', '올림픽', '전쟁', '창작자', '캐릭터']
modified_property = {'분야': '연구분야', '전투':'참가한 전투', '설립':'설립 시기', '개봉':'개봉 시기'}
#model = FastText.load_fasttext_format('D:/word embedding/wiki.ko')
model = FastText.load_fasttext_format('wiki.ko')
triple_type = json.load(open('triple_type.json', 'r', encoding='utf-8'))
graph = list()
with open('graph.tsv', 'r', encoding='utf8') as graph_f :
	while True:
		line = graph_f.readline()
		if not line : break
		graph.append(line)
translator = {'field' : '분야', 'award' : '수상내역', 'creator': '창작자', 'firstAppearance': '첫등장', 'gender': '성별', 'nationality': '국적', 
            'species': '종', 'notableWork': '유명한 작품', 'religion': '종교', 'activeYearsStartYear': '데뷔', 'team': '팀', 'club': '클럽', 
            'position': '포지션', 'height': '키', 'youthClub': '유소년클럽', 'area': '면적', 'populationTotal': '인구', '전역': '이전 역', '후역':'다음 역', 
            'locatedInArea': '지역', 'foundingYear': '설립년도', 'governmentType': '정치체제', 'capital': '수도', 'leaderName': '지도자', 'officialLanguage': '공용어', 
            'length': '길이', 'sourceCountry': '발원국', 'league': '리그', 'ground': '구장', 'location': '지역', 'industry':'산업', 'founded-by':'설립자', 
            'country':'국가', 'city':'도시', 'mascot':'마스코트', 'motto':'모토', 'birthPlace': '출생지', 'occupation': '직업', 'genre': '장르', 'instrument': '악기', 
            'birthDate': '생일', 'battle': '전투', 'education': '학력', 'firstAscentPerson': '처음 등반한 사람', 'Japan': '일본', 'United_States': '미국', 'combatant': '전투부대', 'commander': '지휘관', 'result': '결과', 'place': '장소', 'director': '감독', 'homeStadium': '홈구장', 'product': '제품', 'mountainRange': '산맥', 'writer': '각본', 'address': '소재지', 'description': '설명', 'deathPlace': '죽은곳', 'militaryRank': '최종계급', 'riverMouth': '하구', 'source': '발원지', 'knownFor': '유명'}

# 단어에서 몇가지 특수문자 제거.
def remove_paren(word) :
	_word = parse.sub('', word).replace('_', ' ').replace("'", '').replace('"', '').strip()
	return _word


tagset = {'PS': '사람', 'LC': '장소', 'OG': '기관', 'AF': '인공물', 'DT': '날짜', 'TI': '시간', 'CV': '문명', 'AM':'동물', 'PT':"식물", 'QT':'양', 'FD':'분야', 'TR':'이론', 'EV':'사건', 'MT':'물질', 'TM':'용어'}
# ETRI NER TAGSET을 한글로 변경.
def NER_classify(_ner):
	ner = _ner
	if ner[:2] not in tagset.keys(): ner = '기타'
	else : ner = tagset[ner[:2]]
	return ner

# Graph와 KB의 property 표현이 약간 차이가 있어서 통일시키는 함수.
def revise_p(_p):
	p = _p
	if p.find('http://dbpedia.org/ontology/') != -1 :
		p = p.replace('http://dbpedia.org/ontology/', '')
		if p not in translator.keys() :
			#print(p)
			return None
		p = translator[p]
	elif p.find('http://ko.dbpedia.org/property/') != -1 :
		p = p.replace('http://ko.dbpedia.org/property/', '')
	if p in modified_property.keys() :
		p = modified_property[p]
	return p


# ETRI NER API를 활용해서 NER 분석 
def ETRI_NER(YOUR_SENTENCE) :
	openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"
	accessKey = "abfa1639-8789-43e0-b1da-c29e46b431db"
	analysisCode = "ner"
	text = YOUR_SENTENCE
	
	if (text == '') : return []
	requestJson = {
		"access_key": accessKey,
		"argument": {
			"text": text,
			"analysis_code": analysisCode
		}
	}
	
	http = urllib3.PoolManager()
	response = http.request(
		"POST",
		openApiURL,
		headers={"Content-Type": "application/json; charset=UTF-8"},
		body=json.dumps(requestJson)
	)

	result = json.loads(str(response.data,"utf-8"))
	NE_list = result["return_object"]["sentence"][0]["NE"]
	result = list()
	for NE in NE_list :
		result.append([NE['text'], NER_classify(NE['type'])])
	#print(result)
	return result


# 주어진 topic에 질문할 내용이 있는지 확인.
def hasQuestion(topic, topic_class):
	hasProperty = list()
	for p in types[topic_class]['property'] :
		hasProperty.append(p)
	for triple in graph :
		triple_split = triple.split('\t')
		s = remove_paren(triple_split[0])
		p = revise_p(triple_split[1])
		if p == None : continue
		o = remove_paren(triple_split[2])
		if s == topic :
			with suppress(ValueError) :
				hasProperty.remove(p)
	for Property in hasProperty :
		if (Property not in types[topic_class]['property']) :
			with suppress(ValueError) :
				hasProperty.remove(Property)
	#print(hasProperty)
	length = len(hasProperty)
	return length, hasProperty
	

# 답변 확인
def validate(_s, _p, _c, _answer, _triple_type) :
	#print('validate')
	answer = _answer
	response = '답변이 이상합니다. 다시 말씀해주세요.'
	ner_result = ETRI_NER(answer)
	#print(ner_result)
	for item in [_s, _p] :
		for ner in ner_result :
			if item in ner :
				ner_result.remove(ner)
	if not ner_result :
		return response
	else :
		#print(_s, _p, _c, ner_result)
		response = _s + '의 ' + tossi.postfix(_p, '이') + ' ' + tossi.postfix(ner_result[0][0], '이') + ' 맞습니까?'
		#print(response)
		return response
	'''
	elif ner_result[0][1] not in _triple_type[_c][_p] :
		print(_triple_type[_c][_p])
		return response
	'''
	

# 조사를 알맞게 수정.
def correct_tossi(sentence) :
	hangul = re.compile('[ㄱ-ㅣ가-힣]+')
	tmp = sentence.split()
	symbols = ['(S)', '(P)', '(O)']
	for i in range(len(tmp)) :
		item = tmp[i]
		for symbol in symbols :
			if (item.find(symbol) != -1) :
				morps = item.split(symbol)
				word = morps[0]
				josa = morps[1]
				#print(word, josa)
				if (word != '') and (josa != '') and (hangul.match(word[-1]) != None) :
					#print('정상처리')
					tmp[i] = tossi.postfix(word, josa)
					#print(tmp[i])
				else :
					#print('예외처리')
					tmp[i] = word + josa
					#print(tmp[i])
	output = ' '.join(tmp)
	return output


# 주어진 트리플에 알맞은 문장 생성.
def generate_sentence(triple, mode):
	s, p, o, c = triple
	format_candidiates = sentence_format[c][p][mode]
	index = int(random.random()*len(format_candidiates))
	selected_format = format_candidiates[index]
	#print(property_details['answers'][index])
	if mode == 'answers' :
		sentence = selected_format.replace("(S)", s+'(S)').replace("(P)", p+'(P)').replace("(O)", o+'(O)')
	elif mode == 'questions' :
		sentence = selected_format.replace("(S)", s +'(S)').replace("(P)", p +'(P)')
	#print(answer_sentence)
	sentence = correct_tossi(sentence)
	#print(answer_sentence)
	return sentence


# 랜덤 트리플 선정.
def random_triple(_c):
	c = _c
	if (c == '') :
		c = classes[int(random.random()*len(classes))]

	es = types[c]['entity']
	l = len(es)
	s = remove_paren(es[int(random.random()*l)])
	for edge in graph :
		triple = edge.strip().split()
		if (s == remove_paren(triple[0])) and (revise_p(triple[1]) in types[c]['property']) :
			p = revise_p(triple[1])
			o = remove_paren(triple[2])
			break
	return s, p, o, c


# NLU 모듈
def NLU(input_sentence, pre_state, state):
	# 유저가 '끝'이라고 입력하면 프로그램 종료.
	if (input_sentence == '끝') : exit(0)
	
	ner_result = ETRI_NER(input_sentence)
	keywords = []
	for item in ner_result:
		keywords.append(item[0])

	if (state == 'CHECK_Q') :
		keywords.append(input_sentence)
	
	return keywords, pre_state, state


# DM 모듈
def DM(keywords, question_triple, pre_state, state):
	intro_triples = []

	if (len(keywords) == 0) :
		return intro_triples, question_triple, keywords, state, state

	if (state == 'T_INTRO') :
		most_similarity = 0
		most_similar_index = -1
		a = 1.0 #subject, property의 유사도를 조절.
		for edge in graph :
			triple = edge.strip().split()
			s = remove_paren(triple[0])
			p = revise_p(triple[1])
			if p == None : continue

			# 키워드 중 하나가 KB에 있을 경우.
			if (s in keywords) :
				# 지금은 graph가 불완전해서 예외처리를 하고 있다.
				for i_class in classes :
					if s in types[i_class]['entity'] :
						c = i_class
						break
				if (p not in types[c]['property']) :
					continue
				most_similar_index = graph.index(edge)
				break

			# KB에 일치하는 키워드가 없는 경우.
			similarity_subject = model.wv.n_similarity(keywords, s)
			similarity_property = model.wv.n_similarity(keywords, p)
			tmp_similarity = a * similarity_subject + (1-a) * similarity_property
			if (most_similarity < tmp_similarity) :
				most_similarity = tmp_similarity
				most_similar_index = graph.index(edge)

		bundle = graph[most_similar_index]
		triple = bundle.strip().split()
		topic = remove_paren(triple[0])
		topic_property = revise_p(triple[1])
		topic_object = remove_paren(triple[2])
		topic_class = ''
		for i_class in classes :
			if topic in types[i_class]['entity'] :
				topic_class = i_class
				break
		#print('aaaaaaaaaaaaaaaaaaaaaaaa', (topic, topic_property, topic_object, topic_class))
		intro_triples.append((topic, topic_property, topic_object, topic_class))
		length, hasProperty = hasQuestion(topic, topic_class)
		if (length > 0) :
			pre_state = state
			state = 'SET_Q'
			question_property = hasProperty[int(random.random()*len(hasProperty))]
			question_triple = (topic, question_property, None, topic_class)
		else :
			pre_state = state
			state = 'T_SHIFT'
			# topic shift
			pre_topic = topic
			for triple_line in graph :
				triple = triple_line.split('\t')
				s = remove_paren(triple[0])
				p = revise_p(triple[1])
				o = remove_paren(triple[2])
				if s == topic : continue
				#if p == None : continue
				c = ''
				for i_class in classes:
					if s in types[i_class]['entity'] : c = i_class
				if (topic_property == p) and (topic_object == o) and (topic_class == c):
					question_count, question_properties = hasQuestion(s, topic_class)
					#print("AAAAAAAAAAAAAAAAAAAA", s, question_count, question_properties)
					if question_count == 0 : continue
					topic = s
					break
			pre_state = state
			state = 'SET_Q'
			# 적절한 주제 전환 대상을 찾지 못한 경우.
			if topic == pre_topic :					
				count = 0
				topic, topic_property, topic_object, topic_class = random_triple(topic_class)
				question_count, question_properties = hasQuestion(topic, topic_class)
				#print("BBBBBBBBBBBBBBBBBBBB", topic, question_count, question_properties)
				while (question_count == 0) :
					if count > 20 : 
						topic_class = ''
					topic, topic_property, topic_object, topic_class = random_triple(topic_class)
					question_count, question_properties = hasQuestion(topic, topic_class)
					count += 1
			intro_triples.append((topic, topic_property, topic_object, topic_class))
			question_property = question_properties[int(random.random()*len(question_properties))]
			question_triple = (topic, question_property, None, topic_class)
	elif (state == 'SET_Q') :
		s, p, _, c = question_triple
		for keyword in keywords:
			if keyword in [s, p] :
				keywords.remove(keyword)
		if len(keywords) > 0 : 
			o = keywords[0]
			pre_state = state
			state = 'CHECK_Q'
		else : 
			o = None
			pre_state = state
			state = 'SET_Q'
		question_triple = (s, p, o, c)
	elif(state == 'CHECK_Q') :
		state = 'CLOSE'
	return intro_triples, question_triple, keywords, pre_state, state


# NLG 모듈
def NLG(intro_triples, question_triple, keywords, pre_state, state) :
	sentence = ''
	if (state == 'SET_Q') :
		if (pre_state == 'SET_Q') :
			sentence = '무슨 말인지 모르겠어요. 다시 말씀해주세요.'
		else :
			for triple in intro_triples :
				intro_sentence = generate_sentence(triple, 'answers')
				sentence += intro_sentence + '\n'
			question = generate_sentence(question_triple, 'questions')
			sentence += question
	elif (state == 'CHECK_Q') :
		s, p, o , _ = question_triple
		sentence = s + '의 ' + tossi.postfix(p, '이') + ' ' + tossi.postfix(o, '이') + ' 맞습니까?'
	elif (state == 'CLOSE') :
		if (keywords[0] == '네') :
			sentence = '감사합니다.'
		elif(keywords[0] == '아니요') :
			sentence = '제가 잘못 들었나보네요.'
	else :
		if (keywords == []) :
			sentence = '새로운 주제로 대화를 진행해주세요.'
	return sentence, pre_state, state


# 전체 모듈 통합.
def main():
	state = 'OPEN'
	pre_state = ''
	user_utterence = ''
	system_utterence = '안녕하세요.'
	keywords = None
	intro_triples = None
	question_triple = None

	while True :
		#print(pre_state, state, topic, topic_property, topic_object, topic_class)
		if (state == 'OPEN') :
			pre_state = state
			state = 'T_INTRO'
			system_utterence = '안녕하세요.'
			user_utterence = ''
			keywords = None
			intro_triples = None
			question_triple = None
			print('SYSTEM : ', system_utterence)
		user_utterence = input('USER : ')
		keywords, pre_state, state = NLU(user_utterence, pre_state, state)
		#print('NLU', keywords, state, pre_state)
		intro_triples, question_triple, keywords, pre_state, state = DM(keywords, question_triple, pre_state, state)
		#print('DM', intro_triples, question_triple, keywords, state, pre_state)
		system_utterence, pre_state, state = NLG(intro_triples, question_triple, keywords, pre_state, state)
		#print('NLG', state, pre_state)
		print('SYSTEM : ' + system_utterence)
		if (state == 'CLOSE') :
			print('----------------------------------------------------------------------------------')
			pre_state = state
			state = 'OPEN'

if __name__ == "__main__":
	main()