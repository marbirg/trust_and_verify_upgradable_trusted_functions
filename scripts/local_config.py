import os
base = os.getcwd()
STAGING_DIR = base+'/local/tmp/'
DAFNY_OUT = base+"/local/verified/"
DAFNY_BIN = base+"/dafny/dafny"
DAFNY_TARGET = '/compileTarget:py'
INPUT_DIR=base+'/local/input/'
TEMPLATE_DIR=base+'/templates/'
REPORT_DIR=base+'/reports/'
BANDIT_TARGET=base+'/scripts/'
DAFNY_PYTHON_SUFFIX = '-py'
