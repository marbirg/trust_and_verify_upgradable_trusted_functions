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
all: dafny.manifest
ifeq ($(SGX),1)
all: dafny.manifest.sgx dafny.sig
endif

RA_TYPE ?= none
# RA_TYPE ?= dcap
RA_CLIENT_SPID ?=
RA_CLIENT_LINKABLE ?= 0

build: clean
	${MAKE} SGX=1 

build-debug: clean
	${MAKE} SGX=1 DEBUG=1

dafny.manifest: dafny.manifest.template
	gramine-manifest \
		-Dlog_level=$(GRAMINE_LOG_LEVEL) \
		-Darch_libdir=$(ARCH_LIBDIR) \
		-Dentrypoint="/usr/lib/dafny/dafny"\
		-Dra_type=$(RA_TYPE) \
		-Dra_client_spid=$(RA_CLIENT_SPID) \
		-Dra_client_linkable=$(RA_CLIENT_LINKABLE) \
		$< >$@

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

dafny.manifest.sgx dafny.sig: sgx_sign
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
clean:
	$(RM) *.manifest *.manifest.sgx *.token *.sig OUTPUT* *.PID TEST_STDOUT TEST_STDERR
	$(RM) -r scripts/__pycache__
clean-builds:
	rm -rf scripts/*py
	rm -rf scripts/*.dll
	rm -rf scripts/*.json

.PHONY: distclean
distclean: clean

build-docker:
	sudo docker build -t test \
	.	
run-docker:
	@sudo docker run --rm --name test \
	--device /dev/sgx_enclave \
	--device /dev/sgx_provision \
	test

	# -v ./dotnet:/usr/lib/dotnet 
	# -e DOTNET_ROOT=/usr/lib/dotnet 
	# -v ./dafny.manifest.sgx:/root/dafny.manifest.sgx 
	# -v ./dafny.sig:/root/dafny.sig 
gramine-docker:
	sudo docker run --privileged \
	--device /dev/sgx_enclave -it \
	--device /dev/sgx_provision \
	-v ./dafny:/usr/lib/dafny \
	-v ./dafny:/root/dafny \
	-v ./Makefile:/root/Makefile \
	-v ./docker-setup.sh:/root/setup.sh \
	-v ./dafny.manifest.template:/root/dafny.manifest.template \
	-v ${HOME}/.config/gramine/enclave-key.pem:/root/.config/gramine/enclave-key.pem \
	-v ./scripts:/root/scripts \
	-e DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 \
	gramineproject/gramine

run-direct:
	# gramine-direct mono --versioi
	gramine-direct ./dafny /version
	# gramine-direct ./dafny /compile:0 scripts/Abs.dfy 
	# gramine-direct ./dafny scripts/Abs.dfy /compile:0
	# gramine-direct ./dafny /usr/lib/dafny/Dafny.exe scripts/Abs.dfy /compile:0

run-sgx:
	(2>&3 gramine-sgx ./dafny verify scripts/Abs.dfy |tee ${STD_LOG}) 3>&1 | tee ${ERROR_LOG}
	# gramine-sgx ./dafny /version 2>&1| tee gramine.log

	# gramine-sgx ./dafny /compile:0 scripts/Abs.dfy

dafny:
	wget https://github.com/dafny-lang/dafny/releases/download/v4.6.0/dafny-4.6.0-x64-ubuntu-20.04.zip
	unzip dafny-4.6.0-x64-ubuntu-20.04.zip

python-test:
	var=$(realpath $(shell sh -c "command -v python3"))
