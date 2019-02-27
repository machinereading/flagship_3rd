def memoize(func):
	mem = {}
	def memoizer(*args, **kwargs):
		key = str(args) + str(kwargs)
		if key not in mem:
			mem[key] = func(*args, **kwargs)
		return mem[key]
	return memoizer
@memoize    
def levenshtein(s, t):
	if s == "":
		return len(t)
	if t == "":
		return len(s)
	if s[-1] == t[-1]:
		cost = 0
	else:
		cost = 1
	
	res = min([levenshtein(s[:-1], t)+1,
			   levenshtein(s, t[:-1])+1, 
			   levenshtein(s[:-1], t[:-1]) + cost])
	return res

def lev_all(s, t):
	result = []
	for i in range(len(s)):
		result.append([0]*i)
		for j in range(i, len(s)):
			result[-1].append(levenshtein(s[i:j], t))
	return result