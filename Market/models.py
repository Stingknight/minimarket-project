import sqlite3

def get_user_details():
    db=sqlite3.connect('marketdatabase.db')
    
    return db


