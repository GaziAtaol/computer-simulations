# Game of Life

Interactive cellular automaton with custom rules, drawn with Tkinter. The grid wraps around at its edges (a torus), and the survival and birth rules can be changed while the simulation runs.

## Features

* 40 x 60 cell grid with cyclic (wrap around) boundaries.
* Draw and erase cells with the mouse, click or drag.
* Controls: play and pause, single step, clear, random fill (30 percent alive) and a speed slider from 20 ms to 500 ms per generation.
* Counters for generation and population.
* Rules entered as the digits of the neighbor counts, for example `23` survive and `3` birth for the classic B3/S23 rule.
* Quick rule buttons: Classic, HighLife, Seeds, Day&Night, Diamoeba, Replicator.
* Preset patterns: Glider, Blinker, Toad, Beacon, Pulsar and Gosper Gun.

## Run

```bash
python main.py
```

Requires Python with `tkinter`. On Homebrew Python for macOS, install it with `brew install python-tk`.

## How it works

Each generation, every cell counts its eight neighbors (indices wrap with the modulo operator). A live cell survives if its neighbor count is in the survive set, and a dead cell becomes alive if its count is in the birth set. A new grid is built every generation, so all cells update at the same time.

## Notes from testing

Re-running the same update rule on the same 40 x 60 torus for 400 generations gives these results for the presets:

* Blinker (3 cells), Toad (6) and Beacon (8) keep a constant population, and the Glider keeps 5 cells.
* Pulsar cycles through 48, 56 and 72 cells with period 3, which matches the known oscillator.
* Gosper Gun grows by 5 cells every 30 generations at first (36, 41, 46), as it emits gliders. On this small torus the gliders wrap around and hit the gun, so after a few hundred generations the pattern is no longer a clean gun (150 cells at generation 400).

## Limitations

* The neighbor count and the redraw are not optimized, which is fine for a grid of 2400 cells.
* Typing a rule digit above 8 is ignored.
