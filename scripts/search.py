import search_utils


MAX_PINYIN_SIZE = 6

def find_closest_pinyin(name, do_print):

	unigram_cost = search_utils.create_ucf()

	# iterate through all possible breakings of the name (i.e. powerset of characters)
	def recurse(syllables, rest):
		if len(rest) == 0:
			pinyin = []
			cost = 0
			for u in syllables:
				c, p = unigram_cost(u)
				pinyin.append(p)
				cost += c
			if do_print:
                                print(pinyin, cost + len(syllables))
			return (cost, pinyin)

		syllables[-1] += rest[0]
		syllables_keep = [x for x in syllables]
		cost_keep, s_keep = recurse(syllables_keep, rest[1:])
		syllables[-1] = syllables[-1][:-1]

		#if syllables[0] != "":
		syllables.append(rest[0])
		syllables_end = [x for x in syllables]
		cost_end, s_end = recurse(syllables_end, rest[1:])
		syllables = syllables[:-1]

		return min((cost_end, s_end), (cost_keep, s_keep))
		# else:
		# 	return (cost_keep, s_keep)

	#return unigram_cost(name)
	return recurse([""], name)
	#return all_actions


if __name__ == "__main__":
	while True:
		name = input("name >> ")
		result = find_closest_pinyin(name)
		print(result)
