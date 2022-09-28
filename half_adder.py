import argparse
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(description="Add two numbers together graphically")
parser.add_argument("a", type=int, help="First number")
parser.add_argument("b", type=int, help="Second number")
parser.add_argument("-n", "--nbits", type=int, help="Bit-size of adder", default=4)
parser.add_argument("-r", "--no_render", action="store_true", help="Whether to *not* render an image file")
parser.add_argument("-v", "--verbose", action="store_true", help="Whether to print out a lot of information")

args = parser.parse_args()

N = args.nbits

class Grid:
    def __init__(self, canvas_size, cell_size, render_mode=True):
        self.grid = dict()
        self.queue = []
        self.frames = []
        self.canvas_size = canvas_size
        self.cell_size = cell_size
        self.registers = []
        self.render_mode = render_mode
        self.counter = 0
    def assign(self, signal):
        if signal.x in self.grid and signal.y in self.grid[signal.x]:
            return 1
        if signal.x not in self.grid:
            self.grid[signal.x] = dict()
        self.grid[signal.x][signal.y] = signal.component(self, signal)
        return 0
    def activate_cell(self, signal):
        return self.grid[signal.x][signal.y].activate(signal)
    def queue_signal(self, signal):
        self.queue.append(signal)
    def run_queue(self):
        while self.queue:
            signal = self.queue.pop(0)
            if args.verbose:
                print(signal)
            while True:
                self.counter += 1
                if args.verbose:
                    print("---", self.counter, signal)
                if signal.x < 0 or signal.x > self.canvas_size[0]:
                    break
                elif signal.y < 0 or signal.y > self.canvas_size[1]:
                    break
                grid.assign(signal)
                if signal.direction == (0, 0) or signal.color.sum() == 0:
                    break
                if self.render_mode:
                    self.frames.append(grid.render())
                if grid.activate_cell(signal):
                    pass
                else:
                    break
                signal.x += signal.direction[0]
                signal.y += signal.direction[1]
        if args.verbose:
            print("Queue empty")
    def add_register(self, x, y, address):
        self.registers.append({"x":x, "y":y, "address":address})
    def read_registers(self):
        values = dict()
        for r in self.registers:
            if r["x"] in self.grid and r["y"] in self.grid[r["x"]]:
                values[r["address"]] = self.grid[r["x"]][r["y"]].color.max()
            else:
                values[r["address"]] = 0
        return values
    def render(self):
        image = Image.new("RGB", (self.cell_size*self.canvas_size[0], self.cell_size*self.canvas_size[1]))
        draw = ImageDraw.Draw(image)
        s = self.cell_size
        for x in range(self.canvas_size[0]):
            for y in range(self.canvas_size[1]):
                if x in self.grid and y in self.grid[x]:
                    self.grid[x][y].draw_own_cell(draw, x, y, s)
                else:
                    pass
        draw.text((20, 20), str(self.counter), fill=(255, 255, 255, 128))
        registers = self.read_registers()
        draw.text((20, 40), str(sum([registers.get(f"a{i}", 0)*2**i for i in range(N)])), fill=(255, 255, 255, 128))
        draw.text((40, 40), str(sum([registers.get(f"b{i}", 0)*2**i for i in range(N)])), fill=(255, 255, 255, 128))
        draw.text((60, 40), str(sum([registers.get(f"o{i}", 0)*2**i for i in range(N)])), fill=(255, 255, 255, 128))
        return image
    def __repr__(self):
        return str(self.grid)

class Color:
    # The color here is R, G, B, C, M, Y
    # Primary: red, green, blue
    # Secondary: cyan, magenta, yellow
    def __init__(self, color):
        self.color = color
        if len(color) != 6 or any(x not in (-1, 0, 1) for x in self.color):
            raise ValueError("Color must be a list of 6 -1/0/1 integers")
    def off_color(self):
        return Color([-x for x in self.color])
    def add(self, other_color):
        color_sum = self.color[:]
        for n, s in enumerate(color_sum):
            color_sum[n] = max(0, min(1, s+other_color.color[n]))
        return Color(color_sum)
    def clone(self):
        return Color(self.color[:])
    def sum(self):
        return sum(self.color)
    def min(self):
        return min(self.color)
    def max(self):
        return max(self.color)
    def equals(self, other):
        own = self.color[:]
        other = other.color[:]
        return all([max(0,x)==max(0,y) for x,y in zip(own,other)])
    def to_visible_color(self):
        rgba = [self.color[0], self.color[1], self.color[2]]
        # Cyan, green + blue
        if self.color[3] == 1:
            rgba[1] += 1
            rgba[2] += 1
        # Magenta, red + blue
        if self.color[4] == 1:
            rgba[0] += 1
            rgba[2] += 1
        # Yellow, red + green
        if self.color[5] == 1:
            rgba[0] += 1
            rgba[1] += 1
        # Normalize colors to 0, 255; negative values to 0
        rgba = [0 if x <= 0 else 255 if x == max(rgba) else 128 for x in rgba]
        # Add transparency value, always 255 (opaque) for now
        rgba.append(255)
        # Return as a tuple
        return tuple(rgba)
    def __repr__(self):
        return str(self.color)

