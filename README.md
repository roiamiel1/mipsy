mipsy - MIPS32 assembler
========================

This is an (extremely) basic assembler for MIPS32. The end goal is to support all instructions on the standard MIPS [reference sheet](http://inst.eecs.berkeley.edu/~cs61c/resources/MIPS_Green_Sheet.pdf "MIPS reference sheet") (a.k.a. the "green sheet").

### Install and Use

You can either clone the repository and run
```
python setup.py install
```
or
```
pip install mipsy
```

To use simply run:
```
mipsy input.asm
```

This will produce an output file (out.bin) with the encoded instructions. See the help screen for more info.

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

* Full assembler functionality, allowing for assembler directives and temporarily unresolved external labels.
* All of the instructions. (At least as much as possible.)

### Development

I highly recommend using a virtualenv when developing for mipsy. To "install" mipsy when developing, you can run
```
python setup.py develop
```
to link the development directory to your virtualenv site-package directory.

```
python setup.py develop --uninstall
```
will undo those changes, but will not remove the command-line script.

### Credit

* Using the [bitstring](https://code.google.com/p/python-bitstring/ "bitstring") library for decimal to binary conversion. (It was easier than writing my own 2's complement converter.)