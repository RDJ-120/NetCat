# Python NetCat Tool

Educational NetCat-like tool written in Python for learning networking concepts and socket programming.

This tool can:

- Create chat server with or without password
- Connect to other chat servers
- Scan open ports on IPs and networks
- Send and receive files and directories

---

## ✨ Features

- 🔐 Password protected chat
- 💬 Client / Server chat mode
- 🔍 Port scanning (single IP or whole network)
- 📁 File and directory transfer
- ⚡ Built using Python sockets

---

## ⚙️ Requirements

- Python 3.x

If you use external libraries:
pip install -r requirements.txt
▶️ Usage

All commands are run using:
python netcat.py [mode] [options]

💬 Chat Mode
Start Chat Server
python netcat.py chat -s -ip {IP} -p {PORT}

With password:
python netcat.py chat -s -ip {IP} -p {PORT} -pp {PASSWORD}

Connect to Chat Server
python netcat.py chat -c -ip {IP} -p {PORT}
With password:
python netcat.py chat -c -ip {IP} -p {PORT} -pp {PASSWORD}


🔍 Port Scanning
Scan Full Network

python netcat.py scan --all -ip 192.168.1.0/24

Scan Single IP
python netcat.py scan -ip {IP}

📁 File Transfer
Send File or Directory (Server)
python netcat.py filesend -s -ip {IP} -p {PORT}
The sender waits for one client to connect.

Receive File (Client)
- python netcat.py filesend -r -ip {IP} -p {PORT}
Connects to sender and receives files