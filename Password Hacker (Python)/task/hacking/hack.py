import sys
import socket

# obtain input
args = sys.argv
hostname = args[1]
port = int(args[2])
guess = args[3]

# define socket
# TODO convert to context manager
client_socket = socket.socket()
address = (hostname, port)
client_socket.connect(address)

data = guess
# send request
data = data.encode()
client_socket.send(data)

# receiving response
response = client_socket.recv(1024)  # TODO eliminate magic number
response = response.decode()
print(response)

client_socket.close()
