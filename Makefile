# Copyright (C) 2023 Gramine contributors
# SPDX-License-Identifier: BSD-3-Clause

ARCH_LIBDIR ?= /lib/$(shell $(CC) -dumpmachine)

ERROR_LOG:=error.log
STD_LOG:=stdout.log

ifeq ($(DEBUG),1)
GRAMINE_LOG_LEVEL = debug
else
GRAMINE_LOG_LEVEL = error
endif

.PHONY: all
all: python.manifest
ifeq ($(SGX),1)
all: python.manifest.sgx python.sig
endif

# RA_TYPE ?= none
RA_TYPE ?= dcap
RA_CLIENT_SPID ?=
RA_CLIENT_LINKABLE ?= 0

build: clean
	${MAKE} SGX=1 

setup: dafny
	mkdir input -p

print-path:
	echo $(realpath $(shell sh -c "command -v python3"))
build-debug: clean
	${MAKE} SGX=1 DEBUG=1

python.manifest: python.manifest.template
	gramine-manifest \
		-Dlog_level=$(GRAMINE_LOG_LEVEL) \
		-Darch_libdir=$(ARCH_LIBDIR) \
		-Dentrypoint=$(realpath $(shell sh -c "command -v python3")) \
		-Dra_type=$(RA_TYPE) \
		-Dra_client_spid=$(RA_CLIENT_SPID) \
		-Dra_client_linkable=$(RA_CLIENT_LINKABLE) \
		$< >$@

# Make on Ubuntu <= 20.04 doesn't support "Rules with Grouped Targets" (`&:`),
# see the helloworld example for details on this workaround.
python.manifest.sgx python.sig: python.sgx_sign
	@:

.INTERMEDIATE: sgx_sign
sgx_sign: dafny.manifest
	gramine-sgx-sign \
		--manifest $< \
		--output $<.sgx

python.sgx_sign: python.manifest
	gramine-sgx-sign \
		--manifest $< \
		--output $<.sgx

.PHONY: check
check: all
	./run-tests.sh > TEST_STDOUT 2> TEST_STDERR
	@grep -q "Success 1/4" TEST_STDOUT
	@grep -q "Success 2/4" TEST_STDOUT
	@grep -q "Success 3/4" TEST_STDOUT
	@grep -q "Success 4/4" TEST_STDOUT
ifeq ($(SGX),1)
	@grep -q "Success SGX report" TEST_STDOUT
	@grep -q "Success SGX quote" TEST_STDOUT
endif

.PHONY: clean
clean: clean-builds
	$(RM) *.manifest *.manifest.sgx *.token *.sig OUTPUT* *.PID TEST_STDOUT TEST_STDERR
	$(RM) -r scripts/__pycache__
clean-builds:
	rm -rf scripts/*.dll
	rm -rf scripts/*.json

.PHONY: distclean
distclean: clean

dafny:
	wget https://github.com/dafny-lang/dafny/releases/download/v4.6.0/dafny-4.6.0-x64-ubuntu-20.04.zip
	unzip dafny-4.6.0-x64-ubuntu-20.04.zip

python-test:
	var=$(realpath $(shell sh -c "command -v python3"))

clear-enclave-files:
	rm -rf data/*

clear-input:
	rm -rf input/*

input-max: clear-input
	cp input_files/Max.body input/
input-abs: clear-input
	cp input_files/Abs.body input/
input-sort: clear-input
	cp input_files/BubbeSortDafny.body input/
input-all: clear-input
	cp input_files/*.body input/

run-local-dev:
	. ./venv/bin/activate && ENV=local python scripts/main.py
run-local:
	ENV=local python3 scripts/main.py
run-enclave:
	gramine-sgx ./python
