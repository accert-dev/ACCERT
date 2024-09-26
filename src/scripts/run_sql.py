# if user_defined.sql is present
# then connect to the database and execute the sql

import os
import sys
import mysql.connector
import configparser




def execute_sql_file(conn, sql_file_path):
    """
    Connects to the MySQL database 
    """
    try:
        # Establish the connection
        connection = conn
        
        if connection.is_connected():
            print("Connected to MySQL Server")
            cursor = connection.cursor()
            
            # Read the SQL file
            with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
                sql_commands = sql_file.read()
            
            # Split the SQL commands by ';' to handle multiple statements
            # Note: This simple split may not work for complex SQL files with stored procedures, etc.
            sql_commands = sql_commands.strip().split(';')
            
            for command in sql_commands:
                command = command.strip()
                if command:
                    try:
                        cursor.execute(command)
                        # If the command is a CREATE or INSERT, commit the changes
                        if command.upper().startswith('CREATE') or command.upper().startswith('INSERT') or command.upper().startswith('DROP'):
                            connection.commit()
                        print(f"Executed: {command.splitlines()[0]}...")
                    except Error as e:
                        print(f"Error executing command: {command.splitlines()[0]}...\nError: {e}")
            
            print("All commands executed successfully.")
    
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection is closed.")


def main():
    
    sql_file = "user_defined.sql"
    sql_file_path = os.path.join(os.getcwd(), sql_file)
    print(f"SQL file path: {sql_file_path}")
    # current folder is the folder where this script is located
    current_folder = os.path.dirname(os.path.abspath(__file__))
    code_folder = os.path.dirname(current_folder)
    initfile = os.path.join(code_folder, 'install.conf')
    ins = configparser.ConfigParser()
    ins.read(initfile)
    passwd = ins.get("INSTALL","PASSWD")

    conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=passwd,
    database="accert_db",
    auth_plugin="mysql_native_password"
    )
    # conn.commit()
    # NOTE: cursor is a class that instantiates objects that can execute MySQL statements
    # only commit when you are sure that the transaction is complete
    # c = conn.cursor()
    execute_sql_file(conn, sql_file_path)



if __name__ == '__main__':
    main()


