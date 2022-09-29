# A cat that adds two numbers together

## Examples

This code generates GIFs of N-bit adders. Give it two numbers and it will add them together!

`1 + 1 = 2`

![Meow meow I am performing addition! 1 + 1 = 2](output.gif)

`98 + 123 = 221`

![Meow meow I am performing addition! 98 + 123 = 221](output_large.gif)

## Usage

The examples above were made with

```
python nbit_adder.py 1 1 -n 2 -s 24
```

and

```
python nbit_adder.py 98 123 -n 8 --loop
```

Here is the help information

```
python nbit_adder.py --help

usage: nbit_adder.py [-h] [-n NBITS] [-s CELL_SIZE] [-r] [-l] [-v] a b

Add two numbers together graphically

positional arguments:
  a                     First number
  b                     Second number

options:
  -h, --help            show this help message and exit
  -n NBITS, --nbits NBITS
                        Bit-size of adder
  -s CELL_SIZE, --cell_size CELL_SIZE
                        Size in pixel of each cell in the grid
  -r, --no_render       Whether to *not* render an image file
  -l, --loop            Whether to loop the GIF
  -v, --verbose         Whether to print out a lot of information
```