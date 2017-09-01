import xml.etree.ElementTree as ET
import mysql.connector
from mysql.connector import errorcode

tree = ET.parse('app/etc/local.xml')
root = tree.getroot()

## Xpath query
dbHost = root.find('./global/resources/default_setup/connection/host').text
dbUser = root.find('./global/resources/default_setup/connection/username').text
dbPass = root.find('./global/resources/default_setup/connection/password').text
dbName = root.find('./global/resources/default_setup/connection/dbname').text

try:
    conn = mysql.connector.connect(user=dbUser, password=dbPass, host=dbHost, database=dbName)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

cursor = conn.cursor(buffered=True)
query = "SHOW FULL PROCESSLIST;"
cursor.execute(query)

cursorWrite = conn.cursor(buffered=True)

for (Id, User, Host, db, Command, Time, State, Info) in cursor:
    if Time > 300 and Command == "Sleep" and State == "cleaned up":
        print("Process {Id} has been open for {Time} in - {State} state running - {Command}".format(**locals()))
        killQ = ("CALL mysql.rds_kill({});".format(Id))
        cursorWrite.execute(killQ)

conn.commit()
cursor.close()
cursorWrite.close()
conn.close()
