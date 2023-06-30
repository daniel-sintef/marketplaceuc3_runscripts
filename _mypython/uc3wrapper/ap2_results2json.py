import sys
import pandas as pd
import itertools
import re
import json
import numpy as np


def read_and_parse_input_file(input_file):
    with open(input_file) as f:
        header_row = next(itertools.islice(f, 2, 3))
        header_names = re.findall('"([^"]+)"', header_row)

    def parse_header(name):
        return name.replace('-', '_').lower()

    df = pd.read_csv(input_file, sep='\s+', skiprows=3, header=None, names=[parse_header(name) for name in header_names])
    df = df.fillna(0)

    return df


def df_to_json_file(df, json_file):
    data = {}
    for col in df.columns:
        data[col] = df[col].values.tolist()

    with open(json_file, 'w') as f:
        json.dump(data, f)
	f.write("\n")



#input_file = './catalyst_test_reactor-monitor.out'
#json_file = 'result.json'
input_file = sys.argv[1]
json_file = sys.argv[2]

df = read_and_parse_input_file(input_file)
df_to_json_file(df, json_file)



