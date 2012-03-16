import os
from io import TextIOBase, RawIOBase
try:
	file
except NameError:
	file = RawIOBase
import fcntl
from collections import Iterator
from socket import socket as SocketObj
from subprocess import Popen, PIPE
import doctest

CHUNK_SIZE = 4096

def _run_pipeline(pipeline, chunk_size=CHUNK_SIZE):
	while len(pipeline) > 1:
		for i, part in enumerate(pipeline):	
			if i+1 == len(pipeline):
				break	
		
			chunk = part.read(chunk_size)
			if not chunk and i == 0:
				dead_part = pipeline.pop(0)
				dead_part.close()
				break

			next_part = pipeline[i+1]
			if isinstance(next_part, TextIOBase):
				next_part.buffer.write(chunk)
			else:
				next_part.write(chunk)
			if hasattr(next_part, 'flush'):
				next_part.flush()			

class Plumbing(object):	
	def __init__(self):
		self.parent = None
		self.child = None

	def pipe(self, f):
		if not isinstance(f, Plumbing):
			if hasattr(f, '__call__'):
				f = Turbine(f)
			else:
				f = Pipe(f)
		self.child = f
		f.parent = self
		return f

	def start(self, chunk_size=None):
		if not chunk_size:
			chunk_size = CHUNK_SIZE
		pipeline = []
		l = self
		#TODO trees
		while True:
			if not l.parent:
				break
			l = l.parent
		while True:
			pipeline.append(l)
			l = l.child
			if not l:
				break
		_run_pipeline(pipeline, chunk_size)

	#abstract
	def read(self, chunk_size):
		raise IOError("device is not readable")

	#abstract
	def write(self, chunk):
		raise IOError("device is not writeable")

	#abstract
	def close(self):
		pass

class Pipe(Plumbing):
	def __init__(self, f):
		super(Pipe, self).__init__()
		self.f = f
		if isinstance(f, SocketObj):
			self._write = self._socket_write
		elif isinstance(f, TextIOBase):
			self._write = self._text_write
		else:
			self._write = self._file_write

	def _socket_write(self, chunk):
		self.f.sendall(chunk)
	
	def _text_write(self, chunk):
		self.f.buffer.write(chunk)
		self.f.buffer.flush()

	def _file_write(self, chunk):
		self.f.write(chunk)
		self.f.flush()

	def write(self, chunk):
		self._write(chunk)

	def close(self):
		if hasattr(self.f, 'close'): self.f.close()

def pipe(f):
	return Pipe(f)

class Pump(Plumbing):
	def __init__(self, f):
		super(Pump, self).__init__()
		self.f = f
		if isinstance(f, SocketObj):
			self._read = self._socket_read
		elif isinstance(f, TextIOBase):
			self._read = self._text_read
		elif isinstance(f, file):
			self._read = self._file_read
		elif isinstance(f, Iterator):
			self.buf = bytearray()
			self._read = self._generator_read
		else:
			self._read = self._file_read

	def _socket_read(self, chunk_size):
		return self.f.recv(chunk_size)

	def _generator_read(self, chunk_size):
		data = self.buf
		while len(data) < chunk_size:
			data += next(self.f)

		self.buf = data[chunk_size:]
		return data[:chunk_size]

	def _text_read(self, chunk_size):
		return self.f.buffer.read(chunk_size)

	def _file_read(self, chunk_size):
		return self.f.read(chunk_size)

	def read(self, chunk_size):
		data = self._read(chunk_size)
		if not data:
			return b''
		return data

	def close(self):
		if hasattr(self.f, 'close'): self.f.close()

def pump(f):
	return Pump(f)

class Union(Plumbing):
	def __init__(self):
		super(Union, self).__init__()
		self.buf = b''

	def read(self, chunk_size):
		data = self.buf
		self.buf = data[chunk_size:]
		return data[:chunk_size]
		
	def write(self, chunk):
		self.buf += chunk

def union():
	return Union()

#TODO: still defeated by line buffering
class Engine(Plumbing):
	def __init__(self, command):
		super(Engine, self).__init__()
		self.command = command
		self.process = None
		
	def _check_started(self):
		if not self.process:	
			self.process = Popen(self.command, shell=True, stdout=PIPE, stdin=PIPE, bufsize=1)

	def write(self, chunk):
		self._check_started()
		self.process.stdin.write(chunk)
		self.process.stdin.flush()
	
	def read(self, chunk_size):
		self._check_started()
		data = self.process.stdout.read()

		if not data:
			return b''
		return data

def engine(command):
	return Engine(command)

class Turbine(Plumbing):
	def __init__(self, func):
		super(Turbine, self).__init__()
		self.func = func
		self.output_buf = b''
		self.input_buf = b''

	def read(self, chunk_size):
		data = self.output_buf
		while len(data) < chunk_size:
			backup, output = self.func(self.input_buf)	
			self.input_buf = backup
			
			if not output:
				break
			data += output

		self.output_buf = data[chunk_size:]
		return data[:chunk_size]

	def write(self, chunk):
		self.input_buf += chunk

