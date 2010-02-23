from optparse import OptionParser
import json
import sys

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
	index = reduce(max, [x.get('index', 0) for x in todo['0']])+1
	obj['index'] = index
	todo['0'].append(obj)
	put_file(todo, *args, **kwargs)
	
	
def list(*args, **kwargs):
	todo = get_file(*args, **kwargs)
	items = todo['0']
	
	for x in items:
		if not x.get('done'):
			print "  - %s: %s" % (x.get('index', 'X'),x['name'])
		

def do_task(*args, **kwargs):
	item_id = int(args[0])
	todo = get_file(*args, **kwargs)
	item = [i for i in todo['0'] if i.get('index') == item_id]
	if not item:
		print "Unknown Item"
		return
	else:
		item[0]['done'] = True
	put_file(todo, *args, **kwargs)


commands = {
	'add' : add,
	'ls' : list,
	'do' : do_task,
	}


if __name__ == '__main__' :
	parser = OptionParser()

	(options, args) = parser.parse_args()
	
	if not args:
		print "Unknown Command"
		sys.exit()

	cmd = commands.get(args[0])

	if not cmd:
		raise Exception("Unknown command, %s" % args[0])
	else:
		args = args[1:]
		cmd(*args, **options.__dict__)
	
