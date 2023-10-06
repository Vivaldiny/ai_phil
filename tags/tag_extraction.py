import os
import re
import pandas as pd

subdir = [f.name for f in os.scandir("data") if f.is_dir()]

tags = {}
text_id = []
annotator = []
exp = []
intro = []
clim = []
out = []
loc_unique = []
cut_unique = []
plotlines = []
rvr = []
nest = []

valid_tags = ["exp", "/exp",
              "in", "/in",
              "cl", "/cl",
              "out", "/out",
              "loc", "/loc",
              "cut", "/cut",
              "rvr", "/rvr"]
id_n = 1
for folder in subdir:
    for text in os.listdir("data/" + folder):
        with open(f"data/{folder}/{text}", "r", encoding="UTF-8") as file:
            story = file.read()

        text_id.append(re.search(r"S...", text).group(0))
        annotator.append(folder)
        exp.append(1 if "<exp>" in story else 0)
        intro.append(1 if "<in>" in story else 0)
        clim.append(1 if "<cl>" in story else 0)
        out.append(1 if "<out>" in story else 0)
        loc = re.findall("<loc=.*?>", story)
        if len(loc) > 0:
            loc_list = []
            for loc in set(loc):
                loc_list.append(re.findall(r"<loc=((?:.|\n)*)>", loc)[0].strip())
            loc_unique.append(", ".join(loc_list))
        else:
            loc_unique.append(None)

        cut = re.findall("<cut=.*?>", story)
        if len(cut) > 0:
            cut_list = []
            for cut in set(cut):
                cut_list.append(re.findall(r"<cut=((?:.|\n)*)>", cut)[0].strip())
            cut_unique.append(", ".join(cut_list))
        else:
            cut_unique.append(None)

        plotlines.append(len(set(re.findall("<line[1-9][0-9]?>", story))))
        rvr.append(len(re.findall("<rvr>", story)))

        tags = re.findall(r"<(.*?)>", story)
        tags_clean = []
        for tag in tags:
            if re.sub(r"=.*", "", tag) in valid_tags:
                tags_clean.append(re.sub(r"=.*", "", tag))

        for i in range(0, len(tags_clean)):
            try:
                if "/" not in tags_clean[i]:
                    clos_tag = tags_clean[i:len(tags_clean)].index(f"/{tags_clean[i]}") + i
                    tag_space = tags_clean[i + 1:clos_tag]
                    if tags_clean[i] in tag_space:
                        nested = 1
                        break
                    else:
                        nested = 0
            except:
                continue
        nest.append(nested)

df = pd.DataFrame({"text_id": text_id,
                    "annotator": annotator,
                    "exp": exp,
                    "in": intro,
                    "cl": clim,
                    "out": out,
                    "loc_unique": loc_unique,
                    "cut_unique": cut_unique,
                    "plotlines": plotlines,
                    "rvr": rvr,
                    "nested": nest})

df.to_csv("data/texts.csv", encoding="UTF-8", sep=";")

# print(len(df))

# print(len(df_clean))
locations = {}
df_clean = df[df["loc_unique"].notnull()]
for i in df_clean["text_id"].unique():
    for location in list(set(", ".join(list(df_clean[df_clean["text_id"] == i]["loc_unique"])).split(", "))):
        if location not in locations.keys():
            locations[location] = 1
        else:
            locations[location] += 1

loc_counts = pd.DataFrame.from_dict(locations, "index")
loc_counts.to_csv("data/counts.csv", encoding="UTF-8", sep=";")
