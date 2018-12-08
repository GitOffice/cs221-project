import pandas as pd
import sys
import edit_distance
import os
from pypinyin import pinyin
import search_utils

# this is probably bad style...
arp_to_chin = pd.ExcelFile(os.path.join("..", "data", "ARPtoChineseFinal.xls"))
arp_to_chin_df = arp_to_chin.parse('Sheet2')

def is_consonant(sound):
    return sound in ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L',
                     'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W',
                     'X', 'Z']

def is_vowel(sound):
    return sound in ['A', 'E', 'I', 'O', 'U', 'Y']

def closest_IPA(char):
    print(char)
    smallest_dist = sys.maxsize
    if is_consonant(char):
        closest_sound = '-'
        for col in list(arp_to_chin_df)[1:]:
            for option in col.split(','):
                option = option.strip()
                dist = edit_distance.edit_distance(char, option)
                if dist < smallest_dist:
                    smallest_dist = dist
                    closest_sound = col
        return closest_sound
    else:
        closest_sound = '-'
        for row in list(arp_to_chin_df.index)[1:]:
            for option in row.split(','):
                option = option.strip()
                dist = edit_distance.edit_distance(char, option)
                if dist < smallest_dist:
                    smallest_dist = dist
                    closest_sound = row
        return closest_sound


def baseline(components):
    components = list(components.upper())
    foundPair = False
    i = 0
    all_chars = []
    while i < len(components):        
        foundChar = False
        foundPair = False
        for col in list(arp_to_chin_df):
            curr_IPA = closest_IPA(components[i])
            if foundChar == False and i < len(components) and curr_IPA in col:
                for row in list(arp_to_chin_df.index):
                    if foundChar == False and i + 1 < len(components):
                        next_IPA = closest_IPA(components[i + 1])
                        if next_IPA in row:
                            if (i + 3 == len(components) and not is_consonant(components[i + 2])) \
                               or (i + 3 < len(components) and is_consonant(components[i + 2]) and not(is_consonant(components[i + 3]))) \
                               or (i + 2 == len(components)):
                                #should do the pairing CV; not CVC case
                                part = arp_to_chin_df.loc[row][col].encode('utf-8')
                                chin_char = part.decode('utf-8').split('/')[0].strip()
                                #print "found the pairing " + str(i)
                                all_chars.append(chin_char)
                                foundChar = True
                                foundPair = True
                                i += 1
                                break
                            else:
                                #CVC case
                                second_half = components[i + 1] + components[i + 2]
                                this_row = closest_IPA(second_half)
                                #second_half = components[i + 1][:len(components[i + 1]) - 1] + components[i + 2] + " "
                                #this_row = is_vowel(second_half)
                                part = arp_to_chin_df.loc[this_row][col].encode('utf-8')
                                chin_char = part.decode('utf-8').split('/')[0].strip()
                                all_chars.append(chin_char)
                                foundChar = True
                                foundPair = True
                                i += 2
                                break
                    
                # else, print the lone consonant transcription
                if foundChar == False:
                    part = arp_to_chin_df.loc['-'][col].encode('utf-8')
                    chin_char = part.decode('utf-8').split('/')[0].strip()
                    #print "just the consonant "  + str(i)
                    all_chars.append(chin_char)
                    foundChar = True
                    break
        
        # else, print the lone vowel transcription
        if foundChar == False and foundPair == False:
            for row in list(arp_to_chin_df.index):
                if foundChar == False and i < len(components):
                    curr_IPA = closest_IPA(components[i])
                    if curr_IPA in row:
                        part = arp_to_chin_df.loc[row]['-'].encode('utf-8')
                        chin_char = part.decode('utf-8').split('/')[0].strip()
                        #print "just the vowel " + str(i)
                        all_chars.append(chin_char)
                        foundChar = True
                        break
        i += 1
    return "".join(all_chars)

def evaluate_predictions():
    all_names = search_utils.chinese_names
    distance = 0
    diff_count = 0
    for row_i, row in all_names.iterrows():
        if row_i % 20 == 0:
            print("{}% complete".format(100 * row_i/all_names.shape[0]))
        english, _, _, target_pinyin, _, _, _ = row

        result = baseline(english)
        result_pinyin = pinyin(result)
        
        target_pinyin = ''.join(filter(lambda x: x != ' ', search_utils.normalize(target_pinyin)))
        output_pinyin = ''.join([seg[0] for seg in result_pinyin])
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
            components = input("Enter a name: ")
            res = baseline(components)
            res_pinyin = pinyin(res)
            print(res + ' | ' + ' '.join([seg[0] for seg in res_pinyin]))
