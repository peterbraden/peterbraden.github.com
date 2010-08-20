"""
Accountant
----------

A commandline utility for managing finance and accounting.


Concepts:
	Transaction - double entry accounting.
	Statement - Balance of assets at point in time for verification purpose
	Account - superclass of Equity, Assets, Liabilities, Expenses, Income 


TODO:
	Sort out difference between 'my' accounts and other accounts. Show income/outgoings
	Insert Account object into each transaction instead of key


"""

import datetime
import optparse
import bisect
import sys
from decimal import Decimal



accounts = {}
ordered_objects = []
reports = []



#========= DATA TYPES =============

class Statement():
	def __init__(self, acct, date, currency, balance, *args, **kwargs):
		self.date = datetime.datetime.strptime(date, '%Y-%m-%d')
		self.balance = Decimal('%.2f' % balance)
		self.account = acct
		self.currency = currency
		
		if acct not in accounts:
			accounts[acct] = Account(acct, acct, currency = currency)
		self.account = accounts[acct]
		
		self.key = '%s%s' % (self.date.strftime('%Y-%m-%d'), '1s')
		
		bisect.insort(ordered_objects, (self.key, self))
		#accountant.add_statement(self)

	def will_fire(*args, **kwargs):
		return True

class Account():
	def __init__(self, id, name, *args, **kwargs):
		self.id = id
		self.name = name
		self.balance = 0
		self.owner = kwargs.get('owner') or ''
		self.currency = kwargs.get('currency') or '?'
		
		accounts[self.id] = self
		#accountant.add_account(self)
		
		
		
class Transaction():
	def __init__(self, src, dest, date, currency, amount, category = None, *args, **kwargs):
		self.dest_key = dest
		self.date = datetime.datetime.strptime(date, '%Y-%m-%d')
		self.currency = currency
		self.amount = Decimal('%.2f' % amount)
		self.category = category
		
		if src not in accounts:
			accounts[src] = Account(src, src, currency = self.currency)
		if dest not in accounts:
			accounts[dest] = Account(dest, dest, currency = self.currency)	
		
		self.source = accounts[src]
		self.dest = accounts[dest]
		
		# Hack
		if self.source.currency == '?':
			self.source.currency = self.currency
		
		if self.dest.currency == '?':
			self.dest.currency = self.currency
		
		self.key = '%s%s' % (self.date.strftime('%Y-%m-%d'), '0t')
		bisect.insort(ordered_objects, (self.key, self))
		#accountant.add_transaction(self)

	def will_fire(*args, **kwargs):
		return True

	def __str__(self):
		return "Transaction('%s', '%s', '%s', '%s', %s)" %(
			self.source.id, 
			self.dest.id, 
			self.date.strftime('%Y-%m-%d'), 
			self.currency, 
			self.amount)

#Temp Aliases
class BankAccount(Account):
	pass

class Loan(Account):
	pass

class CurrencyChg(object):
	def __init__(self, src, dest, date, source_currency, source_amount, dest_currency, dest_amount, category = None, *args, **kwargs):
		Transaction(src, 'curr_change', date, source_currency, source_amount, category, *args, **kwargs)
		Transaction('curr_change', dest, date, dest_currency, dest_amount, category, *args, **kwargs)

class OtherCompaniesAccounts(object):#TODO! fix
	def __init__(self, accounts):
		for i in accounts:
			Account(i,i)
			Statement(i, '2005-10-01', '?', 0)

###====

class ProjectedTransaction(Transaction):
	def will_fire(*args, **kwargs):
		return kwargs.get('projection')
			

###===





class Report(object):

	def __init__(self, account = None, owner = None, category= None, *args, **kwargs):
		self.account = account
		self.owner = owner
		self.category = category
		self.args = args
		self.kwargs = kwargs

	def object_event(self, object):
		if not object.will_fire(*self.args, **self.kwargs):
			return
			
		if isinstance(object, Transaction):
			if self.account and (object.source.id != self.account and object.dest.id != self.account):
				return
			if self.category and object.category != self.category:
				return	
			self.transaction_event(object)
		elif isinstance(object, Statement):
			if self.owner and not (object.account.owner and object.account.owner in self.owner):
				return
			if self.account and self.account != object.account.id:
				return
			self.statement_event(object)
	
	def output(self):
		raise
	
	def transaction_event(self, transaction):
		pass
	
	def statement_event(self, statement):
		pass

