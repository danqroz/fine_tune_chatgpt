import json
import os
import pandas as pd

script_dir = os.path.dirname(__file__)
files = [
    os.path.join(script_dir, "data", "intents.json"),
    os.path.join(script_dir, "data", "intents2.json")
]
SAVE_PATH = os.path.join(script_dir, "data", "cleaned_chatbot_data.csv")

tags = [
    "greeting",
    "morning",
    "afternoon",
    "evening",
    "night",
    "goodbye",
    "thanks",
    "name"
]

messages = []
for file in files:
    with open(file, encoding="utf-8") as f:
        data = json.load(f)
    for element in data["intents"]:
        if element["tag"] in tags:
            for pattern in element["patterns"]:
                for response in element["responses"]:
                    messages.append({"questionText": pattern, "clean_answer": response})

df = pd.DataFrame(messages)
df.to_csv(SAVE_PATH, index=False)
