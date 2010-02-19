from optparse import OptionParser
import json

def get_file(*args, **kwargs):
	filename = kwargs.get('f', 'todo.json')
	
	try:
		f = open(filename).read()
		todo = json.loads(f)
	except Exception,e:
		print e
		todo = {'0':[]}
	
	return todo


def put_file(val, *args, **kwargs):
	filename = kwargs.get('f', 'todo.json')
	
	f = open(filename, 'w')
	f.write(json.dumps(val))


def add(*args, **kwargs):
	obj = {'name' : " ".join(args)}
	todo = get_file(*args, **kwargs)	
	todo['0'].append(obj)
	put_file(todo, *args, **kwargs)
	
	
def list(*args, **kwargs):
	todo = get_file(*args, **kwargs)
	items = todo['0']
	for x in items:
		print x['name']

commands = {
	'add' : add,
	'ls' : list,
	}


if __name__ == '__main__' :
	parser = OptionParser()

	(options, args) = parser.parse_args()
		
	cmd = commands.get(args[0])

	if not cmd:
		raise Exception("Unknown command, %s" % args[0])
	else:
		args = args[1:]
		cmd(*args, **options.__dict__)
	
