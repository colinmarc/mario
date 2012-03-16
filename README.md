
Mario.py
========

This is a convenience library for binary and text streams. It really only works with the former right now. It should work in Python 2.7 to 3.x.

**warning: nothing works yet.**

Usage:
-----------

Read from files:

	>>> import sys
	>>> from mario import Pump
	>>> with open('test.txt') as f:
	...		p = Pump(f)
	...		p.pipe(sys.stdout)
	...		p.start()
	but our princess is in another castle!

This works with any file-like object, like sockets:

	>>> import socket
	>>> from mario import Pump
	>>> echoserver = socket.socket()
	>>> echoserver.bind(('', 9599))
	>>> echoserver.listen(1)
	>>> sock, sockaddr = echoserver.accept()
	>>> p = Pump(sock)
	>>> p.pipe(sock) #pipe it back into itself
	>>> p.start()

(to test this, telnet localhost 9599)

It also works with generators, including ones you write yourself:

	>>> from time import sleep
	>>> from mario import Source
	>>> def r():
	...		while True:
	...			sleep(1)
	...			yield b'doo\n'
	... 
	>>> s = Pump(r())
	>>> s.pipe(sys.stdout)
	>>> s.start(chunk_size=2)
	doo
	doo
	doo
	...

You can wrap a process, and pipe data to stdin and pump from stdout:

	>>> from mario import Engine
	>>> e = Engine('cat')
	>>> e.pipe(sys.stdout)
	>>> e.write('dog')
	>>> e.start(chunk_size=1)
	dog

Or wrap your own stream manglers. This would work for parsers, for example. The function you wrap should return a tuple of ``(backup, output)``, where backup is the data to put back into the buffer for next time.

	>>> from mario import Pump, Turbine
	>>> def newlines(chunk):
	...		split = chunk.rsplit(b'.', 1)
	...		if len(split) > 1:
	...			return (split[1][1:], split[0].replace(b'.', '.\n') + '.\n')
	... 	else:
	...			return (chunk, b'')
	>>> p = Pump(open('paragraph.txt'))
	>>> p.pipe(Turbine(newlines)).pipe(sys.stdout)
	>>> p.start(chunk_size=16)
	The three stared heavily as the fog inside the ball began to disappear.	
	The image inside the crystal ball was a short clip of Daisy and Rosalina cuddling Mario and kissing his cheek.
	Peach felt her heart shatter into a million pieces.
	Without a sound, tears streamed down her face.

(text from [Super Mario: The Legend Of The Mushroom Kingdom](http://www.fanfiction.net/s/7866928/1/Super_Mario_The_Legend_Of_The_Mushroom_Kingdom))
