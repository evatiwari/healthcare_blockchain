from utils import Admin, Block, Users
import socket
import pickle
import struct
import getpass
import pandas as pd
import sys
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pubKey = (
    98581262173360837326167111125113695068362686677036762762847714161386363356381, 5)


if __name__ == '__main__':
    ad = Admin()
    choicesDict = {
        '1': 'Create New User',
        '2': 'View All Users',
        '3': 'View Current BlockChain',
        '4': 'View user specific transactions'
    }

    while True:
        print('1', choicesDict['1'])
        print('2', choicesDict['2'])
        print('3', choicesDict['3'])
        print('4', choicesDict['4'])
        inp = input("Enter your choice, q to quit: ")
        if inp == '1':
            username = input("\tEnter Username: ")
            f = open('users.txt', 'rb')
            users = pickle.load(f)
            f.close()
            flag = 0
            for user in users:
                if user.username.lower() == username.lower():
                    print("Username already exists!")
                    flag = 1
                    break
            if flag == 1:
                continue
            password = getpass.getpass(prompt="\tEnter Password: ")
            ad.createUser(username, password)
        elif inp == '2':
            f = open('users.txt', 'rb')
            users = pickle.load(f)
            df = pd.DataFrame([x.as_dict() for x in users])
            print("\n", df, "\n")
            f.close()
        elif inp == '3':
            f = open('blockchain.txt', 'rb')
            blocks = pickle.load(f)
            f.close()
            i = 0
            total_amount = 0

            for block in blocks:
                i += 1
                print('\n')
                print(
                    f'Block {i}: \nBlockUsername: {block.username} \nTime: {block.timestamp} \nCurrent Hash: {block.Hash} \nPrevious Hash: {block.prevHash}')
                print('\n')
        elif inp == '4':
            f = open('users.txt', 'rb')
            users = pickle.load(f)
            df = pd.DataFrame([x.as_dict() for x in users])
            print("\n", df, "\n")
            f.close()
            chosenUser = int(input("Enter user number to view transactions: "))

            uname = users[chosenUser].username
            f = open('blockchain.txt', 'rb')
            blocks = pickle.load(f)
            f.close()
            i = 0
            for block in blocks:
                i += 1
                if(block.username == uname):
                    print('\n')
                    print(
                        f'Block {i}: \nBlockUsername: {block.username} \nTime: {block.timestamp} \nCurrent Hash: {block.Hash} \nPrevious Hash: {block.prevHash}')
                    print('\n')
        elif inp == 'q':
            break
    exit()
