import hostlist
import io
from shutil import copyfile
import subprocess
from pathlib import Path
import os
import genders
import mysql.connector
from mysql.connector import Error
import argparse
import loaddata 
import setP

# Connects to the genders database.
def connectDatabase(password):
    #block tests if gender database exists already
    try:
        try:
            with open('passW.txt') as f:
                password = [line.rstrip('\n') for line in f][0]
        except Error as e:
            print(e)
            print("Please add your password using --password.")
        config = {
            'user': 'root',
            'password': f'{password}',
            'host': 'localhost',
            'database': 'gender'
        }
        mydb = mysql.connector.connect(**config)
        if mydb.is_connected():
            cursor = mydb.cursor(buffered=True,dictionary=True)
    #if it does not exists runs create.sql script
    except Error as e:
        print(e)
        config = {
            'user': 'root',
            'password': f'{password}',
            'host': 'localhost'
        }
        mydb = mysql.connector.connect(**config)
        cursor = mydb.cursor(buffered=True , dictionary=True)
        # Open and read the file as a single buffer
        fd = open('create.sql', 'r')
        sqlFile = fd.read()
        fd.close()
        sqlCommands = sqlFile.split(';')
        # Execute every command from the input file
        for command in sqlCommands:
            # This will skip and report errors
            try:
                cursor.execute(command)
            except Error as e:
                print ("Command skipped: ", e)
    return mydb

def findNodes(mydb,gender_namei):
    sql = "SELECT DISTINCT n.node_name FROM NODE n JOIN CONFIGURATION c WHERE (n.node_name = c.node_name AND c.gender_name = %s )"
    val = (gender_namei,)
    cur = mydb.cursor(buffered=True, dictionary=True)
    cur.execute(sql,val)
    records = cur.fetchall()
    return records

def getVals(mydb,gender_name):
    gender_name = str(gender_name)
    sql = "SELECT val,node_name FROM CONFIGURATION WHERE gender_name = %s"
    cur = mydb.cursor(buffered=True,dictionary=True)
    val = (gender_name,)
    cur.execute(sql,val)
    records = cur.fetchall()
    return records

def getUVals(mydb,gender_name):
    gender_name = str(gender_name)
    sql = "SELECT DISTINCT val FROM CONFIGURATION WHERE gender_name = %s"
    cur = mydb.cursor(buffered=True,dictionary=True)
    val = (gender_name,)
    cur.execute(sql,val)
    records = cur.fetchall()
    return records

def getValinNode(mydb,gender_name,node_name):
    sql = "SELECT val FROM CONFIGURATION WHERE gender_name = %s AND node_name = %s"
    val = (gender_name,node_name)
    cur = mydb.cursor(buffered=True,dictionary=True)
    cur.execute(sql,val,)
    records = cur.fetchall()
    return records

def findNodes(mydb,gender_namei):
    sql = "SELECT DISTINCT n.node_name FROM NODE n JOIN CONFIGURATION c WHERE (n.node_name = c.node_name AND c.gender_name = %s )"
    val = (gender_namei,)
    cur = mydb.cursor(buffered=True, dictionary=True)
    cur.execute(sql,val)
    records = cur.fetchall()
    return records

def findGenders(mydb,node_namei):
    sql = "SELECT DISTINCT g.gender_name FROM GENDER g JOIN CONFIGURATION c WHERE (g.gender_name = c.gender_name AND c.node_name = %s)"
    val = (node_namei,)
    cur = mydb.cursor(buffered=True, dictionary=True)
    cur.execute(sql,val)
    records = cur.fetchall()
    return records

def allGenders(mydb):
    sql = "SELECT DISTINCT gender_name FROM GENDER"
    cur = mydb.cursor(buffered=True, dictionary=True)
    cur.execute(sql)
    records = cur.fetchall()
    return records
