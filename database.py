import sqlite3
conn = sqlite3.connect('HOPE_db.sqlite')
cur = conn.cursor()

   
#cur.execute('DROP TABLE IF EXISTS files;');
#cur.execute('CREATE TABLE files (\
#           id INTEGER,\
#            filename VARCHAR ,\
#            fileid VARCHAR ,\
#            filepath VARCHAR ,\
#            PRIMARY KEY (id));')
#conn.commit()
    

def insertRecords(filename,fileid, filepath):
    conn = sqlite3.connect('HOPE_db.sqlite')
    cur = conn.cursor()
    filepath = filepath.replace('\\', '//')
    cur.execute('INSERT INTO files (filename, fileid, filepath) VALUES (?, ?, ?)',
                (filename, fileid, filepath))
    conn.commit()
    return "record inserted"

def fetchRecords():
    conn = sqlite3.connect('HOPE_db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT filename, fileid, filepath FROM files')    
    return cur.fetchall()


