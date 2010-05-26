from couchdb import client

def get_doc_json(db, key, server = 'http://localhost:5984'):
	s = client.Server(server)
	try:
		db = s[db]
	except client.ResourceNotFound:
		db = s.create(db)
	return dict(db.get(key, {}))
	

def put_doc_json(db, key, value, server = 'http://localhost:5984'):
	s = client.Server(server)
	db = s[db]
	db[key] = value


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


def sync_l(l, db, k):
	dbdoc0 = get_doc_json(db, k)
	dbdoc = dbdoc0.get('content', {}) 

	d = {}
	for x in l:
		d[str(x.get('index', 0))] = x

	d2 = magic_syncing(d, dbdoc)	
	
	dbdoc0['content'] = d2

	put_doc_json(db, k, dbdoc0)
	return d2.values()

