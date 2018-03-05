#!/usr/bin/env python

import socket
import getpass
import hashlib
import time
from md5 import md5, md5ToHex
from xorcipher import encodeDecodeFile, xorString
from ascii_armor import file_to_ascii, mime_encode, ascii_to_file, mime_decode, int_to_bits, binary_to_hex


class Client:

    server = None
    host = None
    port = None
    tries = 0

    def __init__(self):  # creates the class object.
        pass

    def startSocket(self):
        # Start socket protocols
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()  # Obtain host name
        self.port = 12345  # Port that it uses

        self.server.settimeout(10)
        # Connection with host and port eg. 123.00.000.00:12345
        self.server.connect((self.host, self.port))

    def login_user(self):
        user = input("Username: ")
        return user

    def login_password(self, salt):
        pw = getpass.getpass()
        hashed_password = hashlib.sha512((pw + salt).encode()).hexdigest()
        return hashed_password

    def sendMessage(self, message):
        self.server.send(bytes(message, 'utf-8'))

    def recvMessage(self):
        return self.server.recv(1024).decode('utf-8')

    def sendFile(self, fileName, fileStream):
        fstream = open(fileName, 'rb')
        sent = fstream.read(fileStream)
        while(sent):
            self.server.send(sent)
            sent = fstream.read(fileStream)

    def getMD5Key(self, fileName):
        return md5ToHex(md5(fileName))

    def xorCipherString(self, string):
        return xorString(string, "key.txt")

    def xorFile(self, fileName):
        encodeDecodeFile(fileName, "xor" + fileName, "key.txt")

    def asciiArmor(self, fileName):
        file_to_ascii(fileName)

    def clientClose(self):
        self.server.close  # Close connection

    def main(self):
        while True:
            user_token = self.login_user()
            # send username to check if it exists
            self.sendMessage(user_token)

            # receive password salt for that username
            salt = (self.recvMessage()).strip()

            if salt != "0":
                pw_token = self.login_password(salt)

                # send hashed pw to authenticate
                self.sendMessage(pw_token)
                print("attempting to login...")

                # recieve confirmation of successful login
            else:
                accept = "0"

            accept = self.recvMessage().strip()

            if accept == "1":
                print(self.recvMessage())

                fileName = input("File: ")
                fileStream = int(input("Packet Length: "))

                print("Applying MD5...")
                md5 = self.getMD5Key(fileName)
                md5 = self.xorCipherString(md5)

                self.sendMessage(md5)
                print("Finished!")

                print("XOR Cipher on file...")
                self.xorFile(fileName)
                print("Finished!")

                asciiArmor = input("Would you like to ASCII Armor? (Y | N)")

                if(asciiArmor == "Y"):
                    print("Applying ASCII armoring...")
                    self.sendMessage("1")
                    self.asciiArmor("xor" + fileName)
                    self.sendFile("ascii_armored.txt", fileStream)
                else:
                    self.sendMessage("0")
                    self.sendFile("xor" + fileName, fileStream)
                break
            elif accept == "-1":
                print(self.recvMessage())
                break
            else:
                print(self.recvMessage())
                # Sends message back to client
                print("Invalid login information.")

            self.clientClose()
