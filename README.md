# Inefficiency_in_Python_proj
perf record -F 999 --call-graph=fp -g -- python3 my_py_file.py
perf report --stdio > file.txt #--stdio is optional
scp -r roy.zoulty@132.68.206.59:~/Proj_B/Inefficiency_in_Python_proj/results results