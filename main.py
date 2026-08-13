"""
================================================================================
  Statistics Calculator — v5  ✦  CYBERPUNK HOLOGRAPHIC TERMINAL EDITION
  By: Abdelrhman Ramdan Kasem  |  Horus University — Egypt

  UPDATES v5:
  ✦ Enhanced Color Scheme for all 9 topics
  ✦ Raw Data Input option for all Estimation & Test panels
  ✦ Clear decision text: Accept/Reject Null Hypothesis
  ✦ Plots show Acceptance (green) and Rejection (red) regions with legend
  ✦ CI plots show Confidence Interval bounds clearly

  Color Scheme:
  ◈ #BD00FF - Hypotheses (H₀, H₁)
  ◈ #00E5FF - General Info (Distribution, SE, df)
  ◈ #FFD700 - Formulas (t=, Z=, χ²=)
  ◈ #A8D8F0 - Calculations (intermediate steps)
  ◈ #00FF88 - Results & Acceptance Region
  ◈ #FF8800 - Critical Values
  ◈ #FF0040 - p-values & Rejection Region
================================================================================
"""

"""
================================================================================
  Statistics Calculator — v4  ✦  CYBERPUNK HOLOGRAPHIC TERMINAL EDITION
  By: Abdelrhman Ramdan Kasem  |  Horus University — Egypt

  Theme: Cyberpunk Dark Terminal
  ◈ Background #000208 with scanline overlay
  ◈ Neon glow: Teal #00FFC8 · Magenta #FF0078 · Blue #4DA6FF · Amber #FFAA00
  ◈ Clipped-corner widgets via Canvas
  ◈ Animated neon borders on result boxes
  ◈ Sidebar with live indicator bars
  ◈ Status bar with colored dots + live clock

  Fixes preserved:
  ✦ Fixed KeyError crash: th("BLUE") → th("ACCENT2") in SamplingVarPanel
  ✦ Fixed label "t =" → dynamic "Z =" / "t =" in TestMeanPanel
  ✦ Removed duplicate bind_entries_return in NormalDistPanel
  ✦ Improved result_row wraplength for scrolled canvas
  ✦ Fixed result_answer frame expand in scrolled canvas
  ✦ Consistent step labels and formatting across all panels
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math, json, os
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as mpdf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy import stats
import urllib.request, urllib.error, threading

# ══════════════════════════════════════════════════════════════════════════════
#  CYBERPUNK THEMES
# ══════════════════════════════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "BG":        "#000208",
        "SURFACE":   "#050D1A",
        "SURF2":     "#080F1E",
        "SURF3":     "#0A1428",
        "BORDER":    "#0D2040",
        "BORDER2":   "#1A3A5C",
        "ACCENT":    "#4DA6FF",       # Neon Blue
        "ACCENT2":   "#00FFC8",       # Neon Teal
        "ACCENT_DIM":"#001A2E",
        "GOLD":      "#FFAA00",       # Amber
        "GOLD2":     "#FFD060",
        "GOLD_DIM":  "#2A1A00",
        "TEAL":      "#00FFC8",       # Neon Teal
        "GREEN":     "#00FF88",
        "GREEN2":    "#00CC66",
        "RED":       "#FF0078",       # Magenta/Red
        "ORANGE":    "#FF6600",
        "TEXT":      "#C8E8FF",
        "TEXT2":     "#7BBFDF",
        "TEXT3":     "#2A5070",
        "TEXT4":     "#A8D8F0",
        "PLOT_BG":   "#000208",
        "PLOT_AX":   "#050D1A",
        "PLOT_GRID": "#0A2040",
        "PLOT_TEXT": "#4A90B0",
        "MAGENTA":   "#FF0078",
        "CYAN":      "#00FFC8",
        "NEON_BLUE": "#4DA6FF",
        # Enhanced colors for v5
        "GLOW_CYAN": "#00FFFF",
        "GLOW_PINK": "#FF00FF",
        "GLOW_GREEN": "#39FF14",
        "DEEP_BLUE": "#000428",
        "DEEP_PURPLE": "#240b36",
        "GLASS":     "rgba(10, 20, 40, 0.7)",
    },
    "light": {
        "BG":        "#0A0F1E",
        "SURFACE":   "#0D1525",
        "SURF2":     "#101828",
        "SURF3":     "#121E30",
        "BORDER":    "#1A3050",
        "BORDER2":   "#254A70",
        "ACCENT":    "#4DA6FF",
        "ACCENT2":   "#00FFC8",
        "ACCENT_DIM":"#001A2E",
        "GOLD":      "#FFAA00",
        "GOLD2":     "#FFD060",
        "GOLD_DIM":  "#2A1A00",
        "TEAL":      "#00FFC8",
        "GREEN":     "#00FF88",
        "GREEN2":    "#00CC66",
        "RED":       "#FF0078",
        "ORANGE":    "#FF6600",
        "TEXT":      "#C8E8FF",
        "TEXT2":     "#7BBFDF",
        "TEXT3":     "#2A5070",
        "TEXT4":     "#A8D8F0",
        "PLOT_BG":   "#0A0F1E",
        "PLOT_AX":   "#0D1525",
        "PLOT_GRID": "#0A2040",
        "PLOT_TEXT": "#4A90B0",
        "MAGENTA":   "#FF0078",
        "CYAN":      "#00FFC8",
        "NEON_BLUE": "#4DA6FF",
    }
}

T = THEMES["dark"].copy()
def th(key): return T[key]

# ══════════════════════════════════════════════════════════════════════════════
#  CYBERPUNK FONTS
# ══════════════════════════════════════════════════════════════════════════════
FM       = ("Consolas",    12)
FB       = ("Consolas",    11)
FH       = ("Consolas",    14, "bold")
FMONO    = ("Consolas",    12)
FRES     = ("Consolas",    12)
FRES_BIG = ("Consolas",    14, "bold")
FSTEP    = ("Consolas",    11, "bold")
FLBL     = ("Consolas",    10)

# ── Calc History ──────────────────────────────────────────────────────────────
calc_history = []
last_values  = {}
_show_steps  = [True]
_z_prec      = [4]

# ── Math ──────────────────────────────────────────────────────────────────────
def phi(x):          return float(stats.norm.cdf(x))
def z_crit(a):       return float(stats.norm.ppf(1.0 - a))
def t_crit(df, a):   return float(stats.t.ppf(1.0 - a/2.0, df))
def t1tail(df, a):   return float(stats.t.ppf(1.0 - a, df))
Z_TABLE = {0.90:1.6449, 0.95:1.9600, 0.98:2.3263, 0.99:2.5758}
def get_z_crit(conf): return Z_TABLE.get(conf, z_crit((1-conf)/2.0))

def round_z(z):  return round(z, _z_prec[0])
def phi_z(z):    return phi(round_z(z))

def p_interp(p):
    if p < 0.001: return ("EXTREMELY SIGNIFICANT", "#FF0078")
    if p < 0.01:  return ("VERY SIGNIFICANT",      "#FF4466")
    if p < 0.05:  return ("SIGNIFICANT",           "#FFAA00")
    if p < 0.10:  return ("MARGINAL",              "#FF8800")
    return ("NOT SIGNIFICANT", "#00FFC8")

# ── Raw Data Parser ───────────────────────────────────────────────────────────

# ── Smart Problem Parser ────────────────────────────────────────────────────
import re as regex

def smart_extract(text, panel_id):
    """
    Extract statistical values from pasted problem text.
    Supports ALL panels: test_mean, test_prop, test_var, ci_mean, ci_prop, ci_var
    """
    original_text = text
    text = text.lower()
    result = {}

    # ═══════════════════════════════════════════════════════════════════════
    # COMMON PATTERNS (all panels)
    # ═══════════════════════════════════════════════════════════════════════

    # Sample Size (n)
    n_patterns = [
        r'a sample of (\d+)',
        r'sample of (\d+)',
        r'sample size\s*[=\s]+(\d+)',
        r'n\s*[=\s]+(\d+)',
        r'(\d+)\s+days',
        r'(\d+)\s+students',
        r'(\d+)\s+observations',
        r'(\d+)\s+subjects',
        r'(\d+)\s+people',
    ]
    for pattern in n_patterns:
        match = regex.search(pattern, text)
        if match:
            result['n'] = match.group(1)
            break

    # Alpha
    alpha_patterns = [
        r'α\s*[=\s]+(\d+\.?\d*)',
        r'alpha\s*[=\s]+(\d+\.?\d*)',
        r'at\s+(\d+\.?\d*)\s*significance',
        r'significance level\s*[=\s]+(\d+\.?\d*)',
    ]
    for pattern in alpha_patterns:
        match = regex.search(pattern, text)
        if match:
            result['alpha'] = match.group(1)
            break

    # Confidence Level
    conf_patterns = [
        r'(\d+)%\s+confidence',
        r'confidence\s+level\s*[=\s]+(\d+\.?\d*)',
    ]
    for pattern in conf_patterns:
        match = regex.search(pattern, text)
        if match:
            val = match.group(1)
            if float(val) > 1:
                val = str(float(val) / 100)
            result['conf'] = val
            break

    # ═══════════════════════════════════════════════════════════════════════
    # PANEL-SPECIFIC EXTRACTION
    # ═══════════════════════════════════════════════════════════════════════

    # TEST FOR μ  &  CI FOR μ
    if panel_id in ['test_mean', 'ci_mean']:
        mean_patterns = [
            r'has an average.*?of\s+(\d+\.?\d*)',
            r'has a mean.*?of\s+(\d+\.?\d*)',
            r'average.*?of\s+(\d+\.?\d*)',
            r'mean.*?of\s+(\d+\.?\d*)',
            r'x̄\s*[=\s]+(\d+\.?\d*)',
            r'xbar\s*[=\s]+(\d+\.?\d*)',
            r'sample mean\s*[=\s]+(\d+\.?\d*)',
            r'average\s*[=\s]+(\d+\.?\d*)',
            r'mean\s*[=\s]+(\d+\.?\d*)',
        ]
        for pattern in mean_patterns:
            match = regex.search(pattern, text)
            if match:
                result['mean'] = match.group(1)
                break

        # Population SD (σ)
        sigma_patterns = [
            r'standard deviation of the population\s+is\s+(\d+\.?\d*)',
            r'population standard deviation\s*[=\s]+(\d+\.?\d*)',
            r'σ\s*[=\s]+(\d+\.?\d*)',
            r'sigma\s*[=\s]+(\d+\.?\d*)',
        ]
        for pattern in sigma_patterns:
            match = regex.search(pattern, text)
            if match:
                result['sigma'] = match.group(1)
                break

        # Sample SD (s) - if sigma not found
        if 'sigma' not in result:
            s_patterns = [
                r's\s*[=\s]+(\d+\.?\d*)',
                r'sample standard deviation\s*[=\s]+(\d+\.?\d*)',
                r'sd\s*[=\s]+(\d+\.?\d*)',
            ]
            for pattern in s_patterns:
                match = regex.search(pattern, text)
                if match:
                    result['s'] = match.group(1)
                    break

        # Hypothesized mean (μ₀)
        if panel_id == 'test_mean':
            mu0_patterns = [
                r'claim.*?average.*?is\s+(\d+\.?\d*)',
                r'claim.*?mean.*?is\s+(\d+\.?\d*)',
                r'average.*?is\s+(\d+\.?\d*)',
                r'mean.*?is\s+(\d+\.?\d*)',
                r'μ0\s*[=\s]+(\d+\.?\d*)',
                r'mu0\s*[=\s]+(\d+\.?\d*)',
                r'hypothesized\s+mean\s*[=\s]+(\d+\.?\d*)',
                r'test\s+if\s+μ\s*[=\s]+(\d+\.?\d*)',
                r'test\s+if\s+mean\s*[=\s]+(\d+\.?\d*)',
                r'equal to\s+(\d+\.?\d*)',
                r'population mean\s+is\s+(\d+\.?\d*)',
            ]
            for pattern in mu0_patterns:
                match = regex.search(pattern, text)
                if match:
                    result['mu0'] = match.group(1)
                    break

    # TEST FOR P  &  CI FOR P
    elif panel_id in ['test_prop', 'ci_prop']:

        # Find ALL percentages in the text
        all_percentages = regex.findall(r'(\d+\.?\d*)\s*%', text)
        all_percentages = [str(float(p)/100) if float(p) > 1 else p for p in all_percentages]

        # Find sample proportion (p̂) - usually comes after "sample", "shows", "found"
        p_hat_patterns = [
            r'sample.*?shows\s+(\d+\.?\d*)\s*%',
            r'sample.*?found\s+(\d+\.?\d*)\s*%',
            r'sample.*?has\s+(\d+\.?\d*)\s*%',
            r'shows\s+(\d+\.?\d*)\s*%',
            r'found\s+(\d+\.?\d*)\s*%',
            r'p̂\s*[=\s]+(\d+\.?\d*)',
            r'p\s*[=\s]+(\d+\.?\d*)',
            r'sample proportion\s*[=\s]+(\d+\.?\d*)',
        ]
        for pattern in p_hat_patterns:
            match = regex.search(pattern, text)
            if match:
                val = match.group(1)
                if float(val) > 1:
                    val = str(float(val) / 100)
                result['p'] = val
                break

        # If no p̂ found but we have percentages, use the last one (usually sample)
        if 'p' not in result and all_percentages:
            result['p'] = all_percentages[-1]

        # Hypothesized proportion (P₀) - for test only
        if panel_id == 'test_prop':
            P0_patterns = [
                r'claim.*?that\s+(\d+\.?\d*)\s*%',
                r'claim.*?states\s+(\d+\.?\d*)\s*%',
                r'states.*?that\s+(\d+\.?\d*)\s*%',
                r'proportion.*?is\s+(\d+\.?\d*)',
                r'p0\s*[=\s]+(\d+\.?\d*)',
                r'P0\s*[=\s]+(\d+\.?\d*)',
                r'hypothesized\s+proportion\s*[=\s]+(\d+\.?\d*)',
                r'test\s+if\s+p\s*[=\s]+(\d+\.?\d*)',
                r'population proportion\s+is\s+(\d+\.?\d*)',
            ]
            for pattern in P0_patterns:
                match = regex.search(pattern, text)
                if match:
                    val = match.group(1)
                    if float(val) > 1:
                        val = str(float(val) / 100)
                    result['P0'] = val
                    break

            # If no P₀ found but we have multiple percentages, use first one (usually claim)
            if 'P0' not in result and len(all_percentages) >= 2:
                result['P0'] = all_percentages[0]

    # TEST FOR σ²  &  CI FOR σ²
    elif panel_id in ['test_var', 'ci_var']:
        var_patterns = [
            r'variance\s*[=\s]+(\d+\.?\d*)',
            r's²\s*[=\s]+(\d+\.?\d*)',
            r's2\s*[=\s]+(\d+\.?\d*)',
            r'sample variance\s*[=\s]+(\d+\.?\d*)',
        ]
        for pattern in var_patterns:
            match = regex.search(pattern, text)
            if match:
                result['s2'] = match.group(1)
                break

        if panel_id == 'test_var':
            sig20_patterns = [
                r'claim.*?variance.*?is\s+(\d+\.?\d*)',
                r'claim.*?σ².*?is\s+(\d+\.?\d*)',
                r'variance.*?is\s+(\d+\.?\d*)',
                r'σ0²\s*[=\s]+(\d+\.?\d*)',
                r'sig20\s*[=\s]+(\d+\.?\d*)',
                r'hypothesized\s+variance\s*[=\s]+(\d+\.?\d*)',
                r'test\s+if\s+σ²\s*[=\s]+(\d+\.?\d*)',
                r'population variance\s+is\s+(\d+\.?\d*)',
            ]
            for pattern in sig20_patterns:
                match = regex.search(pattern, text)
                if match:
                    result['sig20'] = match.group(1)
                    break

    # TAIL DETECTION
    if panel_id.startswith('test_'):
        if 'two-tailed' in text or 'two sided' in text or 'two-sided' in text or '≠' in original_text:
            result['tail'] = 'Two-tailed'
        elif 'right-tailed' in text or 'greater than' in text or '>' in original_text or 'more than' in text:
            result['tail'] = 'Right-tailed'
        elif 'left-tailed' in text or 'less than' in text or '<' in original_text or 'fewer than' in text:
            result['tail'] = 'Left-tailed'
        else:
            result['tail'] = 'Two-tailed'

    # CASE DETECTION FOR CI
    if panel_id.startswith('ci_'):
        if 'σ known' in text or 'sigma known' in text or 'population standard deviation' in text:
            result['case'] = 1
        elif 'n ≥ 30' in text or 'n >= 30' in text or ('n' in result and int(result['n']) >= 30):
            result['case'] = 2
        elif 'n < 30' in text or 'small sample' in text:
            result['case'] = 3
        else:
            result['case'] = 2

    return result


def parse_raw_data(raw_text):
    """Parse space or comma separated values and return n, mean, std_dev."""
    raw = raw_text.replace(",", " ")
    try:
        vals = [float(x) for x in raw.split() if x.strip()]
    except:
        return None, "Could not parse values. Use numbers separated by spaces or commas."

    if len(vals) < 2:
        return None, "Need at least 2 values"

    n = len(vals)
    mean = sum(vals) / n
    # Sample standard deviation (n-1)
    variance = sum((v - mean)**2 for v in vals) / (n - 1)
    s = math.sqrt(variance)

    return {"n": n, "mean": mean, "s": s, "values": vals}, None


# ── Plot ──────────────────────────────────────────────────────────────────────
def style_ax(ax, title=""):
    ax.set_facecolor(th("PLOT_AX"))
    ax.tick_params(colors=th("PLOT_TEXT"), labelsize=10)
    for sp in ax.spines.values():
        sp.set_edgecolor("#0A2040"); sp.set_linewidth(0.6)
    ax.xaxis.label.set_color(th("PLOT_TEXT"))
    ax.yaxis.label.set_color(th("PLOT_TEXT"))
    if title:
        ax.set_title(title, color=th("CYAN"), fontsize=11, pad=8,
                     fontfamily="Courier New", fontstyle="italic")
    ax.grid(True, color=th("PLOT_GRID"), linewidth=0.4, alpha=0.8, linestyle="--")

def make_fig(h=3.8):
    fig, ax = plt.subplots(1, 1, figsize=(6.6, h), facecolor=th("PLOT_BG"))
    fig.tight_layout(pad=2.8)
    return fig, ax

def draw_normal_shade(ax, mu, sigma, lo=None, hi=None, color=None, label=""):
    color = color or th("GOLD")
    x = np.linspace(mu-4*sigma, mu+4*sigma, 500)
    ax.plot(x, stats.norm.pdf(x, mu, sigma), color=th("CYAN"), linewidth=2.0, alpha=0.9)
    if lo is not None and hi is not None:
        xs = np.linspace(lo, hi, 400)
        ax.fill_between(xs, stats.norm.pdf(xs, mu, sigma), color=color, alpha=0.45, label=label)
        ax.plot(xs, stats.norm.pdf(xs, mu, sigma), color=th("GOLD2"), linewidth=1.0, alpha=0.5)
    ax.axvline(mu, color=th("GOLD_DIM"), linewidth=0.8, linestyle=":", alpha=0.7)
    style_ax(ax)

def draw_chi_shade(ax, df, lo=None, hi=None, color=None):
    color = color or th("CYAN")
    x_max = df + 5*math.sqrt(2*df)
    x = np.linspace(0.01, x_max, 600)
    ax.plot(x, stats.chi2.pdf(x, df), color=th("CYAN"), linewidth=2.0, alpha=0.9)
    if lo is not None and hi is not None:
        xs = np.linspace(max(lo,0.01), hi, 400)
        ax.fill_between(xs, stats.chi2.pdf(xs, df), color=color, alpha=0.40)
    style_ax(ax)

_current_canvas = [None]
_current_fig    = [None]

def embed_plot(fig, parent):
    for w in parent.winfo_children(): w.destroy()
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    _current_canvas[0] = canvas
    _current_fig[0]    = fig

# ══════════════════════════════════════════════════════════════════════════════
#  CYBERPUNK UI PRIMITIVES
# ══════════════════════════════════════════════════════════════════════════════

class Tooltip:
    def __init__(self, widget, text):
        self.w = widget; self.text = text; self.tip = None
        widget.bind("<Enter>", self.show); widget.bind("<Leave>", self.hide)
    def show(self, e=None):
        x = self.w.winfo_rootx()+20; y = self.w.winfo_rooty()+self.w.winfo_height()+4
        self.tip = tk.Toplevel(self.w); self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        f = tk.Frame(self.tip, bg=th("CYAN"), padx=1, pady=1); f.pack()
        tk.Label(f, text=self.text, font=("Consolas", 9),
                 bg=th("SURF3"), fg=th("CYAN"), padx=10, pady=5,
                 justify="left", wraplength=320).pack()
    def hide(self, e=None):
        if self.tip: self.tip.destroy(); self.tip=None


class ValidEntry(tk.Entry):
    def __init__(self, parent, var, kind="float", width=14, tooltip_text="", **kw):
        super().__init__(parent, textvariable=var, font=("Consolas", 12),
                         bg=th("SURF3"), fg=th("CYAN"),
                         insertbackground=th("ACCENT2"),
                         relief="flat", width=width, bd=0,
                         highlightthickness=2,
                         highlightcolor=th("CYAN"),
                         highlightbackground=th("BORDER2"),
                         justify="center",
                         selectbackground=th("ACCENT_DIM"),
                         selectforeground=th("CYAN"), **kw)
        self.var  = var
        self.kind = kind
        self.bind("<FocusIn>",  self._in)
        self.bind("<FocusOut>", self._out)
        self.bind("<Button-3>", self._show_context_menu)  # Right-click
        self.bind("<Control-v>", self._paste)  # Ctrl+V
        var.trace_add("write", self._validate)
        if tooltip_text: Tooltip(self, tooltip_text)

    def _show_context_menu(self, event):
        menu = tk.Menu(self, tearoff=0, bg=th("SURF3"), fg=th("CYAN"),
                       activebackground=th("ACCENT_DIM"), activeforeground=th("CYAN"))
        menu.add_command(label="Cut", command=lambda: self.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: self.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=self._paste)
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self.select_range(0, "end"))
        menu.tk_popup(event.x_root, event.y_root)

    def _paste(self, event=None):
        try:
            text = self.clipboard_get()
            self.delete(0, "end")
            self.insert(0, text.strip())
            return "break"
        except:
            pass

    def _in(self, e=None):
        self.config(highlightcolor=th("GLOW_CYAN"), highlightbackground=th("GLOW_CYAN"), 
                    bg=th("BG"), fg=th("GLOW_CYAN"), insertbackground=th("GLOW_CYAN"))
    def _out(self, e=None):
        self.config(highlightcolor=th("CYAN"), highlightbackground=th("BORDER2"), 
                    bg=th("SURF3"), fg=th("CYAN"), insertbackground=th("ACCENT2"))
        self._validate()

    def _validate(self, *_):
        v = self.var.get().strip()
        if not v: self.config(highlightbackground=th("BORDER2")); return
        try:
            float(v) if self.kind == "float" else int(v)
            self.config(highlightbackground=th("BORDER2"), fg=th("CYAN"))
        except:
            self.config(highlightbackground=th("MAGENTA"), fg=th("MAGENTA"))


def lbl(parent, text, font=None, fg=None, bg=None, **kw):
    font = font or ("Consolas", 11)
    return tk.Label(parent, text=text, font=font,
                    bg=bg or th("SURF2"), fg=fg or th("TEXT2"), **kw)


def row_field(parent, label_text, var, r, note="", tooltip="", kind="float"):
    tk.Label(parent, text=label_text, font=("Consolas", 10),
             bg=th("SURF2"), fg=th("TEXT2"), anchor="w"
             ).grid(row=r, column=0, sticky="w", padx=(16, 10), pady=5)
    e = ValidEntry(parent, var, kind=kind, tooltip_text=tooltip, width=14)
    e.grid(row=r, column=1, padx=(0, 16), pady=5, ipady=6)
    if note:
        tk.Label(parent, text=note, font=("Consolas", 9),
                 bg=th("SURF2"), fg=th("TEXT3")
                 ).grid(row=r, column=2, sticky="w")
    return e


def section_header(parent, text, icon="▸", color=None):
    color = color or th("CYAN")
    f = tk.Frame(parent, bg=th("BG")); f.pack(fill="x", pady=(15, 5))
    # Left glowing bar (thicker)
    bar = tk.Frame(f, bg=color, width=4, height=28)
    bar.pack(side="left", padx=(0, 0))
    tk.Frame(f, bg=th("BG"), width=10).pack(side="left")
    # Section label with cyber prefix
    prefix = tk.Label(f, text=f"[ {icon} ]", font=("Consolas", 12, "bold"),
                      bg=th("BG"), fg=color)
    prefix.pack(side="left")
    tk.Label(f, text=f"  {text.upper()}", font=("Consolas", 13, "bold"),
             bg=th("BG"), fg=th("TEXT4")).pack(side="left")
    # Right trailing line with gradient effect
    line_frame = tk.Frame(f, bg=th("BG"))
    line_frame.pack(side="right", fill="x", expand=True, padx=(10, 6))
    tk.Frame(line_frame, bg=color, height=2).pack(fill="x", pady=(13, 0))


def card(parent, pady=5):
    outer = tk.Frame(parent, bg=th("BORDER2"), padx=1, pady=1)
    outer.pack(fill="x", pady=(0, pady), padx=3)
    inner = tk.Frame(outer, bg=th("SURF2")); inner.pack(fill="x")
    # Add subtle top border glow
    tk.Frame(inner, bg=th("BORDER2"), height=1).pack(fill="x", side="top")
    return inner


def divider(parent):
    f = tk.Frame(parent, bg=th("BG")); f.pack(fill="x", padx=12, pady=3)
    tk.Frame(f, bg=th("BORDER2"), height=1).pack(fill="x")


def result_row(parent, text, color=None, bold=False):
    color = color or th("TEXT4")
    font  = ("Consolas", 12, "bold") if bold else ("Consolas", 11)

    # Container frame
    container = tk.Frame(parent, bg=th("SURF2"))
    container.pack(fill="x", padx=10, pady=2)

    w = tk.Label(container, text=f"  {text}", font=font,
                 bg=th("SURF2"), fg=color, justify="left", anchor="w",
                 wraplength=420)
    w.pack(side="left", fill="x", expand=True)

    # Copy button
    def _copy_line():
        parent.clipboard_clear()
        parent.clipboard_append(text)
        parent.update()

    copy_btn = tk.Label(container, text="📋", font=("Consolas", 9),
                        bg=th("SURF2"), fg=th("TEXT3"), cursor="hand2")
    copy_btn.pack(side="right", padx=(0, 5))
    copy_btn.bind("<Enter>", lambda e: copy_btn.config(fg=th("CYAN")))
    copy_btn.bind("<Leave>", lambda e: copy_btn.config(fg=th("TEXT3")))
    copy_btn.bind("<Button-1>", lambda e: _copy_line())


def result_answer(parent, text, color=None):
    """Animated neon border result box with enhanced glow."""
    color = color or th("GREEN")
    # Outer glow frame (thicker for more glow)
    outer = tk.Frame(parent, bg=color, padx=2, pady=2)
    outer.pack(fill="x", padx=8, pady=(10, 5))
    inner = tk.Frame(outer, bg=th("BG"))
    inner.pack(fill="x")
    # Top accent line (gradient effect)
    top_line = tk.Frame(inner, bg=color, height=2)
    top_line.pack(fill="x")
    # Content
    content_f = tk.Frame(inner, bg=th("BG")); content_f.pack(fill="x")
    # Left glow bar (wider)
    tk.Frame(content_f, bg=color, width=4).pack(side="left", fill="y")
    # Text with shadow effect
    w = tk.Label(content_f, text=f"  {text}", font=("Consolas", 14, "bold"),
                 bg=th("BG"), fg=color, justify="left",
                 wraplength=440)
    w.pack(anchor="w", fill="x", padx=12, pady=10, side="left")
    # Animated neon cursor
    cursor = tk.Label(content_f, text="▮", font=("Consolas", 14, "bold"),
                      bg=th("BG"), fg=color)
    cursor.pack(side="right", padx=10)
    def _blink(on=True):
        cursor.config(fg=color if on else th("BG"))
        parent.after(500, lambda: _blink(not on))
    _blink()


def p_badge(parent, pval):
    label, color = p_interp(pval)
    outer = tk.Frame(parent, bg=color, padx=2, pady=2)
    outer.pack(fill="x", padx=8, pady=(0, 6))
    f = tk.Frame(outer, bg=th("SURF3")); f.pack(fill="x")
    # Dot indicator
    dot_f = tk.Frame(f, bg=th("SURF3")); dot_f.pack(side="left", padx=(10,0))
    tk.Label(dot_f, text="●", font=("Consolas", 12), bg=th("SURF3"), fg=color).pack()
    tk.Label(f, text=f"  p = {pval:.4f}   >>>   {label}",
             font=("Consolas", 11, "bold"),
             bg=th("SURF3"), fg=color).pack(side="left", padx=8, pady=6)


def calc_button(parent, text, cmd, key_widget=None):
    outer = tk.Frame(parent, bg=th("CYAN"), padx=2, pady=2)
    outer.pack(fill="x", pady=(15, 8), padx=3)
    inner = tk.Frame(outer, bg=th("BG")); inner.pack(fill="x")
    b = tk.Button(inner, text=text, font=("Consolas", 12, "bold"),
                  bg=th("BG"), fg=th("GLOW_CYAN"), relief="flat",
                  activebackground=th("SURF3"),
                  activeforeground=th("GLOW_CYAN"),
                  cursor="hand2", pady=12, bd=0, command=cmd)
    b.pack(fill="x")

    def on_enter(e):
        b.config(bg=th("SURF3"), fg=th("GLOW_CYAN"))
        outer.config(bg=th("GLOW_CYAN"))
    def on_leave(e):
        b.config(bg=th("BG"), fg=th("CYAN"))
        outer.config(bg=th("CYAN"))

    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    if key_widget:
        key_widget.bind("<Return>", lambda e: cmd())


def make_combo(parent, var, values, r, label="Type"):
    s = ttk.Style(); s.theme_use("default")
    s.configure("Cyber.TCombobox",
                fieldbackground=th("SURF3"), background=th("SURF3"),
                foreground=th("CYAN"), selectbackground=th("ACCENT_DIM"),
                selectforeground=th("CYAN"), arrowcolor=th("CYAN"),
                borderwidth=0, font=("Consolas", 10))
    tk.Label(parent, text=label, font=("Consolas", 10),
             bg=th("SURF2"), fg=th("TEXT2"), anchor="w"
             ).grid(row=r, column=0, sticky="w", padx=(16, 10), pady=5)
    cb = ttk.Combobox(parent, textvariable=var, values=values,
                      state="readonly", width=16,
                      font=("Consolas", 10), style="Cyber.TCombobox")
    cb.grid(row=r, column=1, pady=5, padx=(0, 16), ipady=4)
    return cb


def conf_combo(parent, var, r, label="Confidence Level"):
    tk.Label(parent, text=label, font=("Consolas", 10),
             bg=th("SURF2"), fg=th("TEXT2"), anchor="w"
             ).grid(row=r, column=0, sticky="w", padx=(16, 10), pady=5)
    e = ValidEntry(parent, var, kind="float", width=14,
                   tooltip_text="Type any value between 0 and 1\ne.g. 0.90 / 0.95 / 0.99")
    e.grid(row=r, column=1, padx=(0, 16), pady=5, ipady=6)
    tk.Label(parent, text="e.g. 0.95", font=("Consolas", 9),
             bg=th("SURF2"), fg=th("TEXT3")
             ).grid(row=r, column=2, sticky="w")
    return e


def alpha_field(parent, var, r, label="Alpha  α"):
    tk.Label(parent, text=label, font=("Consolas", 10),
             bg=th("SURF2"), fg=th("TEXT2"), anchor="w"
             ).grid(row=r, column=0, sticky="w", padx=(16, 10), pady=5)
    e = ValidEntry(parent, var, kind="float", width=14,
                   tooltip_text="Significance level — type any value\ne.g. 0.05 / 0.01 / 0.10")
    e.grid(row=r, column=1, padx=(0, 16), pady=5, ipady=6)
    tk.Label(parent, text="e.g. 0.05", font=("Consolas", 9),
             bg=th("SURF2"), fg=th("TEXT3")
             ).grid(row=r, column=2, sticky="w")
    return e


# ── Animated result builder ────────────────────────────────────────────────────
class AnimatedResults:
    ANSWER_FNS = {result_answer, p_badge}

    def __init__(self, parent, root, lines, delay=60):
        self.parent = parent; self.root = root
        if _show_steps[0]:
            self.lines = lines
        else:
            self.lines = [(fn, args) for fn, args in lines
                          if fn in self.ANSWER_FNS]
        self.delay = delay; self.idx = 0
        self._reveal()

    def _reveal(self):
        if self.idx >= len(self.lines): return
        fn, args = self.lines[self.idx]
        fn(self.parent, *args)
        self.idx += 1
        self.root.after(self.delay, self._reveal)


# ── Export helpers ─────────────────────────────────────────────────────────────
def export_plot_png():
    if _current_fig[0] is None: return
    path = filedialog.asksaveasfilename(defaultextension=".png",
               filetypes=[("PNG Image","*.png"),("PDF","*.pdf")],
               title="Export Plot")
    if not path: return
    _current_fig[0].savefig(path, dpi=200, bbox_inches="tight",
                             facecolor=th("PLOT_BG"))
    messagebox.showinfo("EXPORTED", f"Plot saved:\n{path}")

def export_history_txt():
    if not calc_history:
        messagebox.showinfo("EMPTY","No calculations to export."); return
    path = filedialog.asksaveasfilename(defaultextension=".txt",
               filetypes=[("Text File","*.txt")], title="Export History")
    if not path: return
    with open(path, "w", encoding="utf-8") as f:
        f.write("Statistics Calculator — Calculation History\n")
        f.write(f"Exported: {datetime.now()}\n")
        f.write("="*60 + "\n\n")
        for h in calc_history:
            f.write(f"[{h['time']}]  {h['topic']}\n{h['summary']}\n\n")
    messagebox.showinfo("EXPORTED", f"History saved:\n{path}")


# ── Formula Reference ─────────────────────────────────────────────────────────
FORMULAS = """
╔══════════════════════════════════════════════════════════════╗
║       STATISTICS FORMULA REFERENCE — CYBERPUNK EDITION      ║
║       Abdelrhman Ramdan Kasem · Horus University             ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NORMAL DISTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Z  =  (X − μ) / σ
  P(X < a)   =  Φ(Za)
  P(X > a)   =  1 − Φ(Za)
  P(a<X<b)   =  Φ(Zb) − Φ(Za)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SAMPLING DISTRIBUTION OF p̂
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  μ_p̂  =  P
  σ_p̂  =  √(PQ/n)         where Q = 1−P
  Z    =  (p̂ − P) / σ_p̂

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SAMPLING DISTRIBUTION OF s² (Chi-Square)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  χ²  =  (n−1)·s² / σ²    df = n−1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CONFIDENCE INTERVALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  For μ (σ known, Case 1):    x̄ ± Z(α/2) · σ/√n
  For μ (σ unknown, n≥30):   x̄ ± Z(α/2) · s/√n
  For μ (σ unknown, n<30):   x̄ ± t(α/2, df=n−1) · s/√n
  For P:                      p̂ ± Z(α/2) · √(p̂q̂/n)
  For σ²:                     [ (n−1)s²/χ²_R ,  (n−1)s²/χ²_L ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HYPOTHESIS TESTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Test for μ:   Z or t  =  (x̄ − μ₀) / (σ or s / √n)
  Test for P:   Z  =  (p̂ − P₀) / √(P₀Q₀/n)
  Test for σ²:  χ²  =  (n−1)s² / σ₀²

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL VALUES  [ Z-TABLE ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    90%  →  Z = 1.6449
    95%  →  Z = 1.9600
    98%  →  Z = 2.3263
    99%  →  Z = 2.5758

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  p-VALUE GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  p < 0.001  EXTREMELY SIGNIFICANT  (****)
  p < 0.01   VERY SIGNIFICANT       (***)
  p < 0.05   SIGNIFICANT            (**)
  p < 0.10   MARGINAL               (*)
  p ≥ 0.10   NOT SIGNIFICANT
"""


class FormulaSheet(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("[ F1 ] FORMULA REFERENCE SHEET")
        self.geometry("680x700")
        self.configure(bg=th("BG"))
        self.resizable(True, True)
        tk.Frame(self, bg=th("CYAN"), height=2).pack(fill="x")
        hdr = tk.Frame(self, bg=th("SURFACE")); hdr.pack(fill="x")
        tk.Label(hdr, text="  [ 📐 ]  FORMULA REFERENCE SHEET",
                 font=("Consolas", 13, "bold"), bg=th("SURFACE"), fg=th("CYAN"), pady=10).pack(side="left")
        tk.Button(hdr, text="[ EXPORT TXT ]", font=("Consolas", 9),
                  bg=th("SURF3"), fg=th("TEXT2"), relief="flat",
                  cursor="hand2", padx=10, pady=5,
                  command=self._export).pack(side="right", padx=12, pady=7)
        tk.Frame(self, bg=th("CYAN"), height=1).pack(fill="x")
        f = tk.Frame(self, bg=th("BG")); f.pack(fill="both", expand=True, padx=8, pady=8)
        sc = tk.Scrollbar(f, orient="vertical")
        t = tk.Text(f, font=("Consolas", 10), bg=th("SURFACE"), fg=th("CYAN"),
                    insertbackground=th("CYAN"), relief="flat", bd=0,
                    highlightthickness=0, yscrollcommand=sc.set, padx=14, pady=10,
                    state="normal", wrap="none")
        sc.config(command=t.yview)
        t.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        t.insert("1.0", FORMULAS)
        t.config(state="disabled")
        self.bind("<Escape>", lambda e: self.destroy())

    def _export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                   filetypes=[("Text","*.txt")], title="Export Formula Sheet")
        if not path: return
        with open(path,"w",encoding="utf-8") as f: f.write(FORMULAS)
        messagebox.showinfo("DONE", f"Saved:\n{path}")


class TableViewer(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("[ F2 ] CRITICAL VALUE TABLES")
        self.geometry("560x580")
        self.configure(bg=th("BG"))
        self.resizable(True, True)
        tk.Frame(self, bg=th("CYAN"), height=2).pack(fill="x")
        tk.Label(self, text="  [ 📊 ]  CRITICAL VALUE TABLES",
                 font=("Consolas", 13, "bold"), bg=th("SURFACE"), fg=th("CYAN"), pady=10).pack(fill="x")
        tk.Frame(self, bg=th("CYAN"), height=1).pack(fill="x")
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        zf = tk.Frame(nb, bg=th("SURFACE")); nb.add(zf, text="  Z Table  ")
        z_data = "  α (one-tail)  │  α/2 (two-tail)  │  Z_crit\n"
        z_data += "  ─────────────┼──────────────────┼─────────\n"
        for a1, a2, z in [(0.10,0.05,1.6449),(0.05,0.025,1.9600),
                          (0.025,0.0125,2.2414),(0.02,0.01,2.3263),
                          (0.01,0.005,2.5758),(0.005,0.0025,2.8070)]:
            z_data += f"  {a1:<14} │  {a2:<16} │  {z:.4f}\n"
        t_z = tk.Text(zf, font=("Consolas", 10), bg=th("SURFACE"), fg=th("CYAN"),
                relief="flat", bd=0, highlightthickness=0,
                padx=14, pady=10, state="normal", height=14)
        t_z.pack(fill="both", expand=True)
        t_z.insert("1.0", z_data); t_z.config(state="disabled")
        tf2 = tk.Frame(nb, bg=th("SURFACE")); nb.add(tf2, text="  t Table  ")
        t_head = f"  {'df':<5} │  {'α=0.10':>8}  │  {'α=0.05':>8}  │  {'α=0.02':>8}  │  {'α=0.01':>8}\n"
        t_head += "  " + "─"*58 + "\n"
        t_data = t_head
        for df in [1,2,3,4,5,6,7,8,9,10,12,15,20,25,29,30,40,60,120]:
            row = f"  {df:<5} │"
            for a in [0.10, 0.05, 0.02, 0.01]:
                row += f"  {t_crit(df,a):>8.4f}  │"
            t_data += row + "\n"
        t_box = tk.Text(tf2, font=("Consolas", 10), bg=th("SURFACE"), fg=th("CYAN"),
                        relief="flat", bd=0, highlightthickness=0, padx=14, pady=10, state="normal")
        sc2 = tk.Scrollbar(tf2, orient="vertical", command=t_box.yview)
        t_box.config(yscrollcommand=sc2.set)
        t_box.pack(side="left", fill="both", expand=True)
        sc2.pack(side="right", fill="y")
        t_box.insert("1.0", t_data); t_box.config(state="disabled")
        cf = tk.Frame(nb, bg=th("SURFACE")); nb.add(cf, text="  χ² Table  ")
        c_head = f"  {'df':<5} │  {'α=0.10':>10}  │  {'α=0.05':>10}  │  {'α=0.025':>10}  │  {'α=0.01':>10}\n"
        c_head += "  " + "─"*66 + "\n"
        c_data = c_head
        for df in range(1, 31):
            row = f"  {df:<5} │"
            for a in [0.10, 0.05, 0.025, 0.01]:
                row += f"  {stats.chi2.ppf(1-a,df):>10.4f}  │"
            c_data += row + "\n"
        c_box = tk.Text(cf, font=("Consolas", 10), bg=th("SURFACE"), fg=th("CYAN"),
                        relief="flat", bd=0, highlightthickness=0, padx=14, pady=10, state="normal")
        sc3 = tk.Scrollbar(cf, orient="vertical", command=c_box.yview)
        c_box.config(yscrollcommand=sc3.set)
        c_box.pack(side="left", fill="both", expand=True)
        sc3.pack(side="right", fill="y")
        c_box.insert("1.0", c_data); c_box.config(state="disabled")
        self.bind("<Escape>", lambda e: self.destroy())


class HistoryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("[ F3 ] CALCULATION HISTORY")
        self.geometry("700x520")
        self.configure(bg=th("BG"))
        self.resizable(True, True)
        tk.Frame(self, bg=th("CYAN"), height=2).pack(fill="x")
        hdr = tk.Frame(self, bg=th("SURFACE")); hdr.pack(fill="x")
        tk.Label(hdr, text="  [ ⏱ ]  CALCULATION HISTORY",
                 font=("Consolas", 13, "bold"), bg=th("SURFACE"), fg=th("CYAN"), pady=10).pack(side="left")
        btns = tk.Frame(hdr, bg=th("SURFACE")); btns.pack(side="right", padx=12, pady=7)
        for txt, cmd in [("[ EXPORT ]", export_history_txt), ("[ CLEAR ]", self._clear)]:
            b = tk.Button(btns, text=txt, font=("Consolas", 9),
                          bg=th("SURF3"), fg=th("TEXT2"), relief="flat",
                          cursor="hand2", padx=10, pady=5, command=cmd)
            b.pack(side="left", padx=4)
        tk.Frame(self, bg=th("CYAN"), height=1).pack(fill="x")
        sf = tk.Frame(self, bg=th("BG")); sf.pack(fill="both", expand=True, padx=8, pady=8)
        sc = tk.Scrollbar(sf, orient="vertical")
        self.lb = tk.Listbox(sf, font=("Consolas", 10),
                             bg=th("SURFACE"), fg=th("CYAN"),
                             selectbackground=th("GOLD_DIM"), selectforeground=th("CYAN"),
                             relief="flat", yscrollcommand=sc.set, bd=0,
                             highlightthickness=0, activestyle="none")
        sc.config(command=self.lb.yview)
        self.lb.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self._refresh()
        self.bind("<Escape>", lambda e: self.destroy())

    def _refresh(self):
        self.lb.delete(0,"end")
        if not calc_history:
            self.lb.insert("end","  >> NO CALCULATIONS YET"); return
        for h in reversed(calc_history):
            self.lb.insert("end", f"  [{h['time']}]  {h['topic']}")
            self.lb.insert("end", f"           {h['summary']}")
            self.lb.insert("end", "  "+"─"*60)

    def _clear(self):
        calc_history.clear(); self._refresh()


# ── AI Integration ─────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = ""

_TOPIC_PROMPTS = {
    "normal":    "Extract: mu (mean), sigma (std dev), a (lower value), b (upper value, optional), mode from ['P(a<X<b)','P(X<a)','P(X>a)']. Return JSON only.",
    "samp_prop": "Extract: P (population proportion 0-1), n (sample size), a (lower), b (upper, optional), mode from ['P(a<p<b)','P(p<a)','P(p>a)']. Return JSON only.",
    "samp_var":  "Extract: sigma2 (population variance), n (sample size), a (lower), b (upper, optional), mode from ['P(a<s²<b)','P(s²<a)','P(s²>a)']. Return JSON only.",
    "ci_mean":   "Extract: xbar (sample mean), n (sample size), sigma (population std dev, optional), s (sample std dev, optional), conf (confidence level 0-1, default 0.95), case (1=sigma known, 2=n>=30 unknown sigma, 3=n<30). Return JSON only.",
    "ci_prop":   "Extract: p (sample proportion 0-1), n (sample size), conf (confidence level 0-1, default 0.95). Return JSON only.",
    "ci_var":    "Extract: s2 (sample variance), n (sample size), conf (confidence level 0-1, default 0.95). Return JSON only.",
    "test_mean": "Extract: xbar (sample mean), mu0 (hypothesized mean), n (sample size), sigma (population std dev, optional), s (sample std dev, optional), alpha (significance level, default 0.05), tail from ['Two-tailed','Right-tailed','Left-tailed']. Return JSON only.",
    "test_prop": "Extract: p (sample proportion), P0 (hypothesized proportion), n (sample size), alpha (significance level, default 0.05), tail from ['Two-tailed','Right-tailed','Left-tailed']. Return JSON only.",
    "test_var":  "Extract: s2 (sample variance), sigma20 (hypothesized variance), n (sample size), alpha (significance level, default 0.05), tail from ['Two-tailed','Right-tailed','Left-tailed']. Return JSON only.",
}

def _call_claude_api(problem_text, panel_id, callback):
    import json as _json
    topic_hint = _TOPIC_PROMPTS.get(panel_id, "Extract all numerical values and statistical parameters. Return JSON only.")
    system_msg = (
        "You are a statistics assistant. Given a statistics problem, extract the numerical "
        "values and parameters needed to solve it. " + topic_hint +
        " Return ONLY a valid JSON object with no extra text, no markdown, no explanation."
    )
    body = _json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 400,
        "system": system_msg,
        "messages": [{"role": "user", "content": problem_text}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
            text = data["content"][0]["text"].strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"): text = text[4:]
            result = _json.loads(text.strip())
            callback(result)
    except Exception as ex:
        callback(None, str(ex))


# ── Base Panel ─────────────────────────────────────────────────────────────────
class BasePanel(tk.Frame):
    panel_id = ""

    def __init__(self, master, plot_frame, status_var, root):
        super().__init__(master, bg=th("BG"))
        self.pf = plot_frame
        self.sv = status_var
        self.root = root
        self._res_frame = None

    def _save_vals(self, d: dict):
        last_values[self.panel_id] = d

    def _load_vals(self, d: dict):
        saved = last_values.get(self.panel_id, {})
        for k, var in d.items():
            if k in saved:
                var.set(saved[k])

    def add_copy_btn(self, parent, res_frame):
        self._res_frame = res_frame
        bar = tk.Frame(parent, bg=th("BG")); bar.pack(fill="x", padx=3, pady=(0, 3))
        pill = tk.Frame(bar, bg=th("SURF3"),
                        highlightthickness=1, highlightbackground=th("BORDER2"))
        pill.pack(side="left", padx=(0, 8), pady=2)
        self._steps_var = tk.BooleanVar(value=_show_steps[0])

        def _lbl_text(): return "  [■] SHOW STEPS  " if self._steps_var.get() else "  [□] RESULT ONLY  "
        def _lbl_col():  return th("CYAN") if self._steps_var.get() else th("TEXT3")

        self._steps_lbl = tk.Label(pill, text=_lbl_text(),
                                   font=("Consolas", 9, "bold"),
                                   bg=th("SURF3"), fg=_lbl_col(),
                                   cursor="hand2", padx=5, pady=5)
        self._steps_lbl.pack()

        def _toggle(e=None):
            self._steps_var.set(not self._steps_var.get())
            _show_steps[0] = self._steps_var.get()
            self._steps_lbl.config(text=_lbl_text(), fg=_lbl_col())

        self._steps_lbl.bind("<Button-1>", _toggle)
        pill.bind("<Button-1>", _toggle)

        for txt, cmd in [("[COPY]", self._copy), ("[PNG]", export_plot_png)]:
            b = tk.Button(bar, text=txt, font=("Consolas", 9),
                          bg=th("SURF3"), fg=th("TEXT2"), relief="flat",
                          cursor="hand2", pady=5, padx=10, bd=0,
                          highlightthickness=1, highlightbackground=th("BORDER2"),
                          activebackground=th("ACCENT_DIM"),
                          activeforeground=th("CYAN"), command=cmd)
            b.pack(side="right", padx=2)
            b.bind("<Enter>", lambda e,b=b: b.config(bg=th("ACCENT_DIM"), fg=th("CYAN")))
            b.bind("<Leave>", lambda e,b=b: b.config(bg=th("SURF3"), fg=th("TEXT2")))

    def _copy(self):
        if not self._res_frame: return
        lines = []
        def collect(w):
            if isinstance(w, tk.Label) and w.cget("text").strip():
                lines.append(w.cget("text").strip())
            for c in w.winfo_children(): collect(c)
        collect(self._res_frame)
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lines))
        self.sv.set(">> RESULTS COPIED TO CLIPBOARD")

    def set_status(self, msg): self.sv.set(msg)

    def log(self, topic, summary):
        calc_history.append({"time": datetime.now().strftime("%H:%M:%S"),
                              "topic": topic, "summary": summary})

    def clear_res(self):
        if self._res_frame:
            for w in self._res_frame.winfo_children(): w.destroy()

    def bind_entries_return(self, cmd):
        def _recurse(w):
            if isinstance(w, (tk.Entry, ValidEntry)):
                w.bind("<Return>", lambda e: cmd())
            for child in w.winfo_children():
                _recurse(child)
        self.after_idle(lambda: _recurse(self))

    def add_ai_extract(self, parent):
        ai_card = tk.Frame(parent, bg=th("MAGENTA"), padx=1, pady=1)
        ai_card.pack(fill="x", padx=3, pady=(0, 7))
        inner = tk.Frame(ai_card, bg=th("SURF2")); inner.pack(fill="x")
        hrow = tk.Frame(inner, bg=th("SURF2")); hrow.pack(fill="x", padx=10, pady=(7, 3))
        tk.Frame(hrow, bg=th("MAGENTA"), width=3).pack(side="left", fill="y", padx=(0, 8))
        tk.Label(hrow, text="[AI] PROBLEM READER",
                 font=("Consolas", 10, "bold"),
                 bg=th("SURF2"), fg=th("MAGENTA")).pack(side="left")
        tk.Label(hrow, text=" — paste problem, AI fills fields",
                 font=("Consolas", 9),
                 bg=th("SURF2"), fg=th("TEXT3")).pack(side="left", padx=5)
        self._ai_text = tk.Text(inner, height=4, font=("Consolas", 10),
                                bg=th("SURF3"), fg=th("TEXT"),
                                insertbackground=th("MAGENTA"),
                                relief="flat", bd=0,
                                highlightthickness=2,
                                highlightbackground=th("BORDER2"),
                                highlightcolor=th("MAGENTA"),
                                wrap="word", padx=10, pady=8)
        self._ai_text.pack(fill="x", padx=10, pady=(0, 5))
        PLACEHOLDER = "Paste problem here or type...\ne.g.: A sample of 15 students had mean 40.6 and s=6. Test if μ=36.7 at α=0.05"
        self._ai_text.insert("1.0", PLACEHOLDER)
        self._ai_text.config(fg=th("TEXT3"))

        def _clear_placeholder(e=None):
            current = self._ai_text.get("1.0", "end-1c").strip()
            if current == PLACEHOLDER.replace("\\n", "\n") or current.startswith("e.g.:"):
                self._ai_text.delete("1.0", "end")
                self._ai_text.config(fg=th("TEXT"))

        def _on_paste(e=None):
            # Auto-extract after paste
            self.root.after(100, lambda: self._auto_extract())

        self._ai_text.bind("<FocusIn>", _clear_placeholder)
        self._ai_text.bind("<Control-v>", _on_paste)
        self._ai_text.bind("<Button-3>", lambda e: self._show_text_context(e))

    def _show_text_context(self, event):
        menu = tk.Menu(self, tearoff=0, bg=th("SURF3"), fg=th("CYAN"),
                       activebackground=th("ACCENT_DIM"), activeforeground=th("CYAN"))
        menu.add_command(label="Cut", command=lambda: self._ai_text.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: self._ai_text.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: self._ai_text.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: self._ai_text.tag_add("sel", "1.0", "end"))
        menu.add_separator()
        menu.add_command(label="🧠 Auto Extract", command=self._run_ai_extract)
        menu.tk_popup(event.x_root, event.y_root)

    def _auto_extract(self):
        """Auto-extract when text is pasted"""
        text = self._ai_text.get("1.0", "end-1c").strip()
        if len(text) > 20 and not text.startswith("e.g.:"):
            self._ai_status.config(text=">> TEXT DETECTED - CLICK EXTRACT", fg=th("GLOW_CYAN"))

        brow = tk.Frame(inner, bg=th("SURF2")); brow.pack(fill="x", padx=10, pady=(0, 8))
        self._ai_status = tk.Label(brow, text="",
                                   font=("Consolas", 9),
                                   bg=th("SURF2"), fg=th("TEXT3"), anchor="w")
        self._ai_status.pack(side="left", fill="x", expand=True)
        self._ai_btn = tk.Button(brow, text="[ EXTRACT FIELDS ]",
                                 font=("Consolas", 9, "bold"),
                                 bg=th("BG"), fg=th("MAGENTA"),
                                 relief="flat", cursor="hand2",
                                 padx=12, pady=5, bd=0,
                                 highlightthickness=1,
                                 highlightbackground=th("MAGENTA"),
                                 activebackground=th("MAGENTA"),
                                 activeforeground=th("TEXT"),
                                 command=self._run_ai_extract)
        self._ai_btn.pack(side="right")
        self._ai_btn.bind("<Enter>", lambda e: self._ai_btn.config(bg=th("MAGENTA"), fg=th("TEXT")))
        self._ai_btn.bind("<Leave>", lambda e: self._ai_btn.config(bg=th("BG"), fg=th("MAGENTA")))
        if not ANTHROPIC_API_KEY.strip():
            tk.Label(inner,
                     text="  ⚠  Set ANTHROPIC_API_KEY at the top of the file to enable AI",
                     font=("Consolas", 9), bg=th("SURF2"), fg=th("GOLD"),
                     justify="left").pack(anchor="w", padx=10, pady=(0, 5))

    def _run_ai_extract(self):
        problem = self._ai_text.get("1.0", "end-1c").strip()
        if not problem or problem.startswith("e.g.:"):
            self._ai_status.config(text=">> PASTE A PROBLEM FIRST", fg=th("GOLD"))
            return

        # First try smart local parser (no API needed)
        smart_result = smart_extract(problem, self.panel_id)
        if smart_result:
            filled = self.fill_from_dict(smart_result)
            if filled > 0:
                self._ai_status.config(
                    text=f">> {filled} FIELD(S) AUTO-FILLED FROM TEXT",
                    fg=th("GREEN"))
                self.set_status(f"Smart parser filled {filled} fields")
                return

        # Fallback to AI API if key is set
        if not ANTHROPIC_API_KEY.strip():
            self._ai_status.config(text=">> NO API KEY SET - Smart parser tried", fg=th("MAGENTA"))
            return

        self._ai_btn.config(state="disabled", text="  EXTRACTING...")
        self._ai_status.config(text=">> CALLING CLAUDE API...", fg=th("TEXT3"))

        def _on_done(result, err=None):
            def _ui():
                self._ai_btn.config(state="normal", text="[ EXTRACT FIELDS ]")
                if result is None:
                    self._ai_status.config(text=f"ERROR: {err}", fg=th("MAGENTA"))
                    return
                filled = self.fill_from_dict(result)
                self._ai_status.config(
                    text=f">> {filled} FIELD(S) FILLED — CHECK & CALCULATE",
                    fg=th("GREEN"))
                self.set_status(f"AI extracted {filled} fields from problem text")
            self.root.after(0, _ui)

        threading.Thread(
            target=_call_claude_api,
            args=(problem, self.panel_id, _on_done),
            daemon=True
        ).start()

    def fill_from_dict(self, d: dict) -> int:
        """Fill entry fields from a dict with smart key mapping."""
        filled = 0

        # Key mapping: smart_extract key → panel variable name
        key_map = {
            # Test Mean / CI Mean
            'mean': ['mean', 'xbar'],
            'sigma': ['sigma', 'sig'],
            's': ['s', 'sd'],
            'mu0': ['mu0', 'mu'],

            # Test Prop / CI Prop
            'p': ['p', 'p_hat'],
            'P0': ['P0', 'P'],

            # Test Var / CI Var
            's2': ['s2', 'variance'],
            'sig20': ['sig20', 'sig2'],

            # Common
            'n': ['n'],
            'alpha': ['alpha'],
            'conf': ['conf'],
            'tail': ['tail'],
            'case': ['case'],
        }

        for key, val in d.items():
            mapped = False
            # Try mapped names first
            if key in key_map:
                for var_name in key_map[key]:
                    if hasattr(self, var_name):
                        try:
                            getattr(self, var_name).set(str(val))
                            filled += 1
                            mapped = True
                            break
                        except:
                            pass

            # Fallback: try exact key name
            if not mapped and hasattr(self, key):
                try:
                    getattr(self, key).set(str(val))
                    filled += 1
                except:
                    pass

        return filled


# ═══════════════════════════════════════════════════════════════════════════════
#  PANELS — ALL LOGIC PRESERVED, CYBERPUNK STYLED
# ═══════════════════════════════════════════════════════════════════════════════

class NormalDistPanel(BasePanel):
    panel_id = "normal"
    def __init__(self, master, pf, sv, root):
        super().__init__(master, pf, sv, root)
        self._build()

    def _build(self):
        section_header(self, "Normal Distribution  P(a < X < b)", "𝒩", th("CYAN"))
        c = card(self)
        self.mu=tk.StringVar(); self.sig=tk.StringVar()
        self.a=tk.StringVar();  self.b=tk.StringVar()
        self.mode=tk.StringVar(value="P(a<X<b)")
        g = tk.Frame(c, bg=th("SURF2")); g.pack(fill="x", pady=4)
        row_field(g,"Mean  μ",self.mu,0,tooltip="Population or distribution mean")
        row_field(g,"Std Dev  σ",self.sig,1,tooltip="Must be positive (σ > 0)")
        row_field(g,"Value  a",self.a,2,tooltip="Lower bound")
        row_field(g,"Value  b",self.b,3,tooltip="Upper bound (P(a<X<b) mode only)")
        make_combo(g,self.mode,["P(a<X<b)","P(X<a)","P(X>a)"],4)

        zp = card(self)
        tk.Label(zp, text="  [ Z ] ROUNDING PRECISION",
                 font=("Consolas", 11, "bold"), bg=th("SURF2"), fg=th("GOLD")).pack(
                 anchor="w", padx=14, pady=(8,3))
        rf = tk.Frame(zp, bg=th("SURF2")); rf.pack(fill="x", padx=14, pady=(0,8))
        self.zprec = tk.IntVar(value=_z_prec[0])
        opts = [
            (4, "4 dp — Exact scipy  (e.g. Z = −1.3333,  P = 0.0912)",  th("CYAN")),
            (2, "2 dp — Textbook Z-table  (e.g. Z = −1.33,  P = 0.0918)", th("GOLD2")),
        ]
        for val, txt, col in opts:
            rb = tk.Radiobutton(rf, text=txt, variable=self.zprec, value=val,
                                font=("Consolas", 10), bg=th("SURF2"), fg=col,
                                selectcolor=th("SURFACE"), activebackground=th("SURF3"),
                                cursor="hand2",
                                command=lambda: _z_prec.__setitem__(0, self.zprec.get()))
            rb.pack(anchor="w", pady=2)
        tk.Label(zp,
            text="  ⓘ  Textbook mode rounds Z to 2dp before Φ(Z) lookup.",
            font=("Consolas", 9), bg=th("SURF2"), fg=th("TEXT3"),
            justify="left", wraplength=420).pack(anchor="w", padx=14, pady=(0,8))

        self._load_vals({"mu":self.mu,"sig":self.sig,"a":self.a,"b":self.b})
        self.add_ai_extract(self)
        self.res = card(self); self.add_copy_btn(self, self.res)
        calc_button(self,"  >> CALCULATE",self._calc)
        self.bind_entries_return(self._calc)

    def fill_from_dict(self, d):
        n = 0
        for key, var in [("mu",self.mu),("sigma",self.sig),("a",self.a),("b",self.b)]:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        if "mode" in d and d["mode"] in ["P(a<X<b)","P(X<a)","P(X>a)"]:
            self.mode.set(d["mode"]); n += 1
        return n

    def _calc(self):
        try:
            mu=float(self.mu.get()); sig=float(self.sig.get())
            a=float(self.a.get())
            b=float(self.b.get()) if self.b.get().strip() else a
            mode=self.mode.get()
        except:
            messagebox.showerror("INPUT ERROR","Please check all fields"); return
        if sig<=0:
            messagebox.showerror("ERROR","σ must be > 0"); return
        _z_prec[0] = self.zprec.get()
        self._save_vals({"mu":self.mu,"sig":self.sig,"a":self.a,"b":self.b})
        self.clear_res()
        prec = _z_prec[0]
        Za_exact = (a-mu)/sig;  Za = round(Za_exact, prec)
        Zb_exact = (b-mu)/sig;  Zb = round(Zb_exact, prec)
        mode_tag = "2dp textbook" if prec==2 else "4dp exact"

        if mode=="P(X<a)":
            prob=phi(Za); lo,hi=mu-4*sig,a
            lines=[
                (result_row,[f"Z_exact = ({a} − {mu}) / {sig} = {Za_exact:.6f}", "#00E5FF"]),
                (result_row,[f"Z_used  = {Za}   [{mode_tag}]", "#FFD700"]),
                (result_row,[f"P(X < {a})  =  Φ({Za})  =  {prob:.4f}", "#00FF88"]),
                (result_answer,[f"✦  Probability  =  {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        elif mode=="P(X>a)":
            prob=1-phi(Za); lo,hi=a,mu+4*sig
            lines=[
                (result_row,[f"Z_exact = ({a} − {mu}) / {sig} = {Za_exact:.6f}", "#00E5FF"]),
                (result_row,[f"Z_used  = {Za}   [{mode_tag}]", "#FFD700"]),
                (result_row,[f"P(X > {a})  =  1 − Φ({Za})  =  {prob:.4f}", "#00FF88"]),
                (result_answer,[f"✦  Probability  =  {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        else:
            prob=phi(Zb)-phi(Za); lo,hi=a,b
            lines=[
                (result_row,[f"Za_exact = {Za_exact:.6f}   Zb_exact = {Zb_exact:.6f}", "#00E5FF"]),
                (result_row,[f"Za_used  = {Za}   Zb_used  = {Zb}   [{mode_tag}]", "#FFD700"]),
                (result_row,[f"P({a} < X < {b})  =  Φ({Zb}) − Φ({Za})  =  {prob:.4f}", "#00FF88"]),
                (result_answer,[f"✦  Probability  =  {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]

        AnimatedResults(self.res, self.root, lines, delay=80)
        self.set_status(f">> NORMAL DIST  Z={Za} [{mode_tag}]  P={prob:.4f}  ({prob*100:.2f}%)")
        self.log("Normal Distribution", f"μ={mu}, σ={sig}, Z={Za} ({mode_tag}), P={prob:.4f}")
        fig,ax=make_fig(); draw_normal_shade(ax,mu,sig,lo,hi,label=f"P={prob:.4f}")
        ax.axvline(a,color=th("MAGENTA"),linewidth=1.2,linestyle=":",alpha=0.8)
        if mode=="P(a<X<b)": ax.axvline(b,color=th("MAGENTA"),linewidth=1.2,linestyle=":",alpha=0.8)
        ax.legend(facecolor=th("SURF2"),edgecolor=th("BORDER2"),labelcolor=th("TEXT2"),fontsize=10)
        style_ax(ax,f"Normal  μ={mu},  σ={sig}  |  Z={Za}  |  P={prob:.4f}")
        embed_plot(fig,self.pf)


class SamplingPropPanel(BasePanel):
    panel_id = "samp_prop"
    def __init__(self, master, pf, sv, root):
        super().__init__(master, pf, sv, root); self._build()

    def _build(self):
        section_header(self,"Sampling Distribution of  p̂","𝒑",th("CYAN"))
        c=card(self)
        self.P=tk.StringVar(); self.n=tk.StringVar()
        self.a=tk.StringVar(); self.b=tk.StringVar()
        self.mode=tk.StringVar(value="P(a<p<b)")
        g=tk.Frame(c,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Population Proportion  P",self.P,0,tooltip="0 < P < 1")
        row_field(g,"Sample Size  n",self.n,1,kind="int",tooltip="Positive integer ≥ 1")
        row_field(g,"Value  a",self.a,2); row_field(g,"Value  b",self.b,3)
        make_combo(g,self.mode,["P(a<p<b)","P(p<a)","P(p>a)"],4)
        self._load_vals({"P":self.P,"n":self.n,"a":self.a,"b":self.b})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> CALCULATE",self._calc)
        self.bind_entries_return(self._calc)

    def fill_from_dict(self, d):
        n = 0
        for key, var in [("P",self.P),("n",self.n),("a",self.a),("b",self.b)]:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        if "mode" in d and d["mode"] in ["P(a<p<b)","P(p<a)","P(p>a)"]:
            self.mode.set(d["mode"]); n += 1
        return n

    def _calc(self):
        try:
            P=float(self.P.get()); n=int(self.n.get())
            a=float(self.a.get()); b=float(self.b.get()) if self.b.get().strip() else a
            mode=self.mode.get()
        except:
            messagebox.showerror("INPUT ERROR","Please check all fields"); return
        if not (0<P<1):
            messagebox.showerror("ERROR","0 < P < 1 required"); return
        self._save_vals({"P":self.P,"n":self.n,"a":self.a,"b":self.b})
        sp=math.sqrt(P*(1-P)/n)
        self.clear_res(); Za=(a-P)/sp
        if mode=="P(p<a)":
            prob=phi(Za); lo,hi=P-4*sp,a
            lines=[(result_row,[f"μ_p̂ = {P}   σ_p̂ = {sp:.6f}", "#00E5FF"]),
                   (result_row,[f"Z = ({a} − {P}) / {sp:.4f} = {Za:.4f}", "#00FF88"]),
                   (result_row,[f"P(p̂ < {a})  =  Φ({Za:.4f})  =  {prob:.4f}", "#00FF88"]),
                   (result_answer,[f"✦  P = {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        elif mode=="P(p>a)":
            prob=1-phi(Za); lo,hi=a,P+4*sp
            lines=[(result_row,[f"μ_p̂ = {P}   σ_p̂ = {sp:.6f}", "#00E5FF"]),
                   (result_row,[f"Z = {Za:.4f}", "#00FF88"]),
                   (result_row,[f"P(p̂ > {a})  =  1 − Φ({Za:.4f})  =  {prob:.4f}", "#00FF88"]),
                   (result_answer,[f"✦  P = {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        else:
            Zb=(b-P)/sp; prob=phi(Zb)-phi(Za); lo,hi=a,b
            lines=[(result_row,[f"μ_p̂ = {P}   σ_p̂ = {sp:.6f}", "#00E5FF"]),
                   (result_row,[f"Za = {Za:.4f}   Zb = {Zb:.4f}", "#00E5FF"]),
                   (result_row,[f"P({a} < p̂ < {b})  =  Φ({Zb:.4f}) − Φ({Za:.4f})  =  {prob:.4f}", "#00FF88"]),
                   (result_answer,[f"✦  P = {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        AnimatedResults(self.res,self.root,lines,delay=80)
        self.set_status(f">> SAMPLING p̂  P={prob:.4f}")
        self.log("Sampling Prop",f"P={P}, n={n}, prob={prob:.4f}")
        fig,ax=make_fig(); draw_normal_shade(ax,P,sp,lo,hi,label=f"P={prob:.4f}")
        ax.legend(facecolor=th("SURF2"),edgecolor=th("BORDER2"),labelcolor=th("TEXT2"),fontsize=10)
        style_ax(ax,f"Sampling Dist of p̂  (P={P}, n={n})")
        embed_plot(fig,self.pf)


class SamplingVarPanel(BasePanel):
    panel_id="samp_var"
    def __init__(self,master,pf,sv,root):
        super().__init__(master,pf,sv,root); self._build()

    def _build(self):
        section_header(self,"Sampling Distribution of  s²  (χ²)","χ",th("ACCENT2"))
        c=card(self)
        self.sig2=tk.StringVar(); self.n=tk.StringVar()
        self.a=tk.StringVar();    self.b=tk.StringVar()
        self.mode=tk.StringVar(value="P(a<s²<b)")
        g=tk.Frame(c,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Population Variance  σ²",self.sig2,0)
        row_field(g,"Sample Size  n",self.n,1,kind="int")
        row_field(g,"Value  a",self.a,2); row_field(g,"Value  b",self.b,3)
        make_combo(g,self.mode,["P(a<s²<b)","P(s²<a)","P(s²>a)"],4)
        self._load_vals({"sig2":self.sig2,"n":self.n,"a":self.a,"b":self.b})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> CALCULATE",self._calc)
        self.bind_entries_return(self._calc)

    def fill_from_dict(self, d):
        n = 0
        for key, var in [("sigma2",self.sig2),("n",self.n),("a",self.a),("b",self.b)]:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        if "mode" in d and d["mode"] in ["P(a<s²<b)","P(s²<a)","P(s²>a)"]:
            self.mode.set(d["mode"]); n += 1
        return n

    def _calc(self):
        try:
            sig2=float(self.sig2.get()); n=int(self.n.get())
            a=float(self.a.get()); b=float(self.b.get()) if self.b.get().strip() else a
            mode=self.mode.get()
        except:
            messagebox.showerror("INPUT ERROR","Please check all fields"); return
        if sig2 <= 0:
            messagebox.showerror("ERROR","σ² must be > 0"); return
        if n < 2:
            messagebox.showerror("ERROR","n must be ≥ 2"); return
        self._save_vals({"sig2":self.sig2,"n":self.n,"a":self.a,"b":self.b})
        df=n-1; chi_a=df*a/sig2; chi_b=df*b/sig2
        self.clear_res()
        if mode=="P(s²<a)":
            prob=stats.chi2.cdf(chi_a,df); lo,hi=0,chi_a
            lines=[(result_row,[f"df = n−1 = {df}", "#00E5FF"]),
                   (result_row,[f"χ²_a = (n−1)·a / σ²  =  {df}×{a}/{sig2}  =  {chi_a:.4f}", "#A8D8F0"]),
                   (result_row,[f"P(s² < {a})  =  P(χ² < {chi_a:.4f})  =  {prob:.4f}", "#00FF88"]),
                   (result_answer,[f"✦  P = {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        elif mode=="P(s²>a)":
            prob=1-stats.chi2.cdf(chi_a,df); lo,hi=chi_a,df+5*math.sqrt(2*df)
            lines=[(result_row,[f"df = {df}", "#00E5FF"]),
                   (result_row,[f"χ²_a = {chi_a:.4f}", "#A8D8F0"]),
                   (result_row,[f"P(s² > {a})  =  1 − P(χ² < {chi_a:.4f})  =  {prob:.4f}", "#00FF88"]),
                   (result_answer,[f"✦  P = {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        else:
            prob=stats.chi2.cdf(chi_b,df)-stats.chi2.cdf(chi_a,df); lo,hi=chi_a,chi_b
            lines=[(result_row,[f"df = {df}", "#00E5FF"]),
                   (result_row,[f"χ²_a = {chi_a:.4f}   χ²_b = {chi_b:.4f}", "#00E5FF"]),
                   (result_row,[f"P({a} < s² < {b})  =  P({chi_a:.4f} < χ² < {chi_b:.4f})  =  {prob:.4f}", "#00FF88"]),
                   (result_answer,[f"✦  P = {prob:.4f}   ({prob*100:.2f}%)",th("GOLD2")])]
        AnimatedResults(self.res,self.root,lines,delay=80)
        self.set_status(f">> CHI-SQUARE  P={prob:.4f}")
        self.log("Sampling Var (χ²)",f"σ²={sig2}, n={n}, prob={prob:.4f}")
        fig,ax=make_fig(); draw_chi_shade(ax,df,lo,hi,color=th("GOLD"))
        style_ax(ax,f"Chi-Square  df={df}"); embed_plot(fig,self.pf)


class CIMeanPanel(BasePanel):
    panel_id="ci_mean"
    def __init__(self,master,pf,sv,root):
        super().__init__(master,pf,sv,root); self._build()

    def _build(self):
        section_header(self,"Confidence Interval for  μ","μ",th("GREEN"))
        sel=card(self)
        tk.Label(sel,text="  [ SELECT CASE ]",font=("Consolas",11,"bold"),
                 bg=th("SURF2"),fg=th("GOLD")).pack(anchor="w",padx=14,pady=(8,5))
        self.case_var=tk.IntVar(value=1)
        for val,txt,col in [(1,"CASE 1 — σ known  >>  Z",th("CYAN")),
                            (2,"CASE 2 — σ unknown, n ≥ 30  >>  Z",th("GREEN")),
                            (3,"CASE 3 — σ unknown, n < 30  >>  t",th("GOLD2"))]:
            tk.Radiobutton(sel,text=txt,variable=self.case_var,value=val,
                           font=("Consolas",10,"bold"),
                           bg=th("SURF2"),fg=col,selectcolor=th("SURFACE"),
                           activebackground=th("SURF3"),command=self._on_case,
                           cursor="hand2").pack(anchor="w",padx=18,pady=3)
        tk.Frame(sel,bg=th("BORDER2"),height=1).pack(fill="x",padx=12,pady=6)

        mode_f = tk.Frame(sel, bg=th("SURF2")); mode_f.pack(fill="x", padx=12, pady=(0,8))
        tk.Label(mode_f, text="Input mode:", font=("Consolas",10),
                 bg=th("SURF2"), fg=th("TEXT2")).pack(side="left", padx=(2,8))
        self.input_mode = tk.StringVar(value="summary")
        for val, txt in [("summary","Summary  (x̄, n, s/σ)"), ("raw","Raw data")]:
            tk.Radiobutton(mode_f, text=txt, variable=self.input_mode, value=val,
                           font=("Consolas",10), bg=th("SURF2"), fg=th("CYAN"),
                           selectcolor=th("SURFACE"), activebackground=th("SURF3"),
                           cursor="hand2", command=self._on_input_mode).pack(side="left", padx=5)

        inp=card(self)
        self.xbar=tk.StringVar(); self.n=tk.StringVar()
        self.sig=tk.StringVar();   self.s=tk.StringVar()
        self.conf=tk.StringVar(value="0.95")
        g=tk.Frame(inp,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Sample Mean  x̄",self.xbar,0)
        row_field(g,"Sample Size  n",self.n,1,kind="int")
        lbl(g,"σ — population std dev",font=("Consolas",10)).grid(row=2,column=0,sticky="w",padx=(16,10),pady=5)
        self.sig_e=ValidEntry(g,self.sig,tooltip_text="Case 1: known population σ")
        self.sig_e.grid(row=2,column=1,padx=(0,16),pady=4,ipady=5)
        lbl(g,"<< Case 1",font=("Consolas",9),fg=th("CYAN")).grid(row=2,column=2,sticky="w")
        lbl(g,"s — sample std dev",font=("Consolas",10)).grid(row=3,column=0,sticky="w",padx=(16,10),pady=5)
        self.s_e=ValidEntry(g,self.s,tooltip_text="Cases 2 & 3: sample std dev")
        self.s_e.grid(row=3,column=1,padx=(0,16),pady=4,ipady=5)
        lbl(g,"<< Case 2&3",font=("Consolas",9),fg=th("GREEN")).grid(row=3,column=2,sticky="w")
        conf_combo(g,self.conf,4)

        self.raw_frame = card(self)
        tk.Label(self.raw_frame, text="  [ RAW DATA INPUT ]",
                 font=("Consolas",10,"bold"), bg=th("SURF2"), fg=th("GOLD2")
                 ).pack(anchor="w", padx=10, pady=(7,2))
        self.raw_var = tk.StringVar()
        raw_entry = tk.Entry(self.raw_frame, textvariable=self.raw_var, font=("Consolas",11),
                             bg=th("SURFACE"), fg=th("CYAN"), insertbackground=th("GOLD2"),
                             relief="flat", highlightthickness=1,
                             highlightbackground=th("BORDER2"), highlightcolor=th("GOLD"))
        raw_entry.pack(fill="x", padx=10, pady=3, ipady=7)
        tk.Label(self.raw_frame,
                 text="  e.g.:  23 45 31 28 40 35   or   23,45,31,28,40,35",
                 font=("Consolas",9), bg=th("SURF2"), fg=th("TEXT3")).pack(anchor="w", padx=10, pady=(0,4))
        parse_btn = tk.Button(self.raw_frame, text=">> PARSE & FILL  x̄, n, s",
                              font=("Consolas",10,"bold"),
                              bg=th("SURF3"), fg=th("CYAN"), relief="flat",
                              cursor="hand2", pady=5, bd=0,
                              activebackground=th("GOLD_DIM"), activeforeground=th("TEXT"),
                              command=self._parse_raw)
        parse_btn.pack(fill="x", padx=10, pady=(0,6))
        self.raw_info_lbl = tk.Label(self.raw_frame, text="", font=("Consolas",10),
                                     bg=th("SURF2"), fg=th("GREEN"), justify="left")
        self.raw_info_lbl.pack(anchor="w", padx=10, pady=(0,5))
        self.raw_frame.pack_forget()

        ref=card(self)
        tk.Label(ref,text="  [ QUICK REFERENCE TABLE ]",font=("Consolas",10,"bold"),
                 bg=th("SURF2"),fg=th("GOLD_DIM")).pack(anchor="w",padx=12,pady=(7,2))
        self.tbl=tk.Label(ref,text="",font=("Consolas",10),bg=th("SURF2"),fg=th("TEXT3"),justify="left")
        self.tbl.pack(anchor="w",padx=16,pady=(0,8))
        self._load_vals({"xbar":self.xbar,"n":self.n,"sig":self.sig,"s":self.s})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> CALCULATE INTERVAL",self._calc)
        self.bind_entries_return(self._calc)
        self._on_case()

    def fill_from_dict(self, d):
        n = 0
        mapping = [("xbar",self.xbar),("x_bar",self.xbar),("mean",self.xbar),
                   ("n",self.n),("sigma",self.sig),("s",self.s),("conf",self.conf)]
        for key, var in mapping:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        if "case" in d:
            try: self.case_var.set(int(d["case"])); self._on_case(); n += 1
            except: pass
        return n

    def _on_input_mode(self):
        if self.input_mode.get() == "raw":
            self.raw_frame.pack(fill="x", pady=(0,3), padx=2)
        else:
            self.raw_frame.pack_forget()

    def _parse_raw(self):
        raw = self.raw_var.get().replace(",", " ")
        try:
            vals = [float(x) for x in raw.split() if x.strip()]
        except:
            messagebox.showerror("PARSE ERROR", "Could not parse values.\nUse numbers separated by spaces or commas.")
            return
        if len(vals) < 2:
            messagebox.showerror("ERROR", "Need at least 2 values"); return
        n    = len(vals)
        mean = sum(vals) / n
        s    = math.sqrt(sum((v - mean)**2 for v in vals) / (n - 1))
        self.xbar.set(f"{mean:.6f}")
        self.n.set(str(n))
        self.s.set(f"{s:.6f}")
        self.raw_info_lbl.config(
            text=f"  >> n={n}   x̄={mean:.4f}   s={s:.4f}   >> FIELDS FILLED")
        self.set_status(f"Raw data parsed: n={n}, x̄={mean:.4f}, s={s:.4f}")

    def _on_case(self):
        c=self.case_var.get()
        self.sig_e.configure(state="normal" if c==1 else "disabled",
                             bg=th("SURFACE") if c==1 else th("BG"))
        self.s_e.configure(state="normal" if c!=1 else "disabled",
                           bg=th("SURFACE") if c!=1 else th("BG"))
        if c in (1,2):
            self.tbl.configure(text=(" Conf │ α/2    │ Z_α/2\n"
                                     " ─────┼────────┼───────\n"
                                     "  90% │ 0.0500 │ 1.6449\n"
                                     "  95% │ 0.0250 │ 1.9600\n"
                                     "  98% │ 0.0100 │ 2.3263\n"
                                     "  99% │ 0.0050 │ 2.5758"),fg=th("TEXT3"))
        else:
            self.tbl.configure(text=(" df  │ t₀.₀₂₅  │ t₀.₀₀₅\n"
                                     " ────┼─────────┼────────\n"
                                     "  5  │ 2.5706  │ 4.0321\n"
                                     " 10  │ 2.2281  │ 3.1693\n"
                                     " 15  │ 2.1314  │ 2.9467\n"
                                     " 20  │ 2.0860  │ 2.8453\n"
                                     " 29  │ 2.0452  │ 2.7564"),fg=th("TEXT3"))

    def _step(self,num,txt,col):
        f=tk.Frame(self.res,bg=th("SURF2")); f.pack(fill="x",padx=10,pady=(6,0))
        tk.Frame(f,bg=col,width=3).pack(side="left",fill="y")
        tk.Label(f,text=f"  [STEP {num}]  {txt.upper()}",font=("Consolas",10,"bold"),
                 bg=th("SURF2"),fg=col).pack(side="left",pady=3)

    def _step_title(self,txt,col):
        """For main titles like H0, H1"""
        f=tk.Frame(self.res,bg=th("SURF2")); f.pack(fill="x",padx=10,pady=(6,0))
        tk.Frame(f,bg=col,width=3).pack(side="left",fill="y")
        tk.Label(f,text=f"  {txt}",font=("Consolas",11,"bold"),
                 bg=th("SURF2"),fg=col).pack(side="left",pady=3)

    def _det(self,txt):
        tk.Label(self.res,text=f"       {txt}",font=("Consolas",11),
                 bg=th("SURF2"),fg=th("TEXT4"),anchor="w",justify="left",
                 wraplength=440).pack(fill="x",padx=10,pady=2)

    def _calc(self):
        try:
            xbar=float(self.xbar.get()); n=int(self.n.get()); conf=float(self.conf.get())
            if not (0 < conf < 1): raise ValueError("Confidence must be between 0 and 1 (e.g. 0.95)")
        except ValueError as ex:
            messagebox.showerror("INPUT ERROR", str(ex)); return
        alpha=1-conf; case=self.case_var.get()
        self._save_vals({"xbar":self.xbar,"n":self.n,"sig":self.sig,"s":self.s})
        self.clear_res()
        if case==1:
            try: sig=float(self.sig.get())
            except: messagebox.showerror("ERROR","Enter σ"); return
            crit=get_z_crit(conf); se=sig/math.sqrt(n); margin=crit*se
            lo=xbar-margin; hi=xbar+margin; tc="#00E5FF"
            steps=[(1,"Given",f"x̄={xbar},  n={n},  σ={sig},  conf={conf*100:.0f}%",tc),
                   (2,"α and α/2",f"α={alpha:.4f}  >>  α/2={alpha/2:.4f}",tc),
                   (3,f"Z(α/2) = {crit:.4f}","",tc),
                   (4,"SE = σ/√n",f"SE = {sig}/√{n} = {se:.6f}",tc),
                   (5,"E = Z · SE",f"E = {crit:.4f} × {se:.6f} = {margin:.6f}",tc),
                   (6,"Confidence Interval",f"[{lo:.4f} , {hi:.4f}]",tc)]
        elif case==2:
            if n<30:
                messagebox.showwarning("MISMATCH",f"n={n}<30 >> Use Case 3"); return
            try: s=float(self.s.get())
            except: messagebox.showerror("ERROR","Enter s"); return
            crit=get_z_crit(conf); se=s/math.sqrt(n); margin=crit*se
            lo=xbar-margin; hi=xbar+margin; tc="#00FF88"
            steps=[(1,"Given",f"x̄={xbar},  n={n},  s={s},  conf={conf*100:.0f}%",tc),
                   (2,"α/2",f"{alpha/2:.4f}",tc),
                   (3,f"Z(α/2) = {crit:.4f}","",tc),
                   (4,"SE = s/√n",f"{se:.6f}",tc),
                   (5,"E = Z · SE",f"{margin:.6f}",tc),
                   (6,"CI",f"[{lo:.4f} , {hi:.4f}]",tc)]
        else:
            if n>=30:
                messagebox.showwarning("MISMATCH",f"n={n}≥30 >> Use Case 2"); return
            try: s=float(self.s.get())
            except: messagebox.showerror("ERROR","Enter s"); return
            df=n-1; crit=t_crit(df,alpha); se=s/math.sqrt(n); margin=crit*se
            lo=xbar-margin; hi=xbar+margin; tc="#FFD700"
            steps=[(1,"Given",f"x̄={xbar},  n={n},  s={s},  df={df}",tc),
                   (2,"α/2 and df",f"α/2={alpha/2:.4f}   df={df}",tc),
                   (3,f"t(α/2, df={df}) = {crit:.4f}","",tc),
                   (4,"SE = s/√n",f"{se:.6f}",tc),
                   (5,"E = t · SE",f"{margin:.6f}",tc),
                   (6,"CI",f"[{lo:.4f} , {hi:.4f}]",tc)]

        def _reveal_steps(i=0):
            if i>=len(steps): return
            num,title,detail,col=steps[i]
            self._step(num,title,col)
            if detail: self._det(detail)
            divider(self.res) if i<len(steps)-1 else None
            if i==len(steps)-1:
                result_answer(self.res,f"✦  ESTIMATION INTERVAL ({conf*100:.0f}%) :   {lo:.4f}  <  μ  <  {hi:.4f}",th("GOLD2"))
            self.root.after(100, lambda: _reveal_steps(i+1))
        _reveal_steps()

        self.set_status(f">> CI FOR μ  [{lo:.4f}, {hi:.4f}]  ({conf*100:.0f}%)")
        self.log("CI for μ",f"x̄={xbar}, n={n}, {conf*100:.0f}% CI: [{lo:.4f}, {hi:.4f}]")
        fig,ax=make_fig(h=4.2)

        # Draw the distribution curve
        x = np.linspace(xbar-4*se, xbar+4*se, 500)
        ax.plot(x, stats.norm.pdf(x, xbar, se), color=th("CYAN"), linewidth=2.0, alpha=0.9, label="Sampling Distribution")

        # Shade the confidence interval (acceptance region)
        xs_ci = np.linspace(lo, hi, 400)
        ax.fill_between(xs_ci, stats.norm.pdf(xs_ci, xbar, se), color="#00FF88", alpha=0.30, label=f"{conf*100:.0f}% Confidence Interval")
        ax.plot(xs_ci, stats.norm.pdf(xs_ci, xbar, se), color=th("GOLD2"), linewidth=1.0, alpha=0.5)

        # Vertical lines for bounds
        ax.axvline(lo, color="#FF0040", linewidth=1.8, linestyle="--", label=f"Lower Bound = {lo:.3f}")
        ax.axvline(hi, color="#FF0040", linewidth=1.8, linestyle="--", label=f"Upper Bound = {hi:.3f}")
        ax.axvline(xbar, color=th("GOLD2"), linewidth=2.0, label=f"Sample Mean x̄ = {xbar}")

        # Annotation arrow
        y_top = stats.norm.pdf(xbar, xbar, se)
        y_ann = y_top * 0.15
        ax.annotate("", xy=(hi, y_ann), xytext=(lo, y_ann),
                    arrowprops=dict(arrowstyle="<->", color=th("GOLD2"), lw=2.0))
        ax.text((lo+hi)/2, y_ann * 1.40,
                f"{conf*100:.0f}% CI\n[{lo:.3f} , {hi:.3f}]",
                ha="center", va="bottom", fontsize=10,
                color=th("GOLD2"), fontfamily="Courier New",
                bbox=dict(boxstyle="round,pad=0.4", facecolor=th("SURF3"),
                          edgecolor=th("GOLD_DIM"), alpha=0.90))

        ax.legend(facecolor=th("SURF2"), edgecolor=th("BORDER2"), 
                  labelcolor=th("TEXT2"), fontsize=9, loc="upper right", framealpha=0.9)
        cnames={1:"Case 1 · σ known",2:"Case 2 · n≥30",3:f"Case 3 · t(df={n-1})"}
        style_ax(ax, f"CI for μ — {cnames[case]}")
        embed_plot(fig, self.pf)


class CIPropPanel(BasePanel):
    panel_id="ci_prop"
    def __init__(self,master,pf,sv,root):
        super().__init__(master,pf,sv,root); self._build()

    def _build(self):
        section_header(self,"Confidence Interval for  P","𝒑",th("GREEN"))

        # Input mode selection
        mode_f = tk.Frame(self, bg=th("BG")); mode_f.pack(fill="x", padx=3, pady=(0,3))
        tk.Label(mode_f, text="  [ INPUT MODE ]", font=("Consolas",11,"bold"),
                 bg=th("BG"), fg=th("GOLD")).pack(anchor="w", padx=10, pady=(8,5))
        mf = tk.Frame(mode_f, bg=th("BG")); mf.pack(fill="x", padx=12, pady=(0,8))
        self.input_mode = tk.StringVar(value="summary")
        for val, txt in [("summary","Summary  (p̂, n)"), ("raw","Raw data  (x successes / n trials)")]:
            tk.Radiobutton(mf, text=txt, variable=self.input_mode, value=val,
                           font=("Consolas",10), bg=th("BG"), fg=th("CYAN"),
                           selectcolor=th("SURFACE"), activebackground=th("SURF3"),
                           cursor="hand2", command=self._on_input_mode).pack(side="left", padx=5)

        c=card(self)
        self.p=tk.StringVar(); self.n=tk.StringVar(); self.conf=tk.StringVar(value="0.95")
        self.x_count=tk.StringVar(); self.n_total=tk.StringVar()
        g=tk.Frame(c,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Sample Proportion  p̂",self.p,0,tooltip="0 < p̂ < 1")
        row_field(g,"Sample Size  n",self.n,1,kind="int")
        conf_combo(g,self.conf,2)

        # Raw data frame for proportion
        self.raw_frame = card(self)
        tk.Label(self.raw_frame, text="  [ RAW DATA INPUT ]",
                 font=("Consolas",10,"bold"), bg=th("SURF2"), fg=th("GOLD2")
                 ).pack(anchor="w", padx=10, pady=(7,2))
        tk.Label(self.raw_frame, text="Enter number of successes and total trials:",
                 font=("Consolas",9), bg=th("SURF2"), fg=th("TEXT3")).pack(anchor="w", padx=10)
        rg = tk.Frame(self.raw_frame, bg=th("SURF2")); rg.pack(fill="x", padx=10, pady=5)
        tk.Label(rg, text="Successes  x", font=("Consolas",10),
                 bg=th("SURF2"), fg=th("TEXT2")).grid(row=0, column=0, sticky="w", padx=(0,10))
        ValidEntry(rg, self.x_count, kind="int", width=12).grid(row=0, column=1, padx=(0,15))
        tk.Label(rg, text="Total  n", font=("Consolas",10),
                 bg=th("SURF2"), fg=th("TEXT2")).grid(row=0, column=2, sticky="w", padx=(0,10))
        ValidEntry(rg, self.n_total, kind="int", width=12).grid(row=0, column=3)
        parse_btn = tk.Button(self.raw_frame, text=">> CALCULATE p̂ = x/n",
                              font=("Consolas",10,"bold"),
                              bg=th("SURF3"), fg=th("CYAN"), relief="flat",
                              cursor="hand2", pady=5, bd=0,
                              activebackground=th("GOLD_DIM"), activeforeground=th("TEXT"),
                              command=self._parse_raw)
        parse_btn.pack(fill="x", padx=10, pady=(0,6))
        self.raw_info_lbl = tk.Label(self.raw_frame, text="", font=("Consolas",10),
                                     bg=th("SURF2"), fg=th("GREEN"), justify="left")
        self.raw_info_lbl.pack(anchor="w", padx=10, pady=(0,5))
        self.raw_frame.pack_forget()

        self._load_vals({"p":self.p,"n":self.n})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> CALCULATE INTERVAL",self._calc)
        self.bind_entries_return(self._calc)

    def _on_input_mode(self):
        if self.input_mode.get() == "raw":
            self.raw_frame.pack(fill="x", pady=(0,3), padx=2)
        else:
            self.raw_frame.pack_forget()

    def _parse_raw(self):
        try:
            x = int(self.x_count.get())
            n = int(self.n_total.get())
            if n <= 0: raise ValueError("n must be > 0")
            if x < 0 or x > n: raise ValueError("x must be between 0 and n")
            p = x / n
            self.p.set(f"{p:.6f}")
            self.n.set(str(n))
            self.raw_info_lbl.config(text=f"  >> p̂ = {x}/{n} = {p:.4f}  >> FIELDS FILLED")
            self.set_status(f"Raw data parsed: p̂={p:.4f}, n={n}")
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def fill_from_dict(self, d):
        n = 0
        for key, var in [("p",self.p),("n",self.n),("conf",self.conf)]:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        return n

    def _calc(self):
        try:
            p=float(self.p.get()); n=int(self.n.get()); conf=float(self.conf.get())
        except:
            messagebox.showerror("ERROR","Check inputs"); return
        if not (0<p<1):
            messagebox.showerror("ERROR","0 < p̂ < 1 required"); return
        self._save_vals({"p":self.p,"n":self.n})
        alpha=1-conf; crit=get_z_crit(conf)
        se=math.sqrt(p*(1-p)/n); margin=crit*se; lo=p-margin; hi=p+margin
        self.clear_res()
        lines=[(result_row,[f"α = {alpha:.4f}   Z(α/2) = {crit:.4f}", "#00E5FF"]),
               (result_row,[f"SE = √(p̂·q̂/n) = √({p}·{1-p:.4f}/{n}) = {se:.6f}", "#A8D8F0"]),
               (result_row,[f"E  = Z · SE = {crit:.4f} × {se:.6f} = {margin:.6f}", "#FFD700"]),
               (divider,[]),
               (result_row,[f"Lower = p̂ − E = {p} − {margin:.6f} = {lo:.4f}", "#00FF88"]),
               (result_row,[f"Upper = p̂ + E = {p} + {margin:.6f} = {hi:.4f}", "#00FF88"]),
               (result_answer,[f"✦  ESTIMATION INTERVAL ({conf*100:.0f}%) :   {lo:.4f}  <  P  <  {hi:.4f}",th("GOLD2")])]
        AnimatedResults(self.res,self.root,lines,delay=80)
        self.set_status(f">> CI FOR P  [{lo:.4f}, {hi:.4f}]")
        self.log("CI for P",f"p̂={p}, n={n}, {conf*100:.0f}% CI: [{lo:.4f}, {hi:.4f}]")
        fig,ax=make_fig(h=4.2)

        # Draw the distribution curve
        x = np.linspace(p-4*se, p+4*se, 500)
        ax.plot(x, stats.norm.pdf(x, p, se), color=th("CYAN"), linewidth=2.0, alpha=0.9, label="Sampling Distribution")

        # Shade the confidence interval
        xs_ci = np.linspace(lo, hi, 400)
        ax.fill_between(xs_ci, stats.norm.pdf(xs_ci, p, se), color="#00FF88", alpha=0.30, label=f"{conf*100:.0f}% Confidence Interval")
        ax.plot(xs_ci, stats.norm.pdf(xs_ci, p, se), color=th("GOLD2"), linewidth=1.0, alpha=0.5)

        # Vertical lines
        ax.axvline(lo, color="#FF0040", linewidth=1.8, linestyle="--", label=f"Lower Bound = {lo:.4f}")
        ax.axvline(hi, color="#FF0040", linewidth=1.8, linestyle="--", label=f"Upper Bound = {hi:.4f}")
        ax.axvline(p, color=th("GOLD2"), linewidth=2.0, label=f"Sample Proportion p̂ = {p}")

        # Annotation
        y_top = stats.norm.pdf(p, p, se)
        y_ann = y_top * 0.15
        ax.annotate("", xy=(hi, y_ann), xytext=(lo, y_ann),
                    arrowprops=dict(arrowstyle="<->", color=th("GOLD2"), lw=2.0))
        ax.text((lo+hi)/2, y_ann * 1.40,
                f"{conf*100:.0f}% CI\n[{lo:.4f} , {hi:.4f}]",
                ha="center", va="bottom", fontsize=10,
                color=th("GOLD2"), fontfamily="Courier New",
                bbox=dict(boxstyle="round,pad=0.4", facecolor=th("SURF3"),
                          edgecolor=th("GOLD_DIM"), alpha=0.90))

        ax.legend(facecolor=th("SURF2"), edgecolor=th("BORDER2"), 
                  labelcolor=th("TEXT2"), fontsize=9, loc="upper right", framealpha=0.9)
        style_ax(ax, f"CI for P  (p̂={p}, n={n})")
        embed_plot(fig, self.pf)


class CIVarPanel(BasePanel):
    panel_id="ci_var"
    def __init__(self,master,pf,sv,root):
        super().__init__(master,pf,sv,root); self._build()

    def _build(self):
        section_header(self,"Confidence Interval for  σ²","σ²",th("GREEN2"))

        # Input mode selection
        mode_f = tk.Frame(self, bg=th("BG")); mode_f.pack(fill="x", padx=3, pady=(0,3))
        tk.Label(mode_f, text="  [ INPUT MODE ]", font=("Consolas",11,"bold"),
                 bg=th("BG"), fg=th("GOLD")).pack(anchor="w", padx=10, pady=(8,5))
        mf = tk.Frame(mode_f, bg=th("BG")); mf.pack(fill="x", padx=12, pady=(0,8))
        self.input_mode = tk.StringVar(value="summary")
        for val, txt in [("summary","Summary  (s², n)"), ("raw","Raw data  (values)")]:
            tk.Radiobutton(mf, text=txt, variable=self.input_mode, value=val,
                           font=("Consolas",10), bg=th("BG"), fg=th("CYAN"),
                           selectcolor=th("SURFACE"), activebackground=th("SURF3"),
                           cursor="hand2", command=self._on_input_mode).pack(side="left", padx=5)

        c=card(self)
        self.s2=tk.StringVar(); self.n=tk.StringVar(); self.conf=tk.StringVar(value="0.95")
        g=tk.Frame(c,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Sample Variance  s²",self.s2,0)
        row_field(g,"Sample Size  n",self.n,1,kind="int")
        conf_combo(g,self.conf,2)

        # Raw data frame
        self.raw_frame = card(self)
        tk.Label(self.raw_frame, text="  [ RAW DATA INPUT ]",
                 font=("Consolas",10,"bold"), bg=th("SURF2"), fg=th("GOLD2")
                 ).pack(anchor="w", padx=10, pady=(7,2))
        self.raw_var = tk.StringVar()
        raw_entry = tk.Entry(self.raw_frame, textvariable=self.raw_var, font=("Consolas",11),
                             bg=th("SURFACE"), fg=th("CYAN"), insertbackground=th("GOLD2"),
                             relief="flat", highlightthickness=1,
                             highlightbackground=th("BORDER2"), highlightcolor=th("GOLD"))
        raw_entry.pack(fill="x", padx=10, pady=3, ipady=7)
        tk.Label(self.raw_frame,
                 text="  e.g.:  23 45 31 28 40 35   or   23,45,31,28,40,35",
                 font=("Consolas",9), bg=th("SURF2"), fg=th("TEXT3")).pack(anchor="w", padx=10, pady=(0,3))
        parse_btn = tk.Button(self.raw_frame, text=">> PARSE & CALCULATE  s², n",
                              font=("Consolas",10,"bold"),
                              bg=th("SURF3"), fg=th("CYAN"), relief="flat",
                              cursor="hand2", pady=5, bd=0,
                              activebackground=th("GOLD_DIM"), activeforeground=th("TEXT"),
                              command=self._parse_raw)
        parse_btn.pack(fill="x", padx=10, pady=(0,5))
        self.raw_info_lbl = tk.Label(self.raw_frame, text="", font=("Consolas",10),
                                     bg=th("SURF2"), fg=th("GREEN"), justify="left")
        self.raw_info_lbl.pack(anchor="w", padx=10, pady=(0,5))
        self.raw_frame.pack_forget()

        self._load_vals({"s2":self.s2,"n":self.n})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> CALCULATE INTERVAL",self._calc)
        self.bind_entries_return(self._calc)

    def _on_input_mode(self):
        if self.input_mode.get() == "raw":
            self.raw_frame.pack(fill="x", pady=(0,3), padx=2)
        else:
            self.raw_frame.pack_forget()

    def _parse_raw(self):
        result, error = parse_raw_data(self.raw_var.get())
        if error:
            messagebox.showerror("ERROR", error)
            return
        n = result["n"]
        s2 = result["s"]**2  # variance
        self.s2.set(f"{s2:.6f}")
        self.n.set(str(n))
        self.raw_info_lbl.config(text=f"  >> n={n}   s²={s2:.4f}   >> FIELDS FILLED")
        self.set_status(f"Raw data parsed: n={n}, s²={s2:.4f}")

    def fill_from_dict(self, d):
        n = 0
        for key, var in [("s2",self.s2),("n",self.n),("conf",self.conf)]:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        return n

    def _calc(self):
        try:
            s2=float(self.s2.get()); n=int(self.n.get()); conf=float(self.conf.get())
        except:
            messagebox.showerror("ERROR","Check inputs"); return
        if s2 <= 0:
            messagebox.showerror("ERROR","s² must be > 0"); return
        self._save_vals({"s2":self.s2,"n":self.n})
        df=n-1; alpha=1-conf
        chi_lo=stats.chi2.ppf(alpha/2,df); chi_hi=stats.chi2.ppf(1-alpha/2,df)
        lo=df*s2/chi_hi; hi=df*s2/chi_lo
        self.clear_res()
        lines=[(result_row,[f"df = n−1 = {df}   α/2 = {alpha/2:.4f}", "#00E5FF"]),
               (result_row,[f"χ²_L = χ²(α/2, df) = {chi_lo:.4f}", "#A8D8F0"]),
               (result_row,[f"χ²_R = χ²(1−α/2, df) = {chi_hi:.4f}", "#A8D8F0"]),
               (divider,[]),
               (result_row,[f"Lower = (n−1)·s² / χ²_R = {df}·{s2}/{chi_hi:.4f} = {lo:.4f}", "#00FF88"]),
               (result_row,[f"Upper = (n−1)·s² / χ²_L = {df}·{s2}/{chi_lo:.4f} = {hi:.4f}", "#00FF88"]),
               (result_answer,[f"✦  ESTIMATION INTERVAL ({conf*100:.0f}%) :   {lo:.4f}  <  σ²  <  {hi:.4f}",th("GOLD2")])]
        AnimatedResults(self.res,self.root,lines,delay=80)
        self.set_status(f">> CI FOR σ²  [{lo:.4f}, {hi:.4f}]")
        self.log("CI for σ²",f"s²={s2}, n={n}, {conf*100:.0f}% CI: [{lo:.4f}, {hi:.4f}]")
        fig,ax=make_fig(h=4.2)

        # Draw the chi-square distribution
        x_max = df + 5*math.sqrt(2*df)
        x = np.linspace(0.01, x_max, 500)
        ax.plot(x, stats.chi2.pdf(x, df), color=th("CYAN"), linewidth=2.0, alpha=0.9, label="Chi-Square Distribution")

        # Shade the acceptance region (between chi_lo and chi_hi)
        xs_ci = np.linspace(chi_lo, chi_hi, 400)
        ax.fill_between(xs_ci, stats.chi2.pdf(xs_ci, df), color="#00FF88", alpha=0.30, label=f"{conf*100:.0f}% Acceptance Region")
        ax.plot(xs_ci, stats.chi2.pdf(xs_ci, df), color=th("GOLD2"), linewidth=1.0, alpha=0.5)

        # Vertical lines for critical values
        ax.axvline(chi_lo, color="#FF0040", linewidth=1.8, linestyle="--", label=f"χ²_L = {chi_lo:.2f}")
        ax.axvline(chi_hi, color="#FF0040", linewidth=1.8, linestyle="--", label=f"χ²_R = {chi_hi:.2f}")

        # Annotation
        x_mid = (chi_lo + chi_hi) / 2
        y_mid = stats.chi2.pdf(x_mid, df) * 0.15
        ax.annotate("", xy=(chi_hi, y_mid), xytext=(chi_lo, y_mid),
                    arrowprops=dict(arrowstyle="<->", color=th("GOLD2"), lw=2.0))
        ax.text(x_mid, y_mid * 1.45,
                f"{conf*100:.0f}% Acceptance Region\nσ² ∈ [{lo:.3f} , {hi:.3f}]",
                ha="center", va="bottom", fontsize=10,
                color=th("GOLD2"), fontfamily="Courier New",
                bbox=dict(boxstyle="round,pad=0.4", facecolor=th("SURF3"),
                          edgecolor=th("GOLD_DIM"), alpha=0.90))

        ax.legend(facecolor=th("SURF2"), edgecolor=th("BORDER2"), 
                  labelcolor=th("TEXT2"), fontsize=9, loc="upper right", framealpha=0.9)
        style_ax(ax, f"CI for σ²  (df={df})")
        embed_plot(fig, self.pf)


class TestMeanPanel(BasePanel):
    panel_id="test_mean"
    def __init__(self,master,pf,sv,root):
        super().__init__(master,pf,sv,root); self._build()

    def _build(self):
        section_header(self,"Hypothesis Test for  μ","H₀",th("GOLD2"))
        c=card(self)
        self.xbar=tk.StringVar(); self.mu0=tk.StringVar()
        self.sig=tk.StringVar();   self.s=tk.StringVar()
        self.n=tk.StringVar();     self.alpha=tk.StringVar(value="0.05")
        self.tail=tk.StringVar(value="Two-tailed")

        mode_f = tk.Frame(c, bg=th("SURF2")); mode_f.pack(fill="x", padx=12, pady=(7,3))
        tk.Label(mode_f, text="Input mode:", font=("Consolas",10),
                 bg=th("SURF2"), fg=th("TEXT2")).pack(side="left", padx=(2,8))
        self.input_mode = tk.StringVar(value="summary")
        for val, txt in [("summary","Summary  (x̄, n, s/σ)"), ("raw","Raw data")]:
            tk.Radiobutton(mode_f, text=txt, variable=self.input_mode, value=val,
                           font=("Consolas",10), bg=th("SURF2"), fg=th("CYAN"),
                           selectcolor=th("SURFACE"), activebackground=th("SURF3"),
                           cursor="hand2", command=self._on_input_mode).pack(side="left", padx=5)

        g=tk.Frame(c,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Sample Mean  x̄",self.xbar,0)
        row_field(g,"Hypothesized  μ₀",self.mu0,1,tooltip="H₀: μ = μ₀")
        row_field(g,"σ  (known — leave blank if not)",self.sig,2,tooltip="Leave blank if σ unknown")
        row_field(g,"s  (sample std dev)",self.s,3,tooltip="Used when σ is unknown")
        row_field(g,"Sample Size  n",self.n,4,kind="int")
        alpha_field(g,self.alpha,5)
        make_combo(g,self.tail,["Two-tailed","Right-tailed","Left-tailed"],6,label="Tail")

        self.raw_frame = card(self)
        tk.Label(self.raw_frame, text="  [ RAW DATA INPUT ]",
                 font=("Consolas",10,"bold"), bg=th("SURF2"), fg=th("GOLD2")
                 ).pack(anchor="w", padx=10, pady=(7,2))
        self.raw_var = tk.StringVar()
        raw_entry = tk.Entry(self.raw_frame, textvariable=self.raw_var, font=("Consolas",11),
                             bg=th("SURFACE"), fg=th("CYAN"), insertbackground=th("GOLD2"),
                             relief="flat", highlightthickness=1,
                             highlightbackground=th("BORDER2"), highlightcolor=th("GOLD"))
        raw_entry.pack(fill="x", padx=10, pady=3, ipady=7)
        tk.Label(self.raw_frame,
                 text="  e.g.:  23 45 31 28 40 35   or   23,45,31,28,40,35",
                 font=("Consolas",9), bg=th("SURF2"), fg=th("TEXT3")).pack(anchor="w", padx=10, pady=(0,3))
        parse_btn = tk.Button(self.raw_frame, text=">> PARSE & FILL  x̄, n, s",
                              font=("Consolas",10,"bold"),
                              bg=th("SURF3"), fg=th("CYAN"), relief="flat",
                              cursor="hand2", pady=5, bd=0,
                              activebackground=th("GOLD_DIM"), activeforeground=th("TEXT"),
                              command=self._parse_raw)
        parse_btn.pack(fill="x", padx=10, pady=(0,5))
        self.raw_info_lbl = tk.Label(self.raw_frame, text="", font=("Consolas",10),
                                     bg=th("SURF2"), fg=th("GREEN"), justify="left")
        self.raw_info_lbl.pack(anchor="w", padx=10, pady=(0,5))
        self.raw_frame.pack_forget()

        self._load_vals({"xbar":self.xbar,"mu0":self.mu0,"n":self.n,"alpha":self.alpha})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> RUN HYPOTHESIS TEST",self._calc)
        self.bind_entries_return(self._calc)

    def fill_from_dict(self, d):
        n = 0
        mapping = [("xbar",self.xbar),("x_bar",self.xbar),("mean",self.xbar),
                   ("mu0",self.mu0),("mu_0",self.mu0),("hypothesized_mean",self.mu0),
                   ("sigma",self.sig),("s",self.s),("n",self.n),("alpha",self.alpha)]
        for key, var in mapping:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        tails = ["Two-tailed","Right-tailed","Left-tailed"]
        if "tail" in d and d["tail"] in tails:
            self.tail.set(d["tail"]); n += 1
        return n

    def _on_input_mode(self):
        if self.input_mode.get() == "raw":
            self.raw_frame.pack(fill="x", pady=(0,3), padx=2)
        else:
            self.raw_frame.pack_forget()

    def _parse_raw(self):
        raw = self.raw_var.get().replace(",", " ")
        try:
            vals = [float(x) for x in raw.split() if x.strip()]
        except:
            messagebox.showerror("PARSE ERROR","Could not parse values.\nUse numbers separated by spaces or commas.")
            return
        if len(vals) < 2:
            messagebox.showerror("ERROR","Need at least 2 values"); return
        n    = len(vals)
        mean = sum(vals) / n
        s    = math.sqrt(sum((v - mean)**2 for v in vals) / (n - 1))
        self.xbar.set(f"{mean:.6f}")
        self.n.set(str(n))
        self.s.set(f"{s:.6f}")
        self.raw_info_lbl.config(
            text=f"  >> n={n}   x̄={mean:.4f}   s={s:.4f}   >> FIELDS FILLED")
        self.set_status(f"Raw data parsed: n={n}, x̄={mean:.4f}, s={s:.4f}")

    def _calc(self):
        try:
            xbar=float(self.xbar.get()); mu0=float(self.mu0.get())
            n=int(self.n.get());         alpha=float(self.alpha.get())
            if not (0 < alpha < 1): raise ValueError("alpha must be between 0 and 1")
            tail=self.tail.get()
        except ValueError as ex:
            messagebox.showerror("INPUT ERROR", f"Check inputs:\n{ex}"); return
        self._save_vals({"xbar":self.xbar,"mu0":self.mu0,"n":self.n,"alpha":self.alpha})
        sig_txt=self.sig.get().strip(); s_txt=self.s.get().strip()

        if sig_txt:
            se=float(sig_txt)/math.sqrt(n); dist="Z"; dlabel="Z  (σ known)"
            stat_sym = "Z"
        elif n>=30:
            if not s_txt: messagebox.showerror("ERROR","Enter s for Case 2 (n≥30)"); return
            se=float(s_txt)/math.sqrt(n); dist="Z"; dlabel="Z  (n≥30, CLT)"
            stat_sym = "Z"
        else:
            if not s_txt: messagebox.showerror("ERROR","Enter s for Case 3 (n<30)"); return
            se=float(s_txt)/math.sqrt(n); dist="t"; dlabel=f"t  (df={n-1})"
            stat_sym = "t"

        ts=(xbar-mu0)/se
        if dist=="Z":
            crit=z_crit(alpha/2) if tail=="Two-tailed" else z_crit(alpha)
            if tail=="Two-tailed": pval=2*(1-phi(abs(ts)))
            elif tail=="Right-tailed": pval=1-phi(ts)
            else: pval=phi(ts)
        else:
            df=n-1
            crit=t_crit(df,alpha) if tail=="Two-tailed" else t1tail(df,alpha)
            if tail=="Two-tailed": pval=2*(1-stats.t.cdf(abs(ts),df))
            elif tail=="Right-tailed": pval=1-stats.t.cdf(ts,df)
            else: pval=stats.t.cdf(ts,df)

        if tail=="Two-tailed": reject=abs(ts)>crit
        elif tail=="Right-tailed": reject=ts>crit
        else: reject=ts<-crit

        self.clear_res()
        dec_col="#FF0040" if reject else "#00FF88"
        crit_str=(f"± {crit:.4f}" if tail=="Two-tailed" else
                  f"+{crit:.4f}" if tail=="Right-tailed" else f"−{crit:.4f}")
        h1_map={"Two-tailed":f"μ ≠ {mu0}","Right-tailed":f"μ > {mu0}","Left-tailed":f"μ < {mu0}"}
        conclusion=("At α={}, sufficient evidence to REJECT H₀.".format(alpha)
                    if reject else "At α={}, NOT sufficient evidence to reject H₀.".format(alpha))
        sig_label = "✦  REJECT NULL HYPOTHESIS (H₀)  >>  TEST IS SIGNIFICANT" if reject else "✦  ACCEPT NULL HYPOTHESIS (H₀)  >>  TEST IS NOT SIGNIFICANT"

        lines=[
            (result_row,[f"H₀ :  μ = {mu0}", "#BD00FF"]),
            (result_row,[f"H₁ :  {h1_map[tail]}", "#BD00FF"]),
            (divider,[]),
            (result_row,[f"Distribution :  {dlabel}", "#00E5FF"]),
            (result_row,[f"SE  =  (σ or s) / √n  =  {se:.6f}", "#00E5FF"]),
            (divider,[]),
            (result_row,[f"{stat_sym}  =  (x̄ − μ₀) / SE", "#FFD700", True]),
            (result_row,[f"   =  ({xbar} − {mu0}) / {se:.6f}", "#A8D8F0", True]),
            (result_row,[f"   =  {ts:.4f}", "#00FF88", True]),
            (divider,[]),
            (result_row,[f"Critical Value(s)  =  {crit_str}   (α = {alpha})", "#FF8800"]),
            (result_row,[f"p-value  =  {pval:.4f}", "#FF0040"]),
            (result_answer,[sig_label, dec_col]),
            (result_row,[f">>  {conclusion}", th("CYAN")])]
        AnimatedResults(self.res,self.root,lines,delay=70)
        self.root.after(len(lines)*70+100, lambda: p_badge(self.res, pval))
        verdict="REJECT" if reject else "FAIL TO REJECT"
        self.set_status(f">> TEST FOR μ  {verdict} H₀  ({stat_sym}={ts:.4f}, p={pval:.4f})")
        self.log("Test for μ",f"H₀:μ={mu0}, {stat_sym}={ts:.4f}, p={pval:.4f}, {verdict}")
        fig,ax=make_fig()
        x=np.linspace(-4,4,400); ax.plot(x,stats.norm.pdf(x),color=th("CYAN"),linewidth=2.0,alpha=0.9)
        xs_r=np.linspace(crit,4,200); xs_l=np.linspace(-4,-crit,200)

        # Acceptance region (green) - middle area
        if tail=="Two-tailed":
            xs_mid=np.linspace(-crit,crit,200)
            ax.fill_between(xs_mid,stats.norm.pdf(xs_mid),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xs_l,stats.norm.pdf(xs_l),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")
            ax.fill_between(xs_r,stats.norm.pdf(xs_r),color="#FF0040",alpha=0.35)
        elif tail=="Right-tailed":
            xs_mid=np.linspace(-4,crit,200)
            ax.fill_between(xs_mid,stats.norm.pdf(xs_mid),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xs_r,stats.norm.pdf(xs_r),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")
        else:
            xs_mid=np.linspace(crit,4,200)
            ax.fill_between(xs_mid,stats.norm.pdf(xs_mid),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xs_l,stats.norm.pdf(xs_l),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")

        ax.axvline(min(max(ts,-3.9),3.9),color=th("GOLD2"),linewidth=2.0,linestyle="--",
                   label=f"Test Statistic {stat_sym}={ts:.3f}")
        ax.legend(facecolor=th("SURF2"),edgecolor=th("BORDER2"),labelcolor=th("TEXT2"),fontsize=9,
                  loc="upper right", framealpha=0.9)
        style_ax(ax,f"Test for μ  ({tail}  ·  {dlabel})")
        embed_plot(fig,self.pf)


class TestPropPanel(BasePanel):
    panel_id="test_prop"
    def __init__(self,master,pf,sv,root):
        super().__init__(master,pf,sv,root); self._build()

    def _build(self):
        section_header(self,"Hypothesis Test for  P","H₀",th("GOLD2"))

        # Input mode selection
        mode_f = tk.Frame(self, bg=th("BG")); mode_f.pack(fill="x", padx=3, pady=(0,3))
        tk.Label(mode_f, text="  [ INPUT MODE ]", font=("Consolas",11,"bold"),
                 bg=th("BG"), fg=th("GOLD")).pack(anchor="w", padx=10, pady=(8,5))
        mf = tk.Frame(mode_f, bg=th("BG")); mf.pack(fill="x", padx=12, pady=(0,8))
        self.input_mode = tk.StringVar(value="summary")
        for val, txt in [("summary","Summary  (p̂, n)"), ("raw","Raw data  (x successes / n trials)")]:
            tk.Radiobutton(mf, text=txt, variable=self.input_mode, value=val,
                           font=("Consolas",10), bg=th("BG"), fg=th("CYAN"),
                           selectcolor=th("SURFACE"), activebackground=th("SURF3"),
                           cursor="hand2", command=self._on_input_mode).pack(side="left", padx=5)

        c=card(self)
        self.p=tk.StringVar(); self.P0=tk.StringVar()
        self.n=tk.StringVar(); self.alpha=tk.StringVar(value="0.05")
        self.tail=tk.StringVar(value="Two-tailed")
        self.x_count=tk.StringVar(); self.n_total=tk.StringVar()
        g=tk.Frame(c,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Sample Proportion  p̂",self.p,0)
        row_field(g,"Hypothesized  P₀",self.P0,1,tooltip="H₀: P = P₀  (0<P₀<1)")
        row_field(g,"Sample Size  n",self.n,2,kind="int")
        alpha_field(g,self.alpha,3)
        make_combo(g,self.tail,["Two-tailed","Right-tailed","Left-tailed"],4,label="Tail")

        # Raw data frame
        self.raw_frame = card(self)
        tk.Label(self.raw_frame, text="  [ RAW DATA INPUT ]",
                 font=("Consolas",10,"bold"), bg=th("SURF2"), fg=th("GOLD2")
                 ).pack(anchor="w", padx=10, pady=(7,2))
        tk.Label(self.raw_frame, text="Enter number of successes and total trials:",
                 font=("Consolas",9), bg=th("SURF2"), fg=th("TEXT3")).pack(anchor="w", padx=10)
        rg = tk.Frame(self.raw_frame, bg=th("SURF2")); rg.pack(fill="x", padx=10, pady=5)
        tk.Label(rg, text="Successes  x", font=("Consolas",10),
                 bg=th("SURF2"), fg=th("TEXT2")).grid(row=0, column=0, sticky="w", padx=(0,10))
        ValidEntry(rg, self.x_count, kind="int", width=12).grid(row=0, column=1, padx=(0,15))
        tk.Label(rg, text="Total  n", font=("Consolas",10),
                 bg=th("SURF2"), fg=th("TEXT2")).grid(row=0, column=2, sticky="w", padx=(0,10))
        ValidEntry(rg, self.n_total, kind="int", width=12).grid(row=0, column=3)
        parse_btn = tk.Button(self.raw_frame, text=">> CALCULATE p̂ = x/n",
                              font=("Consolas",10,"bold"),
                              bg=th("SURF3"), fg=th("CYAN"), relief="flat",
                              cursor="hand2", pady=5, bd=0,
                              activebackground=th("GOLD_DIM"), activeforeground=th("TEXT"),
                              command=self._parse_raw)
        parse_btn.pack(fill="x", padx=10, pady=(0,6))
        self.raw_info_lbl = tk.Label(self.raw_frame, text="", font=("Consolas",10),
                                     bg=th("SURF2"), fg=th("GREEN"), justify="left")
        self.raw_info_lbl.pack(anchor="w", padx=10, pady=(0,5))
        self.raw_frame.pack_forget()

        self._load_vals({"p":self.p,"P0":self.P0,"n":self.n,"alpha":self.alpha})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> RUN HYPOTHESIS TEST",self._calc)
        self.bind_entries_return(self._calc)

    def _on_input_mode(self):
        if self.input_mode.get() == "raw":
            self.raw_frame.pack(fill="x", pady=(0,3), padx=2)
        else:
            self.raw_frame.pack_forget()

    def _parse_raw(self):
        try:
            x = int(self.x_count.get())
            n = int(self.n_total.get())
            if n <= 0: raise ValueError("n must be > 0")
            if x < 0 or x > n: raise ValueError("x must be between 0 and n")
            p = x / n
            self.p.set(f"{p:.6f}")
            self.n.set(str(n))
            self.raw_info_lbl.config(text=f"  >> p̂ = {x}/{n} = {p:.4f}  >> FIELDS FILLED")
            self.set_status(f"Raw data parsed: p̂={p:.4f}, n={n}")
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def fill_from_dict(self, d):
        n = 0
        for key, var in [("p",self.p),("P0",self.P0),("n",self.n),("alpha",self.alpha)]:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        if "tail" in d and d["tail"] in ["Two-tailed","Right-tailed","Left-tailed"]:
            self.tail.set(d["tail"]); n += 1
        return n

    def _calc(self):
        try:
            p=float(self.p.get()); P0=float(self.P0.get())
            n=int(self.n.get());   alpha=float(self.alpha.get())
            if not (0 < alpha < 1): raise ValueError("alpha out of range")
            tail=self.tail.get()
        except:
            messagebox.showerror("ERROR","Check inputs"); return
        self._save_vals({"p":self.p,"P0":self.P0,"n":self.n,"alpha":self.alpha})
        se=math.sqrt(P0*(1-P0)/n); ts=(p-P0)/se
        crit=z_crit(alpha/2) if tail=="Two-tailed" else z_crit(alpha)
        if tail=="Two-tailed": pval=2*(1-phi(abs(ts))); reject=abs(ts)>crit
        elif tail=="Right-tailed": pval=1-phi(ts); reject=ts>crit
        else: pval=phi(ts); reject=ts<-crit
        self.clear_res()
        dec_col="#FF0040" if reject else "#00FF88"
        crit_str=(f"± {crit:.4f}" if tail=="Two-tailed" else
                  f"+{crit:.4f}" if tail=="Right-tailed" else f"−{crit:.4f}")
        h1_map={"Two-tailed":f"P ≠ {P0}","Right-tailed":f"P > {P0}","Left-tailed":f"P < {P0}"}
        conclusion=("At α={}, sufficient evidence to REJECT H₀.".format(alpha)
                    if reject else "At α={}, NOT sufficient evidence to reject H₀.".format(alpha))
        sig_label = "✦  REJECT NULL HYPOTHESIS (H₀)  >>  TEST IS SIGNIFICANT" if reject else "✦  ACCEPT NULL HYPOTHESIS (H₀)  >>  TEST IS NOT SIGNIFICANT"
        lines=[
            (result_row,[f"H₀ :  P = {P0}", "#BD00FF"]),
            (result_row,[f"H₁ :  {h1_map[tail]}", "#BD00FF"]),
            (divider,[]),
            (result_row,[f"SE  =  √(P₀·Q₀/n)  =  √({P0}·{1-P0:.4f}/{n})  =  {se:.6f}", "#00E5FF"]),
            (result_row,[f"Z   =  (p̂ − P₀) / SE", "#FFD700", True]),
            (result_row,[f"    =  ({p} − {P0}) / {se:.6f}", "#A8D8F0", True]),
            (result_row,[f"    =  {ts:.4f}", "#00FF88", True]),
            (divider,[]),
            (result_row,[f"Critical Value(s)  =  {crit_str}   (α = {alpha})", "#FF8800"]),
            (result_row,[f"p-value  =  {pval:.4f}", "#FF0040"]),
            (result_answer,[sig_label, dec_col]),
            (result_row,[f">>  {conclusion}", th("CYAN")])]
        AnimatedResults(self.res,self.root,lines,delay=70)
        self.root.after(len(lines)*70+100, lambda: p_badge(self.res,pval))
        verdict="REJECT" if reject else "FAIL TO REJECT"
        self.set_status(f">> TEST FOR P  {verdict} H₀  (Z={ts:.4f}, p={pval:.4f})")
        self.log("Test for P",f"H₀:P={P0}, Z={ts:.4f}, p={pval:.4f}, {verdict}")
        fig,ax=make_fig()
        x=np.linspace(-4,4,400); ax.plot(x,stats.norm.pdf(x),color=th("CYAN"),linewidth=2.0,alpha=0.9)
        xs_r=np.linspace(crit,4,200); xs_l=np.linspace(-4,-crit,200)

        # Acceptance and rejection regions
        if tail=="Two-tailed":
            xs_mid=np.linspace(-crit,crit,200)
            ax.fill_between(xs_mid,stats.norm.pdf(xs_mid),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xs_l,stats.norm.pdf(xs_l),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")
            ax.fill_between(xs_r,stats.norm.pdf(xs_r),color="#FF0040",alpha=0.35)
        elif tail=="Right-tailed":
            xs_mid=np.linspace(-4,crit,200)
            ax.fill_between(xs_mid,stats.norm.pdf(xs_mid),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xs_r,stats.norm.pdf(xs_r),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")
        else:
            xs_mid=np.linspace(crit,4,200)
            ax.fill_between(xs_mid,stats.norm.pdf(xs_mid),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xs_l,stats.norm.pdf(xs_l),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")

        ax.axvline(min(max(ts,-3.9),3.9),color=th("GOLD2"),linewidth=2.0,linestyle="--",
                   label=f"Test Statistic Z={ts:.3f}")
        ax.legend(facecolor=th("SURF2"),edgecolor=th("BORDER2"),labelcolor=th("TEXT2"),fontsize=9,
                  loc="upper right", framealpha=0.9)
        style_ax(ax,f"Test for P  ({tail})")
        embed_plot(fig,self.pf)


class TestVarPanel(BasePanel):
    panel_id="test_var"
    def __init__(self,master,pf,sv,root):
        super().__init__(master,pf,sv,root); self._build()

    def _build(self):
        section_header(self,"Hypothesis Test for  σ²","H₀",th("GOLD2"))

        # Input mode selection
        mode_f = tk.Frame(self, bg=th("BG")); mode_f.pack(fill="x", padx=3, pady=(0,3))
        tk.Label(mode_f, text="  [ INPUT MODE ]", font=("Consolas",11,"bold"),
                 bg=th("BG"), fg=th("GOLD")).pack(anchor="w", padx=10, pady=(8,5))
        mf = tk.Frame(mode_f, bg=th("BG")); mf.pack(fill="x", padx=12, pady=(0,8))
        self.input_mode = tk.StringVar(value="summary")
        for val, txt in [("summary","Summary  (s², n)"), ("raw","Raw data  (values)")]:
            tk.Radiobutton(mf, text=txt, variable=self.input_mode, value=val,
                           font=("Consolas",10), bg=th("BG"), fg=th("CYAN"),
                           selectcolor=th("SURFACE"), activebackground=th("SURF3"),
                           cursor="hand2", command=self._on_input_mode).pack(side="left", padx=5)

        c=card(self)
        self.s2=tk.StringVar(); self.sig20=tk.StringVar()
        self.n=tk.StringVar();   self.alpha=tk.StringVar(value="0.05")
        self.tail=tk.StringVar(value="Two-tailed")
        g=tk.Frame(c,bg=th("SURF2")); g.pack(fill="x",pady=4)
        row_field(g,"Sample Variance  s²",self.s2,0)
        row_field(g,"Hypothesized  σ₀²",self.sig20,1,tooltip="H₀: σ²=σ₀²")
        row_field(g,"Sample Size  n",self.n,2,kind="int")
        alpha_field(g,self.alpha,3)
        make_combo(g,self.tail,["Two-tailed","Right-tailed","Left-tailed"],4,label="Tail")

        # Raw data frame
        self.raw_frame = card(self)
        tk.Label(self.raw_frame, text="  [ RAW DATA INPUT ]",
                 font=("Consolas",10,"bold"), bg=th("SURF2"), fg=th("GOLD2")
                 ).pack(anchor="w", padx=10, pady=(7,2))
        self.raw_var = tk.StringVar()
        raw_entry = tk.Entry(self.raw_frame, textvariable=self.raw_var, font=("Consolas",11),
                             bg=th("SURFACE"), fg=th("CYAN"), insertbackground=th("GOLD2"),
                             relief="flat", highlightthickness=1,
                             highlightbackground=th("BORDER2"), highlightcolor=th("GOLD"))
        raw_entry.pack(fill="x", padx=10, pady=3, ipady=7)
        tk.Label(self.raw_frame,
                 text="  e.g.:  23 45 31 28 40 35   or   23,45,31,28,40,35",
                 font=("Consolas",9), bg=th("SURF2"), fg=th("TEXT3")).pack(anchor="w", padx=10, pady=(0,3))
        parse_btn = tk.Button(self.raw_frame, text=">> PARSE & CALCULATE  s², n",
                              font=("Consolas",10,"bold"),
                              bg=th("SURF3"), fg=th("CYAN"), relief="flat",
                              cursor="hand2", pady=5, bd=0,
                              activebackground=th("GOLD_DIM"), activeforeground=th("TEXT"),
                              command=self._parse_raw)
        parse_btn.pack(fill="x", padx=10, pady=(0,5))
        self.raw_info_lbl = tk.Label(self.raw_frame, text="", font=("Consolas",10),
                                     bg=th("SURF2"), fg=th("GREEN"), justify="left")
        self.raw_info_lbl.pack(anchor="w", padx=10, pady=(0,5))
        self.raw_frame.pack_forget()

        self._load_vals({"s2":self.s2,"sig20":self.sig20,"n":self.n,"alpha":self.alpha})
        self.add_ai_extract(self)
        self.res=card(self); self.add_copy_btn(self,self.res)
        calc_button(self,"  >> RUN HYPOTHESIS TEST",self._calc)
        self.bind_entries_return(self._calc)

    def _on_input_mode(self):
        if self.input_mode.get() == "raw":
            self.raw_frame.pack(fill="x", pady=(0,3), padx=2)
        else:
            self.raw_frame.pack_forget()

    def _parse_raw(self):
        result, error = parse_raw_data(self.raw_var.get())
        if error:
            messagebox.showerror("ERROR", error)
            return
        n = result["n"]
        s2 = result["s"]**2  # variance
        self.s2.set(f"{s2:.6f}")
        self.n.set(str(n))
        self.raw_info_lbl.config(text=f"  >> n={n}   s²={s2:.4f}   >> FIELDS FILLED")
        self.set_status(f"Raw data parsed: n={n}, s²={s2:.4f}")

    def fill_from_dict(self, d):
        n = 0
        for key, var in [("s2",self.s2),("sigma20",self.sig20),
                         ("sig20",self.sig20),("n",self.n),("alpha",self.alpha)]:
            if key in d and d[key] is not None:
                var.set(str(d[key])); n += 1
        if "tail" in d and d["tail"] in ["Two-tailed","Right-tailed","Left-tailed"]:
            self.tail.set(d["tail"]); n += 1
        return n

    def _calc(self):
        try:
            s2=float(self.s2.get()); sig20=float(self.sig20.get())
            n=int(self.n.get());     alpha=float(self.alpha.get())
            tail=self.tail.get()
        except:
            messagebox.showerror("ERROR","Check inputs"); return
        if s2 <= 0 or sig20 <= 0:
            messagebox.showerror("ERROR","s² and σ₀² must be > 0"); return
        self._save_vals({"s2":self.s2,"sig20":self.sig20,"n":self.n,"alpha":self.alpha})
        df=n-1; ts=df*s2/sig20
        if tail=="Two-tailed":
            crit_lo=stats.chi2.ppf(alpha/2,df); crit_hi=stats.chi2.ppf(1-alpha/2,df)
            pval=2*min(stats.chi2.cdf(ts,df),1-stats.chi2.cdf(ts,df))
            reject=ts<crit_lo or ts>crit_hi
        elif tail=="Right-tailed":
            crit_hi=stats.chi2.ppf(1-alpha,df); crit_lo=None
            pval=1-stats.chi2.cdf(ts,df); reject=ts>crit_hi
        else:
            crit_lo=stats.chi2.ppf(alpha,df); crit_hi=None
            pval=stats.chi2.cdf(ts,df); reject=ts<crit_lo
        self.clear_res()
        dec_col="#FF0040" if reject else "#00FF88"
        h1_map={"Two-tailed":f"σ² ≠ {sig20}","Right-tailed":f"σ² > {sig20}","Left-tailed":f"σ² < {sig20}"}
        crit_str=(f"χ²_L = {crit_lo:.4f}   χ²_R = {crit_hi:.4f}" if tail=="Two-tailed" else
                  f"χ²_crit = {crit_hi:.4f}" if tail=="Right-tailed" else f"χ²_crit = {crit_lo:.4f}")
        conclusion=("At α={}, sufficient evidence to REJECT H₀.".format(alpha)
                    if reject else "At α={}, NOT sufficient evidence to reject H₀.".format(alpha))
        sig_label = "✦  REJECT NULL HYPOTHESIS (H₀)  >>  TEST IS SIGNIFICANT" if reject else "✦  ACCEPT NULL HYPOTHESIS (H₀)  >>  TEST IS NOT SIGNIFICANT"
        lines=[
            (result_row,["!! ASSUMPTION: Population must be Normally distributed", "#FFAA00"]),
            (divider,[]),
            (result_row,[f"H₀ :  σ² = {sig20}", "#BD00FF"]),
            (result_row,[f"H₁ :  {h1_map[tail]}", "#BD00FF"]),
            (divider,[]),
            (result_row,[f"df  =  n − 1  =  {df}", "#00E5FF"]),
            (result_row,[f"χ²  =  (n−1) · s² / σ₀²", "#FFD700", True]),
            (result_row,[f"    =  {df} × {s2} / {sig20}", "#A8D8F0", True]),
            (result_row,[f"    =  {ts:.4f}", "#00FF88", True]),
            (divider,[]),
            (result_row,[f"Critical Value(s):  {crit_str}", "#FF8800"]),
            (result_row,[f"p-value  =  {pval:.4f}", "#FF0040"]),
            (result_answer,[sig_label, dec_col]),
            (result_row,[f">>  {conclusion}", th("CYAN")])]
        AnimatedResults(self.res,self.root,lines,delay=70)
        self.root.after(len(lines)*70+100, lambda: p_badge(self.res,pval))
        verdict="REJECT" if reject else "FAIL TO REJECT"
        self.set_status(f">> TEST FOR σ²  {verdict} H₀  (χ²={ts:.4f}, p={pval:.4f})")
        self.log("Test for σ²",f"H₀:σ²={sig20}, χ²={ts:.4f}, p={pval:.4f}, {verdict}")
        x_max=df+5*math.sqrt(2*df)
        fig,ax=make_fig()
        x=np.linspace(0.01,x_max,500); ax.plot(x,stats.chi2.pdf(x,df),color=th("CYAN"),linewidth=2.0,alpha=0.9)

        # Acceptance and rejection regions
        if tail=="Two-tailed":
            xl=np.linspace(0.01,crit_lo,200); xr=np.linspace(crit_hi,x_max,200)
            xs_mid=np.linspace(crit_lo,crit_hi,200)
            ax.fill_between(xs_mid,stats.chi2.pdf(xs_mid,df),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xl,stats.chi2.pdf(xl,df),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")
            ax.fill_between(xr,stats.chi2.pdf(xr,df),color="#FF0040",alpha=0.35)
        elif tail=="Right-tailed":
            xr=np.linspace(crit_hi,x_max,200)
            xs_mid=np.linspace(0.01,crit_hi,200)
            ax.fill_between(xs_mid,stats.chi2.pdf(xs_mid,df),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xr,stats.chi2.pdf(xr,df),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")
        else:
            xl=np.linspace(0.01,crit_lo,200)
            xs_mid=np.linspace(crit_lo,x_max,200)
            ax.fill_between(xs_mid,stats.chi2.pdf(xs_mid,df),color="#00FF88",alpha=0.25,label="Acceptance Region (H₀)")
            ax.fill_between(xl,stats.chi2.pdf(xl,df),color="#FF0040",alpha=0.35,label="Rejection Region (H₁)")

        ax.axvline(min(ts,x_max*0.99),color=th("GOLD2"),linewidth=2.0,linestyle="--",
                   label=f"Test Statistic χ²={ts:.3f}")
        ax.legend(facecolor=th("SURF2"),edgecolor=th("BORDER2"),labelcolor=th("TEXT2"),fontsize=9,
                  loc="upper right", framealpha=0.9)
        style_ax(ax,f"Test for σ²  ({tail})")
        embed_plot(fig,self.pf)


# ═══════════════════════════════════════════════════════════════════════════════
#  CYBERPUNK MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):
    TOPICS = [
        ("  𝒩   Normal Distribution",     NormalDistPanel),
        ("  p̂   Sampling Dist. of p̂",    SamplingPropPanel),
        ("  χ²  Sampling Dist. of s²",    SamplingVarPanel),
        ("  μ   CI for μ",                 CIMeanPanel),
        ("  𝒑   CI for P",                 CIPropPanel),
        ("  σ²  CI for σ²",                CIVarPanel),
        ("  H₀  Test for μ",              TestMeanPanel),
        ("  H₀  Test for P",              TestPropPanel),
        ("  H₀  Test for σ²",             TestVarPanel),
    ]
    TOPIC_COLORS = [
        "#00FFC8","#00FFC8","#4DA6FF",
        "#00FF88","#00FF88","#00CC66",
        "#FFAA00","#FFAA00","#FFAA00"
    ]

    def __init__(self):
        super().__init__()
        self.title("[ STATS CALC v4 ] CYBERPUNK TERMINAL  ·  Abdelrhman Ramdan Kasem  ·  Horus University")
        self.geometry("1540x900")
        self.minsize(1200,720)
        self.configure(bg=th("BG"))
        self.current_theme = "dark"
        self.status_var = tk.StringVar(value=">>  SYSTEM READY  ·  SELECT TOPIC  ·  F1=FORMULAS  F2=TABLES")
        self._build()
        self._bind_shortcuts()

    def _bind_shortcuts(self):
        self.bind("<F1>",    lambda e: FormulaSheet(self))
        self.bind("<F2>",    lambda e: TableViewer(self))
        self.bind("<F3>",    lambda e: HistoryWindow(self))
        self.bind("<F5>",    lambda e: self._toggle_theme())
        self.bind("<Control-s>", lambda e: export_plot_png())

    def _build(self):
        # ── TOP NEON BAR ──
        tk.Frame(self, bg=th("CYAN"), height=2).pack(fill="x")

        # ── HEADER ──
        hdr = tk.Frame(self, bg=th("SURFACE"), height=62)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        # Left accent bars (double neon)
        bar_f = tk.Frame(hdr, bg=th("SURFACE")); bar_f.pack(side="left", fill="y")
        tk.Frame(bar_f, bg=th("CYAN"),    width=3).pack(side="left", fill="y")
        tk.Frame(bar_f, bg=th("BG"),      width=2).pack(side="left", fill="y")
        tk.Frame(bar_f, bg=th("MAGENTA"), width=2).pack(side="left", fill="y")

        tf = tk.Frame(hdr, bg=th("SURFACE")); tf.pack(side="left", padx=14, pady=8)
        # Glowing title
        self._title_lbl = tk.Label(tf,
            text="[ ∑ ]  STATISTICS CALCULATOR  v4  //  CYBERPUNK TERMINAL",
            font=("Consolas", 14, "bold"),
            bg=th("SURFACE"), fg=th("CYAN"))
        self._title_lbl.pack(anchor="w")
        tk.Label(tf,
            text=">>  Abdelrhman Ramdan Kasem  ·  Horus University — Egypt  ·  scipy · numpy · matplotlib",
            font=("Consolas", 9),
            bg=th("SURFACE"), fg=th("TEXT3")).pack(anchor="w")

        rf = tk.Frame(hdr, bg=th("SURFACE")); rf.pack(side="right", padx=12)
        self.date_lbl = tk.Label(rf, text=datetime.now().strftime("%Y-%m-%d"),
                 font=("Consolas", 9),
                 bg=th("SURFACE"), fg=th("TEXT3"))
        self.date_lbl.pack(anchor="e")

        btn_bar = tk.Frame(hdr, bg=th("SURFACE")); btn_bar.pack(side="right", padx=4)
        toolbar_btns = [
            ("[F1] FORMULAS",    lambda: FormulaSheet(self)),
            ("[F2] TABLES",      lambda: TableViewer(self)),
            ("[F3] HISTORY",     lambda: HistoryWindow(self)),
            ("[F5] THEME",       self._toggle_theme),
            ("[^S] EXPORT",      export_plot_png),
        ]
        for txt, cmd in toolbar_btns:
            b = tk.Button(btn_bar, text=txt,
                          font=("Consolas", 8, "bold"),
                          bg=th("BG"), fg=th("CYAN"),
                          relief="flat", cursor="hand2",
                          padx=8, pady=5,
                          highlightthickness=1, highlightbackground=th("BORDER2"),
                          activebackground=th("SURF3"),
                          activeforeground=th("CYAN"),
                          command=cmd)
            b.pack(side="left", padx=2, pady=16)
            b.bind("<Enter>", lambda e, b=b: b.config(bg=th("SURF3"), fg=th("TEXT")))
            b.bind("<Leave>", lambda e, b=b: b.config(bg=th("BG"),    fg=th("CYAN")))

        tk.Frame(self, bg=th("MAGENTA"), height=1).pack(fill="x")
        tk.Frame(self, bg=th("BG"), height=1).pack(fill="x")
        tk.Frame(self, bg=th("BORDER2"), height=1).pack(fill="x")

        body = tk.Frame(self, bg=th("BG")); body.pack(fill="both", expand=True)

        # ── SIDEBAR ──
        self.sidebar = tk.Frame(body, bg=th("SURFACE"), width=240)
        self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)
        # Neon border on sidebar right
        tk.Frame(body, bg=th("CYAN"), width=1).pack(side="left", fill="y")
        tk.Frame(body, bg=th("BG"),   width=1).pack(side="left", fill="y")

        # Sidebar header
        sh = tk.Frame(self.sidebar, bg=th("SURFACE"))
        sh.pack(fill="x", padx=10, pady=(12, 4))
        tk.Frame(sh, bg=th("CYAN"), width=3).pack(side="left", fill="y", padx=(0, 7))
        tk.Label(sh, text="[ MODULES ]", font=("Consolas", 10, "bold"),
                 bg=th("SURFACE"), fg=th("CYAN")).pack(side="left")

        groups = [(0, "DISTRIBUTIONS"), (3, "CONF. INTERVALS"), (6, "HYPOTHESIS TESTS")]
        self.topic_btns = []

        for i, (label, _) in enumerate(self.TOPICS):
            for start, glabel in groups:
                if i == start:
                    gf = tk.Frame(self.sidebar, bg=th("SURFACE"))
                    gf.pack(fill="x", padx=8, pady=(9, 2))
                    hf = tk.Frame(gf, bg=th("SURFACE")); hf.pack(fill="x")
                    tk.Label(hf, text=f"  {glabel}",
                             font=("Consolas", 8, "bold"),
                             bg=th("SURFACE"), fg=th("TEXT3"),
                             anchor="w").pack(side="left", fill="x", padx=3)
                    tk.Frame(gf, bg=th("BORDER2"), height=1).pack(fill="x", padx=4, pady=(2, 0))
                    break

            col = self.TOPIC_COLORS[i]
            fb = tk.Frame(self.sidebar, bg=th("SURFACE"))
            fb.pack(fill="x", padx=7, pady=1)

            # Indicator dot frame
            dot_f = tk.Frame(fb, bg=th("SURFACE"), width=8)
            dot_f.pack(side="left", fill="y")
            dot = tk.Frame(dot_f, bg=th("SURFACE"), width=3, height=20)
            dot.place(relx=0.5, rely=0.5, anchor="center")

            # Neon indicator bar (animated)
            indicator = tk.Frame(fb, bg=th("SURFACE"), width=2)
            indicator.pack(side="left", fill="y")

            b = tk.Button(fb, text=label.strip(),
                          font=("Consolas", 9),
                          bg=th("SURFACE"), fg=th("TEXT2"),
                          relief="flat", anchor="w",
                          padx=8, pady=6, cursor="hand2",
                          activebackground=th("SURF3"),
                          activeforeground=col,
                          command=lambda i=i: self._switch(i))
            b.pack(fill="x", side="left", expand=True)
            self.topic_btns.append((b, col, fb, dot, indicator))

        tk.Frame(self.sidebar, bg=th("BORDER2"), height=1).pack(fill="x", padx=10, pady=(10, 4))

        # Keyboard hints in mono style
        hint_f = tk.Frame(self.sidebar, bg=th("SURFACE")); hint_f.pack(fill="x", padx=10)
        tk.Label(hint_f, text="[ HOTKEYS ]",
                 font=("Consolas", 8, "bold"), bg=th("SURFACE"), fg=th("TEXT3")).pack(anchor="w")
        hints = [f"  [{i+1}]  {self.TOPICS[i][0].strip()[:18]}" for i in range(9)]
        tk.Label(hint_f, text="\n".join(hints),
                 font=("Consolas", 8),
                 bg=th("SURFACE"), fg=th("TEXT3"),
                 justify="left").pack(anchor="w", pady=(2, 5))

        def _safe_switch(i):
            if isinstance(self.focus_get(), tk.Entry): return
            self._switch(i)
        for i in range(9):
            self.bind(str(i + 1), lambda e, i=i: _safe_switch(i))

        # ── MAIN PANED ──
        self.paned = tk.PanedWindow(body, orient="horizontal", bg=th("BG"),
                                    sashwidth=5, sashrelief="flat", handlesize=0)
        self.paned.pack(fill="both", expand=True)

        left_outer = tk.Frame(self.paned, bg=th("BG"))
        self.paned.add(left_outer, minsize=460, width=520)

        self.sc = tk.Canvas(left_outer, bg=th("BG"), bd=0, highlightthickness=0)
        sb_scroll = tk.Scrollbar(left_outer, orient="vertical", command=self.sc.yview)
        self.inner = tk.Frame(self.sc, bg=th("BG"))
        self.inner.bind("<Configure>",
                        lambda e: self.sc.configure(scrollregion=self.sc.bbox("all")))
        self.sc.create_window((0, 0), window=self.inner, anchor="nw")
        self.sc.configure(yscrollcommand=sb_scroll.set)
        self.sc.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=5)
        sb_scroll.pack(side="right", fill="y")

        def _on_mousewheel(e):
            if isinstance(self.focus_get(), tk.Entry): return
            self.sc.yview_scroll(int(-1 * (e.delta / 120)), "units")

        self.sc.bind("<MouseWheel>", _on_mousewheel)
        self.inner.bind("<MouseWheel>", _on_mousewheel)

        def _bind_scroll(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children(): _bind_scroll(child)
        self.inner.bind("<Configure>", lambda e: _bind_scroll(self.inner))

        right_outer = tk.Frame(self.paned, bg=th("BG"))
        self.paned.add(right_outer, minsize=300)

        # Neon left border for plot area
        tk.Frame(right_outer, bg=th("CYAN"), width=1).pack(side="left", fill="y", pady=8)
        tk.Frame(right_outer, bg=th("BG"),   width=3).pack(side="left", fill="y")

        self.plot_frame = tk.Frame(right_outer, bg=th("BG"))
        self.plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ── CYBERPUNK STATUS BAR ──
        sb = tk.Frame(self, bg=th("SURFACE"), height=30)
        sb.pack(fill="x", side="bottom"); sb.pack_propagate(False)

        # Neon top border on status bar
        tk.Frame(self, bg=th("BORDER2"), height=1).pack(fill="x", side="bottom")

        # Left indicator dots with neon glow
        dots_f = tk.Frame(sb, bg=th("SURFACE")); dots_f.pack(side="left", padx=8)
        self._dot_anim = [0]
        self.status_dots = []
        dot_colors = [th("GLOW_CYAN"), th("MAGENTA"), th("GOLD")]
        for dc in dot_colors:
            d = tk.Label(dots_f, text="●", font=("Consolas", 10),
                         bg=th("SURFACE"), fg=dc)
            d.pack(side="left", padx=2)
            self.status_dots.append((d, dc))

        tk.Frame(sb, bg=th("BORDER2"), width=1).pack(side="left", fill="y", pady=5)

        tk.Label(sb, textvariable=self.status_var,
                 font=("Consolas", 9),
                 bg=th("SURFACE"), fg=th("CYAN"),
                 anchor="w", padx=10).pack(side="left", fill="x", expand=True)

        # Right side
        tk.Label(sb,
                 text="F1·F2·F3·F5·Ctrl+S·1-9",
                 font=("Consolas", 8),
                 bg=th("SURFACE"), fg=th("TEXT3")).pack(side="right", padx=8)
        tk.Frame(sb, bg=th("BORDER2"), width=1).pack(side="right", fill="y", pady=5)

        self.clock_lbl = tk.Label(sb, text="",
                                  font=("Consolas", 9, "bold"),
                                  bg=th("SURFACE"), fg=th("GOLD2"))
        self.clock_lbl.pack(side="right", padx=10)

        tk.Frame(sb, bg=th("BORDER2"), width=1).pack(side="right", fill="y", pady=5)

        # LIVE indicator
        self.live_lbl = tk.Label(sb, text="● LIVE",
                                 font=("Consolas", 8, "bold"),
                                 bg=th("SURFACE"), fg=th("GREEN"))
        self.live_lbl.pack(side="right", padx=8)

        self._tick()
        self._placeholder()
        self._switch(0)

    def _tick(self):
        self.clock_lbl.config(text=datetime.now().strftime("%H:%M:%S"))
        # Animate LIVE dot
        on = (datetime.now().second % 2 == 0)
        self.live_lbl.config(fg=th("GREEN") if on else th("TEXT3"))
        self.after(500, self._tick)

    def _placeholder(self):
        fig,ax=make_fig(h=4.0)
        x=np.linspace(-4,4,400)
        ax.plot(x,stats.norm.pdf(x),color=th("CYAN"),linewidth=2.0,alpha=0.8)
        ax.fill_between(x,stats.norm.pdf(x),color=th("NEON_BLUE"),alpha=0.05)
        for s,a in [(1.5,0.03),(2.5,0.015)]:
            ax.fill_between(x,stats.norm.pdf(x,0,s),color=th("CYAN"),alpha=a)
        style_ax(ax,">>  SELECT TOPIC  ·  PRESS CALCULATE  ·  F1 FOR FORMULAS")
        embed_plot(fig,self.plot_frame)

    def _toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        T.update(THEMES[self.current_theme])
        idx = getattr(self, "_current_idx", 0)
        self.configure(bg=th("BG"))
        self.sidebar.configure(bg=th("SURFACE"))
        self._switch(idx)
        self.status_var.set(f">> THEME SWITCHED >> {self.current_theme.upper()}")

    def _switch(self, idx):
        self._current_idx = idx
        for i, (b, col, fb, dot, indicator) in enumerate(self.topic_btns):
            if i == idx:
                b.configure(bg=th("SURF2"), fg=col, font=("Consolas", 10, "bold"))
                fb.configure(bg=th("SURF2"))
                dot.configure(bg=col)
                indicator.configure(bg=col)
                # Add glow effect to active button
                b.configure(activebackground=th("SURF3"), activeforeground=col)
            else:
                b.configure(bg=th("SURFACE"), fg=th("TEXT2"), font=("Consolas", 9))
                fb.configure(bg=th("SURFACE"))
                dot.configure(bg=th("SURFACE"))
                indicator.configure(bg=th("SURFACE"))
        for w in self.inner.winfo_children(): w.destroy()
        panel = self.TOPICS[idx][1](self.inner, self.plot_frame, self.status_var, self)
        panel.pack(fill="both", expand=True, padx=3, pady=2)
        self.sc.yview_moveto(0)
        self.status_var.set(
            f">>  MODULE: {self.TOPICS[idx][0].strip().upper()}  ·  ENTER VALUES  ·  PRESS CALCULATE OR [ENTER]")


if __name__ == "__main__":
    App().mainloop()
