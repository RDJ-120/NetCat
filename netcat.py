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
from pathlib import Path
from rich.console import Console
from rich import traceback

traceback.install()

c = Console()

def execute(cmd):
	cmd = cmd.strip()
	if not cmd:
		return
	cmd = shlex.split(cmd)
	try:
		output = subprocess.check_output(cmd, stderr=subprocess.stdout)
		return output.decode("utf-8")
	except Exception as e:
		return str(e)

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

if args.cmd == "chat":

	IP = args.ipaddress
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
			password = input("Enter The Password:\t")
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

		def broadcast(name, msg, sender_conn):
			msg = msg.encode("utf-8")
			name = name.encode("utf-8")
			name_length = str(len(name)).encode("utf-8")
			name_length += b' ' * (NAME - len(name_length))
			length = str(len(msg)).encode("utf-8")
			length += b' ' * (HEADER - len(length))
			for client in clients:
				if client != sender_conn:
					client.sendall(name_length)
					client.sendall(name)
					client.sendall(length)
					client.sendall(msg)

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
				length = int(length)
				msg = recv_all(conn, length).decode("utf-8")
				if msg.endswith(DISCONNECT):
					connected = False
				else:
					print(f"[{name}]:\t{msg}")
					broadcast(name, msg, conn)
			clients.remove(conn)
			conn.close()
			print(f"[ ! ] {n} Exited The Server..")

		def start():
			server.listen()
			print("[ + ] server is listening..")
			while True:
				conn, addr = server.accept()
				n_length = conn.recv(NAME).decode("utf-8").strip()
				n_length = int(n_length)
				n = recv_all(conn, n_length).decode("utf-8")
				if password:
					pass_msg = "PASSWORD:\t".encode()
					passed_length = str(len(pass_msg)).encode("utf-8")
					passed_length += b' ' * (PASS - len(passed_length))
					conn.send(passed_length)
					conn.sendall(pass_msg)
					pass_length = conn.recv(PASS).decode("utf-8").strip()
					pass_length = int(pass_length)
					sent_password = recv_all(conn, pass_length)
					if sent_password.decode("utf-8") == password:
						threading.Thread(target=handle, args=(conn, addr, n)).start()
					else:
						conn.close()
				else:
					threading.Thread(target=handle, args=(conn, addr, n)).start()

		print("[ + ] Server is starting...")
		start()

	if args.client:
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect(ADDR)
		name = c.input("[bold green]Enter Your Name:\t")

		name_enc = name.encode("utf-8")
		name_length = str(len(name_enc)).encode("utf-8")
		name_length += b' ' * (NAME - len(name_length))
		client.send(name_length)
		client.send(name_enc)

		if args.putpassword:
			length = client.recv(PASS).decode("utf-8").strip()
			length = int(length)
			message = client.recv(length).decode("utf-8")
			password = c.input(f"[bold green]{message}")
			password = password.encode("utf-8")
			length = str(len(password)).encode("utf-8")
			length += b' ' * (PASS - len(length))
			client.sendall(length)
			client.sendall(password)

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
			length += b' ' * (HEADER - len(length))
			client.sendall(length)
			client.sendall(msg)

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
				msg = recv_all(client, length).decode("utf-8")
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
	with open(filepath, "rb") as f:
		while True:
			data = f.read(4096)
			if not data:
				break
			conn.sendall(data)
	c.print(f'[bold green][ [bold cyan]+ [bold green]] File [bold cyan]{filepath} [bold green] Sent Successfully!')
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
		client.connect(ADDR)

		receive_file = Path("/sdcard/received/NetCat Files").resolve()
		receive_dir = Path("/sdcard/received/NetCat Directory").resolve()

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
