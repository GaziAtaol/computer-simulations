import math
import matplotlib.pyplot as plt

# ── Helper: validated input ────────────────────────────────────────────────────
def ask(prompt, min_val=None, max_val=None, exclude_zero=False):
    while True:
        try:
            val = float(input(prompt))
            if exclude_zero and val == 0:
                print(f"Error: value must not be zero.")
                continue
            if min_val is not None and val < min_val:
                print(f"Error: value must be >= {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"Error: value must be <= {max_val}")
                continue
            return val
        except ValueError:
            print("Error: please enter a number.")

# ── User input ─────────────────────────────────────────────────────────────────
print("=" * 52)
print("Projectile Motion Simulation")
print("Methods: Euler | MidPoint | RK4")
print("=" * 52)

v0 = ask("\nInitial speed v0 [m/s] (> 0): ", min_val=0.01)
angle = ask("Launch angle θ [deg] (1 – 89): ", min_val=1.0, max_val=89.0)
if angle >= 90.0:
    print("Error: angle must be < 90°")
    angle = ask("Launch angle θ deg] (1 – 89): ", min_val=1.0, max_val=89.0)
m = ask("Mass m  [kg] (> 0): ", min_val=0.001)
k = ask("Drag coefficient k [kg/m]  (>= 0): ", min_val=0.0)
dt = ask("Time step dt [s] (0.0001–0.1): ", min_val=0.0001, max_val=0.1)

g   = 10.0
vx0 = v0 * math.cos(math.radians(angle))
vy0 = v0 * math.sin(math.radians(angle))

# Guard against floating point rounding near 0° and 90°
if abs(vx0) < 1e-10:
    vx0 = 0.0
if abs(vy0) < 1e-10:
    vy0 = 0.0

print(f"\nRunning simulation (g={g} m/s²) ...")

# ── Physics ────────────────────────────────────────────────────────────────────
# Drag force vector: F_drag = -k*V^2 * (v/V) = -k*V*v
# Components:
# ax = -(k/m)*V*vx
# ay = -g - (k/m)*V*vy

def derivatives(x, y, vx, vy):
    V  = math.sqrt(vx**2 + vy**2)
    ax = -(k / m) * V * vx
    ay = -g - (k / m) * V * vy
    return vx, vy, ax, ay

# ── Euler ──────────────────────────────────────────────────────────────────────
def simulate_euler():
    x, y, vx, vy = 0.0, 0.0, vx0, vy0
    xs, ys = [x], [y]
    while y >= 0:
        dx, dy, ax, ay = derivatives(x, y, vx, vy)
        x  += dx * dt
        y  += dy * dt
        vx += ax * dt
        vy += ay * dt
        xs.append(x)
        ys.append(y)
    return xs, ys


# ── MidPoint (improved Euler) ──────────────────────────────────────────────────
def simulate_midpoint():
    x, y, vx, vy = 0.0, 0.0, vx0, vy0
    xs, ys = [x], [y]
    while y >= 0:
        dx1, dy1, ax1, ay1 = derivatives(x, y, vx, vy)

        xm  = x  + dx1 * dt / 2
        ym  = y  + dy1 * dt / 2
        vxm = vx + ax1 * dt / 2
        vym = vy + ay1 * dt / 2

        dx2, dy2, ax2, ay2 = derivatives(xm, ym, vxm, vym)

        x  += dx2 * dt
        y  += dy2 * dt
        vx += ax2 * dt
        vy += ay2 * dt
        xs.append(x)
        ys.append(y)

    return xs, ys


# ── RK4 ───────────────────────────────────────────────────────────────────────
def simulate_rk4():
    x, y, vx, vy = 0.0, 0.0, vx0, vy0
    xs, ys = [x], [y]
    while y >= 0:
        dx1, dy1, ax1, ay1 = derivatives(x,y,vx,vy)
        dx2, dy2, ax2, ay2 = derivatives(x+dx1*dt/2, y+dy1*dt/2, vx+ax1*dt/2, vy+ay1*dt/2 )
        dx3, dy3, ax3, ay3 = derivatives(x+dx2*dt/2, y+dy2*dt/2, vx+ax2*dt/2, vy+ay2*dt/2 )
        dx4, dy4, ax4, ay4 = derivatives(x+dx3*dt, y+dy3*dt, vx+ax3*dt, vy+ay3*dt   )

        x  += (dt/6) * (dx1 + 2*dx2 + 2*dx3 + dx4)
        y  += (dt/6) * (dy1 + 2*dy2 + 2*dy3 + dy4)
        vx += (dt/6) * (ax1 + 2*ax2 + 2*ax3 + ax4)
        vy += (dt/6) * (ay1 + 2*ay2 + 2*ay3 + ay4)
        xs.append(x)
        ys.append(y)
    return xs, ys


# ── No-drag reference ─────────────────────────────────────────────────────────
def simulate_no_drag():
    x, y, vx, vy = 0.0, 0.0, vx0, vy0
    xs, ys = [x], [y]
    while y >= 0:
        x += vx * dt
        y += vy * dt
        vy -= g * dt
        xs.append(x)
        ys.append(y)
    return xs, ys


# ── Run ────────────────────────────────────────────────────────────────────────
xs_e, ys_e  = simulate_euler()
xs_mp, ys_mp = simulate_midpoint()
xs_rk, ys_rk = simulate_rk4()
xs_nd, ys_nd = simulate_no_drag()

# ── Results table ──────────────────────────────────────────────────────────────
print(f"\n{'─'*52}")
print(f" {'Method':<12} {'Range [m]':>12} {'Max height [m]':>14}")
print(f"{'─'*52}")
for label, xs, ys in [
    ("Euler", xs_e, ys_e),
    ("MidPoint", xs_mp, ys_mp),
    ("RK4", xs_rk, ys_rk),
    ("No drag", xs_nd, ys_nd),
]:

    print(f" {label:<12} {xs[-1]:>12.3f} {max(ys):>14.3f}")
print(f"{'─'*52}\n")

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(xs_nd, ys_nd, color='gray', linewidth=1.5, linestyle='--', label='No drag (ideal parabola)')
ax.plot(xs_e, ys_e, color='#E24B4A', linewidth=3.0, linestyle='-', label='Euler')
ax.plot(xs_mp, ys_mp, color='#1D9E75', linewidth=2.0, linestyle='--', dashes=(8,4), label='MidPoint (improved Euler)')
ax.plot(xs_rk, ys_rk, color='#378ADD', linewidth=2.0, linestyle=':', label='RK4')

ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')
ax.set_title(
    f'Projectile Motion with Drag  '
    f'(v₀={v0} m/s, θ={angle}°, m={m} kg, k={k} kg/m, dt={dt} s)'
)
ax.legend()
ax.grid(True, which='both', linestyle=':', linewidth=0.5, color='grey', alpha=0.6)
ax.minorticks_on()
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig('trajectory.png', dpi=150)
plt.show()
print("Plot saved → trajectory.png")
