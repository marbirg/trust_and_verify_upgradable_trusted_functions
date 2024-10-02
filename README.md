
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