docker build -f build_containers/Dockerfile.get_data -t get_bsm2_data:01.00 ./build_containers/
docker run --rm -v ./data:/data get_bsm2_data:01.00
python model_ffe.py path/to/_final_data_bsm2.pkl path/to/_sewer_flow_data.pkl
python model_ffe.py path/to/_final_data_bsm2.pkl path/to/_sewer_flow_data.pkl
