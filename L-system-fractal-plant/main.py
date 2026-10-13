from turtle import Turtle, Screen

# Lsystem string generator
def generate_lsystem(axiom, rules, iterations):
    current = axiom
    for _ in range(iterations):
        next_str = ""
        for ch in current:
            if ch in rules:
                next_str += rules[ch]
            else:
                next_str += ch
        current = next_str
    return current

# Turtle interpreter
def draw_lsystem(t, instructions, angle, distance):
    stack = []

    for ch in instructions:
        if ch == 'F':
            t.forward(distance)
        elif ch == '+':
            t.left(angle)
        elif ch == '-':
            t.right(angle)
        elif ch == '[':
            stack.append((t.position(), t.heading()))
        elif ch == ']':
            pos, head = stack.pop()
            t.penup()
            t.goto(pos)
            t.setheading(head)
            t.pendown()

# L-system parameters
axiom = "X"
rules = {
    'X': "F+[[X]-X]-F[-FX]+X",
    'F': "FF"
}
angle = 25

# User input
n = int(input("Enter number of iterations (recommended 5-7): "))

# Scale line length by iteration
distance = 200 / (2 ** n)

# Generate L-system string
instructions = generate_lsystem(axiom, rules, n)

# Visualization setup
screen = Screen()
screen.setup(width=800, height=800)
screen.title(f"L System Fractal Plant iteration: {n}")
screen.bgcolor("white")

t = Turtle()
t.speed(0)
screen.tracer(0, 0)

t.pensize(1)
t.color("green")
t.penup()
t.goto(0, -350)
t.setheading(90)
t.pendown()

draw_lsystem(t, instructions, angle, distance)

t.hideturtle()
screen.update()
screen.mainloop()