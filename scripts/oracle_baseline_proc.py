import pandas as pd
import edit_distance
import baseline
import os

def process_oracle(oracle_csv):
    df = pd.ExcelFile(oracle_csv).parse('Sheet1')
    #df = pd.read_csv(oracle_csv)
    o1 = df["Pinyin_O1"]
    o2 = df["Pinyin_O2"]

    distance = 0
    diff_count = 0
    for name1, name2 in zip(o1, o2):
        if name1 != name2:
            diff_count += 1
            dist = edit_distance.edit_distance_pinyin(name1, name2) # 1. penalizes wrong tones as 0.5 
                                                        # 2. doesn't do the "count characters in common" thing because these are longer
            # only print stuff that's different
            print("Distance between", name1, "and", name2, ":", dist)
            distance += dist
    # take the average over ALL names, not just the ones that were wrong
    return (distance/len(o1), diff_count, len(o1))

def process_baseline(oracle_csv):
    df = pd.ExcelFile(oracle_csv).parse('Sheet1')
    df_baseline_pinyin = pd.ExcelFile(os.path.join("..", "data", "proposal", "BaselineResponses.xlsx")).parse('Sheet1')
    #df = pd.read_csv(oracle_csv)
    names = df["English"]
    o1 = df["Pinyin_O1"]
    o2 = df["Pinyin_O2"]
    bp = df_baseline_pinyin["Baseline"]

    distance = 0
    diff_count = 0
    for name, name1, name2, pinyin in zip(names, o1, o2, bp):
        if name != name1 or name != name2:
            diff_count += 1
            baseline_guess = baseline.baseline(name)
            print(baseline_guess)
            dist_o1 = edit_distance.edit_distance_pinyin(pinyin, name1)
            print("Distance between", pinyin, "and", name1, ":", dist_o1)
            dist_o2 = edit_distance.edit_distance_pinyin(pinyin, name2)
            print("Distance between", pinyin, "and", name2, ":", dist_o2)
            distance += ((dist_o1 + dist_o2) / 2)

    # take the average over ALL names
    return (distance/len(names), diff_count, len(names))

if __name__ == "__main__":
    print("\nORACLE:\n")
    avg, count, size = process_oracle(os.path.join("..","data","proposal", "OracleResponses.xlsx"))
    print("Out of {} names, {} were different, with an average edit distance of {}".format(size, count, avg))

    print("\n\nBASELINE:\n")
    avg, count, size = process_baseline(os.path.join("..", "data", "proposal", "OracleResponses.xlsx"))
    print("Out of {} names, {} were different, with an average edit distance of {}".format(size, count, avg))
