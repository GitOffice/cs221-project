import edit_distance
import search_utils
import sys

# for max_len heurisitc 
import curses 
from curses.ascii import isdigit 
import nltk
from nltk.corpus import cmudict 

import pyphen

d = cmudict.dict() 
def nsyl(word): 
    return [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]] 

dic = pyphen.Pyphen(lang='nl_NL')

ok_clusters = {'ch', 'sh', 'th'}

def max_pinyin_length(name):
    """
    heuristic for finding the maximum number of pinyin from an english name
    """
    num_syllables = 0
    try:
        num_syllables = nsyl(name)[0]
    except:
        pass
    hyphenated = dic.inserted(name).split('-')
    hyph_count = len(hyphenated)
    # add 1 for each consonant cluster
    for h in hyphenated:
        for i in range(len(h)):
            bgram = h[i:min(len(h), i+2)]
            if len(bgram) == 2 and not search_utils.is_vowel(bgram[0]) and not search_utils.is_vowel(bgram[1]) and bgram[1] != 'y':#not in ok_clusters:
                hyph_count += 1
                num_syllables += 1

    # starts with vowel
    if search_utils.is_vowel(hyphenated[0][0]):
        hyph_count += 1
        num_syllables += 1

    # has some commonly messed up letter combos :(
    if "ia" in name or "oi" in name or "oui" in name:
        hyph_count += 1
        num_syllables += 1
        
    return max(hyph_count, num_syllables)

def get_n_grams(s, n):
    """
    return list of [n]grams of a string [s]
    """
    n_grams = []
    for i in range(0, len(s) - n + 1):
        n_grams.append(s[i:i+n])
    return n_grams

def get_n_grams_ind(s, n):
    """
    returns a list of tuples where the first element is the start index of the [n]-gram and the
    second element is the associated [n]-gram of the string [s]
    """
    n_grams = []
    for i in range(0, len(s) - n + 1):
        n_grams.append((i, s[i:i+n]))
    return n_grams

def init_ngrams():
    """
    creates a dictionary mapping each 1, 2, and 3-gram of all English names in the corpus to
    a dictionary of pinyin that appear in the same names as those ngrams, weighted by how close
    the pinyin is in the tranliteration to the place the english ngram is in the name
    """
    chinese_names = search_utils.chinese_names
    counter = {}
    whole_corpus = {}
    for rowi, row in chinese_names.iterrows():
        name, _, _, pinyin, _, _, _ = row
        name = "S" + name.lower() + "E"
        all_grams = []
        
        for i in range(1, 4):
            all_grams += get_n_grams_ind(name, i)

        for ng_i, ng in all_grams:
            if ng not in counter:
                counter[ng] = {}
            
            # weight pinyin close to the ngram more
            ng_ind = int((ng_i / len(ng))*len(pinyin.split(' ')))
            for i, p in enumerate(pinyin.split(' ')):
                if ng_ind == i:
                    counter[ng][p] = counter[ng].get(p, 0) + 2 # count the pinyin in the appropriate position 2x as much
                else:
                    counter[ng][p] = counter[ng].get(p, 0) + 1
                whole_corpus[p] = whole_corpus.get(p, 0) + 1

    return counter, whole_corpus

def most_popular(counter, c, n = 1):
    """ 
    takes a dictionary and an english ngram, and returns the [n] pinyin that co-occur most frequently
    """
    return sorted([(counter[c][p], p) for p in counter[c]], key=lambda t: -t[0])[:n]


def enumerate_pinyin(name, counter):
    """
    returns the ngrams and associated counts of the top 2 n-grams
    """
    all_grams = []
    pinyin_count_list = []
    # get list of all uni, bi, and trigrams in the name
    for i in range(1, 4):
        all_grams += get_n_grams(name, i)
    
    for ng in all_grams:
        # ignore single S and E
        if ng != "S" and ng != "E":
            try:
                # get the top 2 most commonly associated pinyin with that ngram
                mp = most_popular(counter, ng, 2)
                for m in mp:
                    if 'S' in ng or 'E' in ng:
                        # if names start with vowels (Sv) or end with vowels (vE) add one to the length 
                        # to give those ngrams' pinyin more weight.
                        if len(ng) > 1 and search_utils.is_vowel(ng[1]):
                            pinyin_count_list.append((len(ng), *m))
                        else:
                            pinyin_count_list.append((len(ng) - 1, *m))
                    else:
                        pinyin_count_list.append((len(ng), *m))
            except:
                continue
    return pinyin_count_list


def parse(pinyin):
    """
    Separates pinyin into consonants, vowels, [consonant] format to keep track of 
    individual pinyin component frequencies
    """
    found_vowel = False
    c1, v1, c2 = '','',''
    for c in pinyin:
        if search_utils.is_vowel(c):
            found_vowel = True
            v1 += c
        elif found_vowel:
            c2 += c
        else:
            c1 += c
    return c1, v1, c2
    


