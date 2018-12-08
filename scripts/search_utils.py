import pandas as pd
import os
from collections import Counter
import math
import edit_distance
import re
import string


data_dir = os.path.join("..", "data")
chinese_names = pd.read_csv(os.path.join(data_dir, "EnglishChineseNames_uniq.txt"))
DATA_SIZE = chinese_names.shape[0]

def normalize(s):
    """
    Right now just converts a string to lowercase but could be something more later
    (such as removing spaces)
    """
    s = re.sub(r"([-.·])", r"", s) # remove punctuation that seems to have seeped in (including chinese dash)
    return s.lower()

def is_vowel(c):
    return c in 'āáǎàaēéěèeīíǐìiōóǒòoūúǔùuǖǘǚǜü'

def has_tone(c):
    return c in 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü'

def toneless_vowel(p):
    if p in 'āáǎà': return 'a'
    if p in 'ēéěè': return 'e'
    if p in 'īíǐì': return 'i'
    if p in 'ōóǒò': return 'o'
    if p in 'ūúǔù': return 'u'
    if p in 'ǖǘǚǜ': return 'ü'
    return p

def remove_tone(pinyin):
    new_pinyin = ""
    for p in pinyin:
        new_pinyin += toneless_vowel(p)
    return new_pinyin

def break_pinyin(line):
    """
    Takes a string of pinyin represenations of characters and breaks them into individual syllables with a heurisitc
    """

    pinyins = []
    first_ind = 0
    found_tone = False
    line  = "{}  ".format(line) # pad to prevent off by one-errors :) 
    for end_ind in range(len(line)):
        # split at explicit syllable stops
        if line[end_ind] == " " or line[end_ind] == "'":
            pinyins.append(line[first_ind : end_ind])
            first_ind = end_ind + 1
            found_tone = False
        
        # only allow for one tone per syllable
        if is_vowel(line[end_ind]) and has_tone(line[end_ind]):
            if found_tone:
                pinyins.append(line[first_ind : end_ind ])
                first_ind = end_ind
                found_tone = False
            else:
                found_tone = True
        
        # vowel followed by consonants mark the end of the words
        if is_vowel(line[end_ind]) and not is_vowel(line[end_ind + 1]):
            offset = 1

            # if the vowel is followed by r, n, or ng, we have a special case
            if line[end_ind + 1] == 'r':
                offset = 2
            elif line[end_ind + 1 : end_ind + 3] == 'ng':
                offset = 3
            elif line[end_ind + 1] == 'n':
                offset = 2
            
            pinyins.append(line[first_ind : end_ind + offset])
            first_ind = end_ind + offset
            found_tone = False
        
    pinyins = filter(lambda c: len(c) > 0, pinyins)
    return " ".join(pinyins).strip()

def test_break_pinyin():
    assert break_pinyin("lì dì xīyǎ") == 'lì dì xī yǎ'
    assert break_pinyin("kèlǐsīdì nà") == 'kè lǐ sī dì nà'
    assert break_pinyin("jīnbǎilì") == "jīn bǎi lì"
    assert break_pinyin("lùsī'ēn") == "lù sī ēn"
    assert break_pinyin("mǎ'ěr kē mǔ") == "mǎ ěr kē mǔ"
    assert break_pinyin("qiáo ānnà") == "qiáo ān nà"
    assert break_pinyin("qiángnàshēng") == "qiáng nà shēng"
    assert break_pinyin("zhānmǔsī") == "zhān mǔ sī"
    assert break_pinyin("jí'ěr") == "jí ěr"
    assert break_pinyin("āndōngní'ào") == "ān dōng ní ào"
    assert break_pinyin("ā bǐ gàiěr") == "ā bǐ gài ěr"

