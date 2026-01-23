import pandas as pd

df = pd.read_csv("data/reference_ranges_age_gender.csv")

def interpret_parameter(param, value, age, gender):
    row = df[
        (df["parameter"] == param) &
        ((df["gender"] == gender) | (df["gender"] == "Any")) &
        (df["age_min"] <= age) &
        (df["age_max"] >= age)
    ]

    if row.empty:
        return "Unknown"

    low, high = row.iloc[0]["low"], row.iloc[0]["high"]

    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Normal"
