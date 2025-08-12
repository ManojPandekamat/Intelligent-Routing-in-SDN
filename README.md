# Intelligent-Routing-in-SDN

### Project Overview
This project implements an intelligent routing system in a Software-Defined Network (SDN) environment, leveraging Mininet for network emulation and OpenDaylight as the SDN controller. The goal is to optimize routing by comparing traditional hop-count and QoS-based routing with machine learning (ML)-based strategies.

---

# Project Structure

```bash
/
│
├── Dataset_generation/             # Generates dataset for QoS based and ML based routing
├── Hop-count-Based-Routing/        # Hop count based routing on (Abilene, AboveNet, German50) topologies 
├── QoS-Based-Routing/              # QoS based routing on (Abilene, AboveNet, German50) topologies 
├── ML-Based-Routing/               # ML based routing on (Abilene, AboveNet, German50) topologies 
├── LSTM_Model/                    # LSTM model training, prediction scripts, datasets for ML based routing
├── Using-Tools/                   # Using various tools such as D-ITG, ping and iperf
├── example_images/                # Image folder for images used in README file
├── README.md                     # This file
└── requirements.txt              # Python dependencies to install
```

# 1 System SetUp

## 1.1. Installing mininet

1. Clone Repository

```
git clone https://github.com/mininet/mininet
cd mininet
```

2. To install everything (using your home directory): 

```
sudo ./util/install.sh -a
```

-a: install everything that is included in the Mininet VM, including dependencies like Open vSwitch as well the additions like the OpenFlow wireshark dissector and POX. By default these tools will be built in directories created in your home directory.


3. Test installation

```
sudo mn --test pingall
```

`You should see hosts pinging each other successfully.`

OR install from packages
```
sudo apt-get install mininet
```



## 1.2. Installing OpenDayLight (ODL)

1. Install Java 8
```
sudo add-apt-repository ppa:webupd8team/java -y
sudo apt-get update
sudo apt-get install oracle-java8-installer
sudo apt-get install oracle-java8-set-default
```
2. Download and Install the ODL Packages.
```

wget https://nexus.opendaylight.org/content/groups/public/org/opendaylight/integration/distribution-karaf/0.6.0-Carbon/distribution-karaf-0.6.0-Carbon.tar.gz

sudo tar -xvzf distribution-karaf-0.6.0-Carbon.tar.gz
cd distribution-karaf-0.6.0-Carbon
./bin/karaf
```

3. Install the ODL Features. (Including Web UI)

In 
`opendaylight-user@root>`

```

 feature:install odl-restconf odl-mdsal-clustering odl-dlux-core odl-dlux-node odl-dlux-yangui odl-dlux-yangvisualizer odl-l2switch-all
```

4. Test Mininet Connectivity with OpenDayLight
```
sudo mn --topo single,2 --controller=remote,ip=127.0.0.1
mininet> pingall
```


Go to this URL and find the Topology in Topology Section

`
http://<Controller IP or localhost>:8181/index.html
`

## 1.3. Install Python package
```
sudo apt install python3
sudo apt install python3-pip
pip3 install -r requirements.txt
```

**Sample In this format we see in ODL Dashboard (Example)**

![alt text](<./example_images/Abilene network.png>)



### If We complete till this step we have completed the setup of our system.

# 2. Comparing Routing methods on Realworld Internet-Zoo Topologies 

Network Topologies Simulated:

**i. Abilene Topology**

![alt text](<./example_images/Abilene network.png>)

**ii. AboveNet Topology**

![alt text](<./example_images/AboveNet network.png>)

**iii. German50 Topology**

![alt text](<./example_images/German50.png>)


## 2.1 Hop-Count Based Routing

**Approach**

- Topology Creation:
Constructed the network topology by assigning random link delays within the range **0.000199 to 0.000262 seconds**. This range was derived by measuring link costs over time, and the average values were used as link weights.

- Cost Matrix Construction and Path Calculation:
Built a **cost matrix** based on the link weights and computed the shortest paths from source to destination nodes using hop-count metrics(Dijktras Algorithm).

- Flow Rule Updates:
Installed **flow rules in the SDN switches** according to the calculated shortest paths to direct traffic efficiently.

- Performance Measurement:
Evaluated network performance by measuring delay, bandwidth, and jitter using tools like **ping and iperf and D-ITG Tool**.


**For 3 Topology run the code from [Hop-count-Based-Routing](./Hop-count-Based-Routing)
 folder**

```bash

python3 ./Hop-count-Based-Routing/Abilene.py

python3 ./Hop-count-Based-Routing/AboveNet.py

python3 ./Hop-count-Based-Routing/German50.py
```
`After Running each script run the ping and iperf command to measure various metrics such as delay,bandwidth and jitter`

**For Measuring metrics refer this folder [Using-Tools](./Using-Tools/)**



Results for Network Topologies Simulated:

**i. Abilene Topology**

![alt text](<./example_images/Abilene network_hopcount_result.png>)

**ii. AboveNet Topology**

