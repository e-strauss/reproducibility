#!/usr/bin/env python3

import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from statistics import mean

optimizer_modes = ["dphyp-equisets"]
benchmarks = ["imdb", "ssb", "ssb-skew"]
routing_strategies = ["default_path", "alternate", "init_once", "opportunistic", "adaptive_reinit", "dynamic", "backpressure"]

sweet_spots = {"adaptive_reinit": {"imdb": "0.1", "ssb": "0.01", "ssb-skew": "0.8"},
               "dynamic": {"imdb": "0.001", "ssb": "0.00001", "ssb-skew": "0.01"}}

results = {}

for mode in optimizer_modes:
    results[mode] = {}
    for benchmark in benchmarks:
        num_files = -1
        alternate_files = []
        results[mode][benchmark] = {}
        for strategy in routing_strategies:
            path = f"{os.getcwd()}/experiment-results/2_3_routing/{benchmark}/{strategy}"
            if strategy == "adaptive_reinit" or strategy == "dynamic":
                path += f"/{sweet_spots[strategy][benchmark]}"

            intms = []
            if strategy == "alternate":
                alternate_files = glob.glob(os.path.join(path, "*.csv"))
                alternate_files.sort()

                if num_files == -1:
                    num_files = len(alternate_files)
                elif num_files != len(alternate_files):
                    print("Warning: " + strategy + " has " + str(len(alternate_files)) + " instead of "
                          + str(num_files))

                for csv_file in alternate_files:
                    df = pd.read_csv(csv_file)
                    df.pop(df.columns[-1])
                    if "path_0" not in df.columns:
                        print("Warning: " + csv_file)
                        continue
                    intms.append(df.min(axis=1).sum())
            else:
                txt_files = glob.glob(os.path.join(path, "*.txt"))
                txt_files.sort()

                csv_files = glob.glob(os.path.join(path, "*.csv"))
                csv_files.sort()

                if len(txt_files) != len(csv_files):
                    print("Warning: " + strategy + " has " + str(len(txt_files)) + " txts and " + str(len(csv_files))
                          + " csvs")

                if num_files == -1:
                    num_files = len(txt_files)
                elif num_files != len(txt_files):
                    print("Warning: " + strategy + " has " + str(len(txt_files)) + " instead of " + str(num_files))

                for i in range(len(csv_files)):
                    csv_file = csv_files[i]
                    txt_file = txt_files[i]

                    if txt_file.split("/")[-1].split("-")[0] != csv_file.split("/")[-1].split(".")[0]:
                        print("Warning: " + txt_file.split("/")[-1] + " != " + csv_file.split("/")[-1])

                    intermediates = 0
                    with open(txt_file) as f:
                        line = f.readline()
                        if line == "":
                            print("Warning: " + txt_file)
                            continue
                        intermediates = int(line)

                    df = pd.read_csv(csv_file)
                    intermediates_2 = df["intermediates"].sum()

                    if intermediates != intermediates_2:
                        print("### Warning ###")
                        print(txt_file + ": " + str(intermediates))
                        print(csv_file + ": " + str(intermediates_2))

                    intms.append(int(intermediates))
            results[mode][benchmark][strategy] = intms
            if strategy == "adaptive_reinit" or strategy == "dynamic":
                print(f"{benchmark} | {strategy}({sweet_spots[strategy][benchmark]}): {sum(intms) / 1000000}M intermediates")

result_str = "\\begin{table}\n\t\\centering\n\t\\begin{tabular}{l"

for mode in results:
    for benchmark in results[mode]:
        if len(results[mode][benchmark]["alternate"]) > 0:
            result_str += "r"

result_str += "}\n\t\t"
result_str += "\\textbf{Routing strategy}"

for benchmark in benchmarks:
    for mode in results:
        if benchmark not in results[mode]:
            continue
        if len(results[mode][benchmark]["alternate"]) > 0:
            result_str += " & " + benchmark + "-" + mode[:2]

result_str += "\\\\\n\t\t"
result_str += "\\hline\n\t\t"

for routing_strategy in routing_strategies:
    if routing_strategy == "alternate":
        result_str += "optimal"
    else:
        result_str += routing_strategy.replace("_", " ")

    for benchmark in benchmarks:
        for mode in results:
            if benchmark not in results[mode]:
                continue
            if len(results[mode][benchmark]["alternate"]) > 0:
                intermediate_count = sum(results[mode][benchmark][routing_strategy])
                result_str += " & " + "{:10.2f}".format(intermediate_count / 1000000) + " M"
    result_str += "\\\\\n\t\t"

result_str += "\hline\n\t\\end{tabular}\n\t\\caption{"
result_str += "Total number of intermediates for POLAR pipelines"
result_str += "}\n\t\\label{"
result_str += "tab:2_4_routing_all"
result_str += "}\n\\end{table}\n"

with open("experiment-results/2_4_routing_all.txt", "w") as file:
    file.write(result_str)