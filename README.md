=== BRMBARSAP ===

== INSTALLATION ==
0) Install required packages:
	sqlite3
	python
	pyqt

1) Create sqlite3 database "brmbar.db" in the brmbarSAP directory:
	$ sqlite3 ./brmbar.db < ./schema.sql
	$ sqlite3 ./brmbar.db < ./stock.sql
	$ sqlite3 ./brmbar.db < ./users.sql


== MIGRATION FROM brmbar3 ==

1) Export users from brmbar3 (spaghetti oneliner):
	$ echo "SELECT name,crbalance FROM account_balances where acctype='debt';" | psql brmbar | head -n -2 | tail -n +3 | sed -r -e 's/[\ ]*\|[\ ]*/,/g' | sed -e "s/[a-zA-Z0-9-]*,/\'&\'/g" | sed -e "s/''//g" | sed -e "s/'-'/-/g" | sed -e "s/,'/',/g" | sed -e 's/^/INSERT INTO users VALUES (NULL,/g' | sed -e "s/$/,NULL,'cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e','');/g" | sqlite3 ./brmbar.db

2) Fixup:
 $ sqlite3 ./brmbar.db "UPDATE users SET code=name;"

3) Stock migration is not possible (yet) - aspon se udela inventura

== EXECUTION ==

1) Run "$ python ./brmbarsap.py"

== DESCRIPTION ==

DB tables:
	users - Users defined in the system (some internal only)
	stock - Stuff to be bought (some internal only)
	barcodes - Barcodes assigned to particular stuff. Each item can have multiple barcodes assigned (1-n relation).
		NOTE: Users have their barcodes directly in "users" table (1-1 relation).
	transactions - Log of events (changes in user's credit, stock replenishment, bought stuff)
	transhuman - Human readable view of "transactions" table
	rechuman - Human readable view of "receipts" table

Files:
	README.brm - Read it for more information

	brmbarsap.py - Main application
	brmstock.py - List of items in the stock
	brmstockedit.py - Stock editor
	brmuser.py - List of users
	brmuseredit.py - User editor
	brmtrans.py - Transfer credit from one user to another - easier way of negative and positive charge
	brmdon.py - Donate money to brmlab
	brmbuy.py - Consume, then die
	brmrec.py - Receipts
	fce.py - Common functions and settings
	brmbar.db - sqlite3 database
	/dev/shm/brmbarsap_msg - Temporary file for internal communication
	schema.sql - CREATE TABLE statements
	stock.sql - Default stock entries (internal ONLY)
	users.sql - Default user entries (internal ONLY)
	brmlab.svg - The logo (c)(r)(tm)(brm)
	
Scripts around:
	userlog.sh USERNAME - Print out daily transaction log for given user
	reports.sh - Send daily report to users which have set the email address (add it to your daily-midnight CRON)
	stats.sh - Display statistics

== MICS ==

Backup:
	Just copy out the brmbar.db database
Debt limit:
	Users can be limited NOT to buy/transfer/donate if their credit is lower than BUY_LIMIT constant (set in fce.py)
	To disable the limit, set BUY_LIMIT to insanly low value (like -999999)
	Note: negative value means that the user can have DEBT up to that value
Password protection:
	Users can set password to prevent unauthorized transactions
	To clear password, store value of NULL512 (see fce.py) to appropriate user in "users" table
Negative sell price:
	Negative price of items can NOT be set in GUI due to its "accidental enrichment" potential
	You can set it manually in the "stock" table
Receipts:
	Receipts can be made ONLY if profit is bigger than sum of user's credit to avoid "run on brmbar" situation.
	The value of the receipt is added to the responsible user's credit
Overflow accounts:
	Overflow accounts are meant for cash holders and basicaly always have negative credit (as they withdrawn money from brmbar).
	Such users can withdrawn regardless of BUY_LIMIT and are listed in "brmedituser.py" in the middle of fce "brmStoreUser()".
	Sum(-credit) on such accounts is equal to brmbar's disponible money.
Reports:
	Users can set an email to which daily reports of their transactions will be sent (add reports.sh to your CRON)

== TODO ==
	Scripts around (IRC yelling, backups, ...)
