## Traffic Generation & Logging with D-ITG

This project uses **D-ITG (Distributed Internet Traffic Generator)** to simulate realistic network traffic and measure performance metrics such as **delay, jitter, packet loss, and throughput**.

---

### 1. Installing D-ITG

On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install ditg
```
## 2.Running a topology
```
sudo mn --topo single,2 --controller=remote,ip=127.0.0.1

```

### Here we are demonstrating D-ITG between two hosts.

## 3. Now get the cli of a host
```
mininet> xterm h1
mininet> xterm h2
```

We get separate CLI window for both Hosts

### 4. Setting up a reciever in h2

```
ITGRecv &
```

### 4. Setting up a sender in h1

```
ITGSend -T TCP -a 10.0.0.2 -C 1000 -c 512 -t 20000 -l send.log

```


**Parameters:**

- -T TCP → transport protocol (can be UDP, TCP, etc.)
- -a → destination IP
- -C 1000 → packets per second
- -c 512 → packet size in bytes
- -t 20000 → duration in ms (20 seconds)
- -l send.log → save sending log to file

### 5. Decoding Log to Text
**Convert the binary log to human-readable format: (from h1)**

```
ITGDec send.log > results.txt
```

Example output:

```
TOTAL SENT PACKETS: 10000
TOTAL RECEIVED PACKETS: 9992
PACKET LOSS: 0.08 %
AVERAGE DELAY: 1.20 ms
AVERAGE JITTER: 0.15 ms
THROUGHPUT: 4.10 Mbps
```
