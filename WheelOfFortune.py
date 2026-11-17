# Connected Discord-GitHub
# Wheel of Fortune - spinnable weighted wheel with presets
import math
import random
import tkinter as tk
from tkinter import ttk, messagebox

COLORS = ["#e6194b", "#d89633", "#ffe119", "#43d843", "#1b05e7", "#911eb4"] # Color presets in hash

# Weighted presets
PRESETS = {
    "Who Lives": [("RazerStar", 100), ("Idklae", 100), ("Spendely", 100),("Claude", 100), ("Emibe", 100), ("Bladian", 100),("zynvol", 1),("newyorkpilot",5),("Roch",30),("Everyone but Roch", 200),("nyxaric against his will",40)],
    "Likelihood of me getting accepted": [("Yes", 1)],
    "Should I play one more game": [("Yes", 90), ("No", 10)],
}

SIZE = 420 # Canvas width/height in pixels
CX = CY = SIZE // 2 # Center of the wheel
R = SIZE // 2 - 20 # Wheel radius, with room for the pointer


class WheelApp(tk.Tk):
    def __init__(self):
        super().__init__()# On init, init with self enabled
         # Vars
        self.title("Wheel of Fortune")
        self.resizable(False, False)
        self.entries = [] # List of (answer, points)
        self.rotation = 0.0 # Current wheel angle in degrees
        self.spinning = False # Blocks double spins


        # Wheel section
        left = tk.Frame(self) # Pre determine values of frame based off self
        left.pack(side="left", padx=10, pady=10)
        self.title_var = tk.StringVar() # Holds the wheel title text
        tk.Entry(left, textvariable=self.title_var, font=("Segoe UI", 16, "bold"),
                 justify="center", relief="flat").pack(fill="x") # Editable title box
        self.canvas = tk.Canvas(left, width=SIZE, height=SIZE, highlightthickness=0) # Wheel drawing area
        self.canvas.pack()
        self.spin_btn = tk.Button(left, text="SPIN", font=("Segoe UI", 14, "bold"),
                                  width=12, command=self.spin)
        self.spin_btn.pack(pady=6)
        self.result_var = tk.StringVar(value="Press SPIN!") # Shows the chosen answer
        tk.Label(left, textvariable=self.result_var, font=("Segoe UI", 14)).pack()

        #presets + entries
        right = tk.Frame(self)
        right.pack(side="left", fill="y", padx=10, pady=10)
        tk.Label(right, text="Preset:").pack(anchor="w")
        self.preset_box = ttk.Combobox(right, values=list(PRESETS), state="readonly", width=32) # Preset dropdown
        self.preset_box.pack(fill="x")
        self.preset_box.bind("<<ComboboxSelected>>", lambda e: self.load_preset(self.preset_box.get())) # Load on pick

        tk.Label(right, text="Entries (answer - points):").pack(anchor="w", pady=(10, 0))
        self.listbox = tk.Listbox(right, height=14, selectmode="extended") # Entry list, multi-select
        self.listbox.pack(fill="both", expand=True)

        # Add entry inputs
        add = tk.Frame(right)
        add.pack(fill="x", pady=6)
        tk.Label(add, text="Answer").grid(row=0, column=0, sticky="w")
        tk.Label(add, text="Points").grid(row=0, column=1, sticky="w")
        self.answer_var = tk.StringVar()
        self.points_var = tk.StringVar(value="1") # Default weight
        ans = tk.Entry(add, textvariable=self.answer_var, width=20)
        ans.grid(row=1, column=0, padx=(0, 4))
        ans.bind("<Return>", lambda e: self.add_entry()) # Enter key adds
        tk.Entry(add, textvariable=self.points_var, width=8).grid(row=1, column=1)

        # Buttons
        btns = tk.Frame(right)
        btns.pack(fill="x")
        tk.Button(btns, text="Add", width=9, command=self.add_entry).pack(side="left")
        tk.Button(btns, text="Remove", width=9, command=self.remove_entry).pack(side="left", padx=4)
        tk.Button(btns, text="Clear", width=9, command=self.clear).pack(side="left")

        # Start on the first preset
        self.preset_box.current(0)
        self.load_preset(self.preset_box.get())

    # Entries
    def load_preset(self, name):
        self.title_var.set(name) # Preset name becomes the title
        self.entries = list(PRESETS[name]) # Copy so edits don't change the preset
        self.refresh()

    def add_entry(self):
        answer = self.answer_var.get().strip()
        try:
            points = float(self.points_var.get()) # Points must be a positive number
            assert points > 0
        except (ValueError, AssertionError):
            return messagebox.showwarning("Points", "Points must be a number above 0.")
        if not answer:
            return messagebox.showwarning("Answer", "Type an answer first.")
        self.entries.append((answer, points))
        self.answer_var.set("") # Clear box for next entry
        self.refresh()

    def remove_entry(self):
        for i in sorted(self.listbox.curselection(), reverse=True): # Delete from the end so indexes stay valid
            del self.entries[i]
        self.refresh()

    def clear(self):
        self.entries = []
        self.refresh()

    def refresh(self):
        # Rebuild the list and redraw the wheel
        total = sum(p for _, p in self.entries) or 1 # "or 1" avoids divide by zero
        self.listbox.delete(0, "end")
        for a, p in self.entries:
            self.listbox.insert("end", f"{a} - {p:g} Value ({p / total:.0%})") # Show points + chance
        self.draw()

    # Preview
    def slices(self):
        total = sum(p for _, p in self.entries)
        start = 0.0
        for i, (a, p) in enumerate(self.entries):
            ext = 360 * p / total # Slice size matches its share of points
            yield a, start, ext, COLORS[i % len(COLORS)] # Colors loop if more entries than colors
            start += ext

    def draw(self):
        c = self.canvas
        c.delete("all") # Wipe and redraw each frame
        if not self.entries: # Empty wheel placeholder
            c.create_oval(CX - R, CY - R, CX + R, CY + R, fill="#ddd", outline="")
            c.create_text(CX, CY, text="Add some entries", font=("Segoe UI", 14))
            return
        for a, start, ext, color in self.slices():
            s = (start + self.rotation) % 360 # Apply current spin
            c.create_arc(CX - R, CY - R, CX + R, CY + R, start=s, extent=min(ext, 359.99),
                         fill=color, outline="white", width=2) # 359.99 since a full 360 arc won't draw
            mid = math.radians(s + ext / 2) # Middle of slice for the label
            c.create_text(CX + R * 0.62 * math.cos(mid), CY - R * 0.62 * math.sin(mid),
                          text=a[:16], font=("Segoe UI", 11, "bold"), fill="black") # Long names cut to 16 chars
        c.create_oval(CX - 18, CY - 18, CX + 18, CY + 18, fill="white", outline="#333", width=2) # Center cap
        # Pointer at the top
        c.create_polygon(CX - 14, 4, CX + 14, 4, CX, 34, fill="#222")

    # ---------- spinning ----------
    def spin(self):
        if self.spinning or not self.entries:
            return
        # Pick the winner by points, then aim the wheel so the pointer (90 deg) lands in it
        winner = random.choices(range(len(self.entries)), weights=[p for _, p in self.entries])[0]
        _, start, ext, _ = list(self.slices())[winner]
        landing = start + ext * random.uniform(0.1, 0.9) # Random spot inside the slice, not the edge
        target = (90 - landing) % 360 # Rotation that puts that spot under the pointer
        self.final = self.rotation + 360 * random.randint(4, 7) + (target - self.rotation) % 360 # Add 4-7 full turns
        self.begin = self.rotation
        self.winner = self.entries[winner][0]
        self.steps, self.step = 180, 0 # 180 frames is about 3 seconds
        self.spinning = True
        self.spin_btn.config(state="disabled")
        self.result_var.set("Spinning...")
        self.animate()

    def animate(self):
        self.step += 1
        t = self.step / self.steps # Progress 0 to 1
        ease = 1 - (1 - t) ** 3  # ease-out: fast then slows down
        self.rotation = self.begin + (self.final - self.begin) * ease
        self.draw()
        if self.step < self.steps:
            self.after(16, self.animate) # Next frame in 16ms (~60 FPS)
        else:
            # Done spinning
            self.rotation %= 360
            self.spinning = False
            self.spin_btn.config(state="normal")
            self.result_var.set(f"Answer: {self.winner}")


if __name__ == "__main__":
    WheelApp().mainloop()
