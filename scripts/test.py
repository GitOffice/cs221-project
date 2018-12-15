import search_phonememod, search_utils
import math

NAME_LIST = ['archana', 'benjamin', 'julia', 'animesh', 'roy', 'miles', 'james', 'mary', 'george',
             'carl', 'einstein', 'liya', 'lia', 'mandy', 'vickie', 'esther', 'jade', 'tom', 'michael',
             'thomas', 'matthew', 'matt', 'andrew', 'andy', 'eliza', 'amy', 'alice', 'john', 'meg',
             'daniel', 'danielle', 'golrokh', 'matin', 'behzad', 'sean', 'robert', 'rupert', 'bruce',
             'claudia', 'angel', 'megan', 'meghan', 'bernard', 'madison', 'chloe', 'charles', 'jack',
             'jenn', 'jennifer', 'jon', 'suvir', 'priscilla', 'veronica', 'vera', 'cynthia', 'spencer',
             'morgan', 'sebastian', 'louis', 'oscar', 'denise', 'dory', 'alicia', 'timothy', 'bowen',
             'owen', 'martin', 'thariq', 'parth', 'dave', 'david', 'victoria', 'micaela', 'lionel']

# test syllable prediction function
##def print_pred_syllables(name):
##    pred_syll = search_utils.expected_syllables(name)
##    # if name begins with vowel, then consonant, increase by 1
##    if len(name) > 1:
##        if search_utils.is_vowel(name[0]) and not search_utils.is_vowel(name[1]):
##            pred_syll += 1.0
##    
##    lower_bound = math.floor(pred_syll)
##    upper_bound = math.ceil(pred_syll)
##    print('# syllables for ' + name + ': ' + str(lower_bound) + '-' + str(upper_bound))

##for name in NAME_LIST:
##    print_pred_syllables(search_utils.phoneme_adjust(name))

# test syllable heuristic function
##def print_heur_syllables(name):
##    pred_syll = search_utils.syllable_heuristic(name)
##    print('# syllables for ' + name + ': ' + str(pred_syll))
##
##for name in NAME_LIST:
##    print_heur_syllables(search_utils.phoneme_adjust(name))
    
# test output names
for name in NAME_LIST:
    print(name + ': ' + str(search_phonememod.find_closest_pinyin(name, False)))

# debug examples
##print(search_phonememod.find_closest_pinyin('jennifer', True))

# test average edit distance
##search_phonememod.evaluate_predictions()
