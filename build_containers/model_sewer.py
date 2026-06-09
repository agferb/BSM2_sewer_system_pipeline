import argparse
import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import solve_ivp

from pathlib import Path


# Load flow data
parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path, help="Path to input .pkl file")
args = parser.parse_args()

input_path = args.input
work_dir = input_path.parent

with open(input_path, "br") as fh:
    flow_data = pkl.load(fh).loc[:, ["Q_0"]]

# Analysis interval
t_min = 360  # d
t_max = 380  # d
flow_data = flow_data[flow_data.index > t_min]
flow_data = flow_data[flow_data.index < t_max]

# Parameters
A_total = 1100  # m2
C_gain = 3000  # -
sub_areas = 4
A_sub = A_total / sub_areas

# Solver inputs
t_eval = flow_data.index.values


# Function to simulate the sewer block
def sewer_block(t, h, Q_fun, A, C):

    Q_in = Q_fun(t)
    dh_dt = (Q_in - C * h ** (3 / 2)) / A

    return dh_dt


# Simulate flow for each sub-area
for i in range(sub_areas):

    Q_in_fun = interp1d(
        t_eval, flow_data.iloc[:, i].values, fill_value="extrapolate", kind="linear"
    )
    h0 = (flow_data.iloc[0, i] / C_gain) ** (2 / 3)  # m

    results_i = solve_ivp(
        sewer_block,
        t_span=(t_eval[0], t_eval[-1]),
        t_eval=t_eval,
        y0=[h0],
        args=(Q_in_fun, A_sub, C_gain),
    )

    flow_data[f"Q_{i+1}"] = C_gain * results_i.y.T ** (3 / 2)

# Plot results and save .png figure
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(t_eval, flow_data["Q_0"], "--g", label="before sewer")
ax.plot(t_eval, flow_data[f"Q_{sub_areas}"], "-k", label=f"after {sub_areas} sub-areas")
ax.set(ylabel="flow rate [m3/d]", xlabel="time [d]")
fig.legend(loc="upper right")
fig.savefig(
    work_dir / f"sewer_flow_{sub_areas}_subareas.png", dpi=300, bbox_inches="tight"
)

# Save results
with open(work_dir / "_sewer_flow_data.pkl", "bw") as fh:
    pkl.dump(flow_data, fh)
