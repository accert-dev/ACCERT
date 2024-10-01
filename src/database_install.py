import configparser 
import mysql.connector
from mysql.connector import Error
import os
import re
from subprocess import Popen, PIPE


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

def executeScriptsFromFile(filename):
    # run mysql --user=root --password accert_db < accertdb.sql
    process = Popen(['mysql', '-h', 'localhost', '-u', 'root', '-p'],
                    stdout=PIPE, stdin=PIPE)
    # then run the source command
    output = process.communicate(str.encode('source ' + filename))[0]

    # output = process.communicate(str.encode('source ' + filename))[0]

def checkstoredProcedures(c):
    print("Checking stored procedures")
    c.execute("""SELECT  routine_schema,
                            routine_name,
                            routine_type
                    FROM information_schema.routines
                    WHERE routine_schema = 'accert_db'""")
    rows = c.fetchall()
    for row in rows:
        print(row)
    print("Above stored procedures have been created")

def main():
    connection = createConnection("localhost", "root", passwd)
    if connection is not None:
        c = connection.cursor()
        dbName='accert_db'
        if not checkDatabase(c, dbName):
            print ("Executing SQL script file: '{}.sql'".format(dbName))
            executeScriptsFromFile('accertdb.sql')
            if checkDatabase(c, dbName):
                print ("MySQL and its connection has been installed successfully")
            else:
                print ("MySQL and its connection failed to install")
        else:
            #check if user want to overwrite the database
            print("Database {} already exist".format(dbName))
            print("Do you want to overwrite it? (y/n)")
            answer = input()
            if answer == 'y':
                executeScriptsFromFile('accertdb.sql')
                connection.commit()
                if checkDatabase(c, dbName):
                    print ("MySQL and its connection has been installed successfully")
                    checkstoredProcedures(c)
                else:
                    print ("MySQL and its connection failed to install")
    else:
        print("No connection found")
    return

if __name__ == '__main__':
    main()

