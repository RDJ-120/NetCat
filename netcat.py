import argparse
import socket
import sys
import subprocess
import shlex
import textwrap
import re
import os
import shutil
import base64
import ipaddress
import threading
import platform
import hashlib
from pathlib import Path
from rich.console import Console
from rich import traceback
import prompt_toolkit as toolkit
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter


def cwd():
    system = platform.system()
    if system == "Linux":
        if "ANDROID_ROOT" in os.environ or "TERMUX_VERSION" in os.environ:
            return Path("/sdcard")
        else:
            return Path.home() / "Desktop"

    elif system == "Windows":
        return Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))

    elif system == "Darwin":
        return Path.home() / "Desktop"

    else:
        return Path.cwd()

fullpath = cwd()

traceback.install()

c = Console()

parser = argparse.ArgumentParser(description="NetCat Like Tool")

sub = parser.add_subparsers(dest="cmd", required=True)

chat = sub.add_parser("chat")

g = chat.add_mutually_exclusive_group(required=True)
g.add_argument("-s", "--server", action="store_true")
g.add_argument("-c", "--client", action="store_true")

chat.add_argument("-ip", "--ipaddress")
chat.add_argument("-p", "--port", type=int, required=True)
chat.add_argument("-pp", "--putpassword", action="store_true")

scan = sub.add_parser("scan")
scan.add_argument("-a", "--all", action="store_true")
scan.add_argument("-ip", "--ipaddress")

fs = sub.add_parser("filesend")

gg = fs.add_mutually_exclusive_group(required=True)
gg.add_argument("-s", "--sender", action="store_true")
gg.add_argument("-r", "--receiver", action="store_true")

fs.add_argument("-ip", "--ipaddress")
fs.add_argument("-p", "--port", type=int, required=True)

def enc(msg):
	msg = base64.b64encode(msg)
	return msg

def dec(msg):
	msg = base64.b64decode(msg)
	return msg

execute = sub.add_parser("execute")

ggg = execute.add_mutually_exclusive_group(required=True)

ggg.add_argument("-s", "--server", action="store_true")
ggg.add_argument("-c", "--client", action="store_true")

execute.add_argument("ip", type=str)
execute.add_argument("-p", "--port", type=int)

args = parser.parse_args()

