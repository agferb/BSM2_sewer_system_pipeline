import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

from pathlib import Path


# Function to simulate the sewer block
def sewer_block(t, h, Q_in_data, t_eval, A, C):

    Q_in = np.interp(t, Q_in_data, t_eval)
    dh_dt = (Q_in - C * h ^ (3 / 2)) / A

    return dh_dt


# Load flow data
data_path = Path(__file__).parent / "data"
with open(data_path / "_final_data_bsm2.pkl", "br") as fh:
    data_df = pkl.load(fh)

data_df = data_df[data_df.index > 364]
data_df = data_df[data_df.index < 380]

# Parameters
A_total = 1100  # m2
C_gain = 15000  # -
sub_areas = 4
A_sub = A_total / sub_areas

# Solver inputs
t_eval = data_df.index.values
h0 = 0.216  # m

for i in range(sub_areas):

    results_i = solve_ivp(
        sewer_block,
        t_span=(t_eval[0], t_eval[-1]),
        t_eval=t_eval,
        y0=[h0],
        args=(data_df.loc[:, "Q_in"].values, t_eval, A_sub, C_gain),
    )

    data_df[f"Q_{i+1}"] = C_gain * results_i.y.T ** (3 / 2)

fig, ax = plt.subplots(1, 1, constrained_layout=True, squeeze=False)
ax.plot(t_eval, data_df["Q_in"], "--g", label="before sewer")
ax.plot(t_eval, data_df[f"Q_{sub_areas}"], "-k", label=f"{sub_areas} sub-areas")
ax.set(ylabel="flow rate [m3/d]", xlabel="time [d]")
fig.legend(loc="upper left")
fig.show()


# if __name__ == "__main__":
#     main()
