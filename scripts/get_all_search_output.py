import search
import pandas as pd
import csv

# read input file
filename = "../data/EnglishChineseNames_uniq.txt"
df = pd.read_csv(filename)

# construct lists that will be columns of output df
dl_input = [] # generated from search
dl_groundtruth = [] # correct pinyin

# get output from search, append to lists
for i in range(len(df["first name"])):
    answer = search.find_closest_pinyin(df["first name"][i], False)
    dl_input.append((' '.join(answer[1])).strip())
    dl_groundtruth.append(df["pinyin"][i])

# produce output csv file
df_out = pandas.DataFrame(data={"search_output": dl_input, "ground_truth": dl_groundtruth})
df_out.to_csv("./TransliterationSearchAndData.csv", sep=',',index=False)

# print(dl_input)
# print(dl_groundtruth)
