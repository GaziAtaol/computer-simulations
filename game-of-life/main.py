import tkinter as tk
import random
# --- Config ---
ROWS = 40
COLS = 60
CELL_SIZE = 14

COLORS = {
    "bg": "#0a0a0f",
    "grid_line": "#151520",
    "cell_alive": "#00ffc8",
    "panel_bg": "#0d0d15",
    "text": "#c8ccd4",
    "accent": "#00ffc8",
    "accent2": "#ff6b9d",
    "accent3": "#ffd93d",
    "dim": "#555555",
    "btn_bg": "#15152a",
}

PRESETS = {
    "Glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "Blinker": [(1, 0), (1, 1), (1, 2)],
    "Toad": [(1, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 2)],
    "Beacon": [(0, 0), (0, 1), (1, 0), (1, 1), (2, 2), (2, 3), (3, 2), (3, 3)],
    "Pulsar": [
        (2, 4), (2, 5), (2, 6), (2, 10), (2, 11), (2, 12),
        (4, 2), (5, 2), (6, 2), (4, 7), (5, 7), (6, 7),
        (4, 9), (5, 9), (6, 9), (4, 14), (5, 14), (6, 14),
        (7, 4), (7, 5), (7, 6), (7, 10), (7, 11), (7, 12),
        (9, 4), (9, 5), (9, 6), (9, 10), (9, 11), (9, 12),
        (10, 2), (11, 2), (12, 2), (10, 7), (11, 7), (12, 7),
        (10, 9), (11, 9), (12, 9), (10, 14), (11, 14), (12, 14),
        (14, 4), (14, 5), (14, 6), (14, 10), (14, 11), (14, 12),
    ],
    "Gosper Gun": [
        (5, 1), (5, 2), (6, 1), (6, 2),
        (3, 13), (3, 14), (4, 12), (4, 16), (5, 11), (5, 17),
        (6, 11), (6, 15), (6, 17), (6, 18), (7, 11), (7, 17),
        (8, 12), (8, 16), (9, 13), (9, 14),
        (1, 25), (2, 23), (2, 25), (3, 21), (3, 22), (4, 21),
        (4, 22), (5, 21), (5, 22), (6, 23), (6, 25), (7, 25),
        (3, 35), (3, 36), (4, 35), (4, 36),
    ],
}

RULE_PRESETS = [
    ("Classic", "23", "3"),
    ("HighLife", "23", "36"),
    ("Seeds", "", "2"),
    ("Day&Night", "34678", "3678"),
    ("Diamoeba", "5678", "35678"),
    ("Replicator", "1357", "1357"),
]

