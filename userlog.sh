#!/bin/bash
# Print out the log for specified user from last midnight

echo ".headers on
SELECT * FROM transhuman WHERE strftime('%Y-%m-%d',age)=date('now','localtime') AND user='$1';" | sqlite3 ./brmbar.db
