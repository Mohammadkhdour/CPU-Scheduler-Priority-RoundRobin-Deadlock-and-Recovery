# 🖥️ CPU Scheduling & Deadlock Detection - Operating Systems Project

## 📌 Project Overview
This project simulates a **CPU Scheduling System** that incorporates **deadlock detection and recovery**. The system consists of a single CPU core and multiple resource types, with only one instance of each resource type. The goal is to:
- Simulate **CPU scheduling** using **Priority Scheduling with Round Robin**.
- Implement **Deadlock Detection** using **Resource Allocation Graphs (RAG) and Wait-for Graphs (WFG)**.
- Apply **Deadlock Recovery** techniques such as **process termination** and **resource preemption**.
- Generate a **Gantt Chart**, compute **average waiting time**, and **average turnaround time**.

---
## 📂 Features & Functionality

### ✅ CPU Scheduling
- Implements **Priority Scheduling** with **Round Robin (RR)** for fair execution.
- Processes are scheduled based on priority, and RR prevents starvation.
- Context switching time is negligible and ignored in the simulation.

### ✅ Deadlock Detection
- **Resource Allocation Graph (RAG)** is used to track process-resource assignments.
- **Wait-for Graph (WFG)** detects cycles, indicating a deadlock.
- If a deadlock is detected, recovery strategies are applied.

### ✅ Deadlock Recovery
- **Process Termination**: The process with the highest resource requests is terminated.
- **Resource Preemption**: Allocated resources are released for waiting processes.
- **Graph Updates**: The system updates the RAG and WFG to resolve deadlocks.

---
## 🏗️ Implementation Details
### 📌 Input Format
The program reads a text file where each line represents a process in the format:
```text
[PID] [Arrival Time] [Priority] [Sequence of CPU and IO bursts]
```
Example:
```text
0 0 1 CPU {R[1], 50, F[1]}   
1 5 1 CPU {20} IO{30} CPU{20, R[2], 30, F[2], 10}
```
- `CPU {R[1], 50, F[1]}` → Process requests **Resource 1**, executes **50 units**, then **releases it**.
- `IO{30}` → The process moves to **I/O queue** for **30 units** before resuming CPU execution.

### 📌 Output
At the end of the simulation, the program displays:
- **Gantt Chart** showing process execution.
- **Average Waiting Time & Turnaround Time**.
- **Deadlock States** and how recovery was handled.

---
## 🚀 Getting Started

### 🔧 Prerequisites
Ensure you have **Python 3.8+** installed along with the necessary libraries:
```sh
pip install matplotlib
```

### 📂 Cloning the Repository
To download and set up the project, use:
```sh
git clone https://github.com/yourusername/OS-CPU-Scheduler.git
cd OS-CPU-Scheduler
```

### ▶️ Running the Project
1. Prepare the input file `input.txt`.
2. Run the main program:
   ```sh
   python main.py
   ```
3. View the **Gantt Chart** and results in the terminal.

---
## 📊 Results & Insights
- **CPU Scheduling Efficiency**: Balances priority and fairness via **Round Robin**.
- **Deadlock Detection**: Successfully detects circular dependencies in RAG.
- **Deadlock Recovery**: Efficiently resolves deadlocks via process termination.
- **Performance Metrics**: Outputs waiting times and turnaround times.

---
## 🤝 Contributing
Contributions are welcome! Feel free to **fork** this repository and submit a **Pull Request**.

---
## 📜 License
This project is licensed under the **MIT License**.

---