def scan_port(ip, port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		if s.connect_ex((ip, port)) == 0:
			c.print(f"[bold green][ [bold cyan]{ip} [bold green]] Status:\t[bold cyan]Open \t\t[bold green]Port:\t[bold cyan]{port}")
	except socket.timeout:
		c.print(f"[bold green][ [bold cyan]{ip} [bold green]] Status:\t[bold cyan]Filtered \t\t[bold green]Port:\t[bold cyan]{port}")
	s.close()

def hashpass(password):
	hashed = hashlib.sha512(password.encode("utf-8")).hexdigest()
	return hashed

if args.cmd == "chat":
	serv = FileHistory("chat_passwords.txt")
	if args.server:
		if args.ipaddress:
			IP = args.ipaddress
		else:
			IP = "0.0.0.0"
	else:
		IP = args.ipaddress

	style = Style.from_dict({"info": "bold cyan",
"regular": "bold green"})
	PORT = args.port
	ADDR = (IP, PORT)
	NAME = 32
	PASS = 64
	HEADER = 4096
	DISCONNECT = "!DISCONNECT"

	if args.server:
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind(ADDR)

		clients = []
		names = []

		if args.putpassword:
			password = toolkit.prompt([("class:regular","Enter "), ("class:regular", "Chat's "), ("class:regular", "password:    ")], is_password=True, style=style, history=serv)
			password = hashpass(password)
		else:
			password = None

		def recv_all(conn, length):
			data = b''
			while len(data) < length:
				packet = conn.recv(length - len(data))
				if not packet:
					break
				data += packet
			return data

		def broadcast(name, msg, sender_conn=None):
			msg = msg.encode("utf-8")
			name = name.encode("utf-8")
			name_length = str(len(name)).encode("utf-8")
			name_length += b' '*(NAME-len(name_length))
			msg_length = str(len(msg)).encode("utf-8")
			msg_length += b' '*(HEADER-len(msg_length))
			for client in clients:
			   if client != sender_conn:
			     try:
			     	client.sendall(name_length)
			     	client.sendall(name)
			     	client.sendall(msg_length)
			     	client.sendall(msg)
			     except:
			     	pass

		def handle(conn, addr, n):
			clients.append(conn)
			names.append(n)
			index = clients.index(conn)
			name = names[index]
			print(f"[ + ] {name} Joined the server..")
			connected = True
			while connected:
				length = conn.recv(HEADER).decode("utf-8").strip()
				if not length:
					break
				try:
					length = int(length)
					msg = recv_all(conn, length)
					msg = msg.decode("utf-8")
					if msg.endswith(DISCONNECT):
						connected = False
					else:
						print(f"[{name}]:\t{msg}")
						broadcast(name, msg, conn)
				except Exception as e:
					print(e)
			clients.remove(conn)
			conn.close()
			print(f"[ ! ] {name} Exited The Server..")

		def start():
			server.listen()
			print("[ + ] server is listening..")
			while True:
				try:
					conn, addr = server.accept()
					try:
						n_length = conn.recv(NAME).decode("utf-8").strip()
						n_length = int(n_length)
						n = recv_all(conn, n_length).decode("utf-8")
					except:
						c.print(f"[red]Something went wrong while receiving client {addr} name!")
					if password:
						pass_msg = "PASSWORD:\t".encode("utf-8")
						passed_length = str(len(pass_msg)).encode("utf-8")
						passed_length += b' ' * (PASS - len(passed_length))
						try:
							conn.send(passed_length)
							conn.sendall(pass_msg)
						except:
							c.print(f"[red]Something went wrong while sending password data to {addr}!")
						pass_length = conn.recv(PASS).decode("utf-8").strip()
						pass_length = int(pass_length)
						try:
							sent_password = recv_all(conn, pass_length)
							sent_password = dec(sent_password).decode("utf-8")
							if hashpass(sent_password) == password:
								threading.Thread(target=handle, args=(conn, addr, n)).start()
							else:
								conn.sendall(b"[ * ] Wrong Password")
								conn.close()
						except:
							c.print(f"[red]Something went wrong while receiving password data from client {addr}")
					else:
						threading.Thread(target=handle, args=(conn, addr, n)).start()
				except Exception:
					pass

		print("[ + ] Server is starting...")
		start()

	if args.client:
		names = FileHistory("names.txt")
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			client.connect(ADDR)
		except:
			c.print("[bold red]Something went wrong in connection!")
			
		name = toolkit.prompt(
		[("class:regular", "Enter "),
		 ("class:regular", "Your "),
		 ("class:regular", "Name:    ")],
		  style=style,
		  history=names)

		name_enc = name.encode("utf-8")
		name_length = str(len(name_enc)).encode("utf-8")
		name_length += b' '*(NAME-len(name_length))
		try:
			client.send(name_length)
			client.send(name_enc)
		except:
			c.print("[red]Something went wrong while sending data!")

		if args.putpassword:
			length = client.recv(PASS).decode("utf-8").strip()
			length = int(length)
			message = client.recv(length).decode("utf-8")
			password = toolkit.prompt([("class:regular",message)], is_password=True, style=style, history=serv)
			password = password.encode("utf-8")
			password = enc(password)
			length = str(len(password)).encode("utf-8")
			length += b' ' * (PASS - len(length))
			try:
				client.sendall(length)
				client.sendall(password)
			except:
				c.print("[red]Something went wrong while sending data!")

		def recv_all(conn, length):
			data = b''
			while len(data) < length:
				packet = conn.recv(length - len(data))
				if not packet:
					break
				data += packet
			return data

		def send(msg):
			msg = msg.encode("utf-8")
			length = str(len(msg)).encode("utf-8")
			length += b' '*(HEADER-len(length))
			try:
				client.sendall(length)
				client.sendall(msg)
			except:
				c.print("[red]Something went wrong while sending data!")

		def receive():
			while True:
				name_length = client.recv(NAME).decode("utf-8").strip()
				if not name_length:
					break
				name = recv_all(client, int(name_length)).decode("utf-8")
				length = client.recv(HEADER).decode("utf-8").strip()
				if not length:
					break
				length = int(length)
				msg = recv_all(client, length)
				msg = msg.decode("utf-8")
				print(f"[{name}]:\t{msg}")

		threading.Thread(target=receive, daemon=True).start()

		while True:
			msg = input("")
			send(msg)
			if msg == DISCONNECT:
				client.close()
				break

if args.cmd == "scan":
	ports = range(1, 6000)

	if args.all:
		network = ipaddress.IPv4Network(str(args.ipaddress))
		hosts = list(network.hosts())
		for ip in hosts:
			max_threads = 50
			threadings = []
			for port in ports:
				t = threading.Thread(target=scan_port, args=(str(ip), port))
				t.start()
				threadings.append(t)
				if len(threadings) >= max_threads:
					for th in threadings:
						th.join()
					threadings = []
			for th in threadings:
				th.join()
	else:
		ip = args.ipaddress
		max_threads = 50
		threadings = []
		for port in ports:
			t = threading.Thread(target=scan_port, args=(ip, port))
			t.start()
			threadings.append(t)
			if len(threadings) >= max_threads:
				for th in threadings:
					th.join()
				threadings = []
		for th in threadings:
			th.join()

def sendfile(filepath, ADDR):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	name = filepath.name.encode("utf-8")
	length = str(len(name)).encode("utf-8")
	length += b' ' * (32 - len(length))
	s.bind(ADDR)
	s.listen(1)
	conn, addr = s.accept()
	conn.sendall(length)
	conn.sendall(name)
	size = filepath.stat().st_size
	size_bytes = str(size).encode("utf-8")
	size_bytes += b' ' * (128 - len(size_bytes))
	conn.sendall(size_bytes)
	try:
		with open(filepath, "rb") as f:
			while True:
				data = f.read(4096)
				if not data:
					break
				conn.sendall(data)
		c.print(f'[bold green][ [bold cyan]+ [bold green]] File [bold cyan]{filepath} [bold green] Sent Successfully!')
	except Exception:
		c.print("[red]Something went wrong..!")
	conn.close()
	s.close()

if args.cmd == "filesend":
	FILE = 32
	HEADER = 4096
	ADDR = (args.ipaddress, args.port)

	if args.sender:
		filepath = Path(input("Enter The Filepath To Send:\t")).resolve()
		name = filepath.name
		parent = filepath.parent

		if filepath.is_file():
			sendfile(filepath, ADDR)

		if filepath.is_dir():
			zip_path = parent.joinpath(name)
			shutil.make_archive(str(zip_path), 'zip', filepath)
			full = parent.joinpath(f"{name}.zip")
			sendfile(full, ADDR)
			full.unlink()

	if args.receiver:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			client.connect(ADDR)
		except:
			c.print("[bold red]Something went wrong in connection!")
		receive_file = (fullpath / "received" / "NetCat Files").resolve()
		
		receive_dir = (fullpath / "received" / "NetCat Dirs").resolve()

		if not receive_dir.exists():
			receive_dir.mkdir(parents=True)

		if not receive_file.exists():
			receive_file.mkdir(parents=True)

		length = client.recv(FILE).decode("utf-8").strip()
		length = int(length)
		name = client.recv(length).decode("utf-8")

		size = client.recv(128).decode("utf-8").strip()
		size = int(size)

		name = Path(name)

		if name.suffix == ".zip":
			name = receive_dir.joinpath(name)
		else:
			name = receive_file.joinpath(name)

		received = 0
		with open(name, "wb") as f:
			while size > received:
				data = client.recv(HEADER)
				if not data:
					break
				f.write(data)
				received += len(data)

		if name.suffix == ".zip":
			shutil.unpack_archive(name, receive_dir)
			name.unlink()

		c.print(f'[bold green][ [bold cyan]+ [bold green]] File [bold cyan]{name} [bold green] Received Successfully!')

def recv_all(conn, length):
    data = b''
    while len(data) < int(length):
        packet = conn.recv(int(length) - len(data))
        if not packet:
            break
        data += packet
    return data


def send_file(filepath, conn):
    size = filepath.stat().st_size
    size_bytes = str(size).encode("utf-8")
    size_bytes += b' '*(128-len(size_bytes))
    conn.sendall(size_bytes)
    with open(filepath, "rb") as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            conn.sendall(data)


def executer(cmd):
    cmd = cmd.strip()
    if not cmd:
        return ""
    if cmd.startswith("cd "):
        path = cmd[3:].strip()
        try:
            os.chdir(path)
            return f"[ + ] Directory changed to: {os.getcwd()}"
        except Exception as e:
            return f"[ - ] cd error: {e}"
    if cmd == "cd":
        return os.getcwd()
    try:
        output = subprocess.getoutput(cmd)
        return output
    except Exception as e:
        return str(e)


def client_execute(ip, port):
    HEADER = 4096
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    while True:
        cmd = input(">> ").encode("utf-8")
        pure = cmd.decode("utf-8")
        length = str(len(cmd)).encode()
        length += b' '*(HEADER-len(length))
        s.sendall(length)
        s.sendall(cmd)

        if pure.startswith("upload "):
            file = Path(pure[7:].strip())
            if file.exists():
                send_file(file, s)
            else:
                print("[ * ] File not found")

        elif pure.startswith("take "):
            dire = fullpath.joinpath("executed")
            dire.mkdir(parents=True, exist_ok=True)
            file = Path(pure[5:].strip()).name
            full = dire / file
            size = int(s.recv(128).decode("utf-8").strip())
            received = 0
            with open(full, "wb") as f:
                while received < size:
                    data = s.recv(HEADER)
                    if not data:
                        break
                    f.write(data)
                    received += len(data)
            print(f"[ - ] Saved: {full}")

        else:
            leng = s.recv(HEADER).decode().strip()
            leng = int(leng)
            full = recv_all(s, leng)
            print(full.decode("utf-8"))


def server_execute(port):
    HEADER = 4096
    IP = "0.0.0.0"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((IP, port))
    s.listen(5)

    def handle_client(conn, addr):
        try:
            while True:
                length = conn.recv(HEADER).decode("utf-8").strip()
                if not length:
                    break
                cmd = recv_all(conn, int(length)).decode("utf-8")

                if cmd.startswith("upload "):
                    filename = Path(cmd[7:].strip()).name
                    file = cwd() / filename
                    size = int(conn.recv(128).decode("utf-8").strip())
                    received = 0
                    with open(file, "wb") as f:
                        while received < size:
                            data = conn.recv(4096)
                            if not data:
                                break
                            f.write(data)
                            received += len(data)

                elif cmd.startswith("take "):
                    file = Path(cmd[5:].strip())
                    if file.exists():
                        send_file(file, conn)
                    else:
                        d = str(0).encode("utf-8")
                        d += b' '*(128-len(d))

                else:
                    final = executer(cmd).encode("utf-8")
                    leng = str(len(final)).encode("utf-8")
                    leng += b' '*(128-len(leng))
                    conn.sendall(leng)
                    conn.sendall(final)
        finally:
            conn.close()

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
  
  
  
if args.cmd == "execute":
    IP = args.ip
    PORT = args.port

    if args.server:
        server_execute(PORT)

    elif args.client:
        c.print(f"[ + ] Connecting to {IP}:{PORT}")
        client_execute(IP, PORT)
