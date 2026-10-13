import math
import matplotlib.pyplot as plt
'''
# ── Helper: validated input ────────────────────────────────────────────────────
def ask(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = float(input(prompt))
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
print("Mathematical Pendulum Simulation")
print("Methods: Euler | MidPoint | RK4")
print("=" * 52)

alpha0_deg = ask("\nInitial angle α₀ [deg] (1–179): ", min_val=1.0, max_val=179.0)
omega0     = ask("Initial angular velocity ω₀ [rad/s]: ")
m          = ask("Mass m [kg] (> 0): ", min_val=0.001)
l          = ask("Pendulum length l [m] (> 0): ", min_val=0.001)
dt         = ask("Time step dt [s] (0.0001–0.1): ", min_val=0.0001, max_val=0.1)
T_sim      = ask("Simulation time T [s] (> 0): ", min_val=0.01)

g      = 10.0
alpha0 = math.radians(alpha0_deg)

print(f"\nRunning simulation (g={g} m/s²) ...")

# ── Physics ────────────────────────────────────────────────────────────────────
def deriv(alpha, omega):
    return omega, -(g / l) * math.sin(alpha)

def potential(alpha):
    return m * g * l * (1 - math.cos(alpha))

def kinetic(omega):
    return 0.5 * m * (l * omega) ** 2

# ── Euler ──────────────────────────────────────────────────────────────────────
def simulate_euler():
    alpha, omega, t = alpha0, omega0, 0.0
    ts, alphas, omegas = [t], [alpha], [omega]
    while t < T_sim:
        da, dw = deriv(alpha, omega)
        alpha += da * dt
        omega += dw * dt
        t += dt
        ts.append(t); alphas.append(alpha); omegas.append(omega)
    return ts, alphas, omegas

# ── MidPoint (Improved Euler) ──────────────────────────────────────────────────
def simulate_midpoint():
    alpha, omega, t = alpha0, omega0, 0.0
    ts, alphas, omegas = [t], [alpha], [omega]
    while t < T_sim:
        da1, dw1 = deriv(alpha, omega)
        da2, dw2 = deriv(alpha + da1*dt/2, omega + dw1*dt/2)
        alpha += da2 * dt
        omega += dw2 * dt
        t += dt
        ts.append(t); alphas.append(alpha); omegas.append(omega)
    return ts, alphas, omegas

# ── RK4 ───────────────────────────────────────────────────────────────────────
def simulate_rk4():
    alpha, omega, t = alpha0, omega0, 0.0
    ts, alphas, omegas = [t], [alpha], [omega]
    while t < T_sim:
        da1, dw1 = deriv(alpha, omega)
        da2, dw2 = deriv(alpha + da1*dt/2, omega + dw1*dt/2)
        da3, dw3 = deriv(alpha + da2*dt/2, omega + dw2*dt/2)
        da4, dw4 = deriv(alpha + da3*dt,   omega + dw3*dt)
        alpha += (dt/6) * (da1 + 2*da2 + 2*da3 + da4)
        omega += (dt/6) * (dw1 + 2*dw2 + 2*dw3 + dw4)
        t += dt
        ts.append(t); alphas.append(alpha); omegas.append(omega)
    return ts, alphas, omegas

# ── Energy helper ──────────────────────────────────────────────────────────────
def energies(alphas, omegas):
    Us, Ts, Es = [], [], []
    for a, w in zip(alphas, omegas):
        U = potential(a); T = kinetic(w)
        Us.append(U); Ts.append(T); Es.append(U + T)
    return Us, Ts, Es

# ── Run ────────────────────────────────────────────────────────────────────────
ts_e,  a_e,  w_e  = simulate_euler()
ts_mp, a_mp, w_mp = simulate_midpoint()
ts_rk, a_rk, w_rk = simulate_rk4()

U_e,  T_e,  E_e  = energies(a_e,  w_e)
U_mp, T_mp, E_mp = energies(a_mp, w_mp)
U_rk, T_rk, E_rk = energies(a_rk, w_rk)

E0 = potential(alpha0) + kinetic(omega0)

# ── Validation printout ────────────────────────────────────────────────────────
eps0 = -(g/l)*math.sin(alpha0)
print(f"\nInitial conditions (t=0):")
print(f"  α={alpha0:.4f} rad, ω={omega0:.4f}, ε={eps0:.4f}")
print(f"  x={l*math.sin(alpha0):.4f}, y={-l*math.cos(alpha0):.4f}")
print(f"  U={potential(alpha0):.4f}, T={kinetic(omega0):.4f}, E={E0:.4f}")
if len(a_mp) > 1:
    print(f"\nAt t={dt} (MidPoint): α={a_mp[1]:.4f}, ω={w_mp[1]:.4f}, "
          f"x={l*math.sin(a_mp[1]):.4f}, y={-l*math.cos(a_mp[1]):.4f}")

# ── Results table ──────────────────────────────────────────────────────────────
print(f"\n{'─'*52}")
print(f" {'Method':<12} {'Max |ΔE| [J]':>14} {'Final E [J]':>14}")
print(f"{'─'*52}")
for label, Es in [("Euler", E_e), ("MidPoint", E_mp), ("RK4", E_rk)]:
    print(f" {label:<12} {max(abs(e-E0) for e in Es):>14.6f} {Es[-1]:>14.6f}")
print(f"{'─'*52}\n")

# ── Plot (2×2) ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(
    f"Mathematical Pendulum  (α₀={alpha0_deg}°, ω₀={omega0} rad/s, "
    f"m={m} kg, l={l} m, dt={dt} s)",
    fontsize=13, fontweight='bold'
)

C_E  = '#E24B4A'
C_MP = '#1D9E75'
C_RK = '#378ADD'

# Panel 1 — α(t) all methods
ax = axes[0, 0]
ax.plot(ts_e,  [math.degrees(a) for a in a_e],  color=C_E,  lw=2.0, label='Euler')
ax.plot(ts_mp, [math.degrees(a) for a in a_mp], color=C_MP, lw=2.0, linestyle='--', dashes=(8,4), label='MidPoint')
ax.plot(ts_rk, [math.degrees(a) for a in a_rk], color=C_RK, lw=2.0, linestyle=':', label='RK4')
ax.set_xlabel('t [s]'); ax.set_ylabel('α [deg]'); ax.set_title('Angle α(t)')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()

# Panel 2 — Phase plane all methods
ax = axes[0, 1]
ax.plot([math.degrees(a) for a in a_e],  w_e,  color=C_E,  lw=2.0, label='Euler')
ax.plot([math.degrees(a) for a in a_mp], w_mp, color=C_MP, lw=2.0, linestyle='--', dashes=(8,4), label='MidPoint')
ax.plot([math.degrees(a) for a in a_rk], w_rk, color=C_RK, lw=2.0, linestyle=':', label='RK4')
ax.set_xlabel('α [deg]'); ax.set_ylabel('ω [rad/s]'); ax.set_title('Phase Plane ω(α)')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()

# Panel 3 — Energy MidPoint
ax = axes[1, 0]
ax.plot(ts_mp, U_mp, color='#E24B4A', lw=2.0, label='U (potential)')
ax.plot(ts_mp, T_mp, color='#F5A623', lw=2.0, label='T (kinetic)')
ax.plot(ts_mp, E_mp, color='gray',    lw=1.5, linestyle='--', label='E (total)')
ax.axhline(E0, color='black', lw=0.8, linestyle=':', alpha=0.6, label=f'E₀={E0:.4f} J')
ax.set_xlabel('t [s]'); ax.set_ylabel('Energy [J]'); ax.set_title('Energy — MidPoint')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()

# Panel 4 — Energy RK4
ax = axes[1, 1]
ax.plot(ts_rk, U_rk, color='#E24B4A', lw=2.0, label='U (potential)')
ax.plot(ts_rk, T_rk, color='#F5A623', lw=2.0, label='T (kinetic)')
ax.plot(ts_rk, E_rk, color='gray',    lw=1.5, linestyle='--', label='E (total)')
ax.axhline(E0, color='black', lw=0.8, linestyle=':', alpha=0.6, label=f'E₀={E0:.4f} J')
ax.set_xlabel('t [s]'); ax.set_ylabel('Energy [J]'); ax.set_title('Energy — RK4')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()
import math
import matplotlib.pyplot as plt

# ── Helper: validated input ────────────────────────────────────────────────────
def ask(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = float(input(prompt))
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
print("Mathematical Pendulum Simulation")
print("Methods: Euler | MidPoint | RK4")
print("=" * 52)

alpha0_deg = ask("\nInitial angle α₀ [deg] (1–179): ", min_val=1.0, max_val=179.0)
omega0     = ask("Initial angular velocity ω₀ [rad/s]: ")
m          = ask("Mass m [kg] (> 0): ", min_val=0.001)
l          = ask("Pendulum length l [m] (> 0): ", min_val=0.001)
dt         = ask("Time step dt [s] (0.0001–0.1): ", min_val=0.0001, max_val=0.1)
T_sim      = ask("Simulation time T [s] (> 0): ", min_val=0.01)

g      = 10.0
alpha0 = math.radians(alpha0_deg)

print(f"\nRunning simulation (g={g} m/s²) ...")

# ── Physics ────────────────────────────────────────────────────────────────────
def deriv(alpha, omega):
    return omega, -(g / l) * math.sin(alpha)

def potential(alpha):
    return m * g * l * (1 - math.cos(alpha))

def kinetic(omega):
    return 0.5 * m * (l * omega) ** 2

# ── Euler ──────────────────────────────────────────────────────────────────────
def simulate_euler():
    alpha, omega, t = alpha0, omega0, 0.0
    ts, alphas, omegas = [t], [alpha], [omega]
    while t < T_sim:
        da, dw = deriv(alpha, omega)
        alpha += da * dt
        omega += dw * dt
        t += dt
        ts.append(t); alphas.append(alpha); omegas.append(omega)
    return ts, alphas, omegas

# ── MidPoint (Improved Euler) ──────────────────────────────────────────────────
def simulate_midpoint():
    alpha, omega, t = alpha0, omega0, 0.0
    ts, alphas, omegas = [t], [alpha], [omega]
    while t < T_sim:
        da1, dw1 = deriv(alpha, omega)
        da2, dw2 = deriv(alpha + da1*dt/2, omega + dw1*dt/2)
        alpha += da2 * dt
        omega += dw2 * dt
        t += dt
        ts.append(t); alphas.append(alpha); omegas.append(omega)
    return ts, alphas, omegas

# ── RK4 ───────────────────────────────────────────────────────────────────────
def simulate_rk4():
    alpha, omega, t = alpha0, omega0, 0.0
    ts, alphas, omegas = [t], [alpha], [omega]
    while t < T_sim:
        da1, dw1 = deriv(alpha, omega)
        da2, dw2 = deriv(alpha + da1*dt/2, omega + dw1*dt/2)
        da3, dw3 = deriv(alpha + da2*dt/2, omega + dw2*dt/2)
        da4, dw4 = deriv(alpha + da3*dt,   omega + dw3*dt)
        alpha += (dt/6) * (da1 + 2*da2 + 2*da3 + da4)
        omega += (dt/6) * (dw1 + 2*dw2 + 2*dw3 + dw4)
        t += dt
        ts.append(t); alphas.append(alpha); omegas.append(omega)
    return ts, alphas, omegas

# ── Energy helper ──────────────────────────────────────────────────────────────
def energies(alphas, omegas):
    Us, Ts, Es = [], [], []
    for a, w in zip(alphas, omegas):
        U = potential(a); T = kinetic(w)
        Us.append(U); Ts.append(T); Es.append(U + T)
    return Us, Ts, Es

# ── Run ────────────────────────────────────────────────────────────────────────
ts_e,  a_e,  w_e  = simulate_euler()
ts_mp, a_mp, w_mp = simulate_midpoint()
ts_rk, a_rk, w_rk = simulate_rk4()

U_e,  T_e,  E_e  = energies(a_e,  w_e)
U_mp, T_mp, E_mp = energies(a_mp, w_mp)
U_rk, T_rk, E_rk = energies(a_rk, w_rk)

E0 = potential(alpha0) + kinetic(omega0)

# ── Validation printout ────────────────────────────────────────────────────────
eps0 = -(g/l)*math.sin(alpha0)
print(f"\nInitial conditions (t=0):")
print(f"  α={alpha0:.4f} rad, ω={omega0:.4f}, ε={eps0:.4f}")
print(f"  x={l*math.sin(alpha0):.4f}, y={-l*math.cos(alpha0):.4f}")
print(f"  U={potential(alpha0):.4f}, T={kinetic(omega0):.4f}, E={E0:.4f}")
if len(a_mp) > 1:
    print(f"\nAt t={dt} (MidPoint): α={a_mp[1]:.4f}, ω={w_mp[1]:.4f}, "
          f"x={l*math.sin(a_mp[1]):.4f}, y={-l*math.cos(a_mp[1]):.4f}")

# ── Results table ──────────────────────────────────────────────────────────────
print(f"\n{'─'*52}")
print(f" {'Method':<12} {'Max |ΔE| [J]':>14} {'Final E [J]':>14}")
print(f"{'─'*52}")
for label, Es in [("Euler", E_e), ("MidPoint", E_mp), ("RK4", E_rk)]:
    print(f" {label:<12} {max(abs(e-E0) for e in Es):>14.6f} {Es[-1]:>14.6f}")
print(f"{'─'*52}\n")

# ── Plot (2×2) ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(
    f"Mathematical Pendulum  (α₀={alpha0_deg}°, ω₀={omega0} rad/s, "
    f"m={m} kg, l={l} m, dt={dt} s)",
    fontsize=13, fontweight='bold'
)

C_E  = '#E24B4A'
C_MP = '#1D9E75'
C_RK = '#378ADD'

# Panel 1 — α(t) all methods
ax = axes[0, 0]
ax.plot(ts_e,  [math.degrees(a) for a in a_e],  color=C_E,  lw=2.0, label='Euler')
ax.plot(ts_mp, [math.degrees(a) for a in a_mp], color=C_MP, lw=2.0, linestyle='--', dashes=(8,4), label='MidPoint')
ax.plot(ts_rk, [math.degrees(a) for a in a_rk], color=C_RK, lw=2.0, linestyle=':', label='RK4')
ax.set_xlabel('t [s]'); ax.set_ylabel('α [deg]'); ax.set_title('Angle α(t)')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()

# Panel 2 — Phase plane all methods
ax = axes[0, 1]
ax.plot([math.degrees(a) for a in a_e],  w_e,  color=C_E,  lw=2.0, label='Euler')
ax.plot([math.degrees(a) for a in a_mp], w_mp, color=C_MP, lw=2.0, linestyle='--', dashes=(8,4), label='MidPoint')
ax.plot([math.degrees(a) for a in a_rk], w_rk, color=C_RK, lw=2.0, linestyle=':', label='RK4')
ax.set_xlabel('α [deg]'); ax.set_ylabel('ω [rad/s]'); ax.set_title('Phase Plane ω(α)')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()

# Panel 3 — Energy MidPoint
ax = axes[1, 0]
ax.plot(ts_mp, U_mp, color='#E24B4A', lw=2.0, label='U (potential)')
ax.plot(ts_mp, T_mp, color='#F5A623', lw=2.0, label='T (kinetic)')
ax.plot(ts_mp, E_mp, color='gray',    lw=1.5, linestyle='--', label='E (total)')
ax.axhline(E0, color='black', lw=0.8, linestyle=':', alpha=0.6, label=f'E₀={E0:.4f} J')
ax.set_xlabel('t [s]'); ax.set_ylabel('Energy [J]'); ax.set_title('Energy — MidPoint')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()

# Panel 4 — Energy RK4
ax = axes[1, 1]
ax.plot(ts_rk, U_rk, color='#E24B4A', lw=2.0, label='U (potential)')
ax.plot(ts_rk, T_rk, color='#F5A623', lw=2.0, label='T (kinetic)')
ax.plot(ts_rk, E_rk, color='gray',    lw=1.5, linestyle='--', label='E (total)')
ax.axhline(E0, color='black', lw=0.8, linestyle=':', alpha=0.6, label=f'E₀={E0:.4f} J')
ax.set_xlabel('t [s]'); ax.set_ylabel('Energy [J]'); ax.set_title('Energy — RK4')
ax.legend(); ax.grid(True, linestyle=':', linewidth=0.5, color='grey', alpha=0.6); ax.minorticks_on()

plt.tight_layout()
plt.savefig('pendulum.png', dpi=150)
plt.show()
print("Plot saved → pendulum.png")
plt.tight_layout()
plt.savefig('pendulum.png', dpi=150)
plt.show()
print("Plot saved → pendulum.png")
'''

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker

