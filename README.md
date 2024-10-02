# Requirements
To be able to run the examples it is necessary to have access to an Intel SGX capable machine, as well as having Gramine installed. The following hardware specifications has been used in Azure cloud during development:

|Property  |Value|
|----------|-----|
|OS/Kernel & Linux SGX 5.4.0-1104-azure \#110$\sim$18.04.1-Ubuntu SMP x86\_64|
|GNU/Linux |
|CPU & Intel(R) Xeon(R) E-2288G CPU @ 3.70GHz |
|Size & Standard DC2ds v3 |
|vCPUs & 2 |
|RAM & 16\,GiB|

Installation options for Gramine can be found here: https://gramine.readthedocs.io/en/stable/installation.html

# Setup
## 1. Dafny:
Download latest binary version from: https://docs.microsoft.com/dotnet/core/install/linux
https://github.com/dafny-lang/dafny/releases

OR

Run ``make dafny`` to fetch version 4.6.0 used during  development.


# Dafny targets
https://dafny.org/dafny/DafnyRef/DafnyRef.html

Default is c#
javascript: '--target:js'
go: '--target:go'
python: '--target:py'
java: '--target:java'
cpp: '--target:cpp'

# Info
is-sgx-available

epc = enclave page cache