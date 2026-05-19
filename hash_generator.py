from tkinter import Label, messagebox, Text, Entry, Tk, END, Canvas, Frame, Scrollbar
from tkinter import ttk
import tkinter as tk
import hashlib
import binascii


# ── Color Palette ────────────────────────────────────────────────────────────
BG_DARK       = "#0d1117"   # main background (GitHub-dark style)
BG_CARD       = "#161b22"   # card / panel background
BG_INPUT      = "#1c2128"   # input field background
ACCENT        = "#58a6ff"   # blue accent
ACCENT_GREEN  = "#3fb950"   # green accent (success)
ACCENT_RED    = "#f85149"   # red (quit button)
ACCENT_PINK   = "#bc8cff"   # purple/pink (show all)
TEXT_PRIMARY  = "#e6edf3"   # primary text
TEXT_MUTED    = "#8b949e"   # muted / label text
BORDER        = "#30363d"   # border color
BTN_HOVER     = "#1f6feb"   # button hover


class HashGenerator:
    def __init__(self, master):
        self.master = master
        master.title("⚡ Hash Generator")
        master.geometry("1400x780")
        master.configure(bg=BG_DARK)
        master.resizable(True, True)

        self._setup_styles()
        self._build_ui()

    # ── ttk Styles ───────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        # Progress bar — blue
        style.configure("blue.Horizontal.TProgressbar",
                        troughcolor=BG_CARD,
                        background=ACCENT,
                        bordercolor=BORDER,
                        lightcolor=ACCENT,
                        darkcolor=ACCENT)

        # Progress bar — green
        style.configure("green.Horizontal.TProgressbar",
                        troughcolor=BG_CARD,
                        background=ACCENT_GREEN,
                        bordercolor=BORDER,
                        lightcolor=ACCENT_GREEN,
                        darkcolor=ACCENT_GREEN)

    # ── UI Builder ───────────────────────────────────────────────────────────
    def _build_ui(self):
        master = self.master

        # ── Top header bar ───────────────────────────────────────────────────
        header = tk.Frame(master, bg=BG_CARD, height=56)
        header.pack(fill="x", side="top")
        tk.Label(header, text="⚡  HASH  GENERATOR",
                 font=("Courier New", 20, "bold"),
                 fg=ACCENT, bg=BG_CARD).pack(side="left", padx=24, pady=10)
        tk.Label(header, text="Secured for use",
                 font=("Courier New", 11),
                 fg=TEXT_MUTED, bg=BG_CARD).pack(side="right", padx=24)

        # Thin accent line under header
        tk.Frame(master, bg=ACCENT, height=2).pack(fill="x")

        # ── Main body ────────────────────────────────────────────────────────
        body = tk.Frame(master, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Left panel
        left = tk.Frame(body, bg=BG_CARD, bd=0,
                        highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 16), pady=0, ipadx=10, ipady=10)

        tk.Label(left, text="INPUT MESSAGE",
                 font=("Courier New", 10, "bold"),
                 fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=14, pady=(14, 4))

        self.text_input = Text(
            left, height=12, width=22,
            font=("Courier New", 11),
            bg=BG_INPUT, fg=TEXT_PRIMARY,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            selectbackground=ACCENT,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self.text_input.pack(padx=14, pady=(0, 14))

        # Buttons in left panel
        self._make_btn(left, "▶  SHOW ALL",  ACCENT_PINK,  self.show_all).pack(
            fill="x", padx=14, pady=4)
        self._make_btn(left, "⌫  CLEAR",     ACCENT,       self.clear).pack(
            fill="x", padx=14, pady=4)
        self._make_btn(left, "✕  QUIT",      ACCENT_RED,   master.quit).pack(
            fill="x", padx=14, pady=(4, 14))

        # Right panel — scrollable hash rows
        right_outer = tk.Frame(body, bg=BG_DARK)
        right_outer.pack(side="left", fill="both", expand=True)

        tk.Label(right_outer, text="HASH OUTPUTS",
                 font=("Courier New", 10, "bold"),
                 fg=TEXT_MUTED, bg=BG_DARK).pack(anchor="w", pady=(0, 8))

        # Canvas + scrollbar for the hash rows
        canvas = tk.Canvas(right_outer, bg=BG_DARK, bd=0,
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_outer, orient="vertical",
                                  command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Define all hash rows
        self.output_entries = {}
        hash_rows = [
            ("MD5",      "128-bit",  self.compute_md5),
            ("SHA-1",    "160-bit",  self.compute_sha1),
            ("SHA2-224", "224-bit",  self.compute_sha2_224),
            ("SHA2-256", "256-bit",  self.compute_sha2_256),
            ("SHA2-384", "384-bit",  self.compute_sha2_384),
            ("SHA3-224", "224-bit",  self.compute_sha3_224),
            ("SHA3-256", "256-bit",  self.compute_sha3_256),
            ("SHA3-384", "384-bit",  self.compute_sha3_384),
            ("BLAKE2s",  "256-bit",  self.compute_blake2s),
            ("BLAKE2b",  "512-bit",  self.compute_blake2b),
        ]

        for name, bits, cmd in hash_rows:
            self._make_hash_row(self.scroll_frame, name, bits, cmd)

        # ── Bottom progress bars ──────────────────────────────────────────────
        bar_frame = tk.Frame(master, bg=BG_DARK)
        bar_frame.pack(fill="x", padx=20, pady=(0, 12))

        tk.Label(bar_frame, text="SHA-2 family",
                 font=("Courier New", 8), fg=TEXT_MUTED,
                 bg=BG_DARK).pack(anchor="w")
        pb1 = ttk.Progressbar(bar_frame, length=680, mode="determinate",
                              style="blue.Horizontal.TProgressbar")
        pb1.pack(side="left", padx=(0, 20))
        pb1["value"] = 72

        tk.Label(bar_frame, text="SHA-3 family",
                 font=("Courier New", 8), fg=TEXT_MUTED,
                 bg=BG_DARK).pack(anchor="w")
        pb2 = ttk.Progressbar(bar_frame, length=680, mode="determinate",
                              style="green.Horizontal.TProgressbar")
        pb2.pack(side="left")
        pb2["value"] = 58

    # ── Widget helpers ────────────────────────────────────────────────────────
    def _make_btn(self, parent, text, color, cmd):
        btn = tk.Button(
            parent, text=text,
            font=("Courier New", 11, "bold"),
            fg=BG_DARK, bg=color,
            activebackground=BTN_HOVER,
            activeforeground=TEXT_PRIMARY,
            relief="flat", bd=0,
            cursor="hand2",
            pady=8,
            command=cmd,
        )
        return btn

    def _make_hash_row(self, parent, name, bits, cmd):
        row = tk.Frame(parent, bg=BG_CARD,
                       highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill="x", pady=4, padx=2)

        # Algorithm badge
        badge = tk.Frame(row, bg=BG_INPUT, width=110)
        badge.pack(side="left", fill="y")
        badge.pack_propagate(False)
        tk.Label(badge, text=name,
                 font=("Courier New", 11, "bold"),
                 fg=ACCENT, bg=BG_INPUT).pack(pady=6, padx=8)
        tk.Label(badge, text=bits,
                 font=("Courier New", 8),
                 fg=TEXT_MUTED, bg=BG_INPUT).pack(pady=(0, 6))

        # Output entry
        entry = tk.Entry(
            row, font=("Courier New", 11),
            bg=BG_INPUT, fg=ACCENT_GREEN,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            readonlybackground=BG_INPUT,
            highlightthickness=0,
        )
        entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.output_entries[name] = entry

        # Compute button
        tk.Button(
            row, text="HASH",
            font=("Courier New", 10, "bold"),
            fg=BG_DARK, bg=ACCENT,
            activebackground=BTN_HOVER,
            activeforeground=TEXT_PRIMARY,
            relief="flat", bd=0,
            cursor="hand2",
            padx=14, pady=6,
            command=cmd,
        ).pack(side="right", padx=(0, 10), pady=8)

        # Copy button
        tk.Button(
            row, text="COPY",
            font=("Courier New", 10, "bold"),
            fg=TEXT_PRIMARY, bg=BORDER,
            activebackground=TEXT_MUTED,
            activeforeground=BG_DARK,
            relief="flat", bd=0,
            cursor="hand2",
            padx=10, pady=6,
            command=lambda e=entry: self._copy(e),
        ).pack(side="right", padx=(0, 4), pady=8)

    # ── Clipboard copy ────────────────────────────────────────────────────────
    def _copy(self, entry):
        val = entry.get()
        if val:
            self.master.clipboard_clear()
            self.master.clipboard_append(val)
            messagebox.showinfo("Copied", "Hash copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "No hash to copy. Compute it first.")

    # ── Core helpers ──────────────────────────────────────────────────────────
    def _get_input(self):
        raw = self.text_input.get(1.0, END)
        return raw.replace("\n", "").encode("utf-8")

    def _hex(self, digest_bytes):
        return binascii.hexlify(digest_bytes).decode("utf-8")

    def _insert(self, key, value):
        e = self.output_entries[key]
        e.delete(0, END)
        e.insert(0, value)

    # ── Hash methods ──────────────────────────────────────────────────────────
    def compute_md5(self):
        try:
            self._insert("MD5", self._hex(hashlib.md5(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_sha1(self):
        try:
            self._insert("SHA-1", self._hex(hashlib.sha1(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_sha2_224(self):
        try:
            self._insert("SHA2-224", self._hex(hashlib.sha224(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_sha2_256(self):
        try:
            self._insert("SHA2-256", self._hex(hashlib.sha256(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_sha2_384(self):
        try:
            self._insert("SHA2-384", self._hex(hashlib.sha384(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_sha3_224(self):
        try:
            self._insert("SHA3-224", self._hex(hashlib.sha3_224(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_sha3_256(self):
        try:
            self._insert("SHA3-256", self._hex(hashlib.sha3_256(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_sha3_384(self):
        try:
            self._insert("SHA3-384", self._hex(hashlib.sha3_384(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_blake2s(self):
        try:
            self._insert("BLAKE2s", self._hex(hashlib.blake2s(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def compute_blake2b(self):
        try:
            self._insert("BLAKE2b", self._hex(hashlib.blake2b(self._get_input()).digest()))
        except Exception as e:
            messagebox.showerror("Error", e)

    def show_all(self):
        for fn in (
            self.compute_md5, self.compute_sha1,
            self.compute_sha2_224, self.compute_sha2_256,
            self.compute_sha2_384, self.compute_sha3_224,
            self.compute_sha3_256, self.compute_sha3_384,
            self.compute_blake2s, self.compute_blake2b,
        ):
            fn()

    def clear(self):
        self.text_input.delete(1.0, END)
        for entry in self.output_entries.values():
            entry.delete(0, END)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = Tk()
    HashGenerator(root)
    root.mainloop()