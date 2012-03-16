from io import TextIOBase 
from socket import _socketobject as socket_object
import json
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
			pipeline.append(l)
			l = l.child if hasattr(l, 'child') else None
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
		if isinstance(f, socket_object):
			self._write = self._socket_write
		elif isinstance(f, TextIOBase):
			self._write = self._text_write
		else:
			self._write = self._file_write

	def _socket_write(self, chunk):
		self.f.sendall(chunk)
	
	def _text_write(self, chunk):
		self.f.buffer.write(chunk)

	def _file_write(self, chunk):
		self.f.write(chunk)

	def write(self, chunk):
		self._write(chunk)

	def close(self):
		self.f.close()

class Pump(Plumbing):
	def __init__(self, f):
		super(Pump, self).__init__()
		self.f = f
		if isinstance(f, socket_object):
			self._read = self._socket_read
		elif isinstance(f, TextIOBase):
			self._read = self._text_read
		else:
			self._read = self._file_read

	def _socket_read(self, chunk_size):
		return self.f.recv(chunk_size)

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
		self.f.close()

class Source(Plumbing):
	def __init__(self, func):
		super(Source, self).__init__()
		self.func = func
		self.buf = b''

	def read(self, chunk_size):
		data = self.buf
		while len(data) < chunk_size:
			data += self.func()

		self.buf = data[chunk_size:]
		return data[:chunk_size]

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

class Engine(Plumbing):
	pass

class Turbine(Plumbing):
	def __init__(self, func):
		super(Turbine, self).__init__()
		self.func = func
		self.output_buf = b''
		self.input_buf = b''

	def read(self, chunk_size):
		data = b''
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

