from PIL import Image, ImageDraw

N = 4

class Grid:
    def __init__(self, canvas_size, cell_size):
        self.grid = dict()
        self.queue = []
        self.frames = []
        self.canvas_size = canvas_size
        self.cell_size = cell_size
        self.counter = 0
        self.registers = []
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
            if self.counter >= 2500:
                break
            signal = self.queue.pop(0)
            while True:
                print(self.counter, signal)
                if signal.x < 0 or signal.x > self.canvas_size[0]:
                    break
                elif signal.y < 0 or signal.y > self.canvas_size[1]:
                    break
                grid.assign(signal)
                if grid.activate_cell(signal):
                    self.frames.append(grid.render())
                else:
                    self.frames.append(grid.render())
                    break
                if signal.direction == (0, 0) or sum(signal.color) == 0:
                    break
                else:
                    signal.x += signal.direction[0]
                    signal.y += signal.direction[1]
        print("Queue empty")
    def add_register(self, x, y, address):
        self.registers.append({"x":x, "y":y, "address":address})
    def read_registers(self):
        values = dict()
        for r in self.registers:
            if r["x"] in self.grid and r["y"] in self.grid[r["x"]]:
                values[r["address"]] = max(self.grid[r["x"]][r["y"]].color)
            else:
                values[r["address"]] = 0
        return values
    def render(self):
        self.counter += 1
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
        print(registers)
        draw.text((20, 40), str(sum([registers.get(f"a{i}", 0)*2**i for i in range(i)])), fill=(255, 255, 255, 128))
        draw.text((40, 40), str(sum([registers.get(f"b{i}", 0)*2**i for i in range(i)])), fill=(255, 255, 255, 128))
        draw.text((60, 40), str(sum([registers.get(f"o{i}", 0)*2**i for i in range(i)])), fill=(255, 255, 255, 128))
        return image
    def __repr__(self):
        return str(self.grid)

class Signal:
    def __init__(self, x, y, direction, component, color, emitter=None):
        self.emitter = emitter
        self.x = x
        self.y = y
        self.direction = direction
        self.component = component
        self.color = color
    def __repr__(self):
        return str([self.x, self.y, self.direction, self.component, self.color, self.emitter])

class Wire:
    def __init__(self, parent_grid, signal):
        self.parent_grid = parent_grid
        self.color = signal.color
        self.position = (signal.x, signal.y)
        self.transparent = 1
    @staticmethod
    def off_color(color):
        return [-x for x in color]
    def activate(self, signal):
        old_color = self.color[:] # For getting rid of an existing signal, get a copy
        for n, s in enumerate(signal.color):
            self.color[n] = max(0, min(1, self.color[n]+s))
        # Give the old and new color for the emit method to decide
        self.emit(old_color, self.color)
        return self.transparent
    def emit(self, old_color, new_color):
        pass
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
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
        self.color_horizontal = signal.color[:]
        self.color_vertical = signal.color[:]
        self.position = (signal.x, signal.y)
        self.transparent = 1
    def activate(self, signal):
        if signal.direction in [(-1, 0), (1, 0)]:
            old_color = self.color_horizontal # For getting rid of an existing signal
            for n, s in enumerate(signal.color):
                self.color_horizontal[n] = max(0, min(1, self.color_horizontal[n]+s))
            self.emit(old_color, self.color_horizontal, signal.direction)
        elif signal.direction in [(0, -1), (0, 1)]:
            old_color = self.color_vertical # For getting rid of an existing signal
            for n, s in enumerate(signal.color):
                self.color_vertical[n] = max(0, min(1, self.color_vertical[n]+s))
            self.emit(old_color, self.color_vertical, signal.direction)
        return self.transparent
    def emit(self, old_color, new_color, direction):
        if sum(new_color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+direction[0], y=self.position[1]+direction[1], direction=direction, color=new_color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+direction[0], y=self.position[1]+direction[1], direction=direction, color=old_color))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s, y_0*s+s//3), (x_0*s+s, y_0*s+2*s//3)],
                         fill=(255*self.color_horizontal[0], 255*self.color_horizontal[1], 255*self.color_horizontal[2], 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//3, y_0*s), (x_0*s+2*s//3, y_0*s+s)],
                         fill=(255*self.color_vertical[0], 255*self.color_vertical[1], 255*self.color_vertical[2], 255),
                         width=5)

