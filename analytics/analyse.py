
"""
Python function for analysing benchmark results.
Requires first argument to be a relative path to a report with results.
"""

import sys
import json
import os
from collections import defaultdict
import statistics
import numpy as np
import matplotlib.pyplot as plt

def geo_mean_overflow(iterable):
    return np.exp(np.log(iterable).mean())

def get_dafny_files():
    dafny_file_dir = './verified/'
    return os.listdir(dafny_file_dir)

def read_json(fname:str):
    with open(fname,'r') as f:
        data = f.read()
    return json.loads(data) 

def print_all(report_data):
    for data in report_data:
        print(data)
        if data['errors']!=0:
            print(data)

def get_file_names(report_data):
    file_names = []
    for data in report_data:
        file_names.append(data['file'])
    return file_names

def find_missing(report_data):
    all_files = get_dafny_files()
    checked_files = get_file_names(report_data)
    missing = []
    for f in all_files:
        if not f in checked_files:
            missing.append(f)
    print(len(all_files), len(checked_files), len(missing)) 
    return missing

def add_missing(report_data):
    missing = find_missing(report_data)
    number = report_data[-1]['number']
    for f in missing:
        number+=1
        res = {'errors':-2, 'verification_time':-1, 'total_time':-1, 'file':f, 'number':number}
        report_data.append(res)
    return report_data

def count_errors(data:list):
    errors = defaultdict(lambda: 0)
    for e in data:
        errors[e['errors']]+=1
    return errors

def compute_mean_time(data):
    mean_time = 0
    mean_total_time = 0
    for d in data:
        mean_time+=d['verification_time']
        mean_total_time+=d['total_time']
    return mean_time/len(data), mean_total_time/len(data) 

def compute_median_time(data):
    mean_time = []
    mean_total_time = []
    for d in data:
        mean_time.append(d['verification_time'])
        mean_total_time.append(d['total_time'])
    return statistics.median(mean_time), statistics.median(mean_total_time)  
    # return mean_time/len(data), mean_total_time/len(data) 

def compute_geometric_mean(data):
    mean_time = []
    mean_total_time = []
    for d in data:
        mean_time.append(d['verification_time'])
        mean_total_time.append(d['total_time'])
    return geo_mean_overflow(mean_time), geo_mean_overflow(mean_total_time)

def analyse(fname):
    data = read_json(fname)
    total_files = os.listdir("./DafnyBench/DafnyBench/dataset/ground_truth/")
    successfull = [d for d in data if d['errors']==0]
    # errors = count_errors(data)
    # print('Errors:', errors)
    faulty = len(data)-len(successfull)
    print("Number of DafnyBench files", len(total_files))
    print("Number of analysed files:", len(data))
    print("Number of Success:", len(successfull))
    print("Number of issues:", faulty)
    mean_verification_time, mean_total_time = compute_mean_time(successfull)
    median_verification_time, median_total_time = compute_median_time(successfull)
    geo_mean_verification_time, geo_mean_total_time = compute_median_time(successfull)
    # mean_verification_time = mean_time[0]
    print("Mean verification time:", mean_verification_time)
    print("Median verification time:", median_verification_time)
    print("Geometric mean verification time:", geo_mean_verification_time)

def write_report_data(report_file_name, report_data):
    with open(report_file_name, 'w+') as f:
        f.write(json.dumps(report_data))

def get_stats(data):
    n = len(data)
    mean = statistics.mean(data)
    median = statistics.median(data)
    return {'n':n, 'mean':mean, 'median': median}

def print_stats(stats):
    # print(stats)
    for func in stats:
        if func=='geomean':
            continue
        fstats = stats[func]
        print("Function:", func)
        print("Number of iterations:", fstats['n'])
        print("Mean:", fstats['mean'])
        print("Median:", fstats['median'])
        print()
    print('Geometric mean:', stats['geomean'])

    print()
    print("=================")
