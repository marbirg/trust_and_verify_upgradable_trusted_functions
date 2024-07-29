
import os
import subprocess
import config
import time
import csv
import datetime
import shutil
data_dir = "./DafnyBench/DafnyBench/dataset/ground_truth"
verified_dir = "./verified/"
faulty_dir = "./error/"

verified = "./result.csv"
skipped = "./skipped.csv"
errors = "./errors.csv"

def copy_files(src, dst):
    shutil.copy(src,dst)
    
def read_csv(fname):
    data = []
    with open(fname, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

def get_verified_files():
    data = read_csv(verified)
    fnames = []
    for row in data:
        fnames.append(row[0])
    return fnames

def get_faulty_files():
    err_files = [s[0] for s in read_csv(errors)]
    skipped_files = [s[0] for s in read_csv(skipped)]
    # return err_files
    return err_files+skipped_files

def copy_verified_files():
    verified_files = get_verified_files()
    verified_paths = [data_dir+'/'+s for s in verified_files]
    for p in verified_paths:
        copy_files(p, verified_dir)

def copy_faulty_files():
    faulty_files = get_faulty_files()
    faulty_paths = [data_dir + '/' + s for s in faulty_files]
    for p in faulty_paths:
        copy_files(p, faulty_dir)

if __name__=='__main__':
    # copy_verified_files()
    # copy_faulty_files()
    exit(0)
