import pandas as pd
import sys

data = pd.read_csv("data.csv")

def plot_data():
    return data

a = plot_data()

print(a)
sys.stdout.flush()