class Signal:
    def __init__(self, x, y, direction, component, color, emitter=None):
        self.emitter = emitter
        self.x = x
        self.y = y
        self.direction = direction
        self.component = component
        self.color = color
    def __repr__(self):
        return f"Emitter: {self.emitter}, Direction: {self.direction}, X, Y: {self.x}, {self.y}, Component created: {self.component}, Color: {self.color}"

class Wire:
    def __init__(self, parent_grid, signal):
        self.parent_grid = parent_grid
        self.color = signal.color
        self.position = (signal.x, signal.y)
        self.transparent = 1
    def activate(self, signal):
        old_color = self.color.clone() # For getting rid of an existing signal, get a copy
        self.color = self.color.add(signal.color)
        # Give the old and new color for the emit method to decide, but only if it has changed
        if not self.color.equals(old_color):
            self.emit(old_color, self.color)
        return self.transparent
    def emit(self, old_color, new_color):
        pass
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=self.color.to_visible_color(),
                         width=5)

class Component(Wire):
    def __init__(self, parent_grid, signal):
        self.parent_grid = parent_grid
        self.color = signal.color
        self.position = (signal.x, signal.y)
        self.transparent = 0

class Junction(Component):
    def __init__(self, parent_grid, signal):
        self.parent_grid = parent_grid
        # Need independant copies of signal colors
        self.color_horizontal = signal.color.clone()
        self.color_vertical = signal.color.clone()
        self.position = (signal.x, signal.y)
        self.transparent = 1
    def activate(self, signal):
        if signal.direction in [(-1, 0), (1, 0)]:
            old_color = self.color_horizontal.clone() # For getting rid of an existing signal, get a copy
            self.color_horizontal = self.color_horizontal.add(signal.color)
            # Give the old and new color for the emit method to decide
            self.emit(old_color, self.color_horizontal, signal.direction)
        elif signal.direction in [(0, -1), (0, 1)]:
            old_color = self.color_vertical.clone() # For getting rid of an existing signal, get a copy
            self.color_vertical = self.color_vertical.add(signal.color)
            # Give the old and new color for the emit method to decide
            self.emit(old_color, self.color_vertical, signal.direction)
        return self.transparent
    def emit(self, old_color, new_color, direction):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+direction[0], y=self.position[1]+direction[1], direction=direction, color=new_color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+direction[0], y=self.position[1]+direction[1], direction=direction, color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s, y_0*s+s//3), (x_0*s+s, y_0*s+2*s//3)],
                         fill=self.color_horizontal.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//3, y_0*s), (x_0*s+2*s//3, y_0*s+s)],
                         fill=self.color_vertical.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//3, y_0*s+s//3), (x_0*s+2*s//3, y_0*s+2*s//3)],
                         fill=self.color_horizontal.add(self.color_vertical).to_visible_color(),
                         width=5)

class ToLeft(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//4), n_sides=3, rotation=90, fill=self.color.to_visible_color())

class ToUp(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//4), n_sides=3, rotation=0, fill=self.color.to_visible_color())

class ToLeftAndDown(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.color))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=old_color.off_color()))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+3*s//4, s//4), n_sides=3, rotation=180, fill=self.color.to_visible_color())
        draw.regular_polygon((x_0*s+s//4, y_0*s+s//2, s//4), n_sides=3, rotation=90, fill=self.color.to_visible_color())

class ToUpAndLeft(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=self.color))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=old_color.off_color()))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//4, s//4), n_sides=3, rotation=0, fill=self.color.to_visible_color())
        draw.regular_polygon((x_0*s+s//4, y_0*s+s//2, s//4), n_sides=3, rotation=90, fill=self.color.to_visible_color())

class ToDownAndRight(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.color))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=old_color.off_color()))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+3*s//4, s//4), n_sides=3, rotation=180, fill=self.color.to_visible_color())
        draw.regular_polygon((x_0*s+3*s//4, y_0*s+s//2, s//4), n_sides=3, rotation=270, fill=self.color.to_visible_color())

class ToDown(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//4), n_sides=3, rotation=180, fill=self.color.to_visible_color())

class ToRight(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=old_color.off_color()))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//4), n_sides=3, rotation=270, fill=self.color.to_visible_color())

class And(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() >= 2:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=Color([0, 1, 0, 0, 0, 0])))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=Color([0, -1, 0, 0, 0, 0])))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+s//5), (x_0*s+4*s//5, y_0*s+4*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+2*s//5), (x_0*s+3*s//5, y_0*s+2.5*s//5)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+3*s//5), (x_0*s+3*s//5, y_0*s+4*s//5)],
                         fill=(192, 192, 192, 255),
                         width=5)

# This is a temporary class to have an AND gate that emits a different color
class And2(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() >= 2:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=Color([0, 0, 0, 0, 0, 1])))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=Color([0, 0, 0, 0, 0, -1])))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+s//5), (x_0*s+4*s//5, y_0*s+4*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+2*s//5), (x_0*s+3*s//5, y_0*s+2.5*s//5)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+3*s//5), (x_0*s+3*s//5, y_0*s+4*s//5)],
                         fill=(192, 192, 192, 255),
                         width=5)

