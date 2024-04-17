import pandas as pd

df = pd.read_csv("../data/visit_probability.csv")

df.to_json("../data/visit_probability.json")
