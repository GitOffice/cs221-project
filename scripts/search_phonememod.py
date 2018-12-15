import search_utils
import edit_distance
import sys
import math

MAX_PINYIN_SIZE = 6
ok_clusters = {'ch', 'sh', 'th'}

def find_closest_pinyin(name, do_print):

    unigram_cost = search_utils.create_ucf()
    name = search_utils.phoneme_adjust(name)
##    target_syllables = search_utils.expected_syllables(name)
    target_syllables = search_utils.syllable_heuristic(name)

    cache = {}
    # iterate through all possible breakings of the name (i.e. powerset of characters)
    def recurse(syllables, rest):
        hash_sylls = ",".join(syllables)
        if hash_sylls in cache:
            return cache[hash_sylls]

        if len(rest) == 0:
            pinyin = []
            cost = 0
            for u in syllables:
                c, p = unigram_cost(u)
                pinyin.append(p)
                cost += c
            # add cost of syllable length deviation
            if len(syllables) != math.floor(target_syllables) and len(syllables) != math.ceil(target_syllables):
                cost += 10 * math.ceil(abs(len(syllables) - target_syllables))
            if do_print:
                print(pinyin, cost)
            result = (cost, pinyin)
            cache[hash_sylls] = result
            return result

        syllables[-1] += rest[0]
        syllables_keep = [x for x in syllables]
        cost_keep, s_keep = recurse(syllables_keep, rest[1:])
        syllables[-1] = syllables[-1][:-1]

        cost_end, s_end = (float('inf'), [])
        if syllables[0] != "":
            syllables.append(rest[0])
            syllables_end = [x for x in syllables]
            cost_end, s_end = recurse(syllables_end, rest[1:])
            syllables = syllables[:-1]

        result = min((cost_keep, s_keep), (cost_end, s_end))
        cache[hash_sylls] = result
        return result
        # else:
        #   return (cost_keep, s_keep)

    #return unigram_cost(name)
    return recurse([""], name)
    #return all_actions

def evaluate_predictions():
    all_names = search_utils.chinese_names
    distance = 0
    diff_count = 0
    for row_i, row in all_names.iterrows():
        if row_i % 20 == 0:
            print("{}% complete".format(100 * row_i/all_names.shape[0]))
        english, _, _, target_pinyin, _, _, _ = row
        english = search_utils.normalize(english)
        target_pinyin = ''.join(filter(lambda x: x != ' ', search_utils.normalize(target_pinyin)))

        output_pinyin = ''.join(find_closest_pinyin(english, False)[1])
        if output_pinyin != target_pinyin:
            #print (english, output_pinyin, target_pinyin)
            diff_count += 1
            distance += edit_distance.edit_distance_pinyin(target_pinyin, output_pinyin)

    print("Out of {} names, {} were different, with an average edit distance of {} ({} for just the different pairs)".format(all_names.shape[0], diff_count, distance/all_names.shape[0], distance/diff_count))





if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'eval':
        evaluate_predictions()
    else:
        while True:
            name = input("name >> ")
            result = find_closest_pinyin(name, True)
            print(result)