class Xor(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() == 1:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=Color([0, 0, 0, 1, 0, 0])))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=Color([0, 0, 0, -1, 0, 0])))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+s//5), (x_0*s+2*s//5, y_0*s+2*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+3*s//5, y_0*s+s//5), (x_0*s+4*s//5, y_0*s+2*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+2*s//5), (x_0*s+3*s//5, y_0*s+3*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+3*s//5), (x_0*s+2*s//5, y_0*s+4*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+3*s//5, y_0*s+3*s//5), (x_0*s+4*s//5, y_0*s+4*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)

class Or(Component):
    def emit(self, old_color, new_color):
        if new_color.sum() >= 1:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=Color([0, 0, 0, 0, 1, 0])))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=Color([0, 0, 0, 0, -1, 0])))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(192, 192, 192, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+s//5), (x_0*s+4*s//5, y_0*s+4*s//5)],
                         fill=self.color.to_visible_color(),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+2*s//5), (x_0*s+3*s//5, y_0*s+3*s//5)],
                         fill=(192, 192, 192, 255),
                         width=5)

frames = []
grid = Grid((14*N, 20), 24, render_mode=not args.no_render)

for i in range(N):
    grid.queue_signal(Signal(component=And, x=2+i*14, y=10, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=Or, x=2+i*14, y=12, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=Xor, x=6+i*14, y=10, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=Xor, x=8+i*14, y=6, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=And2, x=8+i*14, y=12, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))

    grid.queue_signal(Signal(component=ToDownAndRight, x=2+i*14, y=6, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=ToUp, x=2+i*14, y=14, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))

    grid.queue_signal(Signal(component=ToDown, x=4+i*14, y=4, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=Junction, x=4+i*14, y=6, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=ToLeft, x=4+i*14, y=10, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))

    grid.queue_signal(Signal(component=ToDown, x=6+i*14, y=8, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=Junction, x=6+i*14, y=14, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))

    grid.queue_signal(Signal(component=ToLeftAndDown, x=8+i*14, y=4, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=ToLeftAndDown, x=8+i*14, y=8, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=Junction, x=8+i*14, y=10, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=ToLeft, x=8+i*14, y=14, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))

    grid.queue_signal(Signal(component=ToLeft, x=10+i*14, y=10, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))
    grid.queue_signal(Signal(component=ToUpAndLeft, x=10+i*14, y=12, direction=(0, 0), color=Color([0, 0, 0, 0, 0, 0])))

    grid.add_register(x=6+i*14, y=16, address=f"o{N-1-i}")

# Convert a number into an 8-bit integer
def to_bits(n):
    # Convert the input into a real integer
    n = int(n)
    # Prepare a 0 list
    answer = N*[0]
    # Test each bit, from the largest to the smallest
    for x in reversed(range(N)):
        # If bit's ON value is greater or equal to the integer, activate
        # the bit and subtract from the integer
        if n >= 2**x:
            n -= 2**x
            answer[N-1-x] = 1
    return answer

initial_signals = []

def initial_signal(number, n):
    bits = to_bits(number)
    for i, bit in enumerate(bits):
        if n and bit:
            initial_signals.append(Signal(component=Wire, x=2+i*14, y=0, direction=(0, 1), color=Color([1, 0, 0, 0, 0, 0])))
        elif bit:
            initial_signals.append(Signal(component=Wire, x=8+i*14, y=0, direction=(0, 1), color=Color([0, 0, 1, 0, 0, 0])))

first = args.a
second = args.b

initial_signal(first, 0)
initial_signal(second, 1)

initial_signals = sorted(initial_signals, key=lambda signal: -signal.x)

for s in initial_signals:
    grid.queue_signal(s)
    if s.color.color == [0, 0, 1, 0, 0, 0]:
        grid.add_register(x=s.x, y=0, address=f"a{N-1-s.x//14}")
    elif s.color.color == [1, 0, 0, 0, 0, 0]:
        grid.add_register(x=s.x, y=0, address=f"b{N-1-s.x//14}")
    grid.run_queue()

if not args.no_render:
    grid.frames[0].save('./cube.gif', format='GIF', append_images=grid.frames[1:],
                save_all=True, duration=100)#, loop=0)

print(first, to_bits(first))
print(second, to_bits(second))
print(first+second, to_bits(first+second))

registers = grid.read_registers()

a_out = sum([registers.get(f"a{i}", 0)*2**i for i in range(N)])
b_out = sum([registers.get(f"b{i}", 0)*2**i for i in range(N)])
o_out = sum([registers.get(f"o{i}", 0)*2**i for i in range(N)])

print(a_out)
print(b_out)
print(o_out)

try:
    assert first == a_out
except ArithmeticError as e:
    print(f"{first} != {a_out}")
    print(e)

try:
    assert second == b_out
except ArithmeticError as e:
    print(f"{second} != {b_out}")
    print(e)

try:
    assert first+second == o_out
except ArithmeticError as e:
    print(f"{first+second} != {o_out}")
    print(e)