![alt text](<./example_images/Abovenet_hopcount_result.png>)

**iii. German50 Topology**

![alt text](<./example_images/German50_hopcount_result.png>)



## 2.2 QoS-Based Routing

### **Approach**

1. **Building a Delay Measurement Dataset**  
   - Measured delays between switch links over time.  
   - Saved values in `Actual_values.csv`.  

2. **First Iteration — Assigning Lowest Delays**  
   - Extracted the **lowest values** from `Actual_values.csv` → saved in `sorted_csv.csv`.  
   - Assigned these values as link weights in the topology.

3. **Cost Matrix & Path Calculation**  
   - Built a **cost matrix** from link weights.  
   - Computed shortest paths from source to destination using **Dijkstra's Algorithm** (hop-count metrics).  

4. **Flow Rule Installation**  
   - Installed **flow rules** in SDN switches according to calculated shortest paths.

5. **Second Iteration — Assigning Highest Delays**  
   - Extracted the **highest values** for the same links from `Actual_values.csv` → saved in `reversed_rows.csv`.  
   - Updated link weights in the topology.

6. **Recalculate Paths & Update Flow Rules**  
   - Rebuilt the cost matrix with updated link weights.  
   - Recomputed shortest paths and updated flow rules.

7. **Performance Measurement**  
   - Evaluated network performance using:
     - `ping`
     - `iperf`
     - **D-ITG**  
   - Verified that routes shift to the next-best path when link weights increase.

---

### **Running the Code**

Run the scripts for each topology:

```bash
python3 ./QoS-Based-Routing/Abilene.py
python3 ./QoS-Based-Routing/AboveNet.py
python3 ./QoS-Based-Routing/German50.py
```

Results for Network Topologies Simulated:

**i. Abilene Topology**

![alt text](<./example_images/Abilene network Qos based.png>)

**ii. AboveNet Topology**

![alt text](<./example_images/Abovenet qos based.png>)

**iii. German50 Topology**

![alt text](<./example_images/German50 Qos based.png>)

## 2.3 ML-Based Routing

### **Approach**

1. **Building a Delay Measurement Dataset**  
   - Measured delays between switch links over time.  
   - Saved the data in `Actual_values.csv` or `data.csv`.

2. **Training the LSTM Model**  
   - Trained the model using the notebook at [LSTM_Model/Main.ipynb](./LSTM_Model/Main.ipynb).

3. **First Iteration — Assigning Lowest Delays**  
   - Extracted the **lowest delay values** from `Actual_values.csv` → saved in `sorted_csv.csv`.  
   - Assigned these values as initial link weights.

4. **Cost Matrix & Path Calculation**  
   - Built a **cost matrix** based on the assigned link weights.  
   - Computed shortest paths from source to destination using **Dijkstra's Algorithm**.

5. **Flow Rule Installation**  
   - Installed **flow rules** in SDN switches according to the computed shortest paths.

6. **Second Iteration — Assigning Predicted Delays**  
   - Used the trained LSTM model to **predict link weights** dynamically.  
   - In the current scripts, predicted weights are hardcoded; future work can load the model dynamically for real-time predictions.

7. **Recalculate Paths & Update Flow Rules**  
   - Updated the cost matrix with predicted link weights.  
   - Recomputed shortest paths and updated flow rules accordingly.

8. **Performance Measurement**  
   - Evaluated network performance using:
     - `ping`  
     - `iperf`  
     - **D-ITG**  
   - Verified that routing adapts by shifting to next-best paths when link weights change.

---

### **Running the Code**

Run the scripts for each topology:

```bash
python3 ./ML-Based-Routing/Abilene.py
python3 ./ML-Based-Routing/AboveNet.py
python3 ./ML-Based-Routing/German50.py
```

# 3. (Optional) How we generated Dataset
## In the [Dataset_generation](./Dataset_generation) folder,I a script is provided to measure delay between each link and create a demo.csv file.

```
python3 ./Dataset_generation/ditg_delay_measurement.py
```

This will create a demo.csv file.

press Ctrl+C to end the running of script.




# 4. Traffic Simulation:
Utilized D-ITG (Distributed Internet Traffic Generator) to simulate realistic network traffic.

# 5.  Performance Improvement:
Achieved 20–25% reduction in latency by incorporating ML-driven routing decisions.

# 6.  Technologies Used
- Mininet: Network emulator for creating virtual SDN topologies

- OpenDaylight: SDN controller to program network flows

- D-ITG: Traffic generation tool for emulating network traffic

- Python: For LSTM model development and integration

- Machine Learning: LSTM model for link cost prediction



# 7. Results
Latency reduction: 20–25% improvement with ML-based routing compared to hop-count and QoS routing.






---

# Credits

This repository was created and maintained by **Manoj Pandekamat**.

Special thanks to my teammates Anup, Rahul, and Veeresh, and to Dr. Narayan D. G. for guidance and support.

---



Special thanks to the open-source communities behind Mininet, OpenDaylight, D-ITG, and all supporting libraries and tools used in this project.