class ValidateReport(Report):
	"""
		Validate Transaction History against statements.
	"""
		
	accts = {} #{'account' : (balance, date_last_statement)}
	
	
	def object_event(self, object):
		if isinstance(object, Transaction):
			if self.account and (object.source.id != self.account and object.dest.id != self.account):
				return
			if self.category and object.category != self.category:
				return	
			self.transaction_event(object)
		elif isinstance(object, Statement):
			if self.account and self.account != object.account.id:
				return
			self.statement_event(object)
	
	def transaction_event(self, transaction):
		if transaction.source.id in self.accts.keys():
			self.accts[transaction.source.id] = (self.accts[transaction.source.id][0] - transaction.amount, self.accts[transaction.source.id][1])
		else:
			print >> sys.stderr, 'Account %s has no initial statement (%s)' % (transaction.source.name, transaction.date.strftime('%Y-%m-%d'))
			self.accts[transaction.source.id] = (- transaction.amount, transaction.date) # Will invariably be wrong, but we warned them!
		if transaction.dest.id in self.accts.keys():
			self.accts[transaction.dest.id] = (self.accts[transaction.dest.id][0] + transaction.amount, self.accts[transaction.dest.id][1])
		else:
			print >> sys.stderr, 'Account %s has no initial statement (%s)' % (transaction.dest.name, transaction.date.strftime('%Y-%m-%d'))
			self.accts[transaction.dest.id] = (transaction.amount, transaction.date) # Will invariably be wrong, but we warned them!
	
	def statement_event(self, statement):
		if statement.account.id in self.accts.keys():
			if self.accts[statement.account.id][0] == statement.balance:
				pass #Ok!
			else:
				#Transactions don't balance!
				print >> sys.stderr, "Incomplete transactions for account %s in period %s -> %s (Statement : %s%s, Transactions: %s%s, Diff: %s%s) " % (
					statement.account.name,
					self.accts[statement.account.id][1].strftime('%Y-%m-%d'),
					statement.date.strftime('%Y-%m-%d'),
					statement.currency,
					statement.balance,
					statement.currency,
					self.accts[statement.account.id][0],
					statement.currency,
					statement.balance - self.accts[statement.account.id][0]
					)
			self.accts[statement.account.id] = (statement.balance, statement.date)
			
		else:
			self.accts[statement.account.id] = (statement.balance, statement.date)
		
	def output(self):
		return ""
	
		
class MonthlySummaryReport(Report):
	curr_month = 0
	out = []
	categories = {}
	accounts = []
	
	def __init__(self, *args, **kwargs):
		self.start_date = kwargs.get('start_date') and kwargs.pop('start_date') or None
		self.end_date = kwargs.get('end_date') and kwargs.pop('end_date') or None
		super(MonthlySummaryReport, self).__init__(args, kwargs)
	
	def object_event(self, object):
		if self.start_date and self.start_date >= object.date:
			return
	
		if object.date.month != self.curr_month:
			self.month_out()
			self.out.append(object.date.strftime("%B %Y"))
			
			self.curr_month = object.date.month
		super(MonthlySummaryReport, self).object_event(object)	
	
	def transaction_event(self, transaction):
		category = transaction.category or 'No Category'
		if transaction.dest.owner in self.owner['owner']:
			return
		
		if self.categories.get(category):
			if self.categories[category].get(transaction.currency):
				x = self.categories[category][transaction.currency]
				self.categories[category][transaction.currency] = (x[0] + transaction.amount, x[1] + transaction.amount)
			else:
				self.categories[category][transaction.currency] = (transaction.amount, transaction.amount)
		else:
			self.categories[category] = {transaction.currency : (transaction.amount, transaction.amount)}

	def month_out(self):
		"""
		Append months summary to out and reset for next month
		"""		
		categories_out = []
		for k, v in self.categories.iteritems():
			if not any([x[1] for x in v.values()]):
				continue
			values = ", ".join(['%s%.2f' % (currency, x[1]) for currency, x in v.iteritems() if x[1]])
			categories_out.append("\t%s: %s" % (k, values))
			for c, a in v.iteritems():
				self.categories[k][c]  = (v[c][0], 0)	
			
		self.out.append('\n'.join(categories_out))
		

	def statement_event(self, statement):
		pass

	def output(self):
		self.month_out()
		return '\n'.join(self.out)

class BalanceReport(Report):
	recent_statement = {}
	recent_transactions = {}

	def statement_event(self, statement):
		self.recent_statement[statement.account.id] = statement
		self.recent_transactions[statement.account.id] = []	

	def transaction_event(self, transaction):
		if transaction.source.id in self.recent_transactions:
			self.recent_transactions[transaction.source.id].append(transaction)
			
		if transaction.dest.id in self.recent_transactions:
			self.recent_transactions[transaction.dest.id].append(transaction)


	def output(self):
		acct_bals = []
		totals = {}
		
		for acct, statement in self.recent_statement.iteritems():
			balance = statement.balance
			dt = statement.date
			
			for i in self.recent_transactions[acct]:
				if i.source.id == acct:
					balance -= i.amount
				else:
					balance += i.amount
				
				dt = i.date
					
			account = accounts[acct]
			currency = account and account.currency or default_currency
			name = account and account.name or acct
			if balance == 0:
				continue
			
			
			acct_bals.append("%s% .2f   \t :%s (%s)" % (currency, balance, name, dt.date())) 
			
			if currency in totals:
				totals[currency] += balance
			else: 
				totals[currency] = balance

		acct_bals = "\n\t".join(acct_bals)	
		totals = ", ".join(['%s%s' % (k,v) for k,v in  totals.iteritems()])	
		out = "\nCurrent Balance: \n\t%s \n\t----\nTotal: %s" % (acct_bals, totals)
		return out	

