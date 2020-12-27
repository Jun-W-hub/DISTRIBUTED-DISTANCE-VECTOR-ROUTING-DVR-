import socket
import threading
import json
import time



def get_distance(filename = 'test.txt'):
	node_table = {}
	row = 0               # We start from 1 to the end
	with open(filename) as f:
		for line in f:
			dist_list = line.split(' ')
			row += 1
			for i, data in enumerate(dist_list):
				if int(data)!=0:
					if chr(ord('A')+row-1) not in node_table.keys():
						node_table[chr(ord('A')+row-1)] = {chr(ord('A')+i):int(data)}
					else:
						node_table[chr(ord('A')+row-1)].update({chr(ord('A')+i):int(data)})
	return node_table

hostname =socket.gethostname()
ip = socket.gethostbyname(hostname)
port = {}
node_table = get_distance()
loop_num = len(node_table)
for i in range(loop_num):
	port[chr(ord('A') + i)] = 8360 + i

def dict_to_binary(dict):
	string = str(dict)
	res = json.dumps(string).encode('utf-8')
	return res

def binary_to_dict(binary):
	rest = binary.decode()
	rest = eval(eval(rest))
	return rest

def bo_nod_cl(node, node_table, counter): #boss connect node
	c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	c.connect((ip,port[node]))
	c.send(b'do')
	data = c.recv(8100) #received the current DV of node
	data = binary_to_dict(data)
	# compare the data is updated or not
	if counter <= len(node_table):
		print('------------------------------')
		print("Round " + str(counter) + ':' + node)
		print('Current DV matrix = ' + str(data))
		print('Last DV matrix = None')  # Need dist from node
		print('Updated from last DV matrix or the same?' + ' Updated')
		print('')
		state = 'Updated'
		node_table[node] = data
	else:
		if data == node_table[node]:
			print('------------------------------')
			print("Round " + str(counter) + ':' + node)
			print('Current DV matrix = '+str(data))
			print('Last DV matrix = ' + str(node_table[node]))  # Need dist from node
			print('Updated from last DV matrix or the same?' + ' Not update')
			print('')
			state = 'Not'
		else:
			print('------------------------------')
			print("Round " + str(counter) + ':' + node)
			print('Current DV matrix = '+str(data))
			print('Last DV matrix = ' + str(node_table[node]))  # Need dist from node
			print('Updated from last DV matrix or the same?' + ' Updated')
			print('')
			state = 'Updated'
			node_table[node] = data
	# control the node can send its dict to nb
	c.sendall(b'send')

	#waiting the node exit
	while True:
		data = c.recv(1024)
		if data == b'exit':
			break
	c.close()
	return state, node_table


def server(node, filename = 'test.txt'):
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.bind((ip,port[node]))
	s.listen(100)
	node_table_init = get_distance(filename)
	node_table = get_distance(filename)
	for i in node_table.keys():
		for j in node_table:
			if i == j:
				node_table[j].update({i: 0})
			else:
				if i not in node_table[j].keys():
					node_table[j][i] = 999					# Get full table

	dist = node_table[node]
	nb=node_table_init[node].keys()

	while True:
		sock,addr =s.accept()
		t=threading.Thread(target=tcplink,args=(sock,addr,node_table,node,nb,dist))
		t.start()

def tcplink(sock,addr,node_table,node,nb,dist):
	while True:
		data = sock.recv(1024)

		if data == b'stop':
			break
		elif data == b'send':#come from boss
			#!!!!send dict to its nb
			for n in nb:   # initial node_table here
				#nb1
				#creat a conncet with nb
				c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
				c.connect((ip,port[n]))
				c.send(dict_to_binary(dist)) #!!!!send dict to
				print('Sending DV to node ' + n)
				while True:
					data2 = c.recv(1024)
					if data2 == b'exit':
						break
				c.close()
				#nb2
			sock.send(b'exit')#exit the connect with boss

		elif data == b'do':#send the dict to boss
			sock.send(dict_to_binary(node_table[node]))#######

		else: # the data is the dict from nb
			#!!!!!!read the dict and update itself
			if data != b'':
				dist_n = binary_to_dict(data)  # neighbors' new dict
				node_n = list(dist_n.keys())[list(dist_n.values()).index(0)]  # neighbors' name
				dist_str = str(node_table[node])
				#print(node_table[node])
				node_table_cur, dist_cur = bellman_ford(node, dist, dist_n, node_n, node_table, nb)
				## print 2
				print('Node ' + node + ' received DV from ' + node_n)  # add node name
				print('Updating DV matrix at node ' + node)
				dict = eval(dist_str)

				if dist_cur == dict:  # if do not change anything
					print('No change in DV at node ' + node)
					print('')
				else:
					print('New DV matrix at node ' + node + ' = ' + str(dist_cur))  # print new updated dist
					print('')
				sock.send(b'exit')  # exit the connect with nb
	sock.close()


def bellman_ford(node, dist, dist_n, node_n, node_table, nb):

	node_table[node_n] = dist_n

	for i in node_table[node]:
		if dist[node_n]+dist_n[i] < dist[i]:
			node_table[node][i]=dist[node_n]+dist_n[i]

	return node_table, dist



def boss(filename = 'test.txt'):
	table = get_distance(filename)
	for i in table.keys():
		for j in table:
			if i == j:
				table[j].update({i: 0})
			else:
				if i not in table[j].keys():
					table[j][i] = 999
	dict_state = {}
	i=ord('A')
	counter = 0
	while True:
	#connect A
		if i > len(node_table) + 64:
			i = ord('A')
		counter+=1
		ttable=table.copy()
		state, table = bo_nod_cl(chr(i), ttable, counter)
		dict_state[chr(i)] = state
		# check all the node which in dict is update or not,
		if 'Updated' not in dict_state.values() and len(dict_state) == len(node_table):
			break
		i += 1
		# if all are not update,= F, and jomp out loop
	for i in range(len(node_table)):

		node = chr(ord('A')+i)
		c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		c.connect((ip,port[node]))
		c.send(b'stop')
		c.close()
	print('----------------------------------')
	print("Final output")
	res={}
	for i in node_table.keys():
		for j in sorted(table[i].keys()):
			res[j] = table[i][j]
		print('Node '+ i+ ' DV = ' + str(res))
	print('Number of rounds till convergence = '+ str(counter-len(node_table)))
	#print('#Round when one of the nodes last updated its DV: ', str(counter-counter2))



def network_init(filename = 'test.txt'):
	with open(filename) as f:
		node_num = len(f.readlines())
	for i in range(node_num):
		t = threading.Thread(target = server, args=(chr(ord('A')+i), filename))
		t.start()
	b = threading.Thread(target = boss, args=(filename,))
	b.start()

if __name__ == '__main__':
	start = time.clock()
	filename = input('Please enter your file name: ')
	network_init(filename)












