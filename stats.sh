#!/bin/bash
# Display various stats from brmbar

DB="./brmbar.db"

overflow=$(echo "SELECT sum(cash)*(-1) FROM users WHERE name like '%overflow';" | sqlite3 $DB)
cash=$(echo "SELECT (SELECT sum(profit) FROM transactions)-($overflow);" | sqlite3 $DB)
inv=$(echo "SELECT sum(quan*buyprice) FROM stock;" | sqlite3 $DB)
mate=$(echo "SELECT sum(amount) FROM transhuman WHERE strftime('%Y-%m-%d',age)=date('now','localtime') AND (stuff like '%mate%' OR stuff like '%Mate%');" | sqlite3 $DB)

echo "Overflow:  $overflow"
echo "Cash:      $cash"
echo "Inventory: $inv"
echo "Clubmate sold today: $mate bottles"