class ToLeft(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.off_color(old_color)))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//2), n_sides=3, rotation=90, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))

class ToUp(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=self.off_color(old_color)))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//2), n_sides=3, rotation=0, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))

class ToLeftAndDown(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.color))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.off_color(old_color)))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.off_color(old_color)))      
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+3*s//4, s//4), n_sides=3, rotation=180, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))
        draw.regular_polygon((x_0*s+s//4, y_0*s+s//2, s//4), n_sides=3, rotation=90, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))

class ToUpAndLeft(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=self.color))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]-1, direction=(0, -1), color=self.off_color(old_color)))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.off_color(old_color)))      
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//4, s//4), n_sides=3, rotation=0, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))
        draw.regular_polygon((x_0*s+s//4, y_0*s+s//2, s//4), n_sides=3, rotation=90, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))

class ToLeftAndDownAndRight(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.color))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.color))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=self.off_color(old_color)))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.off_color(old_color)))
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=self.off_color(old_color)))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+3*s//4, s//4), n_sides=3, rotation=180, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))
        draw.regular_polygon((x_0*s+s//4, y_0*s+s//2, s//4), n_sides=3, rotation=90, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))
        draw.regular_polygon((x_0*s+s//4, y_0*s+s//2, s//4), n_sides=3, rotation=90, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))

class ToDown(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=self.off_color(old_color)))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//2), n_sides=3, rotation=180, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))

class ToRight(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) > 0:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=self.color))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]+1, y=self.position[1], direction=(1, 0), color=self.off_color(old_color)))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.regular_polygon((x_0*s+s//2, y_0*s+s//2, s//2), n_sides=3, rotation=270, fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255))

class And(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) >= 2:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=[0, 1, 0]))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=[0, -1, 0]))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+s//5), (x_0*s+4*s//5, y_0*s+4*s//5)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+2*s//5), (x_0*s+3*s//5, y_0*s+2.5*s//5)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+3*s//5), (x_0*s+3*s//5, y_0*s+4*s//5)],
                         fill=(255, 255, 255, 255),
                         width=5)

class Xor(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) == 1:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=[0, 1, 0]))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0], y=self.position[1]+1, direction=(0, 1), color=[0, -1, 0]))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+s//5), (x_0*s+2*s//5, y_0*s+2*s//5)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+3*s//5, y_0*s+s//5), (x_0*s+4*s//5, y_0*s+2*s//5)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+2*s//5), (x_0*s+3*s//5, y_0*s+3*s//5)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+3*s//5), (x_0*s+2*s//5, y_0*s+4*s//5)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+3*s//5, y_0*s+3*s//5), (x_0*s+4*s//5, y_0*s+4*s//5)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
                         width=5)

