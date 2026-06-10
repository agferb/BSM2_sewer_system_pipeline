import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.integrate import solve_ivp

from pathlib import Path


# Load flow data
parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path, help="Path to downloaded .txt file")
parser.add_argument(
    "calc_flow", type=Path, help="Path to calculated flow data .csv file"
)
parser.add_argument("--t_min", type=float, default=360)
parser.add_argument("--t_max", type=float, default=380)
args = parser.parse_args()

data_dir = args.input.parent
t_min = args.t_min
t_max = args.t_max

solids_data = pd.read_csv(
    args.input,
    sep=r"\s+",
    header=None,
    usecols=[0, 14],
)

solids_data.columns = ["time", "TSS_0"]
solids_data = solids_data.set_index("time")
solids_data.iloc[:, 0] = solids_data.iloc[:, 0] / 1000

flow_data = pd.read_csv(args.calc_flow, index_col=0)

# Analysis interval
solids_data = solids_data[solids_data.index > t_min]
solids_data = solids_data[solids_data.index < t_max]
flow_data = flow_data[flow_data.index > t_min]
flow_data = flow_data[flow_data.index < t_max]

# Parameters
M_max = 2000  # kg
Q_lim = 70000  # m3/d
n = 15  # -
FF = 500  # -
sub_areas = flow_data.shape[1] - 1


# Solver inputs
t_eval = flow_data.index.values
M0 = 100  # kg


# Function to simulate the first-flush block
def ffe_block(t, M, Q_fun, TSS_fun, M_max, Q_lim, n, FF):

    Q_in = Q_fun(t)
    TSS_in = TSS_fun(t)
    dM_dt = (
        Q_in * TSS_in * (1 - M / M_max)
        - (Q_in) ** n / ((Q_lim) ** n + (Q_in) ** n) * M * FF
    )

    return dM_dt


# Simulate first-flush for the whole area
Q_in_arr = flow_data.iloc[:, 0].values
Q_out_arr = flow_data.iloc[:, sub_areas].values
TSS_in_arr = solids_data.iloc[:, 0].values

Q_in_fun = interp1d(t_eval, Q_in_arr, fill_value="extrapolate", kind="linear")
TSS_in_fun = interp1d(t_eval, TSS_in_arr, fill_value="extrapolate", kind="linear")

results = solve_ivp(
    ffe_block,
    t_span=(t_eval[0], t_eval[-1]),
    t_eval=t_eval,
    y0=[M0],
    args=(Q_in_fun, TSS_in_fun, M_max, Q_lim, n, FF),
)

dM_dt_arr = np.array(
    [
        ffe_block(t, M, Q_in_fun, TSS_in_fun, M_max, Q_lim, n, FF)
        for t, M in zip(t_eval, results.y.T)
    ]
)

solids_data[f"TSS_{sub_areas}"] = np.array(
    [
        (TSS_in * Q_in - dM_dt) / Q_out
        for TSS_in, Q_in, dM_dt, Q_out in zip(
            TSS_in_arr, Q_in_arr, dM_dt_arr, Q_out_arr
        )
    ]
)

# Plot results and save .png figure
fig, ax = plt.subplots(constrained_layout=True)
ax.plot(t_eval, solids_data["TSS_0"], "--g", label="before sewer")
ax.plot(
    t_eval, solids_data[f"TSS_{sub_areas}"], "-k", label=f"after {sub_areas} sub-areas"
)
ax.set(ylabel="total solids [kg/m3]", xlabel="time [d]")
fig.legend(loc="upper right")

# Save results
solids_data.to_csv(data_dir / f"solids_after_{sub_areas}_subareas_{t_min}-{t_max}.csv")
fig.savefig(
    data_dir / f"solids_after_{sub_areas}_subareas_{t_min}-{t_max}.png",
    dpi=300,
    bbox_inches="tight",
)
