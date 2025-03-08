# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import numpy as np


# Set the path to the file you'd like to load
file_path = "src/data/raw_pubmed.csv"
import os
if not os.path.exists("src/data/pubmed-article-summarization-dataset.zip"):
    os.system("curl -L -o src/data/pubmed-article-summarization-dataset.zip  https://www.kaggle.com/api/v1/datasets/download/thedevastator/pubmed-article-summarization-dataset")
# unzip into src/data/pubmed
if not os.path.exists("src/data/pubmed"):
    os.system("unzip src/data/pubmed-article-summarization-dataset.zip -d src/data/pubmed")

if not os.path.exists("src/data/pubmed_test.csv"):
    csv = pd.read_csv("src/data/pubmed/test.csv")
    print(csv.head(5))
    articles = csv.abstract.values # a numpy array of articles saved as strings
    filenames = "PubMed_test_" + csv.index.astype(str) + ".txt" # a numpy array of filenames
    meta_data = np.array(["" for x in csv.abstract.values]) #np.array(["Abstract=" + x for x in csv.abstract.values])
    # now make a dataframe with columns file_name,meta_data,content,last_updated
    df = pd.DataFrame(columns=["file_name","meta_data","content","last_updated"])
    df["content"] = articles
    df["file_name"] = filenames
    df["meta_data"] = meta_data
    df["last_updated"] = pd.Timestamp.now()
    # remove the index
    df.reset_index(drop=True,inplace=True)
    df.to_csv("src/data/pubmed_test.csv", index=False)
    print("Saved as CSV")

