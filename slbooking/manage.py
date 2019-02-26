import sqlite3
import random
import os.path

DB_NAME = 'database.db'

def db(func):
    def func_wrapper(*args, **kw):
        db = sqlite3.connect(DB_NAME)
        c = db.cursor()
        res = func(c, *args, **kw)
        db.commit()
        db.close()
        return res
return func_wrapper

@db
def load_logged_in_admin_id(c, admin_id):
	c.execute('SELECT * FROM admin WHERE id = ?', (admin_id,))
	return c.lastrowid


