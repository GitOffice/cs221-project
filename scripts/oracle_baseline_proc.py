import pandas as pd
import edit_distance
import baseline
import os

def process_oracle(oracle_csv):
    df = pd.read_csv(oracle_csv)
    o1 = df["Pinyin_O1"]
    o2 = df["Pinyin_O2"]

    distance = 0
    diff_count = 0
    for name1, name2 in zip(o1, o2):
        if name1 != name2:
            diff_count += 1
            dist = edit_distance.edit_distance_pinyin(name1, name2) # 1. penalizes wrong tones as 0.5 
                                                        # 2. doesn't do the "count characters in common thing because these are longer
            # only print stuff that's different
            print("Distance between", name1, name2, ": ", dist)
            distance += dist
    # take the average over ALL names, not just the ones that were wrong
    return (distance/len(o1), diff_count, len(o1))

def process_baseline(oracle_csv):
    df = pd.read_csv(oracle_csv)
    names = df["English"]
    #o1 = df["Pinyin_O1"]
    #o2 = df["Pinyin_O2"]
    

    for name in names:
        baseline_guess = baseline.baseline(name)
        print(baseline_guess)

if __name__ == "__main__":
    print("\nORACLE:\n")
    avg, count, size = process_oracle(os.path.join("..", "Oracles.csv"))
    print("Out of {} names, {} were different, with an average edit distance of {}".format(size, count, avg))

    print("\n\nBASELINE:\n")
    process_baseline(os.path.join("..", "Oracles.csv"))
    print("Figure out what to do with these... I'm not sure how you want to handle multiple possible characters. Choose one maybe?")
    print("You're gonna have to edit your baseline.py file to make that work")



