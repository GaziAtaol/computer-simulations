import numpy as np
import matplotlib.pyplot as plt

G = 6.6743e-11
Ms = 1.989e30
Mz = 5.972e24
Mk = 7.347e22
Rzs = 1.5e11
Rzk = 384400e3
Re = 6371000

v_earth = np.sqrt(G * Ms / Rzs)
v_moon_rel = np.sqrt(G * Mz / Rzk)
v1 = np.sqrt(G * Mz / Re)

T_earth = 2 * np.pi * Rzs / v_earth
T_moon = 2 * np.pi * Rzk / v_moon_rel

t_total = T_earth
dt = 3600.0
N = int(t_total / dt)

x_e = Rzs
y_e = 0.0
vx_e = 0.0
vy_e = v_earth

x_m = Rzs + Rzk
y_m = 0.0
vx_m = 0.0
vy_m = v_earth + v_moon_rel

earth_x = np.zeros(N)
earth_y = np.zeros(N)
moon_x = np.zeros(N)
moon_y = np.zeros(N)
earth_x[0] = x_e
earth_y[0] = y_e
moon_x[0] = x_m
moon_y[0] = y_m


def accel_earth(xe, ye):
    r = np.sqrt(xe**2 + ye**2)
    a = -G * Ms / r**3
    return a * xe, a * ye


def accel_moon(xm, ym, xe, ye):
    r_ms = np.sqrt(xm**2 + ym**2)
    ax = -G * Ms * xm / r_ms**3
    ay = -G * Ms * ym / r_ms**3
    dx = xm - xe
    dy = ym - ye
    r_me = np.sqrt(dx**2 + dy**2)
    ax += -G * Mz * dx / r_me**3
    ay += -G * Mz * dy / r_me**3
    return ax, ay


# Midpoint (Improved Euler)
for i in range(N - 1):
    ax_e, ay_e = accel_earth(x_e, y_e)
    x_e_mid = x_e + 0.5 * dt * vx_e
    y_e_mid = y_e + 0.5 * dt * vy_e
    vx_e_mid = vx_e + 0.5 * dt * ax_e
    vy_e_mid = vy_e + 0.5 * dt * ay_e
    ax_e_mid, ay_e_mid = accel_earth(x_e_mid, y_e_mid)
    x_e = x_e + dt * vx_e_mid
    y_e = y_e + dt * vy_e_mid
    vx_e = vx_e + dt * ax_e_mid
    vy_e = vy_e + dt * ay_e_mid

    ax_m, ay_m = accel_moon(x_m, y_m, x_e, y_e)
    x_m_mid = x_m + 0.5 * dt * vx_m
    y_m_mid = y_m + 0.5 * dt * vy_m
    vx_m_mid = vx_m + 0.5 * dt * ax_m
    vy_m_mid = vy_m + 0.5 * dt * ay_m
    ax_m_mid, ay_m_mid = accel_moon(x_m_mid, y_m_mid, x_e_mid, y_e_mid)
    x_m = x_m + dt * vx_m_mid
    y_m = y_m + dt * vy_m_mid
    vx_m = vx_m + dt * ax_m_mid
    vy_m = vy_m + dt * ay_m_mid

    earth_x[i + 1] = x_e
    earth_y[i + 1] = y_e
    moon_x[i + 1] = x_m
    moon_y[i + 1] = y_m

def simulate_satellite(v0, dt_sat=20, n_steps=15000):
    x, y = 0.0, Re + 1
    vx, vy = v0, 0.0
    xs, ys = [x], [y]
    for _ in range(n_steps):
        r = np.sqrt(x**2 + y**2)
        if r < Re * 0.95:
            break
        ax = -G * Mz * x / r**3
        ay = -G * Mz * y / r**3
        x_mid = x + 0.5 * dt_sat * vx
        y_mid = y + 0.5 * dt_sat * vy
        vx_mid = vx + 0.5 * dt_sat * ax
        vy_mid = vy + 0.5 * dt_sat * ay
        r_mid = np.sqrt(x_mid**2 + y_mid**2)
        ax_mid = -G * Mz * x_mid / r_mid**3
        ay_mid = -G * Mz * y_mid / r_mid**3
        x = x + dt_sat * vx_mid
        y = y + dt_sat * vy_mid
        vx = vx + dt_sat * ax_mid
        vy = vy + dt_sat * ay_mid
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


AU = 1.496e11

fig, axes = plt.subplots(2, 2, figsize=(16, 14))

ax = axes[0, 0]
speeds = [7908, 7000, 6000, 5000, 4000]
colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0']
for v0, c in zip(speeds, colors):
    sx, sy = simulate_satellite(v0)
    ax.plot(sx / 1e6, sy / 1e6, color=c, linewidth=0.6, label=f'v₀ = {v0} m/s')
theta = np.linspace(0, 2 * np.pi, 200)
ax.plot(Re * np.cos(theta) / 1e6, Re * np.sin(theta) / 1e6, 'k-', linewidth=2, label='Earth surface')
ax.set_xlabel('x [×10⁶ m]')
ax.set_ylabel('y [×10⁶ m]')
ax.set_title(f'Satellite Orbits (v₁ = {v1:.0f} m/s)', fontweight='bold')
ax.set_aspect('equal')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

ax = axes[0, 1]
ax.plot(moon_x / AU, moon_y / AU, color='#888888', linewidth=0.3, alpha=0.7, label='Moon trajectory')
ax.plot(earth_x / AU, earth_y / AU, color='#2196F3', linewidth=1.2, label='Earth orbit')
ax.plot(0, 0, 'o', color='#FFC107', markersize=12, label='Sun', zorder=5)
ax.set_xlabel('x [AU]')
ax.set_ylabel('y [AU]')
ax.set_title('Moon Trajectory Relative to the Sun', fontweight='bold')
ax.set_aspect('equal')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

ax = axes[1, 0]
rel_x = (moon_x - earth_x) / 1e6
rel_y = (moon_y - earth_y) / 1e6
ax.plot(rel_x, rel_y, color='#9E9E9E', linewidth=0.5)
ax.plot(0, 0, 'o', color='#2196F3', markersize=8, label='Earth', zorder=5)
ax.set_xlabel('x [×10⁶ m]')
ax.set_ylabel('y [×10⁶ m]')
ax.set_title('Moon Orbit Relative to Earth', fontweight='bold')
ax.set_aspect('equal')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

ax = axes[1, 1]
t_days = np.arange(N) * dt / 86400
moon_r = np.sqrt(moon_x**2 + moon_y**2) / AU
earth_r = np.sqrt(earth_x**2 + earth_y**2) / AU
ax.plot(t_days, moon_r, color='#FF5722', linewidth=0.8, label='Moon')
ax.plot(t_days, earth_r, color='#2196F3', linewidth=1.2, label='Earth')
ax.set_xlabel('Time [days]')
ax.set_ylabel('Distance from Sun [AU]')
ax.set_title('Moon Wobble (~13 cycles/year)', fontweight='bold')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

plt.suptitle('Orbital Motion: Improved Euler (Midpoint) Method', fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('orbital_overview.png', dpi=150)
plt.show()

print(f"v₁ (cosmic speed) = {v1:.0f} m/s")
print(f"dt = {dt:.0f} s, steps = {N}")
print(f"earth period: {T_earth/86400:.1f} day, moon period: {T_moon/86400:.1f} day")
print(f"earth speed: {v_earth:.0f} m/s, moon spped: {v_moon_rel:.0f} m/s")