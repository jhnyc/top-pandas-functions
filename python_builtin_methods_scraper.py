import pandas as pd

object_methods = ["string", "list", "tuple", "dictionary", "set", "file"]

all_ = []
for o in object_methods:
    tmp = pd.read_html(
        f"https://www.w3schools.com/python/python_ref_{o}.asp")[0]
    tmp["Object"] = o
    all_.append(tmp)

df = pd.concat(all_).reset_index(drop=True)
df.to_csv("data/all_builtin_methods.csv", index=False)
