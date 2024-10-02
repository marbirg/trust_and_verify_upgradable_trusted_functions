
# Setup
## 1. Dafny:
Download latest binary version from: https://docs.microsoft.com/dotnet/core/install/linux
https://github.com/dafny-lang/dafny/releases

OR

Run ``make dafny`` to fetch version 4.6.0 used during  development.

Run withtout sgx: gramine-direct ./dafny scripts/Abs.dfy


Libs loaded by mono and Dafny (found using debug var)
/usr/lib/boogie
/etc/mono/

Mono: DllImport searching in: '/usr/lib/../lib/libmono-native.so' ('/usr/lib/../lib/libmono-native.so').

/etc/localtime
/usr/bin/z3

Already loaded:
/usr/lib/mono
/usr/lib/dafny

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