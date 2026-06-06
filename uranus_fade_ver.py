# WARNING!!! FADING ORBITS CAUSE IMMENSE LAG!!!

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from astroquery.jplhorizons import Horizons
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from datetime import datetime, timedelta



# Pre-define 1D arrays of JPL IDs before merging into main list
Galileans = np.arange(701, 705+1)
NumIrrs = np.arange(716, 724+1)
ProvIrrs = np.array([75051])

ORBITAL_PERIODS = {
    # Regular moons (Ariel, Umbriel, Titania, Oberon, Miranda)
    701: 2.520,
    702: 4.144,
    703: 8.706,
    704: 13.463,
    705: 1.413,
    # Irregular moons (NumIrrs: 716–724)
    716: 580,
    717: 1286,
    718: 1974,
    719: 2215,
    720: 677,
    721: 749,
    722: 267,
    723: 1655,
    724: 2788,
    # Provisional irregular
    75051: 681,
}

DEFAULT_PERIOD = 500.0  # fallback if ID not in table


# ---------------------------------
# User parameters
# ---------------------------------
DARK_MODE = input("Dark mode? (y/n): ")  # Set to False for default white background
if DARK_MODE == "y":
    DARK_MODE = True
else:
    DARK_MODE = False

def apply_dark_mode(fig, axes_2d, axes_3d):
    fig.patch.set_facecolor('black')
    for ax2d in axes_2d:
        ax2d.set_facecolor('black')
        ax2d.tick_params(colors='white')
        ax2d.xaxis.label.set_color('white')
        ax2d.yaxis.label.set_color('white')
        ax2d.title.set_color('white')
        for spine in ax2d.spines.values():
            spine.set_edgecolor('white')
        ax2d.grid(True, alpha=0.15, color='white')
    for ax3d in axes_3d:
        ax3d.set_facecolor('black')
        ax3d.tick_params(colors='white')
        ax3d.xaxis.label.set_color('white')
        ax3d.yaxis.label.set_color('white')
        ax3d.zaxis.label.set_color('white')
        ax3d.title.set_color('white')
        ax3d.xaxis.pane.set_facecolor('black')
        ax3d.yaxis.pane.set_facecolor('black')
        ax3d.zaxis.pane.set_facecolor('black')
        ax3d.xaxis.pane.set_edgecolor('gray')
        ax3d.yaxis.pane.set_edgecolor('gray')
        ax3d.zaxis.pane.set_edgecolor('gray')


# Define functions for filtering a specific moon's orbit color & opacity
def color_filter(ID):
    if DARK_MODE == True:
        # Regular moons are magenta
        if ID <= 705:
            return "magenta"
        # Moon 722 is red
        if ID == 723:
            return "#64a8ff"
        else:
            return "#ff6464"

    else:  # regular light mode
        # Regular moons are magenta
        if ID <= 705:
            return "magenta"
        # Moon 722 is red
        if ID == 723:
            return "blue"
        else:
            return "red"

def opacity_filter(ID):
    if DARK_MODE == True:
        # Regular moons
        if ID <= 705:
            return 1.0
        # Moon 722
        if ID == 722:
            return 1.0
        else:
            return 1.0
        
    else:  # regular light mode
        # Regular moons
        if ID <= 705:
            return 0.5
        # Moon 722
        if ID == 722:
            return 1.0
        else:
            return 0.75


MOON_IDS = np.concatenate((Galileans, NumIrrs, ProvIrrs))  # merge 1D arrays into a bigger 1D array
N_MOONS = len(MOON_IDS)

START_DATE = "2026-Jan-01"   # orbit start epoch (same for all moons)

# ---------------------------------
# Query JPL Horizons — one full orbit per moon
# ---------------------------------
trajectories = {}

start_dt = datetime.strptime(START_DATE, "%Y-%b-%d")

for i in range(N_MOONS):
    moon_id = int(MOON_IDS[i])
    period_days = ORBITAL_PERIODS.get(moon_id, DEFAULT_PERIOD)

    # Build a stop date that covers exactly one orbital period
    stop_dt = start_dt + timedelta(days=period_days)
    stop_date = stop_dt.strftime("%Y-%b-%d")

    # Always target ~500 points regardless of period length
    step_hours = max(1, int(period_days * 24 / 500))
    step = f"{step_hours}h"

    obj = Horizons(
        id=moon_id,
        location='@7',  # Uranus barycenter
        epochs={
            'start': START_DATE,
            'stop': stop_date,
            'step': step,
        }
    )

    vec = obj.vectors()
    trajectories[i] = {
        "x": np.array(vec['x']),
        "y": np.array(vec['y']),
        "z": np.array(vec['z']),
        "period_days": period_days,
    }

