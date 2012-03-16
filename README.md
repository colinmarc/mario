
Mario.py
========

This is a convenience library for binary and text streams. It really only works with the former right now. It should work in Python 2.7 to 3.x.

**warning: nothing works yet.**

Usage:
-----------

Read from files:

	>>> import mario
	>>> import sys
	>>> p = mario.pump(open('test.txt'))
	>>> p.pipe(sys.stdout)
	>>> p.start()
	but our princess is in another castle!

This works with any file-like object, like sockets:

	import mario
	import socket
	
	#make a socket server
	echoserver = socket.socket()
	echoserver.bind(('', 9599))
	echoserver.listen(1)
	sock, sockaddr = echoserver.accept()

	#pipe the socket back into itself	
	mario.pump(sock).pipe(sock).start()

(to test this, run the script and then telnet localhost 9599)

It also works with generators, including ones you write yourself:

	>>> import mario
	>>> from time import sleep
	>>> def r():
	...		while True:
	...			sleep(1)
	...			yield b'doo\n'
	... 
	>>> mario.pump(r()).pipe(sys.stdout).start(chunk_size=4)
	doo
	doo
	doo
	...

You can wrap a process, and pipe data to stdin and pump from stdout:

	>>> import mario
	>>> import sys
	>>> mario.engine('cowsay "moo!"').pipe(sys.stdout).start()
	 ______
	< moo! >
	 ------
			\   ^__^
			 \  (oo)\_______
				(__)\       )\/\
					||----w |
					||     ||

Or wrap your own stream manglers. This would work for parsers, for example. The function you wrap should return a tuple of ``(backup, output)``, where backup is the data to put back into the buffer for next time.

	>>> import mario
	>>> def newlines(chunk):
	...		split = chunk.rsplit(b'.', 1)
	...		if len(split) > 1:
	...			# split sentences onto separate lines, and return the rest after the 
	...			# last period to parse with the next chunk
	...			return (split[1][1:], split[0].replace(b'. ', b'.\n') + b'.\n')
	... 	else:
	...			return (chunk, b'')
	...
	>>> p = mario.pump(open('paragraph.txt')).pipe(newlines).pipe(sys.stdout)
	>>> p.start(chunk_size=16)
	The three stared heavily as the fog inside the ball began to disappear.	
	The image inside the crystal ball was a short clip of Daisy and Rosalina cuddling Mario and kissing his cheek.
	Peach felt her heart shatter into a million pieces.
	Without a sound, tears streamed down her face.

(text from [Super Mario: The Legend Of The Mushroom Kingdom](http://www.fanfiction.net/s/7866928/1/Super_Mario_The_Legend_Of_The_Mushroom_Kingdom))
