import sys, os, uuid, hashlib
from cryptography.fernet import Fernet

g_metadata = {}
g_VERBOSE = False
g_allowed_arguments = ["-h", "-k", "-e", "-m", "-d", "-o", "-v", "-a"]


def help(prog_name):
	print("Usage: " + prog_name)
	print("-h                Prints the help message.")
	print("-k key_file       Key used for encryption/decryption. If not given, a key is created and saved in 'cloud-key.key'.")
	print("-v                Verbose output.")
	print("-e folder         The folder you want to encrypt.")
	print("-d folder         The folder containing the encrypted files.")
	print("-m metadata_file  The metadata file to use. This is optional for -e, but mandatory for -d.")
	print("-o folder         The output folder. Default is 'out_e/' for -e and 'out_d/' for -d.")
	print("-a                Append to metadata file. If not used, then folder and metadata are synced.")
	print("")
	print("Example encryption: ")
	print("    python " + prog_name + " -e .")
	print("    python " + prog_name + " -e . -m out_e\metadata.txt")
	print("    python " + prog_name + " -e . -v -o ../out_e")
	print("    python " + prog_name + " -e . -m ../out_e/metadata.txt -v -o ../out_e")
	print("Example decryption: ")
	print("    python " + prog_name + " -d out_e -m out_e\metadata.txt")
	print("    python " + prog_name + " -d ../out_e -m ../out_e\metadata.txt -o ../out_d")


