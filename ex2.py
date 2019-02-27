import json
import os
import re
from lev import lev_all
from similarity import remove_paren

S = 6
P = 5
O = 4
Q1 = 2
A1 = 3

def preprocess(sent, s, p, o):
	items_to_sub = []
	bracket = re.compile('\(.*\)')
	date = (r"[0-9]+[년/\-] ?[0-9]+[월/\-] ?[0-9]+[일/\-] ?", "(DATE)")
	items_to_sub.append(date)
	items_to_sub.append((bracket, ""))
	s_bracket_inside_text = s.split("(")[-1][:-1] if len(s.split("(")) > 1 else None
	o_bracket_inside_text = o.split("(")[-1][:-1] if len(o.split("(")) > 1 else None
	x = ("\(%s\)" % s_bracket_inside_text, "") if s_bracket_inside_text else None
	if x is not None:
		items_to_sub.append(x)
	y = ("\(%s\)" % o_bracket_inside_text, "") if o_bracket_inside_text else None
	if y is not None:
		items_to_sub.append(y)
	
	many_blank = (r" +", " ")
	items_to_sub.append(many_blank)
	dot_blank = (r"\. ", ".")
	for fr, to in items_to_sub:
		sent = re.sub(fr, to, sent)

	s = bracket.sub('', s).strip()
	o = bracket.sub('', o).strip()
	
	for old, new in [("'", ""), ("_", " "), (",", ""), ('"', ""), (o, "(O)"), (o.replace(" ", ""), "(O)"), (p, "(P)"), (s, "(S)"), (s.replace(" ", ""), "(S)"), (") ", ")"), (")은", ")는"), (")이", ")가"), (")을", ")를")]:
		sent = sent.replace(old, new)
	if "(S)" not in sent:
		s_rel_part, score = find_most_relavant_str(sent, s)
		if score < 3:
			sent = sent.replace(s_rel_part, "(S)")

	return sent

def find_most_relavant_str(s, x):
	x = lev_all(s, x)
	min_val = 100
	min_ind = None
	for i in range(len(x)):
		for j in range(i, len(x[i])):
			if min_val > x[i][j]:
				min_val = x[i][j]
				min_ind = (i,j)
	# print(i,j, min_val, x[i][j])
	return s[min_ind[0]:min_ind[1]], min_val
	
def date(x):
	pass

def class_entity():
	types = dict()
	type_names = os.listdir('Data')
	for type_name in type_names :
		filenames = os.listdir('Data/'+type_name)
		entities = list()
		for filename in filenames :
			for old, new in [("'", ""), ("_", " "), (",", ""), ('"', "")] :
				filename = filename.replace(old, new)
			entities.append(filename[:-4])
		types[type_name] = entities
	return types

def get(f):
	types = class_entity()
	result = {}
	f.readline() # 첫번째 line은 tag임

	for line in f.readlines():
		x = line.strip().split("\t")
		s = x[S]
		p = x[P]
		o = x[O]
		ox = x[-1]
		if (ox.count('O') < 2) : continue
		c = ''

		mod_s = s
		for old, new in [("'", ""), ("_", " "), (",", ""), ('"', ""), ('&', ' '), (':', ' ')] :
			mod_s = mod_s.replace(old, new)
		for type_name in types.keys() :
			if (mod_s in types[type_name]) : 
				c = type_name
				break
		if (c not in result) :
			result[c] = dict()

		for q,a in [[Q1, A1]]:

			user_q = preprocess(x[q],s,p,o)
			user_a = preprocess(x[a],s,p,o)
			if user_q == "null": continue
			# s = bracket.sub('', s).strip()
			# o = bracket.sub('', o).strip()
			# user_q = bracket.sub('', user_q).strip()
			# user_a = bracket.sub('', user_a).strip()
			
			#tag_result = "".join(x[-1].strip('"').split(","))
			#tc = tag_result.count("O")

			if p not in result[c]:
				result[c][p] = {"count": 0, "questions":set([]), "answers": set([]), "duplicates": [], "banned": [], "elements_not_recognized": []}
			
			for sent in [user_q, user_a]:
				if "(S)" not in sent:
					result[c][p]["elements_not_recognized"].append(sent)
				
			'''if tc < 2:
				result[p]["banned"].append(user_str)
				continue'''

			
			if user_q in result[c][p]["questions"]:
				result[c][p]["duplicates"].append(user_q)
			result[c][p]["questions"].add(user_q)
			if user_a in result[c][p]["answers"]:
				result[c][p]["duplicates"].append(user_a)
			result[c][p]["answers"].add(user_a)
			result[c][p]["count"] += 2
		
	'''	
	for _, v in result.items():
		v["questions"] = list(filter(lambda x: x not in v["elements_not_recognized"], v["questions"]))
		v["answers"] = list(filter(lambda x: x not in v["elements_not_recognized"],v["answers"]))
		v["unique_strings"] = len(v["questions"]) + len(v["answers"])
		v["dup_ratio"] = len(v["duplicates"]) / v["count"]
		v["max_dup_str"] = sorted({s:v["duplicates"].count(s) for s in v["duplicates"]}.items(), key=lambda k: -k[1])[0] if len(v["duplicates"]) > 0 else ""
'''

	for c in result :
		for p in result[c]:
			result[c][p]["questions"] = list(result[c][p]["questions"])
			result[c][p]["answers"] = list(result[c][p]["answers"])
		# print(len(v["questions"]), len(v["answers"]))
	print(result.keys())
	return result


