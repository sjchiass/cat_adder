# A cat that adds two numbers together

## Examples

This code generates GIFs of N-bit adders. Give it two numbers and it will add them together!

`1 + 1 = 2`

![Meow meow I am performing addition! 1 + 1 = 2](output.gif)

`98 + 123 = 221`

![Meow meow I am performing addition! 98 + 123 = 221](output_large.gif)

## Legend

Here's what all the little icons mean

  * Squares with arrows: these redirect a signal/wire into one or more directions :twisted_rightwards_arrows:
  * Squares with crosses: these junctions let signals/wires cross each other without interfering :heavy_plus_sign:
  * X: a XOR gate. It will output a signal if receives exactly one signal. It turns off if it gets 0 or 2. :raised_hands:
  * A: and AND gate. It will output a signal only if it receives two signals. :people_hugging:
  * O: and OR gate. As long as it receives at least one signal, it outputs one too. It's still happy if it gets two signals. :heart_eyes:
  * Science cat: it's a cat! :smiley_cat:

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