import configparser 
import mysql.connector
from mysql.connector import Error
import os
import re


thisfolder = os.path.dirname(os.path.abspath(__file__))
initfile = os.path.join(thisfolder, 'install.conf')
ins = configparser.ConfigParser()
ins.read(initfile)
passwd = ins.get("INSTALL","PASSWD")


def createConnection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            auth_plugin='mysql_native_password'
        )
        print("Connection to MySQL")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def checkDatabase(cursor, databaseName):
    cursor.execute("show databases;")
    if (databaseName,) in cursor.fetchall():
        print('Database {} exist'.format(databaseName))
        return True
    else:
        print('Database {} do not exist'.format(databaseName))
        return False

def executeScriptsFromFile(filename,c):
    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlCommands = sqlFile.split(';')
    for command in sqlCommands:
        try:
            c.execute(command)
        except OperationalError:
            print("Command skipped: ",command)

def main():
    connection = createConnection("localhost", "root", passwd)
    if connection is not None:
        c = connection.cursor()
        dbName='accert_db'
        if not checkDatabase(c, dbName):
            print ("Executing SQL script file: '{}.sql'".format(dbName))
            executeScriptsFromFile('accertdb.sql',c)
            connection.commit()
            print ("MySQL and its connection has been installed successfully")
    else:
        print("No connection found")
    return

if __name__ == '__main__':
    main()

