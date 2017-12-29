CREATE TABLE stock (
  id        INTEGER PRIMARY KEY ON CONFLICT IGNORE AUTOINCREMENT,
  name      TEXT    DEFAULT 'Junkfood',
  quan      INTEGER DEFAULT 0,
  buyprice  FLOAT   DEFAULT 0,
  sellprice FLOAT   DEFAULT 1);

CREATE TABLE users (
  id   INTEGER PRIMARY KEY ON CONFLICT IGNORE AUTOINCREMENT,
  name TEXT    NOT NULL DEFAULT 'Muaddib',
  cash REAL    DEFAULT 0,
  code INTEGER DEFAULT 0,
  pass TEXT    DEFAULT NULL,
	mail TEXT    DEFAULT NULL);

CREATE TABLE transactions (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  age    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  who    INTEGER DEFAULT 0,
  what   INTEGER DEFAULT 0,
  amount INTEGER DEFAULT 0,
  cash   INTEGER DEFAULT 0,
  profit INTEGER DEFAULT 0);

CREATE TABLE barcodes (
  id    INTEGER PRIMARY KEY ON CONFLICT IGNORE AUTOINCREMENT,
  stock INTEGER DEFAULT 0,
  code  INTEGER DEFAULT 0);

CREATE TABLE receipts (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  tid     INTEGER DEFAULT 0,
  comment TEXT DEFAULT NULL);

CREATE VIEW transhuman AS SELECT transactions.id AS tid,age,users.name AS user,stock.name AS stuff,amount,transactions.cash AS price,profit FROM transactions,users,stock WHERE transactions.who=users.id AND transactions.what=stock.id ORDER BY transactions.id DESC;

CREATE VIEW rechuman AS SELECT receipts.id AS rid, transactions.age AS happened, transactions.cash AS price, users.name AS responsible, comment FROM transactions,users,receipts WHERE transactions.who=users.id AND receipts.tid=transactions.id ORDER BY happened DESC;


