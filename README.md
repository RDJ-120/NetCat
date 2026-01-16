# 🐍 Python NetCat Tool

Educational NetCat-like tool written in Python for learning networking, sockets, and basic cybersecurity concepts.  
Works on Linux and Termux (Android).

---

## 📌 Features

This tool can:

- 💬 Create chat server (with or without password)
- 👥 Connect multiple chat clients at the same time
- 🔍 Scan open ports on IPs or full networks
- 📁 Send and receive files and directories
- 🖥️ Remote command execution (execute mode)
- ⚡ Multi-threaded server handling

---

## ⚙️ Requirements

- Python 3.x

External libraries used:
rich
prompt_toolkit

Install them using:

```bash
pip install -r requirements.txt
```
▶️ Usage
All commands:
```bash
python netcat.py [mode] [options]
```
Available modes:
chat
scan
filesend
execute
💬 Chat Mode

Start Chat Server
```Bash
python netcat.py chat -s -ip 0.0.0.0 -p 5555
```
With password:
```Bash
python netcat.py chat -s -ip 0.0.0.0 -p 5555 -pp
```
Connect to Chat Server
```Bash
python netcat.py chat -c -ip SERVER_IP -p 5555
```
With password:
```Bash
python netcat.py chat -c -ip SERVER_IP -p 5555 -pp
```
Chat Commands
!DISCONNECT → exit from chat server
🔍 Port Scanning
Scan Single IP
```Bash
python netcat.py scan -ip 192.168.1.1
```
Scan Full Network
```Bash
python netcat.py scan --all -ip 192.168.1.0/24
```
Features:
Multi-threaded scanning
Shows open and filtered ports

📁 File Transfer Mode
Send File or Directory (Sender)
```Bash
python netcat.py filesend -s -ip 0.0.0.0 -p 4444
```
Then enter file or folder path.
If directory is selected:
It will be zipped
Sent
Then extracted automatically on receiver
Receive File (Receiver)
```Bash
python netcat.py filesend -r -ip SENDER_IP -p 4444
```
Files will be saved to:
/{home}/received/NetCat Files
/{home}/received/NetCat Directory

🖥️ Execute Mode (Remote Command Execution)
Allows executing shell commands remotely.
⚠️ For educational purposes only.
Start Execute Server
```Bash
python netcat.py execute -s 0.0.0.0 -p 9999
```
Connect as Client
```Bash
python netcat.py execute -c SERVER_IP -p 9999
```
Then you can run commands like:
```Bash
ls
pwd
cd /sdcard
whoami
```
Download File from Server
Command:
```Bash
take filename.txt
```
The file will be saved to:
/{home}/executed/

```Bash
upload filename.txt
```
The file will be uploaded to the executed device and saved to home path


⚠️ Important Notes
This tool is for learning and testing only.
Do NOT use on networks or devices you do not own or have permission to test.
Some features may require storage permission on Android.

```Warning
It was fuckin' big, difficult tool
If There is any error Contact me In Telegram At Username:
@BEY0ND39

Enjoy
```
