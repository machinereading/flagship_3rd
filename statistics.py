import os
import json
processed_dir = "process_result/"

def merge(a, b):
	for k, v in b.items():
		if k not in a:
			a[k] = v
		else:
			for k1, v1 in v.items() :
				if k1 not in a[k] :
					a[k][k1] = v1
				else :
					a[k][k1]["count"] += v1["count"]
					for x in ["questions", "answers"]:
						for sentence in v1[x]:
							if sentence not in a[k][k1][x]:
								a[k][k1][x].append(sentence)
					for x in ["duplicates", "banned", "elements_not_recognized"]:
						for sentence in v1[x]:
							a[k][k1][x].append(sentence)
		'''
		for _, v in a.items():
			# v["questions"] = list(filter(lambda x: x not in v["elements_not_recognized"], v["questions"]))
			# v["answers"] = list(filter(lambda x: x not in v["elements_not_recognized"],v["answers"]))
			v["unique_strings"] = len(v["questions"]) + len(v["answers"])
			v["dup_ratio"] = len(v["duplicates"]) / v["count"]
			v["max_dup_str"] = sorted({s:v["duplicates"].count(s) for s in v["duplicates"]}.items(), key=lambda k: -k[1])[0] if len(v["duplicates"]) > 0 else "'''
	return a



if __name__ == '__main__':
	result = {}
	for item in os.listdir(processed_dir):
		if item.startswith("_"): continue
		with open(processed_dir + item, encoding="UTF8") as f:
			j = json.load(f)
			result = merge(result, j)
	'''
	total = {"unique": 0, "dup": 0}
	for _, v in result.items():
		total["unique"] += v["unique_strings"]
		total["dup"] += len(v["duplicates"])
	total["dup_ratio"] = total["dup"] / (total["unique"]+total["dup"])
	print(total)
	'''
	with open(processed_dir+"_merged.json", "w", encoding="UTF8") as f:
		json.dump(result, f, ensure_ascii=False, indent="\t")
	print(result.keys())
	'''
	with open(processed_dir+"_stat.tsv", "w", encoding="UTF8") as f:
		f.write("\t".join(["Property", "Count", "Questions", "Answers", "Q. Dup. Ratio", "A. Dup. Ratio", "Dup. Ratio"])+"\n")
		f.write("\t".join(list(map(lambda x: str(x), ["Total", total["unique"]+total["dup"], "-", "-", "-", "-", total["dup_ratio"]])))+"\n")
		for k, v in result.items():
			f.write("\t".join([k, str(v["count"]), 
				str(len(v["questions"])), 
				str(len(v["answers"])), 
				str((v["count"] / 2 - len(v["questions"])) / (v["count"] / 2)),
				str((v["count"] / 2 - len(v["answers"])) / (v["count"] / 2)),
				str(v["dup_ratio"])
				]))
			f.write("\n")
	'''