class GameOfLife:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Game of Life")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.rows = ROWS
        self.cols = COLS
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.running = False
        self.generation = 0
        self.speed = 100
        self.survive_rule = {2, 3}
        self.birth_rule = {3}
        self.painting = False
        self.paint_mode = 1
        self.after_id = None

        self._build_ui()
        self._update_stats()

    def _build_ui(self):
        # --- Title ---
        tf = tk.Frame(self.root, bg=COLORS["bg"])
        tf.pack(pady=(10, 2))
        tk.Label(tf, text="GAME OF LIFE", font=("Consolas", 18, "bold"),
                 fg=COLORS["accent"], bg=COLORS["bg"]).pack()
        tk.Label(tf, text="CYCLIC BOUNDARY  |  CUSTOM RULES",
                 font=("Consolas", 9), fg=COLORS["dim"], bg=COLORS["bg"]).pack()

        # --- Stats ---
        sf = tk.Frame(self.root, bg=COLORS["bg"])
        sf.pack(pady=4)
        self.lbl_gen = tk.Label(sf, text="GEN: 0", font=("Consolas", 10, "bold"),
                                fg=COLORS["accent"], bg=COLORS["bg"])
        self.lbl_gen.pack(side=tk.LEFT, padx=14)
        self.lbl_pop = tk.Label(sf, text="POP: 0", font=("Consolas", 10, "bold"),
                                fg=COLORS["accent2"], bg=COLORS["bg"])
        self.lbl_pop.pack(side=tk.LEFT, padx=14)
        self.lbl_speed_val = tk.Label(sf, text="SPEED: 100ms", font=("Consolas", 10, "bold"),
                                      fg=COLORS["accent3"], bg=COLORS["bg"])
        self.lbl_speed_val.pack(side=tk.LEFT, padx=14)
        self.lbl_status = tk.Label(sf, text="PAUSED", font=("Consolas", 10, "bold"),
                                   fg="#ff4444", bg=COLORS["bg"])
        self.lbl_status.pack(side=tk.LEFT, padx=14)

        # --- Canvas ---
        cw = self.cols * CELL_SIZE
        ch = self.rows * CELL_SIZE
        cf = tk.Frame(self.root, bg="#1a1a2e", padx=1, pady=1)
        cf.pack(pady=(2, 6))
        self.canvas = tk.Canvas(cf, width=cw, height=ch,
                                bg=COLORS["panel_bg"], highlightthickness=0,
                                cursor="crosshair")
        self.canvas.pack()

        # Pre-create all cell rectangles
        self.cell_rects = []
        for r in range(self.rows):
            row_rects = []
            for c in range(self.cols):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                rid = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=COLORS["panel_bg"],
                    outline=COLORS["grid_line"],
                    width=1
                )
                row_rects.append(rid)
            self.cell_rects.append(row_rects)

        # Mouse bindings
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # --- Control Buttons ---
        bf = tk.Frame(self.root, bg=COLORS["bg"])
        bf.pack(pady=4)
        btn_kw = dict(font=("Consolas", 10), bg=COLORS["btn_bg"],
                      activebackground="#1e1e3a", bd=0, relief="flat",
                      cursor="hand2", padx=12, pady=5)

        self.btn_play = tk.Button(bf, text="PLAY", fg=COLORS["accent"],
                                  activeforeground=COLORS["accent"],
                                  command=self._toggle_run, **btn_kw)
        self.btn_play.pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text="STEP", fg=COLORS["text"],
                  activeforeground=COLORS["text"],
                  command=self._step, **btn_kw).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text="CLEAR", fg=COLORS["text"],
                  activeforeground=COLORS["text"],
                  command=self._clear, **btn_kw).pack(side=tk.LEFT, padx=3)
        tk.Button(bf, text="RANDOM", fg=COLORS["text"],
                  activeforeground=COLORS["text"],
                  command=self._randomize, **btn_kw).pack(side=tk.LEFT, padx=3)

        # --- Speed Slider ---
        spf = tk.Frame(self.root, bg=COLORS["bg"])
        spf.pack(pady=2)
        tk.Label(spf, text="FAST", font=("Consolas", 8), fg=COLORS["dim"],
                 bg=COLORS["bg"]).pack(side=tk.LEFT, padx=(0, 4))
        self.speed_scale = tk.Scale(
            spf, from_=20, to=500, orient=tk.HORIZONTAL,
            length=220, showvalue=False,
            bg=COLORS["bg"], fg=COLORS["accent"],
            troughcolor=COLORS["btn_bg"], highlightthickness=0,
            bd=0, sliderrelief="flat",
            command=self._on_speed_change
        )
        self.speed_scale.set(self.speed)
        self.speed_scale.pack(side=tk.LEFT)
        tk.Label(spf, text="SLOW", font=("Consolas", 8), fg=COLORS["dim"],
                 bg=COLORS["bg"]).pack(side=tk.LEFT, padx=(4, 0))

        # --- Pattern Presets ---
        pf = tk.Frame(self.root, bg=COLORS["bg"])
        pf.pack(pady=4)
        tk.Label(pf, text="PATTERNS:", font=("Consolas", 9),
                 fg=COLORS["dim"], bg=COLORS["bg"]).pack(side=tk.LEFT, padx=(0, 6))
        for name in PRESETS:
            tk.Button(pf, text=name, font=("Consolas", 9),
                      bg=COLORS["btn_bg"], fg=COLORS["accent2"],
                      activebackground="#1e1e3a", activeforeground=COLORS["accent2"],
                      bd=0, relief="flat", cursor="hand2", padx=6, pady=2,
                      command=lambda n=name: self._load_preset(n)
                      ).pack(side=tk.LEFT, padx=2)

        # --- Rules Panel ---
        ro = tk.Frame(self.root, bg=COLORS["accent3"], padx=1, pady=1)
        ro.pack(pady=6, padx=20, fill=tk.X)
        rf = tk.Frame(ro, bg="#111118", padx=12, pady=8)
        rf.pack(fill=tk.BOTH)

        tk.Label(rf, text="RULES (change anytime)", font=("Consolas", 10, "bold"),
                 fg=COLORS["accent3"], bg="#111118").pack(anchor="w")

        entry_row = tk.Frame(rf, bg="#111118")
        entry_row.pack(anchor="w", pady=(6, 0))

        tk.Label(entry_row, text="Survive:", font=("Consolas", 10),
                 fg=COLORS["text"], bg="#111118").pack(side=tk.LEFT, padx=(0, 4))
        self.survive_entry = tk.Entry(entry_row, width=10, font=("Consolas", 12),
                                      bg=COLORS["panel_bg"], fg=COLORS["accent3"],
                                      insertbackground=COLORS["accent3"],
                                      bd=1, relief="solid", justify="center")
        self.survive_entry.insert(0, "23")
        self.survive_entry.pack(side=tk.LEFT, padx=(0, 20))
        self.survive_entry.bind("<KeyRelease>", self._on_rules_change)

        tk.Label(entry_row, text="Birth:", font=("Consolas", 10),
                 fg=COLORS["text"], bg="#111118").pack(side=tk.LEFT, padx=(0, 4))
        self.birth_entry = tk.Entry(entry_row, width=10, font=("Consolas", 12),
                                    bg=COLORS["panel_bg"], fg=COLORS["accent3"],
                                    insertbackground=COLORS["accent3"],
                                    bd=1, relief="solid", justify="center")
        self.birth_entry.insert(0, "3")
        self.birth_entry.pack(side=tk.LEFT)
        self.birth_entry.bind("<KeyRelease>", self._on_rules_change)

        self.lbl_rule = tk.Label(rf, text="B3/S23", font=("Consolas", 9),
                                 fg=COLORS["dim"], bg="#111118")
        self.lbl_rule.pack(anchor="w", pady=(4, 4))

        # Quick rule buttons
        qf = tk.Frame(rf, bg="#111118")
        qf.pack(anchor="w")
        tk.Label(qf, text="QUICK:", font=("Consolas", 8),
                 fg=COLORS["dim"], bg="#111118").pack(side=tk.LEFT, padx=(0, 6))
        for label, s, b in RULE_PRESETS:
            tk.Button(qf, text=label, font=("Consolas", 8),
                      bg=COLORS["btn_bg"], fg=COLORS["accent3"],
                      activebackground="#1e1e3a", activeforeground=COLORS["accent3"],
                      bd=0, relief="flat", cursor="hand2", padx=5, pady=1,
                      command=lambda ss=s, bb=b: self._set_rules(ss, bb)
                      ).pack(side=tk.LEFT, padx=2)

        # Footer
        tk.Label(self.root,
                 text="Click/drag to draw  |  Edges wrap around (cyclic)  |  Rules apply in real-time",
                 font=("Consolas", 8), fg="#333333", bg=COLORS["bg"]).pack(pady=(2, 8))

    # ══════════════════════════════════════
    #  GAME LOGIC
    # ══════════════════════════════════════
    def _count_neighbors(self, r, c):
        total = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                total += self.grid[nr][nc]
        return total

    def _next_generation(self):
        new = [[0] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                n = self._count_neighbors(r, c)
                if self.grid[r][c] == 1:
                    new[r][c] = 1 if n in self.survive_rule else 0
                else:
                    new[r][c] = 1 if n in self.birth_rule else 0
        self.grid = new
        self.generation += 1

    # ══════════════════════════════════════
    #  DRAWING
    # ══════════════════════════════════════
    def _update_cell(self, r, c):
        fill = COLORS["cell_alive"] if self.grid[r][c] else COLORS["panel_bg"]
        self.canvas.itemconfig(self.cell_rects[r][c], fill=fill)

    def _redraw_all(self):
        for r in range(self.rows):
            for c in range(self.cols):
                fill = COLORS["cell_alive"] if self.grid[r][c] else COLORS["panel_bg"]
                self.canvas.itemconfig(self.cell_rects[r][c], fill=fill)
        self._update_stats()

    def _update_stats(self):
        pop = sum(self.grid[r][c] for r in range(self.rows) for c in range(self.cols))
        self.lbl_gen.config(text=f"GEN: {self.generation}")
        self.lbl_pop.config(text=f"POP: {pop}")

    # ══════════════════════════════════════
    #  MOUSE EVENTS
    # ══════════════════════════════════════
    def _pos_to_cell(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None, None

    def _on_press(self, event):
        r, c = self._pos_to_cell(event)
        if r is None:
            return
        self.painting = True
        self.paint_mode = 0 if self.grid[r][c] == 1 else 1
        self.grid[r][c] = self.paint_mode
        self._update_cell(r, c)
        self._update_stats()

    def _on_drag(self, event):
        if not self.painting:
            return
        r, c = self._pos_to_cell(event)
        if r is None:
            return
        if self.grid[r][c] != self.paint_mode:
            self.grid[r][c] = self.paint_mode
            self._update_cell(r, c)
            self._update_stats()

    def _on_release(self, _event):
        self.painting = False

    # ══════════════════════════════════════
    #  CONTROLS
    # ══════════════════════════════════════
    def _toggle_run(self):
        if self.running:
            self.running = False
            self.btn_play.config(text="PLAY")
            self.lbl_status.config(text="PAUSED", fg="#ff4444")
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None
        else:
            self.running = True
            self.btn_play.config(text="PAUSE")
            self.lbl_status.config(text="RUNNING", fg=COLORS["accent"])
            self._run_loop()

    def _run_loop(self):
        if not self.running:
            return
        self._next_generation()
        self._redraw_all()
        self.after_id = self.root.after(self.speed, self._run_loop)

    def _step(self):
        self._next_generation()
        self._redraw_all()

    def _clear(self):
        self.running = False
        self.btn_play.config(text="PLAY")
        self.lbl_status.config(text="PAUSED", fg="#ff4444")
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.generation = 0
        self._redraw_all()

    def _randomize(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if random.random() > 0.7 else 0
        self.generation = 0
        self._redraw_all()

    def _on_speed_change(self, val):
        self.speed = int(val)
        self.lbl_speed_val.config(text=f"SPEED: {self.speed}ms")

    def _load_preset(self, name):
        self._clear()
        off_r = self.rows // 2 - 5
        off_c = self.cols // 2 - 5
        for r, c in PRESETS[name]:
            nr = (r + off_r) % self.rows
            nc = (c + off_c) % self.cols
            self.grid[nr][nc] = 1
        self._redraw_all()

    # ══════════════════════════════════════
    #  RULES
    # ══════════════════════════════════════
    def _parse_rule(self, text):
        return {int(ch) for ch in text if ch.isdigit() and 0 <= int(ch) <= 8}

    def _on_rules_change(self, _event=None):
        s_text = self.survive_entry.get()
        b_text = self.birth_entry.get()
        self.survive_rule = self._parse_rule(s_text)
        self.birth_rule = self._parse_rule(b_text)
        self.lbl_rule.config(text=f"B{b_text}/S{s_text}")

    def _set_rules(self, s, b):
        self.survive_entry.delete(0, tk.END)
        self.survive_entry.insert(0, s)
        self.birth_entry.delete(0, tk.END)
        self.birth_entry.insert(0, b)
        self._on_rules_change()


# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLife(root)
    root.mainloop()