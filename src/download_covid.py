##!/bin/bash
#curl -L -o ~/Downloads/CORD-19-research-challenge.zip\
#  https://www.kaggle.com/api/v1/datasets/download/allen-institute-for-ai/CORD-19-research-challenge/metadata.csv

# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
import numpy as np
#curl -L -o ~/Downloads/covid-abstracts.zip\
#  https://www.kaggle.com/api/v1/datasets/download/anandhuh/covid-abstracts

# Set the path to the file you'd like to load
file_path = "src/data/raw_covid.csv"
import os
if not os.path.exists("src/data/COVID-abstracts.zip"):
    os.system("curl -L -o src/data/COVID-abstracts.zip  https://www.kaggle.com/api/v1/datasets/download/anandhuh/covid-abstracts")
# unzip into src/data/pubmed
if not os.path.exists("src/data/covid"):
    os.system("unzip src/data/COVID-abstracts.zip -d src/data/covid")

if not os.path.exists("src/data/covidds.csv"):
    csv = pd.read_csv("src/data/covid/covid_abstracts.csv", nrows=10000)
    #print(csv.head(5).abstract)
    vals = csv.abstract.values
    articles = csv.abstract.values # a numpy array of articles saved as strings
    filenames = csv.url.values
    meta_data = np.array(["title=" + x for x in csv.title.values]) #np.array(["Abstract=" + x for x in csv.abstract.values])
    # now make a dataframe with columns file_name,meta_data,content,last_updated
    df = pd.DataFrame(columns=["file_name","meta_data","content","last_updated"])
    df["content"] = articles
    df["file_name"] = filenames
    df["meta_data"] = meta_data
    df["last_updated"] = pd.Timestamp.now()
    # remove the index
    df.reset_index(drop=True,inplace=True)
    df.to_csv("src/data/covidds.csv", index=False)
    print("Saved as CSV")


