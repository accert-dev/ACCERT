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
    # execute the sql script file
    # filename: the name of the sql script file
    # c: the cursor of the connection
    # return: None
    curPath = os.path.dirname(os.path.abspath(__file__))
    sqlPath = os.path.join(curPath, filename)
    f = open(sqlPath, 'r')
    sqlFile = f.read()
    f.close()
    def extract_blocks_and_other_lines(content):
        # split the sqlCommands into database creation and procedure creation
        # procedure commands start with 'CREATE DEFINER' and end with 'END ;'
        # all the middle lines between 'CREATE DEFINER' and 'END' are procedure commands
        # the other lines are database creation commands
        # extract the procedure commands first
        # Use regular expressions to find the blocks
        pattern = r'CREATE DEFINER.*?END ;'
        procedureCommands = re.findall(pattern, content, re.DOTALL)
        return procedureCommands
    procedureCommands = extract_blocks_and_other_lines(sqlFile)
    
    sqlCommands = sqlFile.split(';')
    for command in sqlCommands:
        try:
            c.execute(command)
        except Error as e:
            continue
    for command in procedureCommands:
        try:
            c.execute(command)
        except Error as e:
            print(f"The error '{e}' occurred at command:")
    return None

def main():
    connection = createConnection("localhost", "root", passwd)
    if connection is not None:
        c = connection.cursor()
        dbName='accert_db'
        if not checkDatabase(c, dbName):
            print ("Executing SQL script file: '{}.sql'".format(dbName))
            executeScriptsFromFile('accertdb.sql',c)
            connection.commit()
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
                executeScriptsFromFile('accertdb.sql',c)
                connection.commit()
                if checkDatabase(c, dbName):
                    print ("MySQL and its connection has been installed successfully")
                else:
                    print ("MySQL and its connection failed to install")
    else:
        print("No connection found")
    return

if __name__ == '__main__':
    main()

