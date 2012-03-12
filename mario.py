
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
	...    sleep(1)
    ...    return 'test\n'
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
