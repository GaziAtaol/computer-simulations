# Projectile Motion Simulation

Numerical simulation of projectile motion with aerodynamic drag, implemented using three ODE integration methods: **Euler**, **MidPoint** (improved Euler), and **RK4** (fourth-order Runge-Kutta).

Built as part of the PSM (Physical Simulation Methods) lab course at PJAIT.

---

## Physics

The projectile is subject to two forces:

- **Gravity:** `Fg = mg` (downward)
- **Drag:** `Fr = -k·V²` (opposite to velocity direction)

In 2D, the drag force is decomposed along each axis using the unit velocity vector:

```
ax = -(k/m) · V · vx
ay = -g - (k/m) · V · vy
```

where `V = √(vx² + vy²)` is the total speed. This produces a trajectory that is **no longer a perfect parabola** — the drag reduces both range and maximum height, and the descent side is steeper than the ascent.

---

## Numerical Methods

All three methods solve the same system of 4 coupled first-order ODEs:

```
dx/dt  = vx
dy/dt  = vy
dvx/dt = ax
dvy/dt = ay
```

| Method | Order | derivatives() calls per step | Notes |
|---|---|---|---|
| Euler | 1st | 1 | Simplest, least accurate |
| MidPoint | 2nd | 2 | Improved Euler — evaluates at midpoint |
| RK4 | 4th | 4 | Most accurate, reference solution |

### Euler
```
state(t + dt) = state(t) + dt · f(state(t))
```

### MidPoint
```
k1 = f(state(t))
k2 = f(state(t) + k1·dt/2)
state(t + dt) = state(t) + dt · k2
```

### RK4
```
k1 = f(state(t))
k2 = f(state(t) + k1·dt/2)
k3 = f(state(t) + k2·dt/2)
k4 = f(state(t) + k3·dt)
state(t + dt) = state(t) + (dt/6)·(k1 + 2k2 + 2k3 + k4)
```

---

## Usage

### Requirements

```bash
pip install matplotlib
```

### Run

```bash
python projectile_motion.py
```

The program prompts for all parameters interactively:

```
====================================================
   Projectile Motion Simulation
   Methods: Euler | MidPoint | RK4
====================================================

Initial speed     v0 [m/s]   (> 0)         : 50
Launch angle      θ  [deg]   (1 – 89)      : 45
Mass              m  [kg]    (> 0)         : 1
Drag coefficient  k  [kg/m]  (>= 0)        : 0.1
Time step         dt [s]     (0.0001–0.1)  : 0.01
```

Invalid inputs are rejected with an error message and the prompt repeats.

### Output

Terminal results table:

```
────────────────────────────────────────────────────
  Method          Range [m]   Max height [m]
────────────────────────────────────────────────────
  Euler              19.832           9.804
  MidPoint           19.998           9.861
  RK4                19.994           9.858
  No drag           250.669          62.677
────────────────────────────────────────────────────
```

A matplotlib window opens with the trajectory plot, and `trajectory.png` is saved to the working directory.

---

## Parameter Guide

| Parameter | Symbol | Valid range | Recommended |
|---|---|---|---|
| Initial speed | v₀ | > 0 m/s | 10 – 100 m/s |
| Launch angle | θ | 1° – 89° | 30° – 60° |
| Mass | m | > 0 kg | 1 – 10 kg |
| Drag coefficient | k | ≥ 0 kg/m | 0 (no drag) – 0.5 |
| Time step | dt | 0.0001 – 0.1 s | 0.01 s |

> **Note:** Setting `k = 0` disables drag and produces a perfect parabola identical to the reference curve.

> **Note:** Large `dt` values cause numerical instability. The simulation enforces `dt ≤ 0.1 s` to prevent divergence.

---

## Example Results

With `v₀ = 50 m/s`, `θ = 45°`, `m = 1 kg`, `k = 0.1 kg/m`, `dt = 0.01 s`:

| Method | Range | Max height |
|---|---|---|
| Euler | 19.832 m | 9.804 m |
| MidPoint | 19.998 m | 9.861 m |
| RK4 | 19.994 m | 9.858 m |
| No drag | 250.669 m | 62.677 m |

Drag reduces the range from **250 m → 20 m** (×12.5 reduction). MidPoint and RK4 agree to within 0.004 m; Euler undershoots by ~0.2 m relative to RK4.

---

## Project Structure

```
projectile_motion.py   ← single-file simulation
trajectory.png         ← plot saved on each run (generated)
README.md
```