def score_tuples(pinyin_list, whole_corpus):
    """
    Input in form [(n-gram size, count, pinyin)]. Calculates a score for each pinyin
    based on the length of the ngram, the count, and the prevalence in both the list
    and the dataset
    """
    # first set up histogram to keep track of common consontants/vowels in pinyin list
    histogram = {}
    for _, _, pinyin in pinyin_list:
        for c in parse(pinyin):
            if len(c) > 0:
                histogram[c] = histogram.get(c, 0) + 1

    # now score each pinyni on the list
    pinyin_scores = []
    for ng_size, count, pinyin in pinyin_list:
        score = count / (search_utils.DATA_SIZE / (26**min(ng_size,2) )) # count trigrams and bigrams the same, and both more than unigrams
        score /= whole_corpus[pinyin] # normalize by the number of times in corpus to penalize background noise
        score = sum(score*histogram[c] if c != '' else 0 for c in parse(pinyin)) # consonants/vowels that appear more often will 
                                                                                 # have a larger score
        pinyin_scores.append((score, pinyin))
        
    return pinyin_scores

def find_closest_pinyin(name, whole_corpus, counter):
    """
    Normally, we want to find the minimum cost pinyin, in this case, we actually want to find the maximum "cost"
    pinyin (that is the highest score).
    """
    cache = {}
    def recurse(syllables, rest, max_pinyin_len, do_print = False):
        hash_sylls = ",".join(syllables)
        if hash_sylls in cache:
            return cache[hash_sylls]

        # base case - calculate the score of the pinyin
        if len(rest) == 0:
            pinyin = []
            cost = 0
            if len(syllables) <= max_pinyin_len:
                for u in syllables:
                    if len(u) > 0 and len(u) < 4 and u != 'S' and u != 'E':
                        c, p = max(score_tuples(enumerate_pinyin(u, counter), whole_corpus))
                        pinyin.append(p)
                        cost += c

            result = (cost, pinyin)
            cache[hash_sylls] = result
            return result

        # add the next letter of the rest of the english characters to the
        # current segmentation
        syllables[-1] += rest[0]
        syllables_keep = [x for x in syllables]
        cost_keep, s_keep = recurse(syllables_keep, rest[1:], max_pinyin_len)
        syllables[-1] = syllables[-1][:-1]

        cost_end, s_end = (0, [])
        if syllables[0] != "": # the first character shouldn't be empty
            # repeat vowels on both sides of breaks "julia" -> "ju", "li", "ia"
            if search_utils.is_vowel(syllables[-1][-1]) or syllables[-1][-1] == 'y':
                syllables.append(syllables[-1][-1] + rest[0])
                syllables_end = [x for x in syllables]
                cost_end, s_end = recurse(syllables_end, rest[1:], max_pinyin_len)
                syllables = syllables[:-1]
            # repeat consonants on both side when left is consonant blend - "blake" -> "bl", "la", "ke"
            elif not search_utils.is_vowel(syllables[-1][-1]) and not search_utils.is_vowel(rest[0]) and not syllables[-1][-1] + rest[0] in ok_clusters:
                syllables[-1] += rest[0]
                syllables.append(rest[0])
                syllables_end = [x for x in syllables]
                cost_end, s_end = recurse(syllables_end, rest[1:], max_pinyin_len)
                syllables = syllables[:-1]
                syllables[-1] = syllables[-1][:-1]

            # end the last syllable segment and start the new segment
            syllables.append(rest[0])            
            syllables_end = [x for x in syllables]
            cost_end2, s_end2 = recurse(syllables_end, rest[1:], max_pinyin_len)
            
            cost_end, s_end = max( (cost_end2, s_end2), (cost_end, s_end))
            syllables = syllables[:-1]

        result = max((cost_end, s_end), (cost_keep, s_keep))
        cache[hash_sylls] = result
        return result

    
    mpl = max_pinyin_length(name)
    if search_utils.is_vowel(name[-1]):
        name += 'E'
    if search_utils.is_vowel(name[0]):
        name = 'S' + name
    
    res = recurse([""], name, mpl)
    return res


def evaluate_predictions(**kwargs):
    distance = 0
    diff_count = 0
    for row_i, row in search_utils.chinese_names.iterrows():
        # if row_i > 10:
        #     break
        if row_i % 50 == 0:
            print("{}% complete".format(100 * row_i/search_utils.chinese_names.shape[0]))
        english, _, _, target_pinyin, _, _, _ = row
        english = search_utils.normalize(english)
        target_pinyin = ''.join(filter(lambda x: x != ' ', search_utils.normalize(target_pinyin)))
        #print(english)
        if search_utils.is_vowel(english[0]): english = 'S' + english
        if search_utils.is_vowel(english[-1]): english = english + 'E'
        output_pinyin = ''.join(find_closest_pinyin(english, **kwargs)[1])
        if output_pinyin != target_pinyin:
            #print (english, output_pinyin, target_pinyin)
            diff_count += 1
            distance += edit_distance.edit_distance_pinyin(target_pinyin, output_pinyin)

    print("Out of {} names, {} were different, with an average edit distance of {} ({} for just the different pairs)".format(search_utils.chinese_names.shape[0], diff_count, distance/search_utils.chinese_names.shape[0], distance/diff_count))



if __name__ == "__main__":

    counter, whole_corpus = init_ngrams()
    if len(sys.argv) > 1 and sys.argv[1] == 'eval':
        evaluate_predictions(whole_corpus=whole_corpus, counter=counter)
    else:
        while True:
            name = input("name >> ")
            result = find_closest_pinyin(name, whole_corpus, counter)
            print(result)


