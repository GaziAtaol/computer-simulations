# Computer Simulations

Python implementations of numerical simulations. The projects solve ordinary differential equations with Euler, midpoint and fourth-order Runge-Kutta (RK4) integrators, solve a steady-state heat problem as a sparse linear system, and run two cellular-automaton and grammar-based models.

## Projects

| Folder | What it simulates | Method | Main finding |
|---|---|---|---|
| [pendulum](pendulum) | Mathematical pendulum, 45 degrees, 10 s | Midpoint, RK4 | Total energy drift 5.9e-4 J (midpoint) versus 2.9e-8 J (RK4) |
| [orbital-motion](orbital-motion) | Earth and Moon around the Sun, Earth satellites | Midpoint | A satellite at the first cosmic speed stays on a near circular orbit, slower ones fall to Earth |
| [lorenz-attractor](lorenz-attractor) | Lorenz system, dt = 0.03 | Euler, midpoint, RK4 | Euler overflows after about 1.4 time units, midpoint and RK4 stay bounded |
| [heat-plate](heat-plate) | Steady-state temperature of a 15 x 15 cm plate | Finite differences, sparse solver | 1600 unknowns solved directly, residual about 3e-13 |
| [string-wave](string-wave) | Vibrating string with fixed ends | Midpoint on the wave equation | Relative energy drift 6.2e-7 over 4000 steps |
| [rolling-motion](rolling-motion) | Solid and hollow sphere rolling down a ramp | Midpoint | Solid sphere arrives first, 2.390 s versus 2.607 s |
| [projectile-motion](projectile-motion) | Projectile with quadratic air drag | Euler, midpoint, RK4 | Drag cuts the range from about 250 m to about 20 m in the example |
| [game-of-life](game-of-life) | Cellular automaton with custom rules | Cyclic grid, Tkinter | Six rule sets and six preset patterns, rules editable while running |
| [L-system-fractal-plant](L-system-fractal-plant) | Fractal plant | L-system with turtle graphics | The command string grows about 4 times per iteration |

## Setup

Python 3.10 or newer.

```bash
pip install -r requirements.txt
```

`game-of-life` and `L-system-fractal-plant` use `tkinter` and `turtle`, which ship with Python. On Homebrew Python for macOS you may need `brew install python-tk`.

Each project is a single script. Run it from inside its folder:

```bash
cd pendulum
python main.py
```

`projectile-motion` and `L-system-fractal-plant` ask for input in the terminal. The other scripts run without input.

## Notes on accuracy

Each folder README states what the script does and does not show. Some points that apply across the repository:

* Several scripts save their figures into the working directory, so run them from their own folder.
* Where a README quotes a number, it comes from running the script in this repository. Comparisons with analytic solutions that are not part of a script are labeled as separate checks.
* The ODE projects use fixed time steps, no adaptive step size and no error control.

## License

GPL-3.0, see [LICENSE](LICENSE).
