## Implement of ICTCP

### Author: Zeyu Chen(chenzy@gatech.edu), Ruijia Wang(rwang@gatech.edu)

## Foreword
The project is implement ICTCP in NS3.
Group Member: Zeyu Chen, Ruijia Wang, Minghe Zhang

The document is sperated into TCP modification, topology construction and data analysis. 

## TCP Modification
In the model directory, you can find all files I modified and added under src/internet/model
In the modified file, all codes change or added are clearly marked.(By 'name' or 'My code')
To make it clear, the function of each file is shown:

### Modified files:
Receive window, throughput measurement are added in:
tcp-socket-base.h
tcp-socket-base.cc

Slow Start and Congestion Control are added in:
tcp-congestion-ops.h
tcp-congestion-ops.cc

### New TCP files:
tcp-ictcp.h
tcp-ictcp.cc
tcp-ictcp-improved.h
tcp-ictcp-improved.cc

The detail is marked in each file.

REMEBER when you add files to the model directory, you need to add codes in wscript under src/internet
We provide the file too.

PLEASE USE GCC to compile. LLVM on mac may be not working.


## Topology
The topo file is ICTCP_TEST.cc, move it into your scratch/
Use `--Activate_clients` to set the number of the activated clients
	`--Protocol`         to set the TCP protocol, TCPVeno, ICTCP, ICTCP-Improved available
	`--Start`            to set the start time of simulation
	`--End`              to set the end time of simulation  

The default max clients are 48. You can change the number as you want by modifying the the code(The array and lx_cli variables).

The structure of the topology is shown in the .cc file. Check it for more detail.

When you run the file, it will output the pcap file of the receiver. All the information we analyze is based on the pcap file.

```
$ ./waf --run "ICTCP_TEST --para1 --para2 ..."
```

## Data Analysis
Use Python and MATLAB to analyze the data.

The steps is:

1. Choose one protocol, and use Python script `run.py` to run the topo from 1-48 clients. And the pcap files will be stored in the folder results in your current path.
2. Manually put them into a named directory.
3. Change the protocol and repeat step 1 and 2.
4. Now suppose you have three directories: results_ICTCP, results_Tcpveno, results_Improved. `readpcap.py` is used to extract data form pcap files.Use command to get the txt files recording Throughput, Goodput, Loss rate and ratio of retransmission timeout.

``` 
$ python2 readpcap.py
```

Be careful the python used is based on Python 2.7. and the code must in the same directory of the pcap files.

In .txt files:
col1: Ratio of TCP reransmission timeout
col2: Goodput
col3: Loss rate
col4: Throughput

All .txt files are in result/

5. Use MATLAB to plot. 
Input data of txt files, use `myplot.m` to plot. 
`output_data.mat` is the generated according to .txt files. We do not provide the pcap files since they are too large. You can simulate the model to get them or just use the `output_data.mat` provided to reproduce the figure.