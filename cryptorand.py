import os

# generate a cryptographically secure random
# number between 0 and 256 ^ size (size bytes
# of random data)
def generate(size):
	n = 0
	for i, b in enumerate(os.urandom(size)):
		n += b * (256 ** i)
	return n