# ── Style ──────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0e1117',
    'axes.facecolor': '#161b22',
    'axes.edgecolor': '#30363d',
    'axes.labelcolor': '#c9d1d9',
    'text.color': '#c9d1d9',
    'xtick.color': '#8b949e',
    'ytick.color': '#8b949e',
    'grid.color': '#21262d',
    'grid.linestyle': '-',
    'grid.linewidth': 0.6,
    'legend.facecolor': '#161b22',
    'legend.edgecolor': '#30363d',
    'legend.labelcolor': '#c9d1d9',
    'font.family': 'monospace',
    'font.size': 10,
})

# ── Constants ──────────────────────────────────────────────────────────────────
g   = 9.81
r   = 1.0
dt  = 0.01
t_end = 10.0

# ── Starting conditions ───────────────────────────────────────────────────────
alpha0 = np.radians(45)
omega0 = 0.0

t = np.arange(0, t_end, dt)

def epsilon(alpha):
    return -(g / r) * np.sin(alpha)

# ── MidPoint Method (Improved Euler) ──────────────────────────────────────────
def midpoint_method(alpha0, omega0):
    alpha_list = [alpha0]
    omega_list = [omega0]
    alpha = alpha0
    omega = omega0
    for _ in t[:-1]:
        eps1 = epsilon(alpha)
        alpha_mid = alpha + omega * (dt / 2)
        omega_mid = omega + eps1 * (dt / 2)
        eps2 = epsilon(alpha_mid)
        alpha = alpha + omega_mid * dt
        omega = omega + eps2  * dt
        alpha_list.append(alpha)
        omega_list.append(omega)
    return np.array(alpha_list), np.array(omega_list)