# ---------------------------------
# Figure setup — 1x3 layout: 3D | XY | XZ
# ---------------------------------
fig = plt.figure(figsize=(25, 9))
ax    = fig.add_subplot(131, projection='3d')
ax_xy = fig.add_subplot(132)
ax_xz = fig.add_subplot(133)

### Uranus as a sphere ###
r_uranus = 0.0001708353192  # Uranus radius in AU
u, v = np.mgrid[0:2*np.pi:50j, 0:np.pi:50j]

x_uranus = r_uranus * np.cos(u) * np.sin(v)
y_uranus = r_uranus * np.sin(u) * np.sin(v)
z_uranus = r_uranus * np.cos(v)

ax.plot_surface(x_uranus, y_uranus, z_uranus, color='turquoise', alpha=1, rstride=1, cstride=1)

# Uranus dot on 2D projections
circle_xy = plt.Circle((0, 0), r_uranus, facecolor='turquoise', edgecolor='none')
circle_xz = plt.Circle((0, 0), r_uranus, facecolor='turquoise', edgecolor='none')
ax_xy.add_patch(circle_xy)
ax_xz.add_patch(circle_xz)

# Plot full orbits with fade
max_range = 0.0

for i in range(N_MOONS):
    x = trajectories[i]['x']
    y = trajectories[i]['y']
    z = trajectories[i]['z']

    # Build per-segment RGBA colors (shared by all three plots)
    base_color = plt.matplotlib.colors.to_rgb(color_filter(MOON_IDS[i]))
    max_alpha  = opacity_filter(MOON_IDS[i])

    # --- 3D ---
    points_3d = np.array([x, y, z]).T.reshape(-1, 1, 3)
    segments_3d = np.concatenate([points_3d[:-1], points_3d[1:]], axis=1)
    alphas = np.linspace(0.0, max_alpha, len(segments_3d))
    colors = [(*base_color, a) for a in alphas]

    lc = Line3DCollection(segments_3d, colors=colors, linewidth=1.0)
    ax.add_collection3d(lc)

    # --- XY projection ---
    points_xy = np.array([x, y]).T.reshape(-1, 1, 2)
    segments_xy = np.concatenate([points_xy[:-1], points_xy[1:]], axis=1)
    lc_xy = LineCollection(segments_xy, colors=colors, linewidth=1.0)
    ax_xy.add_collection(lc_xy)

    # --- XZ projection ---
    points_xz = np.array([x, z]).T.reshape(-1, 1, 2)
    segments_xz = np.concatenate([points_xz[:-1], points_xz[1:]], axis=1)
    lc_xz = LineCollection(segments_xz, colors=colors, linewidth=1.0)
    ax_xz.add_collection(lc_xz)

    r = np.max(np.sqrt(x**2 + y**2 + z**2))
    max_range = max(max_range, r)

# ---------------------------------
# Axis formatting — 3D
# ---------------------------------
for axis in "xyz":
    getattr(ax, f"set_{axis}lim")((-max_range, max_range))

ax.set_aspect("equal")
ax.set_xlabel("X (AU)")
ax.set_ylabel("Y (AU)")
ax.set_zlabel("Z (AU)")

grid_alpha = 0.3
ax.xaxis.gridlines.set_alpha(grid_alpha)
ax.yaxis.gridlines.set_alpha(grid_alpha)
ax.zaxis.gridlines.set_alpha(grid_alpha)

ax.xaxis.set_pane_color((1.0, 1.0, 1.0, grid_alpha))
ax.yaxis.set_pane_color((1.0, 1.0, 1.0, grid_alpha))
ax.zaxis.set_pane_color((1.0, 1.0, 1.0, grid_alpha))

ax.set_title(f"3D View", fontsize=18)

# ---------------------------------
# Axis formatting — 2D projections
# ---------------------------------
for axis_2d, xlabel, ylabel, title in [
    (ax_xy, "X (AU)", "Y (AU)", "XY Projection (ecliptic plane, top view)"),
    (ax_xz, "X (AU)", "Z (AU)", "XZ Projection (side view)"),
]:
    axis_2d.set_xlim(-max_range, max_range)
    axis_2d.set_ylim(-max_range, max_range)
    axis_2d.set_aspect("equal")
    axis_2d.set_xlabel(xlabel)
    axis_2d.set_ylabel(ylabel)
    axis_2d.set_title(title, fontsize=18)
    axis_2d.grid(True, alpha=0.3)


if DARK_MODE:
    apply_dark_mode(fig, axes_2d=[ax_xy, ax_xz], axes_3d=[ax])
    fig.suptitle(f"Uranian irregular moons ({START_DATE})", fontsize=20, color='white')
else:
    fig.suptitle(f"Uranian irregular moons ({START_DATE})", fontsize=22)

plt.tight_layout()

plt.savefig("uranus_fade_ver.svg", dpi=300, bbox_inches="tight")
print(f"Saved as uranus_fade_ver.svg")
#plt.show()
