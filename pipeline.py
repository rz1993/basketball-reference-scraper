from config import DB_ADDRESS

import csv
import json

def save_to_csv(tuples, header, csv_out):
    with open(csv_out, 'w+', newline='') as f:
        f.write(", ".join(header) + "\n")
        for t in tuples:
            row = ", ".join(map(str, t)) + "\n"
            f.write(row)

def save_to_json(data, json_out, **kwargs):
    with open(json_out, 'w') as f:
        json.dump(data, json_out, **kwargs)

def load_from_csv(filename, delimiter=", "):
    with open(filename, 'r') as f:
        header = f.readline()
        return header, [row.strip('\n').split(delimiter) for row in f]

def load_from_json(filename, **kwargs):
    with open(filename, 'r') as f:
        return json.load(f, **kwargs)
