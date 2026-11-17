"""Pythagoras Calculator - a small, friendly right-triangle solver.

Enter any two sides of a right triangle, leave the third empty, and the app
solves it with a^2 + b^2 = c^2, shows the working and draws the triangle.

Pure standard library (tkinter); packaged as a Windows executable.
"""

from __future__ import annotations

import math
import os
import sys
import tkinter as tk

APP_NAME = "Pythagoras Calculator"

# Palette
BG = "#0F172A"
CARD = "#16233A"
CARD_DARK = "#0B1220"
BORDER = "#2B3B55"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
ACCENT = "#38BDF8"
ACCENT_SOFT = "#93C5FD"
GOOD = "#4ADE80"
BAD = "#F87171"
ENTRY_BG = "#0B1220"


class SolveError(Exception):
    """A user-facing input problem."""


def fmt(x: float) -> str:
    """Compact, human-friendly number: no trailing zeros, no float noise."""
    if not math.isfinite(x):
        return str(x)
    if abs(x) < 1e15 and abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    if abs(x) >= 1e7 or (0 < abs(x) < 1e-4):
        return f"{x:.6g}"
    return f"{x:.6f}".rstrip("0").rstrip(".")


def is_whole(x: float) -> bool:
    return abs(x - round(x)) < 1e-9


def parse_side(raw: str, name: str) -> float | None:
    text = raw.strip().replace(" ", "")
    if not text:
        return None
    if "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        raise SolveError(f"“{raw.strip()}” isn’t a number — use digits like 3 or 4.5.") from None
    if not math.isfinite(value):
        raise SolveError(f"Please enter a normal, finite value for {name}.")
    if value <= 0:
        raise SolveError(f"Side {name} must be greater than zero.")
    return value


def solve_triangle(a_raw: str, b_raw: str, c_raw: str) -> dict:
    """Work out the missing side (or check a complete triangle).

    Returns a dict with the three sides, a headline, working lines, and which
    side was solved. Raises SolveError for anything the user needs to fix.
    """
    a = parse_side(a_raw, "a")
    b = parse_side(b_raw, "b")
    c = parse_side(c_raw, "c")

    filled = sum(v is not None for v in (a, b, c))
    if filled < 2:
        raise SolveError("Enter any two sides — the third one will be solved.")
    if filled == 3:
        # All three given: check the triangle instead of solving.
        left = a * a + b * b
        right = c * c
        tolerance = 1e-6 * max(1.0, right)
        if abs(left - right) > tolerance:
            diff = abs(left - right)
            raise SolveError(
                "Those three sides don’t form a right triangle "
                f"(a² + b² is off by {fmt(diff)}). Leave one field empty to solve for it."
            )
        steps = (
            f"a² + b² = {fmt(a)}² + {fmt(b)}² = {fmt(a * a)} + {fmt(b * b)} = {fmt(left)}\n"
            f"c² = {fmt(c)}² = {fmt(right)}\n"
            "The two sides match, so this is a right triangle."
        )
        angle_a = math.degrees(math.atan2(a, b))
        steps += f"\n∠A = {angle_a:.2f}°,  ∠B = {90 - angle_a:.2f}°"
        return {
            "a": a, "b": b, "c": c,
            "target": None,
            "headline": "✔ Right triangle",
            "steps": steps,
        }

    if a is None:
        assert b is not None and c is not None
        if c <= b:
            raise SolveError("The hypotenuse (c) must be longer than the other leg (b).")
        value = math.sqrt(c * c - b * b)
        a = value
        steps = (
            "a² = c² − b²\n"
            f"a² = {fmt(c)}² − {fmt(b)}² = {fmt(c * c)} − {fmt(b * b)} = {fmt(c * c - b * b)}\n"
            f"a = √{fmt(c * c - b * b)} {'=' if is_whole(value) else '≈'} {fmt(value)}"
        )
        target = "a"
        symbol = "=" if is_whole(value) else "≈"
        headline = f"a {symbol} {fmt(value)}"
    elif b is None:
        assert a is not None and c is not None
        if c <= a:
            raise SolveError("The hypotenuse (c) must be longer than the other leg (a).")
        value = math.sqrt(c * c - a * a)
        b = value
        steps = (
            "b² = c² − a²\n"
            f"b² = {fmt(c)}² − {fmt(a)}² = {fmt(c * c)} − {fmt(a * a)} = {fmt(c * c - a * a)}\n"
            f"b = √{fmt(c * c - a * a)} {'=' if is_whole(value) else '≈'} {fmt(value)}"
        )
        target = "b"
        symbol = "=" if is_whole(value) else "≈"
        headline = f"b {symbol} {fmt(value)}"
    else:
        assert a is not None and b is not None
        value = math.sqrt(a * a + b * b)
        c = value
        steps = (
            "c² = a² + b²\n"
            f"c² = {fmt(a)}² + {fmt(b)}² = {fmt(a * a)} + {fmt(b * b)} = {fmt(a * a + b * b)}\n"
            f"c = √{fmt(a * a + b * b)} {'=' if is_whole(value) else '≈'} {fmt(value)}"
        )
        target = "c"
        symbol = "=" if is_whole(value) else "≈"
        headline = f"c {symbol} {fmt(value)}"

    angle_a = math.degrees(math.atan2(a, b))
    steps += f"\n∠A = {angle_a:.2f}°,  ∠B = {90 - angle_a:.2f}°"

    return {"a": a, "b": b, "c": c, "target": target, "headline": headline, "steps": steps}


