import mysql.connector
from mysql.connector import Error

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db"
)

mycursor = mydb.cursor()

sql = "SELECT * FROM tb_user"