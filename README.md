docker build -f build_containers/Dockerfile.get_data -t get_bsm2_data:01.00 ./build_containers/
docker run --rm -v ./data:/data get_bsm2_data:01.00

python model_sewer.py path/to/input_data.pkl --t_min 360 --t_max 380 --sub_areas 4
python model_ffe.py path/to/_final_data_bsm2.pkl path/to/_sewer_flow_data.pkl --t_min 360 --t_max 380 --sub_areas 4

use .filter to get dates that are bigger than 0 and smaller than 609
use .combine to generate tuples (t_min, t_max, sub_areas)
use .filter to check if t_min < t_max in each tuple