def hash_file(file_path):
	
	# read data in 64kb chunks
	BUF_SIZE = 65536

	sha1 = hashlib.sha1()

	with open(file_path, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			sha1.update(data)

	final_sha1 = sha1.hexdigest()
	return final_sha1


def create_uuid():
	return uuid.uuid4()


def mprint(arg):
	if g_VERBOSE:
		print(arg)


def create_key():
	return Fernet.generate_key()
	

def encrypt_data(data, key):
	f = Fernet(key)
	return f.encrypt(data)


def decrypt_data(data, key):
	f = Fernet(key)
	return f.decrypt(data)


def encrypt_file(file_path, key):
	fernet = Fernet(key)
	with open(file_path, 'rb') as f:
		data = f.read()
		return fernet.encrypt(data)
		

def decrypt_file(encr_file_path, key):
	fernet = Fernet(key)
	with open(encr_file_path, 'rb') as f:
		data = f.read()
		return fernet.decrypt(data)


import base64, getpass
def fernet_key_from_user_pass():

	user_password = getpass.getpass()
	sha256 = hashlib.sha256()
	sha256.update(user_password)
	hd = sha256.hexdigest()
	key = base64.urlsafe_b64encode(hd[:32])
	return key


def write_file(file_name, data):

	# if directories do not exist, create them
	if not os.path.exists(os.path.dirname(file_name)):
		try:
			os.makedirs(os.path.dirname(file_name))
		except OSError as exc: # Guard against race condition
			print("Something went wrong while creating file '" + file_name + "':" + str(exc))
	
	# write to file
	with open(file_name, 'wb') as f:
		f.write(data)
	

def get_all_files_in_folder(startpath):
	files_list = []

	for path, _, files in os.walk(startpath):
		for name in files:
			full_path = os.path.join(path, name)
			full_path = full_path.replace('.\\', '')
			full_path = full_path.replace('\\', '/')
			files_list.append(full_path)

	return files_list
	

def get_arguments(argv):
	prog_name = argv[0]
	opts = {}

	while argv:
	
		# if the user asked for help
		if argv[0] == "-h":
			help(prog_name)
			exit(0)
			
		elif argv[0] == "-v":
			global g_VERBOSE
			g_VERBOSE = True
			
		elif argv[0] == "-a":
			opts["-a"] = True
			
		# if argument starts with '-'
		elif argv[0][0] == '-': 
			if argv[0] not in g_allowed_arguments:
				print("Error! argument " + argv[0] + " is not recognised.\n")
				help(prog_name)
				exit(1)
			else:
				opts[argv[0]] = argv[1]
			
		# reduce argv by one
		argv = argv[1:]
		
	return opts



import json
def main(myargs):
	
	global g_metadata
	
	fernet_key = None
	if "-k" in myargs:

		# Load key

		# user password to decrypt encrypted file containing Fernet key
		pwd = fernet_key_from_user_pass()
		fernet_key = decrypt_file(encr_file_path=myargs["-k"], key=pwd)
	else:

		# Create a new Fernet key and use the user's password to encrypt it
		# We could use user's password to directly encrypt data, but it could be a weak password

		# create Fernet key
		fernet_key = create_key()

		# encrypt Fernet key in a file using user's password
		pwd = fernet_key_from_user_pass()

		# save encrypted Fernet key to file 
		write_file('./cloud-key.key', encrypt_data(data=fernet_key, key=pwd))


	# if encrypt
	if "-e" in myargs:
	
		# get all files in the provided folder
		files = get_all_files_in_folder(myargs["-e"])
		print("Total files in folder: " + str(len(files)))
		# counts how many files have been encrypted so far
		encr_files_ctr = 0
		
		out_folder = 'out_e/'
		# if the user has provided an out folder then use that
		if "-o" in myargs:
			out_folder = myargs["-o"]
			if not out_folder.endswith("/"):
				out_folder += "/"
				
		metadata = None
		if "-m" in myargs:
			if os.path.exists(myargs["-m"]):
				metadata = json.load(open(myargs["-m"]))
			else:
				print("metadata file doesn't exist!")
				exit(1)
				
		if "-a" in myargs:
			# in case of 'append', we need to use the old dictionary and then add anything new there
			g_metadata = metadata
			mprint("Appending data, without deleting older structure...")
				
		# for every file: encrypt it, name it using a uuid and store the hash of the unencrypted file
		for f in files:
		
			# if file (i.e. not folder)
			if os.path.isfile(f):
			
				# calculate the SHA1 hash of the plaintext, i.e. the hash of the unencrypted file
				sha1_hash = hash_file(f)
				
				# get a unique id 
				uuid = str(create_uuid())
				
				# if file already exists in user provided metadata, check if its sha1 hash is different
				same_sha1 = False
				if "-m" in myargs and f in metadata:
				
					# if file already exists in metadata, use the old uuid
					uuid = metadata[f]["uuid"]
					
					old_sha1_hash = metadata[f]["sha1"]
					
					# if they are equal, that means that the file hasn't been edited since last time
					if old_sha1_hash == sha1_hash:
						same_sha1 = True
						mprint("file '" + f + "' hasn't changed!")						
				
				if not same_sha1:
					
					# write the encrypted file
					write_file(file_name=out_folder + uuid, data=encrypt_file(f, fernet_key))
					mprint("encrypted file '" + f + "'")
					
					# stats
					encr_files_ctr += 1
					if not g_VERBOSE: 
						if encr_files_ctr % 10 == 0:
							print("encrypted " + str(encr_files_ctr) + "/" + str(len(files)) + " so far...")
						
				# add metadata to the metadata dictionary
				g_metadata[f] = {"uuid": uuid, "sha1" : sha1_hash}
		
		# show final stats
		print("encrypted " + str(encr_files_ctr) + "/" + str(len(files)) + "!")
		
		# if metadata has been given, then check all metadata files to see if something has been deleted
		# if it has been deleted, delete it
		if "-m" in myargs and "-a" not in myargs:
			for f in metadata:
				if f not in files:
					# delete file from out_folder
					os.remove(out_folder + metadata[f]["uuid"])
					mprint("deleted file: '" + f + "' -> '" + out_folder + metadata[f]["uuid"] + "'")
		
		# write metadata to file
		with open('metadata.txt', 'w') as file:
			file.write(json.dumps(g_metadata, indent=4, sort_keys=True))
		
		print("metadata are stored in " + out_folder + 'metadata.txt')
	
	# else if decrypt
	elif "-d" in myargs:
	
		if "-m" not in myargs:
			print("You need to specify a metadata file to be used for decryption.")
			exit(1)
	
		# load metadata
		metadata = json.load(open(myargs["-m"]))
		print("Total files to decrypt: " + str(len(metadata)))
		# counts how many files have been decrypted so far
		decr_files_ctr = 0 
		
		out_folder = 'out_d/'
		# if the user has provided an out folder then use that
		if "-o" in myargs:
			out_folder = myargs["-o"]
			if not out_folder.endswith("/"):
				out_folder += "/"
		
		# decrypt every file
		for f in metadata:
		
			# decrypt file
			write_file(file_name=out_folder + f, data=decrypt_file(myargs["-d"] + "/" + metadata[f]["uuid"], fernet_key))
			
			# show stats
			decr_files_ctr += 1
			if not g_VERBOSE:				
				if decr_files_ctr % 10 == 0:
					print("decrypted " + str(decr_files_ctr) + "/" + str(len(metadata)) + " so far")
		
		# show final stats
		print("decrypted " + str(decr_files_ctr) + "/" + str(len(metadata)) + "!")
		
	exit(0)

	
if __name__ == '__main__':
	import sys
	myargs = get_arguments(sys.argv)
	
	# if it has been executed using double click
	if len(myargs) == 0:
		exit(1)

	main(myargs)