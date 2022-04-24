from utils import Block
import getpass
import socket
import pickle, struct


serverPubKey = (98581262173360837326167111125113695068362686677036762762847714161386363356381, 5)

username = input("Enter Username: ")
password = getpass.getpass(prompt="Enter Password: ")
#rsa = RSA()
#password = rsa.getEncryption(password, serverPubKey[0], serverPubKey[1])#RSA(password, serverPubKey[0], serverPubKey[1])
print(password)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5000))
print('Client has been assigned socket name ', sock.getsockname())
print(username)
sock.sendall(username.encode())
reply = sock.recv(4096)
print(reply.decode())
pswd = pickle.dumps(password)
sock.sendall(struct.pack("L", len(pswd))+pswd)

reply = sock.recv(4096)
reply = reply.decode()
if reply == 'Authentication Failed':
    print('Authentication Failed')
    exit(1)
if reply == 'Send Block':
    print('Authentication Successful, enter Data for block formation')

    items = [
    { "name": "Expresso"  , "amount": 80},   
    { "name": "Milk"  , "amount": 15},
    { "name": "Cafè Late"  , "amount": 55},
    { "name": "Cafè Mocha"  , "amount": 25},
    { "name": "Cardamom Tea"  , "amount": 25},
    { "name": "Ginger Tea"  , "amount": 20},
    { "name": "Paneer Momos"  , "amount": 75},
    { "name": "Chicken Chilli Momos"  , "amount": 90},
    { "name": "Chicken 65"  , "amount": 120},
    { "name": "Cappuccino"  , "amount": 20},
    { "name": "Hot Chocolate"  , "amount": 25},
    ]
    

    print('''Menu : 
    1. Expresso 80
    2. Milk 15
    3. Cafè Late 55
    4. Cafè Mocha 25
    5. Cardamom Tea 25
    6. Ginger Tea 20
    7. Paneer Momos 75
    8. Chicken Chilli Momos 90
    9. Chicken 65 120
    10. Cappuccino 20
    11. Hot Chocolate 25
    ''')
    choices=[]
    n = int(input("Enter Number of the items you want: "))
    while n:
        choice= items[int(input("Enter serial number of item: "))-1]
        choices.append(choice)
        n-=1
        
    f = open('Users.txt', 'rb')
    users = pickle.load(f)
    f.close()
    for user in users:
        if user.username == username:
            currUser = user
            break
    f = open('BlockChain.txt', 'rb')
    blocks = pickle.load(f)
    f.close()
    prevHash = blocks[-1].Hash
    block = Block(choices, currUser.username, prevHash)
    data = pickle.dumps(block)
    sock.sendall(struct.pack("L", len(data))+data)
    reply = sock.recv(4096)
    reply = reply.decode()
    print(repr(reply))

sock.close()