MIPS Assembler
==============

This is an (extremely) basic assembler for MIPS32. The end goal is to support all instructions on the standard MIPS [reference sheet](http://inst.eecs.berkeley.edu/~cs61c/resources/MIPS_Green_Sheet.pdf "MIPS reference sheet") (a.k.a. the "green sheet").

### Usage

Simply clone the repository and run
```sh
python assembler.py [-o out_filepath] in_filepath
```

This will produce an output file with the encoded instructions. My plan is to work on a better distribution method, specifically, the ability to call the assembler directly from the command line under any path.

### Labels

Labels are now supported. Either "format" is fine.

```
sort: addi $s0, $s0, -20
```
or
```
sort:
    addi $s0, $s0, -20
```
will result in equivalent instruction memory.

### Goals

* All of the instructions. (At least as much as possible.)
* Better distribution/invocation.

### Credit

* Using the [bitstring](https://code.google.com/p/python-bitstring/ "bitstring") library for decimal to binary conversion. (It was easier than writing my own 2's complement converter.)