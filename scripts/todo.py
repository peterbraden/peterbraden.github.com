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

def get_data(*args, **kwargs):
	data = get_file(*args, **kwargs)['0']
	data.sort(key = lambda x:x.get('importance', 4))
	return data

def put_file(val, *args, **kwargs):
	filename = kwargs.get('f', 'todo.json')
	
	f = open(filename, 'w')
	f.write(json.dumps(val))

def put_data(val, *args, **kwargs):
	put_file({'0' : val}, *args, **kwargs)

def get_item(item_id, *args, **kwargs):
	todo = get_data(*args, **kwargs)
	item = [i for i in todo if i.get('index') == item_id]
	
	def save():
		put_data(todo, *args, **kwargs)
	
	if not item:
		print "Unknown Item"
		sys.exit(1)
	return item[0], save	


# ==== 


def add(*args, **kwargs):
	obj = {'name' : " ".join(args)}
	todo = get_data(*args, **kwargs)
	index = reduce(max, [x.get('index', 0) for x in todo])+1
	obj['index'] = index
	todo.append(obj)
	put_data(todo, *args, **kwargs)
	
	
def list(*args, **kwargs):
	items = get_data(*args, **kwargs)
	
	colors = {
			0 : "\033[1;31;40m",
			1 : "\033[1;33;40m",
			2 : "\033[1;34;40m",
			3 : '',
	}
	default = "\033[0;0;0m"

	for x in items:
		if (not x.get('done')) or kwargs.get('a'):
			fmt = {
				'done' : x.get('done') and 'X' or ' ',
				'index' : x.get('index', '?'),
				'name' : x['name'],
				'col' : kwargs.get('c') and (x.get('importance') is not None) and colors.get(x['importance']) or "",
				'defcol' : default,
			}
			print "%(col)s%(done)s %(index)s: %(name)s%(defcol)s" % fmt
		

def do_task(*args, **kwargs):
	item_id = int(args[0])
	item, save = get_item(item_id, *args, **kwargs)	
	item['done'] = True
	save()


def importance(*args, **kwargs):
	item_id = int(args[0])
	importance = int(args[1])
	item, save = get_item(item_id, *args, **kwargs)
	item['importance'] = importance
	save()

commands = {
	'add' : add,
	'ls' : list,
	'do' : do_task,
	'importance' : importance,
	}


if __name__ == '__main__' :
	parser = OptionParser()

	parser.add_option('-a', action='store_true')
	parser.add_option('-c', action='store_true')
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
	
