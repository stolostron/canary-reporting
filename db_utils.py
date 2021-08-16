import json
import datetime
import os
import sys
import pymysql

TABLE_NAME = "canary_issues"
c = None
conn = None

def env_set(env_var, default):
    if env_var in os.environ:
        return os.environ[env_var]
    elif os.path.exists(env_var) and os.path.getsize(env_var) > 0:
        with open(env_var, 'r') as env_file:
            var = env_file.read().strip()
            env_file.close()
        return var
    else:
        return default

def connect_to_db():
    db_user = env_set('db_user', 'root')
    db_host = env_set('db_host', 'localhost')
    db_pass = env_set('db_pass', None)
    db_port = env_set('db_port', 3306)
    global conn, c
    conn = pymysql.connect(host=db_host,user=db_user,db="tests",password=db_pass,port=int(db_port))
    c = conn.cursor()
    sql = "CREATE TABLE IF NOT EXISTS {} (\
        id int NOT NULL AUTO_INCREMENT, \
        github_id text, \
        status text, \
        severity text, \
        priority text, \
        date datetime, \
        squad_tag text, \
        payload text, \
        dup_count int, \
        PRIMARY KEY (id))".format(TABLE_NAME)
    c.execute(sql)

def payload_exists(payload_string):
    payload = "{}".format(payload_string)
    payload = payload.replace('"', '""')

    sql = "SELECT github_id FROM {} where payload = \"{}\" AND status = \"open\";".format(TABLE_NAME,payload)
    num_rows = c.execute(sql)
    fetch = c.fetchone()
    if (num_rows > 0):
        return(list(fetch)[0])
    else:
        return None

def bump_dup_count(github_id):
    global conn, c, TABLE_NAME
    sql = "UPDATE {} SET dup_count = dup_count + 1 WHERE github_id = \"{}\";".format(TABLE_NAME, github_id)
    return_code = c.execute(sql)
    conn.commit()
    return return_code

def update_status(github_id, status):
    global conn, c, TABLE_NAME
    sql = "UPDATE {} SET status = \"{}\" WHERE github_id = \"{}\";".format(TABLE_NAME, github_id, status)
    return_code = c.execute(sql)
    conn.commit()
    return return_code

def insert_canary_issue(issue):
    global conn, c, TABLE_NAME
    payload_string = issue['payload']
    payload = "{}".format(payload_string)
    payload = payload.replace('"', '""')
    sql = "INSERT into {} values ({}, {}, {}, {}, {}, {}, {}, \"{}\", {})".format(TABLE_NAME, \
        0, \
        json.dumps(issue['github_id']), \
        json.dumps(issue['status']), \
        json.dumps(issue['severity']), \
        json.dumps(issue['priority']), \
        json.dumps(issue['date']), \
        json.dumps(issue['squad_tag']), \
        payload, \
        0 )
    return_code = c.execute(sql)
    conn.commit()
    return return_code

def disconnect_from_db():
    conn.commit()
    conn.close()