# ── RK4 Method (Runge-Kutta 4th order) ────────────────────────────────────────
def rk4_method(alpha0, omega0):
    alpha_list = [alpha0]
    omega_list = [omega0]
    alpha = alpha0
    omega = omega0
    for _ in t[:-1]:
        k1_alpha = omega
        k1_omega = epsilon(alpha)
        k2_alpha = omega + k1_omega * (dt / 2)
        k2_omega = epsilon(alpha + k1_alpha * (dt / 2))
        k3_alpha = omega + k2_omega * (dt / 2)
        k3_omega = epsilon(alpha + k2_alpha * (dt / 2))
        k4_alpha = omega + k3_omega * dt
        k4_omega = epsilon(alpha + k3_alpha * dt)
        alpha = alpha + (dt / 6) * (k1_alpha + 2*k2_alpha + 2*k3_alpha + k4_alpha)
        omega = omega + (dt / 6) * (k1_omega + 2*k2_omega + 2*k3_omega + k4_omega)
        alpha_list.append(alpha)
        omega_list.append(omega)
    return np.array(alpha_list), np.array(omega_list)

# ── Energy calculations ───────────────────────────────────────────────────────
def calc_energy(alpha, omega, m=1.0):
    KE = 0.5 * m * (r * omega)**2
    PE = m * g * r * (1 - np.cos(alpha))
    E  = KE + PE
    return KE, PE, E

