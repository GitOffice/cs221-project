etoarp_address = ".\CMUDictionarySmall.txt"
e_to_arp_add = open(etoarp_address, "r")
e_to_arp_lines = e_to_arp_add.readlines()
e_to_arp_lines = [line.strip() for line in e_to_arp_lines]
#print(e_to_arp_lines)

# map from English to Arpabet mappings, list of lists
# entry 0 is word
# entry 1 is list of arpabet components
e_to_arp = []

for line in e_to_arp_lines:
    item = line.split()
    entry = [item[0]]
    item.remove(entry[0])
    arp_list = []
    
    for word in item:
        arp_list.append(word)
        
    entry.append(arp_list)
    e_to_arp.append(entry)

#print(e_to_arp)

import pandas as pd
arp_to_chin = pd.ExcelFile(".\ARPtoChineseFinal.xls")
arp_to_chin_df = arp_to_chin.parse('Sheet2')

components = e_to_arp[1][1]
# 45 Aaronson
# issue with Z in 7
print (components)

def is_consonant(sound):
    for col in list(arp_to_chin_df):
        if sound[:-1] in col:
            return True
    return False

def is_vowel(sound):
    for row in list(arp_to_chin_df.index):
        if sound[:-1] in row:
            return row
    return None

foundPair = False
i = 0
while i < len(components):        
    foundChar = False
    foundPair = False
    for col in list(arp_to_chin_df):
        if foundChar == False and i < len(components) and components[i] in col:
            for row in list(arp_to_chin_df.index):
                if foundChar == False and i + 1 < len(components) and components[i + 1][:-1] in row:
                    if (i + 3 == len(components) and not is_consonant(components[i + 2])) \
                       or (i + 3 < len(components) and is_consonant(components[i + 2]) and not(is_consonant(components[i + 3]))) \
                       or (i + 2 == len(components)):
                        #should do the pairing CV; not CVC case
                        part = arp_to_chin_df.loc[row][col].encode('utf-8')
                        chin_char = part.decode('utf-8')
                        #print "found the pairing " + str(i)
                        print (chin_char)
                        foundChar = True
                        foundPair = True
                        i += 1
                        break
                    else:
                        #CVC case
                        second_half = components[i + 1][:len(components[i + 1]) - 1] + components[i + 2] + " "
                        this_row = is_vowel(second_half)
                        if this_row is not None:
                            part = arp_to_chin_df.loc[this_row][col].encode('utf-8')
                            chin_char = part.decode('utf-8')
                            print (chin_char)
                            foundChar = True
                            foundPair = True
                            i += 2
                            break
                        else:
                            part = arp_to_chin_df.loc[row][col].encode('utf-8')
                            chin_char = part.decode('utf-8')
                            print (chin_char)
                            foundChar = True
                            foundPair = True
                            i += 1
                            break
                
            # else, print the lone consonant transcription
            if foundChar == False:
                part = arp_to_chin_df.loc['-'][col].encode('utf-8')
                chin_char = part.decode('utf-8')
                #print "just the consonant "  + str(i)
                print (chin_char)
                foundChar = True
                break
    
    # else, print the lone vowel transcription
    if foundChar == False and foundPair == False:
        for row in list(arp_to_chin_df.index):
            if foundChar == False and i < len(components) and components[i][:-1] in row:
                part = arp_to_chin_df.loc[row]['-'].encode('utf-8')
                chin_char = part.decode('utf-8')
                #print "just the vowel " + str(i)
                print (chin_char)
                foundChar = True
                break
    i += 1
