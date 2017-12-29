#!/bin/bash
# Send reports to all users with filled mail (from last midnight)

db="./brmbar.db"

usr=$(echo "SELECT name FROM users where mail!='';" | sqlite3 $db)

for u in $usr
do
	m=$(echo "SELECT mail FROM users where name='"$u"';" | sqlite3 $db)
	l=$(echo ".headers on
SELECT * FROM transhuman WHERE strftime('%Y-%m-%d',age)=date('now','localtime') AND user='$u';" | sqlite3 $db)

	if [ -n "$l" ]; then
		echo "$l" | mail -s "brmbar report" "$m"
	fi
done
