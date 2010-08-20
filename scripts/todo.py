"""
Command line task management.


$> todo ls
 1. Buy bacon
 2. Take over world
 
$> todo do 1

"""

from optparse import OptionParser
import json
import sys
import datetime
from json_couch import sync_l
import uuid



def get_file(*args, **kwargs):
	filename = kwargs.get('f', 'todo.json')
	
	try:
		f = open(filename).read()
		todo = json.loads(f)
	except Exception,e:
		print >> sys.stderr, e
		todo = {'0':[]}

	return todo

DATA = {}

def get_data(*args, **kwargs):
	'''
	We support a number of storage's
	> Flat json file
	> CouchDB
	
	We'll sync on read
	''' 
	global DATA
	if DATA:
		return DATA

	data = get_file(*args, **kwargs)['0']

	try:
		username = kwargs.get('user', '')
		pwd = kwargs.get('pwd', '')
		data = sync_l(data, 'http://%s:%s@peterbraden.couchone.com' % (username, pwd), 'todo', '0')
	except Exception, e:
			print e.__class__.__name__, e.__class__, e

	data.sort(key = lambda x:(x.get('importance', 4), x.get('index', '')))
	DATA = data
	return DATA

def put_file(val, *args, **kwargs):
	filename = kwargs.get('f', 'todo.json')
	
	f = open(filename, 'w')
	data = json.dumps(val, indent=2, sort_keys=True)
	f.write(data)

def put_data(val, *args, **kwargs):
	put_file({'0' : val}, *args, **kwargs)

def find(seg, *args, **kwargs):
	todo = get_data(*args, **kwargs)
	o = None
	for x in todo:
		i = str(x.get('index', ''))
		if i.startswith(seg):
			if o:
				print o
				raise Exception, "Duplicate items by that ID"
			o = i	
	if o:
		return o			
	raise Exception, "Item not Found"			

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
 
 
 

def get_ordered_items(*args, **kwargs):
	items = get_data(*args, **kwargs)
	
	
	#Goals

	for i in items:
		#node, parent
		def ag(x,y):
			x['_importance'] = min(x.get('importance', 100), x.get('_importance', 100))
			if x.get('done') or x.get('deleted'):
				for k, j in enumerate(y.get('prereq', [])):
					if j == x:
						y.get('prereq',[]).pop(k)
				return
			
				
			if y.get('importance') is not None:	
				x['_importance'] = min(y['importance'] - 0.1, y.get('_importance', 100) - 0.1, x['_importance'])
				if y['importance'] < x.get('importance',100):
					x['importance'] = y['importance']
					
						
			if x.get('prereq'):
				for p in x['prereq']:
					n = get_item_id(items, int(p))
					if n:
						ag(n, x)
						if kwargs.get('g') and ('goal' in i.get('tags', [])):
							n['goals'] = "(Goal %s: %s)" % (i.get('index'), i['name'])
		ag(i, i)
	items.sort(key = lambda x: x['_importance'])
 	return items
 
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
	index = str(uuid.uuid4())
	obj['index'] = index
	print index
	todo.append(obj)
	put_data(todo, *args, **kwargs)
	
	
def ls(*args, **kwargs):
	items = get_ordered_items(*args, **kwargs)
	
	colors = {
			0 : "\033[1;31;40m",
			1 : "\033[1;33;40m",
			2 : "\033[1;36;40m",
			3 : '\033[1;34;40m',
	}
	default = "\033[0;0;0m"

	
	items.reverse()
	for x in items:
		if ((not x.get('done')) and (not x.get('deleted')) and ('goal' not in x.get('tags', []))) or kwargs.get('a'):
			
		
			
			prereqs = x.get('prereq', []) or ""
			if prereqs:
				prereqs = "(Reqs. " + ", ".join(prereqs) + ")" 
			tags = x.get('tags', '') or ''
			if tags:
				tags = " ".join(['#' + t for t in tags])
			
			fmt = {
				'done' : x.get('done') and 'X' or ' ',
				'index' : str(x.get('index', '?')) [:4],
				'name' : x['name'],
				'col' : kwargs.get('c') and (x.get('importance') is not None) and colors.get(x['importance']) or "",
				'defcol' : default,
				'prereqs' : prereqs,
				'tags' : tags,
				'goals' : x.get('goals', '')
			}
			print "%(col)s%(done)s %(index)s: %(name)s %(tags)s%(defcol)s %(prereqs)s %(goals)s" % fmt


def curr(*args, **kwargs):
	items = get_ordered_items(*args, **kwargs)
	items = [i for i in items if not i.get('deleted') and not i.get('done')]
	x = items and items[0]
	if not x: return
	
	colors = {
			0 : "\033[1;31;40m",
			1 : "\033[1;33;40m",
			2 : "\033[1;36;40m",
			3 : '\033[1;34;40m',
	}
	default = "\033[0;0;0m"

	prereqs = x.get('prereq', []) or ""
	if prereqs:
		prereqs = "(Reqs. " + ", ".join(prereqs) + ")" 
	tags = x.get('tags', '') or ''
	if tags:
		tags = " ".join(['#' + t for t in tags])
	

	fmt = {
		'done' : kwargs.get('a') and (x.get('done') and 'X ' or '') or '',
		'index' : x.get('index', '?'),
		'name' : x['name'],
		'col' : kwargs.get('c') and (x.get('importance') is not None) and colors.get(x['importance']) or "",
		'defcol' :  kwargs.get('c') and default or "",
		'prereqs' : prereqs and ' ' + prereqs or '',
		'tags' : tags,
		'goals' : x.get('goals') and ' ' + x['goals'] or '' 
	}
	print "%(col)s%(done)s%(index)s: %(name)s %(tags)s%(defcol)s%(prereqs)s%(goals)s" % fmt

def add_prereq(*args, **kwargs):
	item_id = find(args[0], *args, **kwargs)
	item, save = get_item(item_id, *args, **kwargs)
	item['prereq'] = list(set(item.get('prereq', []) + list(args[1:]))) 
	
	save() 
	
			
def tag(*args, **kwargs):
	item_id = find(args[0], *args, **kwargs)
	item, save = get_item(item_id, *args, **kwargs)
	item['tags'] = list(set(item.get('tags', []) + list(args[1:]))) 
	
	save() 


def do_task(*args, **kwargs):
	item_id = find(args[0], *args, **kwargs)
	item, save = get_item(item_id, *args, **kwargs)	
	item['done'] = True
	save()
	#TODO - remove reqs


def importance(*args, **kwargs):
	item_id = find(args[0], *args, **kwargs)
	importance = int(args[1])
	item, save = get_item(item_id, *args, **kwargs)
	item['importance'] = importance
	save()

def remove(*args, **kwargs):
	item_id = find(args[0], *args, **kwargs)
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
	'curr' : curr,
	}


if __name__ == '__main__' :
	parser = OptionParser()

	parser.add_option('-a', action='store_true')
	parser.add_option('-c', action='store_true')
	parser.add_option('-g', action='store_true')
	parser.add_option('--user', dest='user')
	parser.add_option('--pwd', dest='pwd')
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
	