class NetWorthGraph(Report):

	out = {}
	prev = {}
	
	def transaction_event(self, transaction):
		l = self.out.get(transaction.currency, {})
		
		k = transaction.date

		if l.get(k):
			w = l[k]
		else:
			w = self.prev.get(transaction.currency, 0)
		
		
		if transaction.source.owner in self.owner and transaction.dest.owner not in self.owner:
			w -= transaction.amount

		elif transaction.dest.owner in self.owner and transaction.source.owner not in self.owner:
			w += transaction.amount
		
		l[k] = w
		self.prev[transaction.currency] = w
		self.out[transaction.currency] = l
		
	def output(self):
	
		return "\n".join(sorted(["%s, %s" % x for x in self.out["$"].items()]))

class IncomeOutgoingReport(Report):
	incomings = {}
	outgoings = {}
		
	def transaction_event(self, transaction):
		curr_i = self.incomings.get(transaction.dest.id, 0)
		self.incomings[transaction.dest.id] = curr_i + transaction.amount
	
		curr_o = self.outgoings.get(transaction.source.id, 0)
		self.outgoings[transaction.source.id] = curr_o + transaction.amount	

	def output(self):
		out = ["-"*82, "| %s | %s | %s | %s |" %( 'Account'.center(25), 'Income'.center(15), 'Outgoing'.center(15), 'Balance'.center(15)), "-"*82]
		for acct in list(set(self.incomings.keys()).union(set(self.outgoings.keys()))):
			if accounts[acct].owner not in self.owner:
				continue
		
			out.append('| %s | %s | %s | %s |' % (
				accounts[acct].name[:25].ljust(25),
				accounts[acct].currency + str(self.incomings.get(acct, '-')).ljust(14),
				accounts[acct].currency + str(self.outgoings.get(acct, '-' )).ljust(14),
				accounts[acct].currency + str(self.incomings.get(acct, 0) - self.outgoings.get(acct, 0)).ljust(14)
				))
		return '\n'.join(out)
				



def run_reports():
	for obj in ordered_objects:
		for report in reports:
			report.object_event(obj[1])				

	for report in reports:
		print report.output()



def run():
	parser = optparse.OptionParser("usage: %prog [options] accounts", version='%prog 0.1')
	
	parser.add_option('-a', '--account', action = 'append', dest = 'accounts', help = 'Limit output to specified account(s)')
	parser.add_option('-o', '--owner', action = 'append', dest = 'owner', help = 'Limit output to specified owner(s)')
	parser.add_option('-p', '--projection', action = 'store_true', dest = 'projection', help = '')
	parser.add_option('-s', '--start_date', action = 'append', dest = 'start', help = 'Start reports after start date (YYYY-MM-DD)')
	
	rpts = []
	
	#==Reports
	def balance(*args):
		rpts.append(BalanceReport)	
	parser.add_option('-b', '--balance', action = 'callback', callback = balance, help = 'Print Balance information')
	
	def in_out(*args):
		rpts.append(IncomeOutgoingReport)
	parser.add_option('-i', '--inout', action = 'callback', callback = in_out, help = ' ')

	
	def monthly_summary(*args):
		rpts.append(MonthlySummaryReport)
	parser.add_option('-m', '--monthly_summary', action = 'callback', callback = monthly_summary, help = 'Summary of Month to Month Expenses')
	
	
	def net_worth_graph(*args):
		rpts.append(NetWorthGraph)
	parser.add_option('-n', '--net', action = 'callback', callback = net_worth_graph, help = '')

	
	def validate(*args):
		rpts.append(ValidateReport)
	parser.add_option('-v', '--validate', action = 'callback', callback = validate, help = 'Validate data is complete')
	


	(options, args) = parser.parse_args() 
	for i in rpts:	
		reports.append(
			i(
				start_date = options.start and datetime.datetime.strptime(options.start[0], '%Y-%m-%d'),
				 **options.__dict__
				)
			)


	for arg in args:
		execfile(arg)
	run_reports()



if __name__ == '__main__':
	run()