def resource_path(relative: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


class PythagorasApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title(APP_NAME)
        root.configure(bg=BG)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        width = min(580, screen_w - 40)
        height = min(860, screen_h - 90)
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2 - 20)
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.minsize(500, 660)

        try:
            root.iconbitmap(resource_path(os.path.join("assets", "pythagoras.ico")))
        except Exception:
            pass

        self.a_var = tk.StringVar()
        self.b_var = tk.StringVar()
        self.c_var = tk.StringVar()
        self.sides: tuple[float, float, float] | None = None  # None = placeholder
        self.copy_text = ""
        self._entries: list[tk.Entry] = []

        self._build()

        root.bind("<Return>", self.solve)
        root.bind("<KP_Enter>", self.solve)
        root.bind("<Escape>", lambda _e: self.clear())
        self.reset_view()

    # ------------------------------------------------------------------ UI ---
    def _build(self) -> None:
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=22, pady=14)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=2, minsize=110)  # triangle
        outer.rowconfigure(5, weight=1, minsize=70)   # working

        # Header
        header = tk.Frame(outer, bg=BG)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            header, text=APP_NAME, bg=BG, fg=TEXT,
            font=("Segoe UI", 20, "bold"), anchor="w",
        ).pack(fill="x")
        tk.Label(
            header, text="a² + b² = c²   ·   solve any side of a right triangle",
            bg=BG, fg=MUTED, font=("Segoe UI", 10), anchor="w",
        ).pack(fill="x", pady=(2, 0))

        # Triangle drawing card
        draw_card = tk.Frame(
            outer, bg=CARD, highlightbackground=BORDER, highlightthickness=1,
        )
        draw_card.grid(row=1, column=0, sticky="nsew")
        self.canvas = tk.Canvas(
            draw_card, bg=CARD, height=1, highlightthickness=0, bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _e: self.redraw())

        # Inputs card
        inputs = tk.Frame(
            outer, bg=CARD, highlightbackground=BORDER, highlightthickness=1,
            padx=18, pady=8,
        )
        inputs.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self._side_row(inputs, "a", "leg", self.a_var)
        self._side_row(inputs, "b", "leg", self.b_var)
        self._side_row(inputs, "c", "hypotenuse", self.c_var)

        # Buttons
        buttons = tk.Frame(outer, bg=BG)
        buttons.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        self.solve_btn = self._button(
            buttons, "Solve", self.solve, primary=True,
        )
        self.solve_btn.pack(side="left", fill="x", expand=True, ipady=5)

        self.copy_btn = self._button(
            buttons, "Copy result", self.copy_result, primary=False,
        )
        self.copy_btn.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=5)

        self.clear_btn = self._button(
            buttons, "Clear", self.clear, primary=False,
        )
        self.clear_btn.pack(side="left", fill="x", expand=True, padx=(8, 0), ipady=5)

        # Result card
        result_card = tk.Frame(
            outer, bg=CARD_DARK, highlightbackground=BORDER, highlightthickness=1,
            padx=16, pady=6,
        )
        result_card.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        tk.Label(
            result_card, text="RESULT", bg=CARD_DARK, fg=MUTED,
            font=("Segoe UI", 8, "bold"), anchor="w",
        ).pack(fill="x")
        self.result_lbl = tk.Label(
            result_card, text="—", bg=CARD_DARK, fg=ACCENT,
            font=("Segoe UI", 20, "bold"), anchor="w",
        )
        self.result_lbl.pack(fill="x", pady=(1, 0))

        # Working / steps
        steps_card = tk.Frame(
            outer, bg=CARD_DARK, highlightbackground=BORDER, highlightthickness=1,
            padx=16, pady=8,
        )
        steps_card.grid(row=5, column=0, sticky="nsew", pady=(8, 0))
        self.steps_lbl = tk.Label(
            steps_card, text="", bg=CARD_DARK, fg="#CBD5E1",
            font=("Consolas", 10), justify="left", anchor="nw",
            wraplength=470,
        )
        self.steps_lbl.pack(fill="both", expand=True)
        self.steps_lbl.bind("<Configure>", self._wrap_steps)

        # Status line and tip
        self.status_lbl = tk.Label(
            outer, text="", bg=BG, fg=MUTED, font=("Segoe UI", 9), anchor="w",
        )
        self.status_lbl.grid(row=6, column=0, sticky="ew", pady=(6, 0))

        tk.Label(
            outer, text="Tip: press Enter to solve · Esc to clear",
            bg=BG, fg="#64748B", font=("Segoe UI", 8), anchor="w",
        ).grid(row=7, column=0, sticky="ew", pady=(2, 0))

    def _side_row(self, parent: tk.Frame, name: str, note: str,
                  var: tk.StringVar) -> None:
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=1)
        row.columnconfigure(1, weight=1)

        tk.Label(
            row, text=name, bg=CARD,
            fg=ACCENT if name != "c" else ACCENT_SOFT,
            font=("Segoe UI", 15, "bold"), width=2, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        box = tk.Frame(
            row, bg=ENTRY_BG, highlightthickness=1, highlightbackground=BORDER,
        )
        box.grid(row=0, column=1, sticky="ew", padx=(6, 12))

        entry = tk.Entry(
            box, textvariable=var, bg=ENTRY_BG, fg=TEXT,
            insertbackground=ACCENT, justify="right",
            font=("Segoe UI", 14), relief="flat", bd=0,
            highlightthickness=0,
        )
        entry.pack(fill="x", padx=10, pady=5)
        entry.bind(
            "<FocusIn>", lambda _e, b=box: b.configure(highlightbackground=ACCENT)
        )
        entry.bind(
            "<FocusOut>", lambda _e, b=box: b.configure(highlightbackground=BORDER)
        )
        self._entries.append(entry)

        tk.Label(
            row, text=note, bg=CARD, fg=MUTED,
            font=("Segoe UI", 9), width=11, anchor="w",
        ).grid(row=0, column=2, sticky="w")

    def _button(self, parent: tk.Frame, text: str, command, *, primary: bool) -> tk.Button:
        bg = ACCENT if primary else CARD
        fg = "#0B1220" if primary else TEXT
        active_bg = "#7DD3FC" if primary else "#233452"
        btn = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            activebackground=active_bg, activeforeground=fg,
            font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
            cursor="hand2", highlightthickness=1,
            highlightbackground=ACCENT if primary else BORDER,
            highlightcolor=ACCENT,
        )
        btn.bind("<Enter>", lambda _e: btn.configure(bg=active_bg))
        btn.bind("<Leave>", lambda _e: btn.configure(bg=bg))
        return btn

    def _wrap_steps(self, event) -> None:
        self.steps_lbl.configure(wraplength=max(200, event.width - 8))

    # --------------------------------------------------------------- solve ---
    def solve(self, _event=None) -> None:
        try:
            data = solve_triangle(self.a_var.get(), self.b_var.get(), self.c_var.get())
        except SolveError as exc:
            self._status(str(exc), BAD)
            return

        # Put the computed (or normalised) sides into the fields.
        self.a_var.set(fmt(data["a"]))
        self.b_var.set(fmt(data["b"]))
        self.c_var.set(fmt(data["c"]))

        self.sides = (data["a"], data["b"], data["c"])
        self.redraw()

        self.result_lbl.configure(text=data["headline"], fg=ACCENT if data["target"] else GOOD)
        self.steps_lbl.configure(text=data["steps"])
        self.copy_text = data["headline"] + "\n\n" + data["steps"]

        if data["target"]:
            self._status(f"Solved for {data['target']}. Change any value and solve again.", GOOD)
            self._entries[{"a": 0, "b": 1, "c": 2}[data["target"]]].focus_set()
        else:
            self._status("Checked: a² + b² = c² holds exactly for these sides.", GOOD)

    def copy_result(self) -> None:
        if not self.copy_text:
            self._status("Solve something first, then copy the result.", BAD)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.copy_text)
        self._status("Result and working copied to the clipboard.", GOOD)

    def clear(self) -> None:
        for var in (self.a_var, self.b_var, self.c_var):
            var.set("")
        self.reset_view()
        self._entries[0].focus_set()

    def reset_view(self) -> None:
        self.sides = None
        self.copy_text = ""
        self.result_lbl.configure(text="—", fg=ACCENT)
        self.steps_lbl.configure(
            text="Enter any two sides, leave the third empty,\n"
                 "then press Solve (or Enter)."
        )
        self._status("Ready — two sides in, third side out.", MUTED)
        self.redraw()

    def _status(self, message: str, color: str) -> None:
        self.status_lbl.configure(text=message, fg=color)

    # ------------------------------------------------------------- drawing ---
    def redraw(self) -> None:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1 or height <= 1:
            width, height = 500, 236

        a, b, c = self.sides if self.sides else (3.0, 4.0, 5.0)
        has_values = self.sides is not None
        cv = self.canvas
        cv.delete("all")

        pad_left = min(62, width * 0.12)
        pad_right = min(68, width * 0.13)
        pad_top = min(38, max(24, height * 0.18))
        pad_bottom = min(52, max(36, height * 0.24))
        avail_w = max(40, width - pad_left - pad_right)
        avail_h = max(40, height - pad_top - pad_bottom)

        # Fit the (a vertical, b horizontal) triangle inside the drawing area.
        bw = avail_w
        ah = bw * (a / b)
        if ah > avail_h:
            ah = avail_h
            bw = ah * (b / a)

        cx = pad_left + (avail_w - bw) / 2
        cy = pad_top + (avail_h - ah) / 2 + ah
        ax, ay = cx, cy - ah
        bx, by = cx + bw, cy

        # Filled triangle + outline
        cv.create_polygon(
            cx, cy, ax, ay, bx, by,
            fill="#132238", outline=ACCENT, width=2, joinstyle="round",
        )

        # Right-angle marker
        mark = max(9, min(16, bw * 0.16, ah * 0.16))
        cv.create_line(
            cx, cy - mark, cx + mark, cy - mark, cx + mark, cy,
            fill=MUTED, width=2,
        )

        # Side labels
        cv.create_text(
            cx - 14, cy - ah / 2,
            text=f"a = {fmt(a)}" if has_values else "a", anchor="e",
            fill=ACCENT_SOFT, font=("Segoe UI", 12, "bold"),
        )
        cv.create_text(
            cx + bw / 2, cy + 15,
            text=f"b = {fmt(b)}" if has_values else "b", anchor="n",
            fill=ACCENT_SOFT, font=("Segoe UI", 12, "bold"),
        )

        length = math.hypot(bw, ah) or 1.0
        nx, ny = ah / length, -bw / length  # outward from the right angle
        mx, my = cx + bw / 2, cy - ah / 2
        cv.create_text(
            mx + nx * 22, my + ny * 22,
            text=f"c = {fmt(c)}" if has_values else "c", anchor="center",
            fill=ACCENT, font=("Segoe UI", 12, "bold"),
        )

        # Vertex letters (A opposite a at bottom-right, B opposite b at top)
        cv.create_text(
            ax - 6, ay - 6, text="B", anchor="se",
            fill="#64748B", font=("Segoe UI", 9, "bold"),
        )
        cv.create_text(
            bx + 6, by + 4, text="A", anchor="nw",
            fill="#64748B", font=("Segoe UI", 9, "bold"),
        )

        # Small angle readout near A and B (once there are real values)
        if has_values:
            angle_a = math.degrees(math.atan2(a, b))
            cv.create_text(
                width - 16, 16,
                text=f"∠A {angle_a:.1f}°   ∠B {90 - angle_a:.1f}°",
                anchor="ne", fill="#64748B", font=("Segoe UI", 9),
            )


def main() -> None:
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72.0)
    except Exception:
        pass
    PythagorasApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
