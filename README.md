# Python NetCat Utility

A multi-functional, thread-safe network interface utility modeled after standard NetCat functionalities. Built using Python socket libraries for network diagnostic tasks, socket streaming, and automated remote payload execution.

## Features

* **Multi-Client Chat Operations:** Multi-threaded TCP relay server with optional string authentication parameters.
* **Network Port Scanner:** Concurrent socket connection mapping supporting single IP hosts or full IPv4 CIDR blocks (`/24`).
* **Automated File Transfer Protocol:** Automatic directory compression (`.zip`), byte-stream transmission, and automated extraction upon stream completion.
* **Remote Command Execution (RCE) Module:** Interactive reverse shell session handler with custom stream operators (`take` and `upload`) for host file synchronization.

## Prerequisites

* Python 3.8+
* Third-party module dependencies: `rich`, `prompt_toolkit`

Install execution dependencies:

```bash
pip install -r requirements.txt
```

## Installation

Clone the repository and access the directory:

```bash
git clone https://github.com/RDJ-120/NetCat.git
cd NetCat
```

## Usage

Standard invocation syntax:

```bash
python netcat.py [mode] [options]
```
![Tool Running Example](https://github.com/user-attachments/assets/f421a26b-1b49-476a-a7fd-758baa9bdba6)
### 1. Chat Mode

Start server instance:

```bash
python netcat.py chat -s -ip 0.0.0.0 -p 5555
```

Start server with password protection:

```bash
python netcat.py chat -s -ip 0.0.0.0 -p 5555 -pp
```

Connect client instance:

```bash
python netcat.py chat -c -ip SERVER_IP -p 5555
```

*Terminate session via client input:* `!DISCONNECT`

### 2. Port Scanning Mode

Scan single target host:

```bash
python netcat.py scan -ip 192.168.1.1
```

Scan entire IPv4 subnet range:

```bash
python netcat.py scan --all -ip 192.168.1.0/24
```

### 3. File Transfer Mode

Initialize host receiver listener:

```bash
python netcat.py filesend -r -ip 0.0.0.0 -p 4444
```

Transmit file or directory from client:

```bash
python netcat.py filesend -s -ip RECEIVER_IP -p 4444
```

*Note: Received assets are automatically mapped to `$HOME/received/`.*

### 4. Remote Execution Mode

Start interactive execution host:

```bash
python netcat.py execute -s -ip 0.0.0.0 -p 9999
```

Connect client terminal handler:

```bash
python netcat.py execute -c -ip SERVER_IP -p 9999
```

Custom stream flags during active execution sessions:

* `take <file_path>` - Pull remote target file to local host execution directory (`$HOME/executed/`).
* `upload <file_path>` - Push local host file to remote target environment.

## Disclaimer

This software is strictly intended for educational testing, authorized system administration, and internal network diagnostics. Unauthorized execution against unapproved network infrastructure is prohibited.

## License

Distributed under the MIT License. See `LICENSE` for details.
