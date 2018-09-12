import sys, socket, time, os, _thread, pickle, argparse, threading
from client import Client
class Server:
	def __init__(self, threadCount):
		print("Initializing client...")
		# Listen for incoming connections
		self.index = 0
		localLog = Log()
		localDict = BlockDictionary()
		self.serverAddr = socket.gethostbyname(socket.gethostname())
		sock = self.createSocket()
		_thread.start_new_thread(self.run, (sock, localLog, localDict, threadCount))
		#^-- how to run server and client at same time???
	def createSocket(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# Bind the socket to the port
		server_address = (self.serverAddr, 9912)
		print('starting up on {} port {}'.format(*server_address))
		sock.bind(server_address)
		self.serverAddr = server_address[0]

		# Listen for incoming connections
		return sock

	def run(self, sock, log, localDict, threads):
		sock.listen(threads)
		sock.setblocking(0)
		while 1:
			# Wait for a connection
			try:
				connection, client_address = sock.accept()
				print('waiting for a connection')
				#_thread.start_new_thread(self.connectClient, (connection, client_address, log, localDict))
			except socket.error:
				'''NO DATA FOUND YET!'''

	def connectClient(self, connection, client_address, log, localDict):
		print('connection from', client_address)
		# Receive the data in small chunks and retransmit it
		while 1:
			try:
				data = connection.recv(256)
				if data:
				#print("data received from client")
					self.parseMessage(client_address, self.deserializeMessage(data), log, localDict)
				#connection.sendall(log.serialize())
				else:
					print("no data recvd")
					break
			except socket.error:
				'''no data yet...'''
		connection.close()
		# Clean up the connection
	def deserializeMessage(self, data):
		return pickle.loads(data)

	def parseMessage(self, clientAddr, userInput, log, dictionary):
		#msg = userInput.decode('UTF-8')
		#strList = msg.split(" ")
		command = userInput["type"]#(strList[0]).lower()
		#process tweet
		if (command == "tweet"):
			logEntry = log.createEntry(command, clientAddr, userInput["message"])
			log.addEntry(logEntry)
		elif (command == "block"):
			logEntry = log.createEntry(command, clientAddr, userInput["message"])
			log.addEntry(logEntry)
			dictionary.addBlock(self.index, userInput["message"])
			#print("Got block command " + userInput["message"])#localDictionary.addBlock()
		elif (command == "unblock"):
			logEntry = log.createEntry(command, clientAddr, userInput["message"])
			log.addEntry(logEntry)
			dictionary.removeBlock(self.index, userInput["message"])
		elif (command == "view"):
			log.view()
		elif (command == "clear"):
			log.clear()
		elif (command == "dict"):
			dictionary.printDictionary()

class BlockDictionary:
	def __init__(self):
		self.fname = "blocked.txt"
		if (not os.path.exists(self.fname)):
			print("creating new log")
			file = open(self.fname, "w")
			file.close()

	def getBlocked(self, index):
		if (os.stat(self.fname).st_size == 0):
			return []
		file = open(self.fname,"rb")
		loadedDict = pickle.load(file)
		file.close()
		return loadedDict[index]

	def isBlocked(self, blocklist, toBlock):
		for blocked in blocklist:
			if toBlock in blocklist[blocked]:
				return True
		return False

	def addBlock(self, index, toBlock):
		if (os.stat(self.fname).st_size != 0):
		 	file = open(self.fname,"rb")
		 	loadedDict = pickle.load(file)
		 	check = self.isBlocked(loadedDict, toBlock)
		 	if not check:
		 		outDict = loadedDict
		 		outDict[index].append(toBlock)
		 		file.close()
		 		file = open(self.fname, "wb")
		 		pickle.dump(outDict, file)
		 		file.close()
		else:
		 	file = open(self.fname, "wb")
		 	pickle.dump({index:[toBlock]}, file)
		 	file.close()
		 	print("st_size == 0")

	def removeBlock(self, index, unBlock):
		if (os.stat(self.fname).st_size == 0):
			return
		file = open(self.fname, "rb")
		loadedDict = pickle.load(file)
		if (loadedDict == None):
			print("INVALID REMOVAL: NO ENTRY FOUND IN DICTIONARY")
			file.close()
			return
		else:
		 	check = self.isBlocked(loadedDict, unBlock)
		 	if check:
		 		outDict = loadedDict
		 		outDict[index].remove(unBlock)
		 		file.close()
		 		file = open(self.fname, "wb")
		 		pickle.dump(outDict, file)
		 		file.close()

	def printDictionary(self):
		file = open(self.fname, "rb")
		loadedDict = pickle.load(file)
		for i in loadedDict:
			print(loadedDict[i])
		file.close()

class Log:
	#Filepath of log file
	fname = ""
	#dataStructure holding entries of log
	#todo: restore data structure based on local log on init
	entries = []
	def __init__(self):
		self.fname = "local.log"
		self.count = 0
		if (not os.path.exists(self.fname)):
			print("creating new log")
			file = open(self.fname, "w")
			file.close()
		self.checkCount()

	def checkCount(self):
		if (os.path.exists(self.fname)):
			file = open(self.fname, "r")
			lines = file.readlines()
			if (len(lines) == 0):
				self.count = 0
			else:
				for l in lines:
					print(l)
					fileCount = int(l[0])
					if fileCount >= self.count:
						self.count = fileCount+1
			file.close()
		else:
			self.count = 0

	def createEntry(self, command, clientAddr, msg):
		user = clientAddr[0] +":" + str(clientAddr[1])
		t =  str(time.time())
		entry = str(self.count) + "|" + user + "|" + command + "|" + msg + "|" +  t
		self.count += 1
		return entry
	#Reads the file and creates a dictionary with the 
	#lamport time stamp as key, 
	#value is tuple of event info

	#Writes entry to log file
	def addEntry(self, entry):
		file = open(self.fname, "a")
		file.write(entry + "\n")
		self.entries.append(tuple(entry))
		print("Writing to file", entry)
		file.close()

	def view(self):
		print("Viewing Log...")
		file = open(self.fname, "r")
		for line in file.readlines():
			l = line.strip("\n")
			entry = tuple(l.split("|"))
			print(entry)
		file.close()
	#Wipe the log
	def clear(self):
		print("Clearing Log...")
		file = open(self.fname, "w")
		file.write("")
		file.close()

def test():
	print("hi")
def main():
	parser = argparse.ArgumentParser(description='ip addr.')
	parser.add_argument('ip_addr', type=str,
                    help='IP Address')
	args = parser.parse_args()
	threads = []
	#s = Server(5)
	serverThread = threading.Thread(target=Server, args=(5,))
	serverThread.start()
	serverThread.join()
	threads.append(serverThread)
	print("created serverThread")
	time.sleep(2)
	#c = Client(5, args.ip_addr)
	clientThread = threading.Thread(target=Client, args=(5, args.ip_addr))
	clientThread.start()
	clientThread.join()
#	c = _thread.start_new_thread(Client, (5, args.ip_addr))
if __name__ == '__main__':
	main()