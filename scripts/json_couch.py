from decorators import memoized
from couchdb import client
from couchdb.http import ResourceNotFound
import uuid

@memoized
def _server(url):
	return client.Server(url)


def get_doc_json(db, key, server = 'http://localhost:5984'):
	s = _server(server)
	try:
		db = s[db]
	except ResourceNotFound:
		db = s.create(db)
	return dict(db.get(key, {}))
	

def put_doc_json(db, key, value, server = 'http://localhost:5984'):
	s = _server(server)
	try:
		db = s[db]
	except ResourceNotFound:
		db = s.create(db)

	db[str(key)] = value


def magic_syncing(d1, d2):
	keys_visited = []

	for k, v in d1.items():
		e = d2.get(k)
		
		#compare e and v -> put newer back in d1
		if v.get('date_modified'):
			if e.get('date_modified') and e['date_modified'] > v['date_modified']:
				d1[k] = e
			else:
				d1[k] = v
			
		elif v.get('_rev') and e.get('_rev'):
			if e['_rev'].split('-')[0] > v['rev'].split('-')[0]:
				d1[k] = e
			else:
				d1[k] = v
		else:
			pass

		keys_visited.append(k)
		

	other_keys = list(set(d2.keys()) - set(keys_visited))
	for k in other_keys:
		d1[k] = d2[k]

	return d1


def sync_l(l, serv, db, k):
	dbdoc0 = get_doc_json(db, k, server=serv)
	dbdoc = dbdoc0.get('content', {}) 
	d = {}
	for x in l:
		d[str(x.get('index', 0))] = x

	d2 = magic_syncing(d, dbdoc)	
	dbdoc0['content'] = d2

	put_doc_json(db, k, dbdoc0, server=serv)
	return d2.values()


def sync_list(l, serv, dbk):
	try:
		db = _server(serv)[dbk]
	except ResourceNotFound:
		db = _server(serv).create(dbk)

	dbdocsl = db['_all_docs'].get('rows', [])
	dbdocs = dict([(x['id'], db[x['id']]) for x in dbdocsl]) 

	d = {}


	for x in l:
		if not x.get('index'):
			x['index'] = uuid.uuid4() #Assign UUID
		d[x['index']] = x
	d2 = magic_syncing(d, dbdocs)
	
	for k,v in d2.items():
		put_doc_json(dbk, k, v, server=serv)
	return d2.values() 

