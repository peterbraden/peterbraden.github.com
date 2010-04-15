from optparse import OptionParser
import json
import sys
import datetime


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
	data = json.dumps(val, indent=2)
	f.write(data)

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

def get_item_id(items, index):
	for x in items:
		if x.get('index') == index:
			return x
	return None		
 
# ==== 


def parse_add(args):
	tags = []
	for i, x in enumerate(args):
		if x[0] == '#':
			tags.append(x[1:])
			args.pop(i)
			
	return {'name' : " ".join(args), 'tags' : tags, 'added' : str(datetime.datetime.now())}

def add(*args, **kwargs):
	obj = parse_add(args)
	todo = get_data(*args, **kwargs)
	index = reduce(max, [x.get('index', 0) for x in todo])+1
	obj['index'] = index
	print index
	todo.append(obj)
	put_data(todo, *args, **kwargs)
	
	
def ls(*args, **kwargs):
	items = get_data(*args, **kwargs)
	
	
	#Goals

	for i in items:
		def ag(x,y):
			if x.get('done') or x.get('deleted'):
				for k, j in enumerate(y.get('prereq', [])):
					y.get('prereq',[]).pop(k)
				return
				
			if x.get('prereq'):
				for p in x['prereq']:
					n = get_item_id(items, int(p))
					if n:
						ag(n, x)
						if kwargs.get('g') and ('goal' in i.get('tags', [])):
							n['goals'] = "(Goal %s: %s)" % (i.get('index'), i['name'])
		ag(i, i)
	
	
	colors = {
			0 : "\033[1;31;40m",
			1 : "\033[1;33;40m",
			2 : "\033[1;36;40m",
			3 : '\033[1;34;40m',
	}
	default = "\033[0;0;0m"

	for x in items:
		if ((not x.get('done')) and (not x.get('deleted'))) or kwargs.get('a'):
			
		
			
			prereqs = x.get('prereq', []) or ""
			if prereqs:
				prereqs = "(Reqs. " + ", ".join(prereqs) + ")" 
			tags = x.get('tags', '') or ''
			if tags:
				tags = " ".join(['#' + t for t in tags])
			
			fmt = {
				'done' : x.get('done') and 'X' or ' ',
				'index' : x.get('index', '?'),
				'name' : x['name'],
				'col' : kwargs.get('c') and (x.get('importance') is not None) and colors.get(x['importance']) or "",
				'defcol' : default,
				'prereqs' : prereqs,
				'tags' : tags,
				'goals' : x.get('goals', '')
			}
			print "%(col)s%(done)s %(index)s: %(name)s %(tags)s%(defcol)s %(prereqs)s %(goals)s" % fmt


def add_prereq(*args, **kwargs):
	item_id = int(args[0])
	item, save = get_item(item_id, *args, **kwargs)
	item['prereq'] = list(set(item.get('prereq', []) + list(args[1:]))) 
	
	save() 
	
			
def tag(*args, **kwargs):
	item_id = int(args[0])
	item, save = get_item(item_id, *args, **kwargs)
	item['tags'] = list(set(item.get('tags', []) + list(args[1:]))) 
	
	save() 


def do_task(*args, **kwargs):
	item_id = int(args[0])
	item, save = get_item(item_id, *args, **kwargs)	
	item['done'] = True
	save()
	#TODO - remove reqs


def importance(*args, **kwargs):
	item_id = int(args[0])
	importance = int(args[1])
	item, save = get_item(item_id, *args, **kwargs)
	item['importance'] = importance
	save()

def remove(*args, **kwargs):
	item_id = int(args[0])
	item, save = get_item(item_id, *args, **kwargs)	
	item['deleted'] = True
	save()


commands = {
	'add' : add,
	'ls' : ls,
	'do' : do_task,
	'importance' : importance,
	'pre' : add_prereq,
	'rm' : remove,
	'tag' : tag,
	}


if __name__ == '__main__' :
	parser = OptionParser()

	parser.add_option('-a', action='store_true')
	parser.add_option('-c', action='store_true')
	parser.add_option('-g', action='store_true')
	parser.add_option('-f')
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
	
