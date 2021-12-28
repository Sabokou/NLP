import json
import pandas as pd

# Open training dataset (downloaded from: https://rajpurkar.github.io/SQuAD-explorer/)
with open("train-v2.0.json", "r") as f:
    # Load data from json
    output = json.load(f)
    # Discarding version from 1st level json hierarchy
    output = output.get("data")

# create list with all question and answer pairs from json
liste_to_df = list()
for i in output[:]:
    title = i.get("title")
    paragrahs = i.get("paragraphs")
    # print("I-Keys:", i.keys())
    for j in paragrahs:
        quest_list = j.get("qas")
        # Add token to context string
        context = "<CNTXT> " + j.get("context")
        # print("\n\nJ-Keys:",j.keys())
        for k in quest_list:
            # print("\n\nK-Keys:", k.keys())
            if not k.get("is_impossible"):
                question = k.get("question")
                # Add token to answer string
                answers = "<ANWSR> " + k.get("answers")[0].get("text") + " "
                # Combine answer and context
                combined_for_model = answers + context
                # print(f"Frage:{question}\nAntwort:{answers}\nKontext:{context}\n\n")
                liste_to_df.append([question, combined_for_model])

# Create Dataframe to more easily work with the data
df = pd.DataFrame(liste_to_df, columns=["frage", "kontext"])
# split Dataframe into training and validation datasets
training_df = df.sample(frac=0.75)
validation_df = df.drop(training_df.index)
# Save datasets to CSVs
training_df.to_csv("training.csv", sep=";", index=False)
validation_df.to_csv("validation.csv", sep=";", index=False)