def users(f):
	worker_result = {}
	f.readline()
	for line in f.readlines():
		x = line.strip().split("\t")
		o, p ,s = x[4:7]
		user_str = x[9]
		user_id = x[13]
		for old, new in [(",", ""), ('"', ""), (o, "(O)"), (p, "(P)"), (s, "(S)"), (")은", ")는"), (")이", ")가")]:
			user_str = user_str.replace(old, new)
		if user_id not in worker_result:
			worker_result[user_id] = {}
		if user_str not in worker_result[user_id]:
			worker_result[user_id][user_str] = 0
		worker_result[user_id][user_str] += 1
	x = open("workerstat.csv", "w")
	for k, v in worker_result.items():
		dupc = 0
		work = 0
		for _, vv in v.items():
			dupc += vv - 1
			work += vv
		v["work"] = work
		v["dup"] = dupc
		x.write("%s,%d,%d\n" %(k, work, dupc))
	x.close()
	return worker_result


def s(j, wf):
	wf.write("\t".join(["키워드", "수집 수", "중복 제외 문장 수"])+"\n")
	for k, v in j.items():
		wf.write("\t".join([k, str(v["count"]), str(v["unique_strings"])])+"\n")

if __name__ == '__main__':
	'''
	with open("process_result/문장의미비교대량3차.json", encoding="UTF8") as f, open("x.tsv", "w", encoding="UTF8") as wf:
		s(json.load(f), wf)
		import sys
		sys.exit(0)
	'''
	with open("대량3/감독 580문장.txt", 'r') as f:
		result = get(f)
	'''
	max_dup = (0, 0)
	min_dup = (100, 0)
	alldup = 0
	max_banned = (0,0)
	min_banned = (100, 0)
	allban = 0
	for k, v in result.items():

		dl = v["dup_ratio"]
		alldup += dl
		if dl > max_dup[0]:
			max_dup = (dl, k)
		if dl < min_dup[0]:
			min_dup = (dl, k)
		bl = len(v["banned"])
		print("%s,%d,%d" %(k, dl, bl))
		allban += bl
		if bl > max_banned[0]:
			max_banned = (bl, k)
		if bl < min_banned[0]:
			min_banned = (bl, k)

	print(min_dup, max_dup, min_banned, max_banned, alldup / len(result), allban / len(result))
	with open("3.csv", "w", encoding="UTF8") as f:
		for k, v in result.items():
			f.write(",".join([k, str(v["count"]), 
				str(len(v["questions"])), 
				str(len(v["answers"])), 
				str((v["count"] / 2 - len(v["questions"])) / (v["count"] / 2)),
				str((v["count"] / 2 - len(v["answers"])) / (v["count"] / 2)),
				str(v["dup_ratio"])
				]))
			f.write("\n")
	'''
	
	with open("process_result/문장의미비교대량1차.json", "w", encoding="UTF8") as f:
		json.dump(result, f, ensure_ascii=False, indent="\t")
'''	with open("worker.txt", encoding="UTF8") as f, open("worker.json", "w", encoding="UTF8") as wf:
		json.dump(users(f), wf, ensure_ascii=False, indent="\t")'''