# handle phonetically similar cases
def phoneme_adjust(eng):            
    eng = eng.lower()
    eng = eng.replace('ju', 'zhu')
    eng = eng.replace('ew', 'iu')
    eng = eng.replace('r', 'l')

    # get rid of repeating letters
    for i in range(len(eng)):
        if i < len(eng) - 1 and eng[i] == eng[i + 1]:
            eng = eng[0:i] + eng[i + 1:]
            
    eng = eng.replace('ia', 'iya')
    eng = eng.replace('ce', 'si')
    eng = eng.replace('ci', 'si')
    eng = eng.replace('ch', 'q')
    eng = eng.replace('c', 'k')
    eng = eng.replace('ck', 'k')
    eng = eng.replace('ph', 'f')
    if eng.count('y') > 1:
        eng = "".join(reversed("".join(reversed(eng)).replace('y', 'i', 1))) # y is i if at end of string
    if eng != "" and eng[-1] == 'y':
        eng = eng[0:len(eng) - 1] + 'i'
    eng = eng.replace('th', 'x')
    eng = eng.replace('v', 'w')

    # get rid of repeating letters once more
    for i in range(len(eng)):
        if i < len(eng) - 1 and eng[i] == eng[i + 1]:
            eng = eng[0:i] + eng[i + 1:]
            
    return eng

# syllable number heuristic
import numpy as np
from sklearn import linear_model

def len_without_vowels(eng):
    return len([char for char in eng if not is_vowel(char)])

def num_cons_clusters(eng):
    num = 0
    for i in range(len(eng)):
        if i < len(eng) - 1 and not is_vowel(eng[i]) and not is_vowel(eng[i + 1]):
            num += 1
    return num

lin_mod = linear_model.LinearRegression()
chinese_names['length'] = chinese_names.apply(lambda row: len(phoneme_adjust(row['first name'])), axis = 1)
chinese_names['consonants'] = chinese_names.apply(lambda row: len_without_vowels(phoneme_adjust(row['first name'])), axis = 1)
##chinese_names['clusters'] = chinese_names.apply(lambda row: num_cons_clusters(row['first name']), axis = 1)
chinese_names['syllables'] = chinese_names.apply(lambda row: len(row['chinese']), axis = 1)

train_input = chinese_names[chinese_names.columns[-3:-1]]
train_output = chinese_names[chinese_names.columns[-1:]]

lin_mod.fit(train_input, train_output)

def expected_syllables(eng):
    name_length = len(eng)
    name_consonants = len_without_vowels(eng)
##    name_clusters = num_cons_clusters(eng)
    pred_input = pd.DataFrame({'length': [name_length], 'consonants': [name_consonants]})
    return lin_mod.predict(pred_input)[0][0]


# uniform cost function inspired from reconstruction assignment
def create_ucf(pinyins = None):
    split_pinyin = []

    if pinyins is None:
        pinyins = chinese_names.pinyin

    for p in pinyins:
        split_pinyin.extend(p.split())

    total_unigrams = len(split_pinyin)
    unigram_freqs = Counter(split_pinyin)
    
    def ucf(p):
        """
        We want to mizimize the score edit_distance(p, other_pinyin) * surprisal(other_pinyin) over all other pinyin and take the 
        pinyin that minimizes this 
        """

        # this is essentially the "surprisal" of a word. Higher surprisal means higher cost
        if p not in unigram_freqs:
            ucs = math.log(total_unigrams + 1) - math.log(1) + 10 * len(p) # b/c why not
        else:
            ucs =  math.log(total_unigrams) - math.log(unigram_freqs[p]) # English names dont have tones, so we can just ignore them

        # edit_distance.edit_distance_pinyin takes into account tone differences
        p = phoneme_adjust(p)
        return min([(edit_distance.edit_distance(p, remove_tone(pinyin)) * ucs, pinyin) for pinyin in unigram_freqs])
        
    return ucf
    
def test_ucf():
    my_ucf = create_ucf()
    print("Enter words to find the unigram cost of")
    while True:
        word = input(">> ")
        s = my_ucf(word)
        print(s)
    

if __name__ == "__main__":
    test_break_pinyin()
    test_ucf()

