## Authors: Esther An and Sammi Zhu

## Running Code
1. Please make sure to have the following installed:
    - python3 -m pip install grpcio
    - python3 -m pip install grpcio-tools
2. Run `python -m grpc_tools.protoc -I=. --python_out=. --grpc_python_out=. chat.proto` if neccessary
3. Run `./run_all.sh` to start all three virtual machines at once
    - If permission errors, please run `chmod +x run_all.sh`

## Tests
Unit tests were written to test the various functionalities of the code in `src/test_utils.py`. 
To run the tests, simply run:
- coverage run --source=utils -m unittest test_utils.py
- coverage report -m

87% coverage was met for utils.py
![alt text](images/coverage.png.png)
