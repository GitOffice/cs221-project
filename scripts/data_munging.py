import codecs
from sys import argv

filename = argv[1]

#  converting chinese-character filled files

#
#new_lines = []
#with codecs.open(filename, encoding="utf-16", mode='r') as old_file:
#    for line in old_file:
#        new_lines.append(line.strip())# + ",m")
#
#newfilename= "{}.tmp".format(filename)
#with codecs.open(newfilename, encoding="utf-8", mode='w') as new_file:
#   new_file.write("\n".join(new_lines)) 


# editing the large all-name file
import pandas as pd

df = pd.read_csv(filename)

df["first name"] = df["first name"].apply(lambda x: x.strip().split()[0])
df.drop("last name", axis=1, inplace=True)
df.to_csv("{}.tmp".format(filename), header="column_names", index=False)
