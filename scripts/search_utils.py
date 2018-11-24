import pandas as pd
import os
from collections import Counter
import math
import edit_distance
import re


data_dir = os.path.join("..", "data")
chinese_names = pd.read_csv(os.path.join(data_dir, "EnglishChineseNames_uniq.txt"))

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




# inspired from reconstruction assignment
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

        # edit_distance.edit_distance_piyin takes into account tone differences
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