# ── Run simulations ───────────────────────────────────────────────────────────
alpha_mp, omega_mp = midpoint_method(alpha0, omega0)
alpha_rk, omega_rk = rk4_method(alpha0, omega0)

KE_mp, PE_mp, E_mp = calc_energy(alpha_mp, omega_mp)
KE_rk, PE_rk, E_rk = calc_energy(alpha_rk, omega_rk)

# ── Console output ────────────────────────────────────────────────────────────
print("=" * 45)
print("  Pendulum Simulation")
print("=" * 45)
print(f"  Pendulum length : {r} m")
print(f"  Start angle     : 45 degrees")
print(f"  Duration        : {t_end} s")
print("-" * 45)
print(f"  MidPoint - total energy drift : {abs(E_mp[-1] - E_mp[0]):.6f} J")
print(f"  RK4      - total energy drift : {abs(E_rk[-1] - E_rk[0]):.6f} J")
print("=" * 45)
print("  Lower drift = more accurate method")
print("=" * 45)

# ── Colors ─────────────────────────────────────────────────────────────────────
C_MP   = '#58a6ff'   # blue
C_RK   = '#3fb950'   # green
C_KE   = '#58a6ff'   # kinetic - blue
C_PE   = '#f0883e'   # potential - orange
C_TOT  = '#f85149'   # total - red
C_FILL = 0.08

