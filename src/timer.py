import time

def time_me(f):
	'''Decorator function to time functions' runtime in ms'''
	def wrapper(*args, **kwargs):
		start = time.time()
		res = f(*args, **kwargs)
		print(f'function: {f.__name__} took {(time.time()-start)*1000:.4f}ms')
		return res
	return wrapper