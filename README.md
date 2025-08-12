# Intelligent-Routing-in-SDN

### Project Overview
This project implements an intelligent routing system in a Software-Defined Network (SDN) environment, leveraging Mininet for network emulation and OpenDaylight as the SDN controller. The goal is to optimize routing by comparing traditional hop-count and QoS-based routing with machine learning (ML)-based strategies.

Key Features
Network Topologies Simulated:

Abilene

AboveNet

German50


### Traffic Simulation:
Utilized D-ITG (Distributed Internet Traffic Generator) to simulate realistic network traffic.

### Routing Strategies Compared:

Hop-count based routing

QoS-based routing

## ML-driven routing using LSTM predictions

### Machine Learning Model:
Built an LSTM (Long Short-Term Memory) model to predict dynamic link costs based on historical traffic data, enabling smarter routing decisions.

### Performance Improvement:
Achieved 20–25% reduction in latency by incorporating ML-driven routing decisions.

Technologies Used
Mininet: Network emulator for creating virtual SDN topologies

OpenDaylight: SDN controller to program network flows

D-ITG: Traffic generation tool for emulating network traffic

Python: For LSTM model development and integration

Machine Learning: LSTM model for link cost prediction

Project Structure
bash
Copy
Edit
/project-root
│
├── topology/             # Network topology definitions (Abilene, AboveNet, German50)
├── traffic/              # D-ITG traffic scripts and logs
├── controller/           # OpenDaylight configurations and routing modules
├── ml_model/             # LSTM model training, prediction scripts, datasets
├── results/              # Performance evaluation results and plots
├── README.md             # This file
└── requirements.txt      # Python dependencies
How to Run
Set up Mininet and OpenDaylight:
Ensure both are installed and running on your system.

Load desired network topology in Mininet:
Use provided scripts in /topology to create Abilene, AboveNet, or German50 networks.

Start OpenDaylight controller and deploy routing modules:
Configure the controller to use your routing algorithms.

Generate traffic with D-ITG:
Use scripts under /traffic to simulate network load on the topology.

Train the LSTM model:
Navigate to /ml_model and run the training scripts with historical link data.

Run ML-driven routing:
Use the trained model to predict link costs and update routing paths dynamically.

Evaluate:
Compare latency and other QoS metrics for different routing strategies from /results.

Results
Latency reduction: 20–25% improvement with ML-based routing compared to hop-count and QoS routing.

Detailed graphs and logs are available in the /results directory.

Acknowledgements
Special thanks to Dr. Narayan D. G. for guidance and support throughout this project.