# ── Helper: style an axis ─────────────────────────────────────────────────────
def style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=12, fontweight='bold', color='white', pad=12)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(True)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax.tick_params(axis='both', which='both', length=4)

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 1 — Angle over Time
# ══════════════════════════════════════════════════════════════════════════════
fig1, ax1 = plt.subplots(figsize=(12, 5))

ax1.plot(t, np.degrees(alpha_mp), color=C_MP, linestyle='--', linewidth=1.8,
         label='MidPoint', alpha=0.9)
ax1.plot(t, np.degrees(alpha_rk), color=C_RK, linestyle='-',  linewidth=1.8,
         label='RK4', alpha=0.9)
ax1.fill_between(t, np.degrees(alpha_mp), alpha=C_FILL, color=C_MP)
ax1.fill_between(t, np.degrees(alpha_rk), alpha=C_FILL, color=C_RK)
ax1.axhline(0, color='#30363d', linewidth=0.8, zorder=0)

style_ax(ax1, 'Pendulum Angle over Time', 'Time (s)', 'Angle (degrees)')
fig1.tight_layout(pad=1.5)
fig1.savefig('pendulum_angle.png', dpi=150, facecolor=fig1.get_facecolor())

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 2 — Energy: MidPoint Method
# ══════════════════════════════════════════════════════════════════════════════
fig2, ax2 = plt.subplots(figsize=(12, 5))

