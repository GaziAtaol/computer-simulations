import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
import matplotlib.pyplot as plt

def create_grid(Lx, Ly, n_intervals):
    N  = n_intervals + 1
    ni = n_intervals - 1
    x = np.linspace(0, Lx, N)
    y = np.linspace(0, Ly, N)
    X, Y = np.meshgrid(x, y, indexing='ij')
    return x, y, X, Y, N, ni

def apply_boundary_conditions(N, T_bottom, T_left, T_top, T_right):
    T_full = np.zeros((N, N))
    T_full[:, 0]   = T_bottom
    T_full[:, -1]  = T_top
    T_full[0, :]   = T_left
    T_full[-1, :]  = T_right
    T_full[0,   0] = 0.5 * (T_left  + T_bottom)
    T_full[-1,  0] = 0.5 * (T_right + T_bottom)
    T_full[0,  -1] = 0.5 * (T_left  + T_top)
    T_full[-1, -1] = 0.5 * (T_right + T_top)
    return T_full

def build_system(N, ni, T_full):
    total = ni * ni

    def idx(i, j):
        return (j - 1) * ni + (i - 1)

    rows, cols, vals = [], [], []
    b = np.zeros(total)

    for j in range(1, ni + 1):
        for i in range(1, ni + 1):
            k = idx(i, j)
            rows.append(k);  cols.append(k);  vals.append(-4.0)

            if i - 1 == 0:
                b[k] -= T_full[0, j]
            else:
                rows.append(k);  cols.append(idx(i-1, j));  vals.append(1.0)

            if i + 1 == N - 1:
                b[k] -= T_full[N-1, j]
            else:
                rows.append(k);  cols.append(idx(i+1, j));  vals.append(1.0)

            if j - 1 == 0:
                b[k] -= T_full[i, 0]
            else:
                rows.append(k);  cols.append(idx(i, j-1));  vals.append(1.0)

            if j + 1 == N - 1:
                b[k] -= T_full[i, N-1]
            else:
                rows.append(k);  cols.append(idx(i, j+1));  vals.append(1.0)

    A = sparse.csr_matrix((vals, (rows, cols)), shape=(total, total))
    return A, b

def solve_system(A, b, T_full, ni):
    t_sol = spsolve(A, b)
    for j in range(1, ni + 1):
        for i in range(1, ni + 1):
            k = (j - 1) * ni + (i - 1)
            T_full[i, j] = t_sol[k]
    return T_full

def plot_2d_color(X, Y, T, ax):
    c = ax.pcolormesh(X, Y, T, shading='gouraud', cmap='jet')
    plt.colorbar(c, ax=ax, label='T [°C]')
    ax.set_xlabel('x [cm]')
    ax.set_ylabel('y [cm]')
    ax.set_title('(a) 2D colour gradient')
    ax.set_aspect('equal')

def plot_2d_contour(X, Y, T, ax):
    levels = np.linspace(T.min(), T.max(), 25)
    cf = ax.contourf(X, Y, T, levels=levels, cmap='jet')
    ax.contour(X, Y, T, levels=levels, colors='k', linewidths=0.3)
    plt.colorbar(cf, ax=ax, label='T [°C]')
    ax.set_xlabel('x [cm]')
    ax.set_ylabel('y [cm]')
    ax.set_title('(b) 2D contour')
    ax.set_aspect('equal')

def plot_3d_surface(X, Y, T, ax):
    ax.plot_surface(X, Y, T, cmap='jet', edgecolor='none', alpha=0.95)
    ax.set_xlabel('x [cm]')
    ax.set_ylabel('y [cm]')
    ax.set_zlabel('T [°C]')
    ax.set_title('(c) 3D surface')

def plot_3d_wireframe(X, Y, T, ax, step=2):
    ax.plot_wireframe(X[::step, ::step],
                      Y[::step, ::step],
                      T[::step, ::step],
                      color='tab:blue', linewidth=0.4)
    ax.set_xlabel('x [cm]')
    ax.set_ylabel('y [cm]')
    ax.set_zlabel('T [°C]')
    ax.set_title('(d) 3D wireframe')

def create_figure(X, Y, T, info_text, save_path):
    fig = plt.figure(figsize=(16, 14))
    fig.suptitle('Steady State Temperature Distribution\n' + info_text,
                 fontsize=14, fontweight='bold')

    ax1 = fig.add_subplot(2, 2, 1)
    plot_2d_color(X, Y, T, ax1)

    ax2 = fig.add_subplot(2, 2, 2)
    plot_2d_contour(X, Y, T, ax2)

    ax3 = fig.add_subplot(2, 2, 3, projection='3d')
    plot_3d_surface(X, Y, T, ax3)

    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    plot_3d_wireframe(X, Y, T, ax4)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.show()
    print(f"Figure saved to: {save_path}")

def print_summary(N, ni, A, T_full, bc):
    print("\n===== SUMMARY =====")
    print(f"Grid size         : {N} x {N}  ({N*N} total nodes)")
    print(f"Interior unknowns : {ni} x {ni} = {ni*ni}")
    print(f"Matrix A size     : {ni*ni} x {ni*ni}")
    print(f"Non zero entries  : {A.nnz}")
    print(f"T_min = {T_full.min():.2f} C    T_max = {T_full.max():.2f} C")
    print(f"\nBoundary conditions:")
    print(f"  Bottom (j=0)    : {bc['bottom']} C")
    print(f"  Left   (i=0)    : {bc['left']} C")
    print(f"  Top    (j=N-1)  : {bc['top']} C")
    print(f"  Right  (i=N-1)  : {bc['right']} C")

def main():
    Lx, Ly       = 15.0, 15.0
    n_intervals  = 41
    T_bottom     = 150.0
    T_left       = 100.0
    T_top        = 200.0
    T_right      =  50.0

    x, y, X, Y, N, ni = create_grid(Lx, Ly, n_intervals)
    T_full = apply_boundary_conditions(N, T_bottom, T_left, T_top, T_right)
    A, b = build_system(N, ni, T_full)
    T_full = solve_system(A, b, T_full, ni)

    info = (f'Square plate {Lx:.0f}x{Ly:.0f} cm,   '
            f'grid {N}x{N},   unknowns {ni}x{ni} = {ni*ni}')
    create_figure(X, Y, T_full, info, 'task7_temperature.png')

    bc = dict(bottom=T_bottom, left=T_left, top=T_top, right=T_right)
    print_summary(N, ni, A, T_full, bc)

if __name__ == '__main__':
    main()