def collect_stats(report_file):
    # print(report_file)
    report_data = read_json(report_file)
    # print(report_data.keys())
    all_data = []
    all_stats = {}
    for func in report_data.keys():
        fdata = report_data[func]
        all_data+=fdata
        stats = get_stats(fdata)
        all_stats[func]=stats
    geomean = geo_mean_overflow(all_data)
    all_stats['geomean']=geomean
    # print('Geometric mean:', geomean)
    return all_stats
    # for i in range(len(report_data)):
        # func = report_data[i]['func']
        # print(sum(result[func])/len(result[func]))
        # print(func, 'mean:', statistics.mean(result[func]))
        # print(func)

def pretty_name(fname:str):
    if fname.lower().startswith('non-'):
        return 'Non-Enclave'
    elif fname.lower().startswith('enclave'):
        return 'Enclave'

    return fname
from tabulate import tabulate
# print(tabulate([['Alice', 24], ['Bob', 19]], headers=['Name', 'Age']))
def compare_stats(stat1, stat2, scale=1, tableformat='plain'):
    print(stat1)
    print()
    print(stat2)
    headers = ['', pretty_name(stat1['name']), pretty_name(stat2['name']), 'Overhead']
    functions = set(list(stat1.keys())+list(stat2.keys()))
    functions.remove('name')
    functions.remove('geomean')
    # print(functions)
    print(stat1['name'], stat2['name'])
    tab_data = []
    for func in functions:
        print("Function:", func)
        mean1 = stat1[func]['mean']*scale
        mean2 = stat2[func]['mean']*scale
        median1 = stat1[func]['median']*scale
        median2 = stat2[func]['median']*scale
        mean_v = ['Mean', mean1, mean2, mean1/mean2]
        median_v = ['Median', median1, median2, median1/median2]
        tab_data.append([func])
        tab_data.append(mean_v)
        tab_data.append(median_v)
        tab_data.append(['-'])

        print("Mean:", mean1, mean2, mean1/mean2)
        print("Median:", median1, median2, median1/median2)
        print()
    geomean1 = stat1['geomean']*scale
    geomean2 = stat2['geomean']*scale

    tab_data.append(["Geometric mean:", geomean1, geomean2, geomean1/geomean2])
    print("Table:")
    tab = tabulate(tab_data, headers=headers, tablefmt=tableformat)
    print(tab)
    # print("Geometric mean:", geomean1, geomean2, geomean1/geomean2)
    # functions = report_stats[name].keys()
    # sim = list(report_stats.keys())[0]
    # print(sim)
    # functions = list(report_stats[sim].keys())
    # print(functions)
    

if __name__=='__main__':
    if len(sys.argv)<2:
        print(__doc__)
        exit(0)

    command = sys.argv[1]
    # command = 'print_all'

    print("Command:", command)
    if command == 'print_all':
        report_data = read_json(fname)
        fname = sys.argv[2]
        print_all(report_data)
    elif command == 'add_missing':
        report_data = read_json(fname)
        # find_missing(report_data)
        fname = sys.argv[2]
        new_report = add_missing(report_data)
        write_report_data(fname, new_report)
    elif command == 'analyse':
        fname = sys.argv[2]
        analyse(fname)
    elif command == 'benchmark':
        fnames = []
        report_stats = []
        benchmarks = []
        for i in range(2, len(sys.argv)):
            report_name = sys.argv[i]
            stats = collect_stats(report_name)
            stats['name']=report_name
            report_stats.append(stats)
            print(report_stats)
        if len(report_stats)==2:
            compare_stats(report_stats[0], report_stats[1], scale=1000, tableformat='latex')
        # print(len(report_stats.keys()))
    elif command == 'plot_verification_time':
        data = {}
        for i in range(2, len(sys.argv)):
            fname = sys.argv[i]
            files = []
            t = []
            print(fname)
            result = read_json(fname)
            for d in result:
                files.append(d['file'])
                t.append(d['verification_time'])

        plt.scatter(files,t)
        # print(files)
        # print(t)
        plt.show()
        print("Done")
        # print(data)
