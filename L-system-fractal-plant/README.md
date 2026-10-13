# L-System Fractal Plant

Generates a fractal plant from an L-system (Lindenmayer system) and draws it with turtle graphics.

## L-system

| Item | Value |
|---|---|
| Axiom | `X` |
| Rule for `X` | `F+[[X]-X]-F[-FX]+X` |
| Rule for `F` | `FF` |
| Angle | 25 degrees |

Symbols are interpreted as follows:

* `F` moves forward and draws a line.
* `+` turns left and `-` turns right by the angle.
* `[` saves the current position and heading on a stack.
* `]` restores the last saved position and heading, which creates a branch.
* `X` only controls the growth and draws nothing.

At every iteration all symbols are rewritten in parallel with the rules. The line length is scaled as `200 / 2^n`, because every `F` doubles in length with each iteration, so the plant keeps the same size on the screen.

## Run

```bash
python main.py
```

Enter the number of iterations. A value from 5 to 7 is recommended. Requires `tkinter` (see the root README).

## Growth of the command string

Length of the generated string for each iteration:

| Iterations | Symbols | Forward lines (`F`) |
|---|---|---|
| 5 | 6,263 | 1,488 |
| 6 | 25,159 | 6,048 |
| 7 | 100,839 | 24,384 |

The string grows about 4 times per iteration, so values above 7 make the drawing slow. Turtle animation is turned off and the screen is updated once at the end.

## Limitations

* The input is not validated, so a value that is not an integer stops the program with an error.
