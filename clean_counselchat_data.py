import os
import re
import unicodedata

import pandas as pd
import spacy
from bs4 import BeautifulSoup
from datasets import load_dataset


def _remove_phone_number(text):
    pattern = r"\(?\d{3}\)?\s?-?\s?\d{3}\s?-?\s?\d{4}"
    return re.sub(pattern, "", text)


def _remove_entity(text):
    doc = nlp(text)
    clean_text = text
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            clean_text = text.replace(ent.text, "")
    return clean_text


def _clean_text(text):
    soup = BeautifulSoup(text, "html.parser")
    new_text = soup.get_text()
    normalized_text = re.sub(r" +", " ", unicodedata.normalize("NFKD", new_text))
    no_phone_text = _remove_phone_number(normalized_text)
    no_ent_text = _remove_entity(no_phone_text)
    clean_text = re.sub(r"(?<![.!?])\r?\n", " ", no_ent_text)
    return clean_text.strip()


def _remove_blanks(df, column):
    new_df = df.replace(r"^s*$", float("NaN"), regex=True)
    return new_df.dropna(subset=column)


def _clean_df(df):
    df.dropna(subset=["answerText"], inplace=True)
    df["questionText"].fillna(df["questionTitle"], inplace=True)
    df["clean_answer"] = df["answerText"].apply(_clean_text)
    df = _remove_blanks(df, "clean_answer")
    return df


script_dir = os.path.dirname(__file__)
files = [
    os.path.join(script_dir, "data", "20200325_counsel_chat.csv"),
    os.path.join(script_dir, "data", "counselchat-data.csv")
]
SAVE_PATH = os.path.join(script_dir, "data", "cleaned_counselchat.csv")
nlp = spacy.load("en_core_web_sm")


def main():
    cols = ["questionTitle", "questionText", "answerText"]

    dfs = [pd.read_csv(file, usecols=cols) for file in files]
    df = pd.concat(dfs)
    df.dropna(axis=0, subset="questionTitle", inplace=True)
    cleaned_df = _clean_df(df)
    cleaned_df["temp"] = cleaned_df["clean_answer"].apply(lambda x: x.lower())

    dataset = load_dataset("nbertagnolli/counsel-chat")
    dataset = dataset["train"].to_pandas()

    dataset = dataset[["questionTitle", "questionText", "answerText"]]
    cleaned_dataset = _clean_df(dataset)
    cleaned_dataset["temp"] = cleaned_dataset["clean_answer"].apply(lambda x: x.lower())

    mask = cleaned_dataset["temp"].isin(cleaned_df["temp"])
    dataset_out = cleaned_dataset[~mask]

    full_df = pd.concat([cleaned_df, dataset_out])

    full_df.drop_duplicates(subset=["temp"], inplace=True)
    full_df.drop(columns=["answerText", "temp", "questionTitle"], inplace=True)
    span_idxs = [1092, 1091, 1090, 1089, 1088]
    full_df.drop(index=span_idxs, inplace=True)

    full_df.to_csv(SAVE_PATH, index=False)


if __name__ == "__main__":
    main()