def main():
    mydb = connectDatabase()
    parser = argparse.ArgumentParser(description='Connect with database')
    parser.add_argument('--password', action = 'store_true')
    parser.add_argument('--load', action="store_true")
    parser.add_argument('-dd',help='drops entire database',action='store_true',dest='dd')

    parser.add_argument('-q', nargs='*',help='prints list of nodes having the specified attribute in host range',action='store', dest='hostlist')

    parser.add_argument('-Q',nargs='*',help='returns 0 if attribute exists in nide else 1, if no node specified checks entire database',action='store')

    parser.add_argument('-c',nargs='*',help='prints list of nodes having specified attribute in comma seperated format',action='store',dest='comma')
    
    parser.add_argument('-n',nargs=1,help='prints list of nodes having specified attribute in newline separated list',action='store',dest='newline')
    
    parser.add_argument('-s',nargs=1,help='prints list of nodes having specified attribute in space separated list',action='store',dest='space')
    parser.add_argument('-v',nargs=1,help='outputs values associated with gender on a particular node',action='store')
    
    parser.add_argument('-vv',nargs=1,help='outputs values associated with gender and with node listed',action='store',dest='valuesWnodes')
    
    parser.add_argument('-l',nargs='*',help='list of attributes for a particular node, if no node all attributes in database')
    
    parser.add_argument('-V',nargs='*', help='outputs all values associated with gender, if U is specified only unqiue values')
    
    parser.add_argument('-U',help='V will only output unique values')
    
    parser.add_argument('-X',nargs='*',help='exlcude node from query')
    

    args = parser.parse_args()	

    if args.password != None:
        setP.store()  
        #finds nodes w specified gender in hostlist format
    if args.load:
        loaddata.main(mydb)
    if results.hostlist != None:
        finLi = []
        records = []
        prev = False
        hosts = ''
        clusterN = ""
        if results.X != None:
            record = findNodes(mydb,str(results.hostlist[0]))
            for row in record:
                if row['node_name'] != results.X[0]:
                    records.append(row)
                else:
                    records = findNodes(mydb,str(results.hostlist[0]))
                    if (len(records)) > 0:
                        cluster0 = records[0]
                        cluster0 = cluster0['node_name']
                        cluster0 = cluster0[:-1]
                        for row in records:
                            clusterT = row['node_name']
                            clusterT = clusterT[:-1]
                            if cluster0 == clusterT:
                                hosts += ( row['node_name'] + ',')
                                prev = True
                            elif cluster0 != clusterT and prev == True:
                                finLi.append(hosts)
                                hosts = ''
                                hosts += ( row['node_name'] + ',')
                                prev = False
                            elif cluster0 != clusterT and prev == False:
                                hosts = ''
                                hosts += ( row['node_name'] + ',')
                                prev = True
                                cluster0 = clusterT
                                finLi.append(hosts)
                        for y in finLi:
                            y = y[:-1]
                            y = hostlist.compress_range(y)
                            print(y, end= " ")
    if results.comma != None:
        finLi = []

        else:
            records = findNodes(mydb,str(results.comma[0]))
            if results.X != None:
                for row in records:
                    if row['node_name'] != results.X[0]:
                        finLi.append(row['node_name'])
                    else:
                        for row in records:
                            finLi.append(row['node_name'])
                    print(*finLi,sep=", ")

    if results.newline != None:
        records = findNodes(mydb,str(results.newline[0]))
            if results.X != None:
                for row in records:
                    if row['node_name'] != results.X[0]:
                        print(row['node_name'])

                    else:
                        for row in records:
                            print(row['node_name'])

    if results.space != None:
        records = findNodes(mydb,str(results.space[0]))
            if results.X != None:
                for row in records:
                    if row['node_name'] != results.X[0]:
                        print(row['node_name'],end=" ")
            else:
                for row in records:
                    print(row['node_name'],end=" ")

    if results.V != None:

        if len(results.V) == 0:
            if results.U != None:
                records = getUVals(mydb,results.U)
                for row in records:
                    print(row['val'])

        if len(results.V) == 1:
            records = getVals(mydb,results.V[0])
            for row in records:
                print(row['val'])

    if results.v != None:
        records = getValinNode(mydb,results.v[1],results.v[0])
        for row in records:
            print(row['val'])

    if results.Q != None:
        if len(results.Q) == 1:
            records = findNodes(mydb,str(results.Q[0]))
            if len(records) > 0:
                sys.exit(0)
            else:
                sys.exit(1)
        if len(results.Q) == 2:

            records =  findNodes(mydb,results.Q[1])
            for rec in records:

                if rec['node_name'] == results.Q[0]:
                    sys.exit(0)
            sys.exit(1)
    if results.valuesWnodes != None:
        records = getVals(mydb,*results.valuesWnodes)
        for row in records:
            print(row['node_name']," ",row['val'])

            if results.l != None:
                if len(results.l) > 0:
                    findGenders(mydb,*results.l)
                else:
                    records = allGenders(mydb)
                    for row in records:
                        print(row['gender_name'])

if __name__ == "__main__":
    main()
