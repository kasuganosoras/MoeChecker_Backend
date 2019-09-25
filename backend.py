#!/usr/bin/python36
#!coding:utf-8

import time
import struct
import socket
import select
import sys
import re
import requests
import urllib.parse

from multiprocessing import Process

def chesksum(data):
	n = len(data)
	m = n % 2
	sum = 0 
	for i in range(0, n - m ,2):
		sum += (data[i]) + ((data[i+1]) << 8)
	if m:
		sum += (data[-1])
	sum = (sum >> 16) + (sum & 0xffff)
	sum += (sum >> 16)
	answer = ~sum & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)
	return answer 

def raw_socket(dst_addr, imcp_packet):
	rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
	send_request_ping_time = time.time()
	rawsocket.sendto(imcp_packet, (dst_addr, 80))
	return send_request_ping_time, rawsocket, dst_addr

def request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body):
	imcp_packet = struct.pack('>BBHHH32s', data_type, data_code, data_checksum, data_ID, data_Sequence, payload_body)
	icmp_chesksum = chesksum(imcp_packet)
	imcp_packet = struct.pack('>BBHHH32s', data_type, data_code, icmp_chesksum, data_ID, data_Sequence, payload_body)
	return imcp_packet

def reply_ping(send_request_ping_time, rawsocket, data_Sequence, timeout = 2):
	while True:
		started_select = time.time()
		what_ready = select.select([rawsocket], [], [], timeout)
		wait_for_time = (time.time() - started_select)
		if what_ready[0] == []:
			return -1
		time_received = time.time()
		received_packet, addr = rawsocket.recvfrom(1024)
		icmpHeader = received_packet[20:28]
		type, code, checksum, packet_id, sequence = struct.unpack(
			">BBHHH", icmpHeader
		)
		if type == 0 and sequence == data_Sequence:
			return time_received - send_request_ping_time
		timeout = timeout - wait_for_time
		if timeout <= 0:
			return -1

def ping(host):
	data_type = 8
	data_code = 0
	data_checksum = 0
	data_ID = 0
	data_Sequence = 1
	payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'
	dst_addr = socket.gethostbyname(host)
	for i in range(0,1):
		icmp_packet = request_ping(data_type, data_code, data_checksum, data_ID, data_Sequence + i, payload_body)
		send_request_ping_time, rawsocket,addr = raw_socket(dst_addr, icmp_packet)
		times = reply_ping(send_request_ping_time, rawsocket, data_Sequence + i)
		if times > 0:
			return("" + str(int(times*1000)))
		else:
			return("-1")

def handle_client(client_socket):
	request_data = client_socket.recv(1024)
	request_lines = request_data.splitlines()
	request_start_line = request_lines[0]
	file_name = re.match(r"\w+ +(/[^ ]*) ", request_start_line.decode("utf-8")).group(1)
	action = file_name[1:5]
	hostname = file_name[6:1000]
	result = "404 Not Found"
	if hostname == "":
		result = "400 Bad Request"
	else:
		if action == "ping":
			print("ping:", hostname)
			try:
				result = str(ping(hostname))
			except Exception as e:
				result = str(e)
		elif action == "curl":
			print("curl:", hostname)
			try:
				rs = requests.get(urllib.parse.unquote(hostname), timeout=5)
				result = str(rs.status_code)
			except Exception as e:
				result = str(e)
		else:
			result = "404 Not Found"
	response_start_line = "HTTP/1.1 400 Bad Request\r\n"
	response_headers = "Server: ZeroDream\r\n"
	response_body = result
	response = response_start_line + response_headers + "\r\n" + response_body
	client_socket.send(bytes(response, "utf-8"))
	client_socket.close()
	
if __name__ == "__main__":
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("", 1012))
	server_socket.listen(128)

	while True:
		client_socket, client_address = server_socket.accept()
		handle_client_process = Process(target = handle_client, args = (client_socket,))
		handle_client_process.start()
		client_socket.close()
