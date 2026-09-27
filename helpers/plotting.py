"""
Project-specific figure helpers for the ENG2440 Assignment 1 notebook.

The general house style (fonts, colours, tick/frame rules, the figure audit) lives in
`helpers/paper_plot_style.py`. This file only adds what this project needs on top:
drawing a radiograph panel, overlaying a Grad-CAM map, styling notebook tables, and a
`save_and_show` wrapper that audits + saves a figure and then displays it in the notebook.

Nothing in this file touches the data or the models.
"""
import matplotlib as mpl
import matplotlib.patches as mpatches
import numpy as np
from IPython.display import display

from helpers.paper_plot_style import *            # noqa: F401,F403  (house style + audit)
from helpers.paper_plot_style import (GOLD, RED, PETROL, INK, MUTED, RULE, TICK_PT,
                                      save_fig, text_color)

# Colours with a fixed meaning in every figure
POS, NEG = RED, PETROL               # positive class = the accent (red), negative class = petrol
BOX = GOLD                           # annotated opacity boxes on radiographs



def tint(color, strength):
    """Mix `color` with white: strength 1 gives the full colour, 0 gives white (quiet fills, shaded cells)."""
    return tuple(1 - strength * (1 - c) for c in mpl.colors.to_rgb(color))


def readable_on(background):
    """White or dark ink, whichever contrasts more with `background` (WCAG relative luminance)."""
    def luminance(color):
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in mpl.colors.to_rgb(color)]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    bg = luminance(background)
    white_contrast = (1 + 0.05) / (bg + 0.05)
    ink_contrast = (bg + 0.05) / (luminance(INK) + 0.05)
    return "white" if white_contrast > ink_contrast else INK


def save_and_show(fig, name, width="full", rel=1.0):
    """Audit + save the figure (vector PDF and preview PNG under figures/), then show it in the notebook."""
    save_fig(fig, name, width=width, rel=rel)
    display(fig)


def show_xray(ax, img, title=None, note=None, boxes=None, box_scale=1.0, tag=None, tag_color=None,
              box_color=None, title_color=None):
    """Draw one radiograph on `ax`.

    title      short panel title naming the condition (e.g. "True positive · typical").
    note       one line of facts under the image (e.g. "p = 0.91 · AP · 64 y").
    boxes      optional list of (x, y, w, h) boxes in original 1024-px coordinates.
    box_scale  factor mapping original coordinates to `img` pixels (e.g. 224/1024).
    tag        optional short label in the top-left corner (e.g. the ground-truth class).
    box_color  colour of the boxes (default gold; white on Grad-CAM overlays, where gold would blend in).
    title_color  colour of the title (default ink), e.g. red for the error columns in G1/G3.
    """
    ax.imshow(img, cmap="gray", interpolation="lanczos")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    for (x, y, w, h) in (boxes or []):
        ax.add_patch(mpatches.Rectangle((x * box_scale, y * box_scale), w * box_scale, h * box_scale,
                                        fill=False, edgecolor=box_color or BOX, linewidth=1.0))
    if tag:
        ax.text(0.04, 0.96, tag, transform=ax.transAxes, fontsize=TICK_PT, fontweight="bold",
                color=text_color(tag_color or INK), ha="left", va="top",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="none", alpha=0.9))
    if title:
        ax.set_title(title, fontsize=TICK_PT, pad=3, color=text_color(title_color or INK))
    if note:
        ax.set_xlabel(note, fontsize=TICK_PT, color=MUTED, labelpad=2)


def place_text(ax, text, prefer=(0.03, 0.97), **kw):
    """Put `text` in an empty part of `ax`, as close as possible to `prefer` (axes fractions, 0-1).

    Candidate positions on a 15 x 15 grid are tried from the nearest to the farthest; the first one whose
    text box stays inside the axes and touches no plotted line, no bar and no other text is kept.
    This uses the same geometry as the figure audit, so labels never need hand-tuned coordinates.
    """
    from helpers.paper_plot_style import _line_pts
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    points = [p for line in ax.lines for p in _line_pts(ax, line)]
    boxes = [t.get_window_extent(renderer) for t in fig.findobj(mpl.text.Text) if t.get_visible() and t.get_text().strip()]
    boxes += [p.get_window_extent(renderer) for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    grid = [(x, y) for x in np.linspace(0.02, 0.98, 15) for y in np.linspace(0.03, 0.97, 15)]
    grid.sort(key=lambda xy: (xy[0] - prefer[0]) ** 2 + (xy[1] - prefer[1]) ** 2)
    kw = {"fontsize": TICK_PT, "color": INK, **kw}
    for x, y in grid:
        t = ax.text(x, y, text, transform=ax.transAxes, ha="left" if x < 0.5 else "right",
                    va="top" if y > 0.5 else "bottom", **kw)
        bb = t.get_window_extent(renderer)
        inside = ax.bbox.contains(bb.x0, bb.y0) and ax.bbox.contains(bb.x1, bb.y1)
        free = not any(bb.padded(2).contains(px, py) for px, py in points) and not any(bb.overlaps(b) for b in boxes)
        if inside and free:
            return t
        t.remove()
    print(f"place_text: no empty spot for {text[:30]!r}; placed at the preferred position")
    return ax.text(*prefer, text, transform=ax.transAxes, ha="left" if prefer[0] < 0.5 else "right",
                   va="top" if prefer[1] > 0.5 else "bottom", **kw)


def overlay_cam(ax, cam, max_alpha=0.6):
    """Draw a Grad-CAM map (2-D array scaled to [0, 1]) over an image already shown on `ax`.

    Low values are transparent and high values opaque, so the radiograph stays visible where the
    model is not looking. Colour map: 'inferno' (perceptually uniform, dark -> yellow), chosen over
    cividis/viridis because its dark low end does not tint the grey radiograph.
    """
    rgba = mpl.colormaps["inferno"](cam)
    rgba[..., 3] = max_alpha * cam ** 0.8
    ax.imshow(rgba, interpolation="bilinear")


def box_legend_handle(label="annotated opacity"):
    """Legend handle for the ground-truth boxes."""
    return mpatches.Patch(facecolor="none", edgecolor=BOX, linewidth=1.0, label=label)


def style_table(df, precision=3, caption=None):
    """Render a pandas DataFrame as a clean HTML table in the notebook."""
    styler = (df.style
              .format(precision=precision, thousands=",", na_rep="–")
              .set_table_styles([
                  {"selector": "th", "props": [("background", "#f4f4f4"), ("color", INK),
                                                ("font-weight", "600"), ("text-align", "center"),
                                                ("padding", "6px 10px"), ("border-bottom", f"1px solid {RULE}")]},
                  {"selector": "td", "props": [("padding", "5px 10px"), ("text-align", "center"),
                                                ("border-bottom", "1px solid #ebebeb"),
                                                ("font-variant-numeric", "tabular-nums")]},
                  {"selector": "caption", "props": [("caption-side", "top"), ("text-align", "left"),
                                                     ("font-weight", "600"), ("color", INK),
                                                     ("padding-bottom", "6px")]},
              ]))
    int_cols = [c for c in df.columns if df[c].dtype.kind in "iuf"
                and df[c].notna().any() and (df[c].dropna() % 1 == 0).all()
                and df[c].dropna().abs().max() > 1]                      # counts, not 0/1 rates
    if int_cols:
        styler = styler.format("{:,.0f}", subset=int_cols, na_rep="–")
    if caption:
        styler = styler.set_caption(caption)
    return styler
