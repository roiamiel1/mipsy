MIPS Assembler
==============

This is an (extremely) basic assembler for MIPS32. The end goal is to support all instructions on the standard MIPS [reference sheet](http://inst.eecs.berkeley.edu/~cs61c/resources/MIPS_Green_Sheet.pdf "MIPS reference sheet") (a.k.a. the "green sheet").

**Please read the TODO section below for important information on what currently works. I designed and implemented this for educational purposes. It is currently not intended to replace any real tool you would use to program a MIPS processor.**

### Usage

Simply clone the repository and run
```sh
python assembler.py [-o out_filepath] in_filepath
```

This will produce an output file with the encoded instructions. My plan is to work on a better distribution method, specifically, the ability to call the assembler directly from the command line under any path.

### TODO

* Support labels (There is currently no support for this and the assembler will barf if your input file has them. Yes, this means you *must* translate label addresses manually. For now.)
* All of the instructions. (At least as much as possible.)
* Better distribution/invocation.

There are certainly more TODO items, but those are major ones that come to mind.

### Credit

* Using the [bitstring](https://code.google.com/p/python-bitstring/ "bitstring") library for decimal to binary conversion. (It was easier than writing my own 2's complement converter.)