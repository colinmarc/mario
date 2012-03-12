import doctest

class Pump:
	pass

class Pipe:
	pass

class Emitter:
	pass

def pump(f):
	"""reads from file-like object f and returns a Pump object.

	>>> with open('test.txt') as f:
		    p = pump(f).pipe(sys.stdout)
			p.join()

	"""
	pass

def pipe():
	"""mimes a file-like object, and returns a Pipe object.

	>>> p = Pipe()
	>>> p.pipe(sys.stdout)
	>>> p.write('test')
	>>> p.join()
	test

	"""
	pass

def emitter(func):
	"""returns an Emitter object that  runs the function func in a loop to generate output.
	
	Return false from func to stop emitting.

	>>> def r():
	...		sleep(1)
    ...		return 'test\\n' 
	... 
	>>> e = emitter(r)
	>>> e.pipe(sys.stdout)
	>>> e.join()
	test
	test
	test
	...
	"""
	pass

def tee(f):
	"""pipes output to file-like object f, and also returns a pipe object.

	>>> t = tee(sys.stderr)
	>>> t.pipe(sys.stdout)
	>>> t.write('test\n')
	>>> t.join()
	test
	test

	"""
	pass

def engine(cmd):
	"""wraps a Popen-compatible command and returns an Engine object. The engine object
	pipes incoming data to stdin of the process and pumps stdout. 
	
	>>> e = engine('cat')
	>>> e.pipe(sys.stdout)
	>>> e.write('test')
	>>> e.join()
	test
	
	"""
	pass

def turbine(func):
	"""wraps a function func and returns a Turbine object. The turbine pipes incoming data into func,
	and pumps the output. The function should take one argument, which will be a chunk of data, and
	return a tuple (backup, output).

	>>> def parse_sentences(chunk):
	...		split = chunk.rsplit('.', 1)
	...		return (split[0].replace('.', '\n', split[1])
	... 
	>>> p = pump(open('test.txt'))
	>>> t = turbine(parse_sentences)
	>>> p.pipe(t).pipe(sys.stdout)
	>>> p.join()
	this is a test.
	this is another test.
	test.
	stuff.
	testing.

	"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()
