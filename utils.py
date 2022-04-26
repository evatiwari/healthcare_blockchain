import datetime
import pickle
import struct
import hashlib
import json
import socket
from threading import Thread
import os
import sys
import random
import pandas as pd
from zkp import zkp
import re
prKey = (98581262173360837326167111125113695068362686677036762762847714161386363356381,
         39432504869344334930466844450045478027093153642958253734301565008685708450381)


class PatientData:
    def __init__(self, name, age, bp, temp, sugar):
        self.name = name
        self.age = age
        self.bp = bp
        self.temp = temp
        self.sugar = sugar

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Block:
    def __init__(self, patient, username, prevHash='0', nonce=0):
        self.username = username
        self.patient = patient
        self.jsonData = json.dumps(patient)
        self.timestamp = datetime.datetime.now().isoformat()
        self.prevHash = prevHash
        self.nonce = nonce
        self.Hash = self.calculateHash().upper()

    def as_dict(self):
        return {'     Username': self.username, '        Data': self.data, '     Timestamp': self.timestamp, '    Hash:': self.Hash, '         Previous Hash': self.prevHash}

    def calculateHash(self):
        return hashlib.sha256((self.timestamp + self.prevHash + self.jsonData + str(self.nonce)).encode()).hexdigest()


class Users:
    def __init__(self, username, password):
        self.timestamp = datetime.datetime.now().isoformat()
        self.username = username
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.blockChain = []
        self.serverPubKey = ''

    def as_dict(self):
        return {'      Username': self.username, '        Timestamp': self.timestamp}

    def createBlock(self, patient):
        return Block(patient, self.username)

    def verifyTransaction(self, currentBlock):
        blocks = self.blockChain
        print(currentBlock.prevHash)
        print(blocks[-1].Hash)
        if currentBlock.prevHash == blocks[-1].Hash:
            return True
        return False

    def verifyBlockChain(self):
        blocks = self.blockChain
        for i in range(1, len(blocks)):
            if blocks[i].prevHash != blocks[i-1].Hash:
                return False
        return True

    def verifyPoW(self, block):
        date_int = re.sub('\D', '', block.timestamp)
        date_int = int(date_int[-3:])
        result = zkp(date_int)
        print("result for user "+self.username+" is "+str(result))
        return result


class Admin:  # Miner
    def __init__(self):
        print("Admin Initiated")
        sock = self.create_socket(('localhost', 5000))
        Thread(target=self.start_threads, args=(sock,)).start()
        if os.stat("blockchain.txt").st_size == 0:
            f = open('blockchain.txt', 'wb')
            block = Block("Genesis", 'admin')
            pickle.dump([block], f)
            f.close()
        if os.stat("users.txt").st_size == 0:
            f = open('users.txt', 'wb')
            user = self.createUser('Dexter', 'admin')
            pickle.dump([user], f)
            f.close()

    def createUser(self, username, password):
        print("Inside createUser")
        user = Users(username, password)
        if not os.stat("blockchain.txt").st_size == 0:
            f = open('blockchain.txt', 'rb')
            blocks = pickle.load(f)
            f.close()
            user.blockChain = blocks
        if not os.stat("users.txt").st_size == 0:
            f = open('users.txt', 'rb')
            users = pickle.load(f)
            f.close()
            users.append(user)
            f = open('users.txt', 'wb')
            pickle.dump(users, f)
            f.close()
        return user

    def checkData(self, block):
        f = open('users.txt', 'rb')
        users = pickle.load(f)
        f.close()
        transactbool = 0
        hashbool = 0
        print("here")
        for i in range(0, len(users)):
            #transact = users[i].verifyTransaction(block)
            hashing = users[i].verifyPoW(block)
            # if transact:
            #transactbool += 1
            if hashing:
                hashbool += 1
        print(transactbool, hashbool)
        if hashbool > len(users)/2:
            # and transactbool > len(users)/2:
            return True
        return False

    def addBlock(self, block):
        f = open('blockchain.txt', 'rb')
        blocks = pickle.load(f)
        f.close()
        blocks.append(block)
        f = open('blockchain.txt', 'wb')
        pickle.dump(blocks, f)
        f.close()
        f = open('users.txt', 'rb')
        users = pickle.load(f)
        f.close()
        f = open('users.txt', 'wb')
        pickle.dump(users, f)
        f.close()
        return

    def create_socket(self, address):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(address)
        listener.listen(64)
        print('listening at {}'.format(address))
        return listener

    def accept_forever(self, listener):
        while True:
            sock, address = listener.accept()
            print('Accepted connection from {}'.format(address))
            ans = self.authenticate(sock)
            if not ans:
                sock.sendall('Authentication Failed'.encode())
                continue
            self.handle_conversation(sock, address)

    def authenticate(self, sock):
        data = sock.recv(4096)
        username = data.decode()
        print(username)
        f = open('users.txt', 'rb')
        users = pickle.load(f)
        f.close()
        currUser = ''
        for user in users:
            if user.username == username:
                currUser = username
                break
        if currUser == '':
            sock.sendall('Username not in record'.encode())
            return False
        sock.sendall('Username Received'.encode())

        data = b''
        payload_size = struct.calcsize("L")
        print("Expecting Password")
        while len(data) < payload_size:
            data += sock.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += sock.recv(4096)
        block_data = data[:msg_size]
        data = data[msg_size:]
        password = pickle.loads(block_data)
        # rsa = RSA()
        # password = rsa.getDecryption(password, prKey[0], prKey[1])

        f = open('Users.txt', 'rb')
        users = pickle.load(f)
        f.close()
        for user in users:
            if user.username == username:
                currUser = user
                break
        hashedPT = hashlib.sha256(password.encode()).hexdigest()
        if not hashedPT == user.password:
            return False
        return True

    def handle_conversation(self, sock, address):
        try:
            val = self.handle_request(sock)
            if not val:
                print("Mining not verified by consensus of the users")
                return
        except EOFError:
            print('Client socket to {} has closed'.format(address))
        except Exception as e:
            print('Client {} error {}'.format(address, e))
        finally:
            sock.close()

    def handle_request(self, sock):
        data = b''
        payload_size = struct.calcsize("L")
        sock.sendall('Send Block'.encode())
        print("Expecting Data")
        while len(data) < payload_size:
            data += sock.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += sock.recv(4096)
        block_data = data[:msg_size]
        data = data[msg_size:]
        block = pickle.loads(block_data)

        self.mineBlock(block)

        toProceed = self.checkData(block)

        if not toProceed:
            return False
        print("PoW done by miner verified by consensus of users")
        self.addBlock(block)
        sock.sendall('Block has been added to the BlockChain'.encode())
        return True

    def mineBlock(self, block, difficulty=3):
        while block.Hash[:difficulty] != '0'*difficulty:
            block.nonce += 1
            block.Hash = block.calculateHash()
        finalHash = block.Hash.upper()
        print(str(finalHash))
        block.Hash = finalHash
        return

    def start_threads(self, listener, workers=4):
        print("here")
        t = (listener,)
        for i in range(workers):
            Thread(target=self.accept_forever, args=t).start()
        return
