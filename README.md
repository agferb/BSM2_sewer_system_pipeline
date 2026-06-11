# BSM2 flow and solids after sewer system

This pipeline simulates wastewater flowrate and total solids concentration from the benchmark dynamic BSM2 data after it goes through the sewer system. In a physical perspective, the wastewater flowrate peaks and drops are smoothed by the sewer system, and solids can be released by the first flush effect, when a higher flowrate carries downstream the solids accumulated in the system. The main parameter to be tunned in this pipeline is the number of catchment sub-areas, so it is possible to compare the different behaviour on the sewage depending on how many areas we discretise it.

For more details of the work refer to Gernaey *et al.* (2011) [DOI:10.1016/j.envsoft.2011.06.001].

The pipeline consists of 3 processes customly built. Each of them execute docker images to avoid environment requirements and system dependencies issues.

BSM2 stands for *Benchmark Simulation Model no. 2*.

## Input and ouput files

This is a benchmark pipeline, so there are no input files. The input time series is retrieved from the BSM2 online platform. The main input argument to be set is the number of sub-areas of the sewer system catchment (default is 4). The time range in which the analysis is made can also be changed, and it can be any interval in between [0, 609] days (default is [360, 380]). Remark that for long time intervals the analysis might take long to run and the figures with the results might be hard to interpret.

The model outputs the following files:
- `flow_after_n_subareas_t-min_t-max.csv`: the input (upstream) flowrate (`Q_0`) and the flowrate downstream of each sub-area (`Q_i` for in [1, sub-areas]). Values are in m3/d.
- `solids_after_n_subareas_t-min_t-max.csv`: the input (upstream) total solids (`TSS_0`) and the total solids downstream the last sub-area (`Q_n` with n = # of sub-areas). Values are in kg/m3.
- `flow_after_n_subareas_t-min_t-max.png`: a time series plot of the input (upstream) flowrate and the flowrate downstream of the last sub-area.
- `solids_after_n_subareas_t-min_t-max.csv`: a time series plot the input (upstream) total solids and the total solids downstream the last sub-area.

## How to use

Given the new restriction on VSC to pull docker images, the images can not be pulled from the dockerhub inside VSC. We hope soon this issue will be addressed and the pipeline can be run in the HPC.

## Pipeline structure

### Process `bsm2_get_data`

- Data is retrieved as time series from the BSM2 platform, which consist of various parameters of a dynamic wastewater profile.
- The time series consists of 609 days.
- Full tim-series dataset is saved as bsm2_full_data.txt.

### Process `bsm2_sewer_model`

- Upstream flowrate in m3/d and time data in d is extracted from the full dataset.
- Time series is applied to the sewer model in order to calculate downstream flowrates.
- Flowrate downstream of each sub-area is calculated; default number of sub-areas is 4.
- Input and output data is saved in a .csv file
- A time series plot for a specific time range is generated as a .png file; default time range is from day 360 to day 380.

### Process `bsm2_ffe_model`

- Upstream total solids in mg/L and time data in d is extracted from the full dataset.
- Time series is applied to the first-flush model in order to calculate downstream solids flux.
- Downstream solids concentration is calculated with the flowrate downstream the sewer system calculated by `bsm2_sewer_model`.
- Flowrate downstream of each sub-area is calculated; default number of sub-areas is 4.
- Input and output data is saved in a .csv file
- A time series plot for a specific time range is generated as a .png file; default time range is from day 360 to day 380.

# Build and run get_data container
docker build -f build_containers/Dockerfile.get_data -t get_bsm2_data:01.00 ./build_containers/
docker run --rm -v ./data:/data get_bsm2_data:01.00

# Build and run sewer model container
docker build -f build_containers/Dockerfile.model_sewer -t bsm2_model_sewer:01.00 ./build_containers/
docker run --rm -v ./data:/data bsm2_model_sewer:01.00 /path/to/input_data.txt --t_min 360 --t_max 380 --sub_areas 4

# Build and run ffe model container
docker build -f build_containers/Dockerfile.model_ffe -t bsm2_model_ffe:01.00 ./build_containers/
docker run --rm -v ./data:/data bsm2_model_ffe:01.00 /path/to/input_data.txt /path/to/calc_flow_data.csv --t_min 360 --t_max 380

use .filter to get dates that are bigger than 0 and smaller than 609
use .combine to generate tuples (t_min, t_max, sub_areas)
use .filter to check if t_min < t_max in each tuple