class Or(Component):
    def emit(self, old_color, new_color):
        if sum(self.color) >= 1:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=[0, 1, 0]))
        else:
            self.parent_grid.queue_signal(Signal(emitter=self, component=Wire, x=self.position[0]-1, y=self.position[1], direction=(-1, 0), color=[0, -1, 0]))
    def draw_own_cell(self, draw, x_0, y_0, s):
        draw.rectangle(xy=[(x_0*s, y_0*s), (x_0*s+s, y_0*s+s)],
                         fill=(255, 255, 255, 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+s//5, y_0*s+s//5), (x_0*s+4*s//5, y_0*s+4*s//5)],
                         fill=(255*self.color[0], 255*self.color[1], 255*self.color[2], 255),
                         width=5)
        draw.rectangle(xy=[(x_0*s+2*s//5, y_0*s+2*s//5), (x_0*s+3*s//5, y_0*s+3*s//5)],
                         fill=(255, 255, 255, 255),
                         width=5)

frames = []
grid = Grid((120, 24), 12)

for i in range(N):
    grid.queue_signal(Signal(component=And, x=2+i*14, y=6, direction=(0, 0), color=[0, 0, 0]))
    grid.queue_signal(Signal(component=Or, x=2+i*14, y=10, direction=(0, 0), color=[0, 0, 0]))
    grid.queue_signal(Signal(component=Xor, x=4+i*14, y=8, direction=(0, 0), color=[0, 0, 0]))
    grid.queue_signal(Signal(component=Xor, x=6+i*14, y=6, direction=(0, 0), color=[0, 0, 0]))
    grid.queue_signal(Signal(component=And, x=6+i*14, y=10, direction=(0, 0), color=[0, 0, 0]))

    grid.queue_signal(Signal(component=ToDown, x=2+i*14, y=4, direction=(0, 0), color=[0, 0, 0]))

    grid.queue_signal(Signal(component=Junction, x=4+i*14, y=4, direction=(0, 0), color=[0, 0, 0]))
    grid.queue_signal(Signal(component=ToLeftAndDownAndRight, x=4+i*14, y=6, direction=(0, 0), color=[0, 0, 0]))
    
    grid.queue_signal(Signal(component=ToLeftAndDown, x=6+i*14, y=4, direction=(0, 0), color=[0, 0, 0]))
    grid.queue_signal(Signal(component=Junction, x=6+i*14, y=8, direction=(0, 0), color=[0, 0, 0]))

    grid.queue_signal(Signal(component=ToLeft, x=8+i*14, y=8, direction=(0, 0), color=[0, 0, 0]))
    grid.queue_signal(Signal(component=ToUpAndLeft, x=8+i*14, y=8, direction=(0, 0), color=[0, 0, 0]))

    grid.add_register(x=6+i*14, y=14, address=f"o{N-1-i}")

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
            initial_signals.append(Signal(component=Wire, x=6+i*14, y=2, direction=(0, 1), color=[1, 0, 0]))
        elif bit:
            initial_signals.append(Signal(component=Wire, x=4+i*14, y=2, direction=(0, 1), color=[0, 0, 1]))

first = 1
second = 3

initial_signal(first, 0)
initial_signal(second, 1)

initial_signals = sorted(initial_signals, key=lambda signal: -signal.x)

for s in initial_signals:
    grid.queue_signal(s)
    print("register", s.x, s.x//14, N-1-s.x//14)
    if s.color == [0, 0, 1]:
        grid.add_register(x=s.x, y=s.y, address=f"b{N-1-s.x//14}")
    elif s.color == [1, 0, 0]:
        grid.add_register(x=s.x, y=s.y, address=f"a{N-1-s.x//14}")
    grid.run_queue()

grid.frames[0].save('./cube.gif', format='GIF', append_images=grid.frames[1:],
               save_all=True, duration=25)#, loop=0)

print(first, to_bits(first))
print(second, to_bits(second))
print(first+second, to_bits(first+second))

registers = grid.read_registers()

try:
    a_out = sum([registers.get(f"a{i}", 0)*2**i for i in range(i)])
    assert first == a_out
except ArithmeticError as e:
    print(f"{first} != {a_out}")
    print(e)

try:
    b_out = sum([registers.get(f"b{i}", 0)*2**i for i in range(i)])
    assert second == b_out
except ArithmeticError as e:
    print(f"{second} != {b_out}")
    print(e)

try:
    o_out = sum([registers.get(f"o{i}", 0)*2**i for i in range(i)])
    assert first+second == o_out
except ArithmeticError as e:
    print(f"{first+second} != {o_out}")
    print(e)