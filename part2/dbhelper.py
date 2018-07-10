import sqlite3


class DBHelper:

    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS rules (description text, owner text)"
        ruleidx = "CREATE INDEX IF NOT EXISTS ruleIndex ON rules (description ASC)"
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON rules (owner ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(ruleidx)
        self.conn.execute(ownidx)

        navtblstmt = "CREATE TABLE IF NOT EXISTS nav (description text, owner text)"
        navidx = "CREATE INDEX IF NOT EXISTS navIndex ON nav (description ASC)"
        navownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON nav (owner ASC)"
        self.conn.execute(navtblstmt)
        self.conn.execute(navidx)
        self.conn.execute(navownidx)

        self.conn.commit()

    def add_rule(self, rule_text, owner):
        stmt = "INSERT INTO rules (description, owner) VALUES (?, ?)"
        args = (rule_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_rule(self, rule_text, owner):
        stmt = "DELETE FROM rules WHERE description = (?) AND owner = (?)"
        args = (rule_text, owner )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_rules(self, owner):
        stmt = "SELECT description FROM rules WHERE owner = (?)"
        args = (owner, )
        return [x[0] for x in self.conn.execute(stmt, args)]

    def get_nav(self, owner):
        stmt = "SELECT description FROM nav WHERE owner = (?)"
        args = (owner, )
        return [x[0] for x in self.conn.execute(stmt, args)]