ax2.plot(t, KE_mp, color=C_KE, linewidth=1.8, label='Kinetic',   alpha=0.9)
ax2.plot(t, PE_mp, color=C_PE, linewidth=1.8, label='Potential',  alpha=0.9)
ax2.plot(t, E_mp,  color=C_TOT, linewidth=1.8, linestyle='--', label='Total', alpha=0.9)
ax2.fill_between(t, KE_mp, alpha=C_FILL, color=C_KE)
ax2.fill_between(t, PE_mp, alpha=C_FILL, color=C_PE)

# drift annotation
drift_mp = abs(E_mp[-1] - E_mp[0])
ax2.annotate(f'ΔE = {drift_mp:.6f} J', xy=(0.98, 0.04), xycoords='axes fraction',
             ha='right', fontsize=9, color='#8b949e',
             bbox=dict(boxstyle='round,pad=0.4', fc='#161b22', ec='#30363d', alpha=0.9))

style_ax(ax2, 'Energy — MidPoint Method', 'Time (s)', 'Energy (J)')
fig2.tight_layout(pad=1.5)
fig2.savefig('pendulum_energy_midpoint.png', dpi=150, facecolor=fig2.get_facecolor())

# ══════════════════════════════════════════════════════════════════════════════
# PLOT 3 — Energy: RK4 Method
# ══════════════════════════════════════════════════════════════════════════════
fig3, ax3 = plt.subplots(figsize=(12, 5))

ax3.plot(t, KE_rk, color=C_KE, linewidth=1.8, label='Kinetic',   alpha=0.9)
ax3.plot(t, PE_rk, color=C_PE, linewidth=1.8, label='Potential',  alpha=0.9)
ax3.plot(t, E_rk,  color=C_TOT, linewidth=1.8, linestyle='--', label='Total', alpha=0.9)
ax3.fill_between(t, KE_rk, alpha=C_FILL, color=C_KE)
ax3.fill_between(t, PE_rk, alpha=C_FILL, color=C_PE)

drift_rk = abs(E_rk[-1] - E_rk[0])
ax3.annotate(f'ΔE = {drift_rk:.6f} J', xy=(0.98, 0.04), xycoords='axes fraction',
             ha='right', fontsize=9, color='#8b949e',
             bbox=dict(boxstyle='round,pad=0.4', fc='#161b22', ec='#30363d', alpha=0.9))

style_ax(ax3, 'Energy — RK4 Method', 'Time (s)', 'Energy (J)')
fig3.tight_layout(pad=1.5)
fig3.savefig('pendulum_energy_rk4.png', dpi=150, facecolor=fig3.get_facecolor())

plt.show()
