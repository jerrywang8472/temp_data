#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
file: recv.py
socket service
"""

import socket
import threading
import time
import sys
import os
import struct


def socket_service():
    try:
        csv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        csv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        csv_socket.bind(('192.168.43.70', 6666))
        csv_socket.listen(10)

        image_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        image_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        image_socket.bind(('192.168.43.70', 6667))
        image_socket.listen(10)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print('Waiting connection...')

    csv_t = threading.Thread(target=deal_data, args=(csv_socket, "csv_data/"))
    csv_t.start()

    image_t = threading.Thread(target=deal_data, args=(image_socket, "image_data/"))
    image_t.start()

def deal_data(socket_instance, save_dir):
    while True:
        conn, addr = socket_instance.accept()
        print('Accept new connection from {0}'.format(addr))
        #conn.settimeout(500)
        conn.send('Hi, Welcome to the server!'.encode('utf-8'))

        while True:
            fileinfo_size = struct.calcsize('128sl')
            buf = conn.recv(fileinfo_size)
            if buf:
                filename, filesize = struct.unpack('128sl', buf)
                fn = filename.decode("utf-8").strip('\00')
                new_filename = os.path.join('./', fn)
                print('file new name is {0}, filesize is {1}'.format(new_filename,filesize))

                recvd_size = 0  # 定義已接收檔案的大小
                fp = open(save_dir + new_filename, 'wb')
                print('start receiving...')

                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        data = conn.recv(1024)
                        recvd_size += len(data)
                    else:
                        data = conn.recv(filesize - recvd_size)
                        recvd_size = filesize
                    fp.write(data)
                fp.close()
                print('end receive...')
            conn.close()
            break

if __name__ == '__main__':
    socket_service()