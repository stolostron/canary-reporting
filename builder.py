import json
import datetime
from os.path import join
import re
import os
import sys
import pymysql
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize


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


#inintalize test database
def populate_db(json_file):
    c.execute("CREATE TABLE IF NOT EXISTS snapshots_staging (id text, time datetime, acm_release varchar(10), verification_level text, \
        test_total int, passes integer, fails int, skips int, ignored int, hub_platform varchar(10), hub_version varchar(10), \
        stage varchar(20), branch varchar(20), issue_url text)")
    c.execute("CREATE TABLE IF NOT EXISTS squad_tests_staging (id text, time datetime, acm_release varchar(10), verification_level text, \
        `squad(s)` varchar(50), testsuite varchar(200), passes int, fails int, skips int, ignored int, severity text, priority text, \
        hub_platform varchar(10), hub_version varchar(10), stage varchar(20), branch varchar(20), issue_url text)")
    data = json_file.read()
    d = json.loads(data)
    date_time_str= re.findall("\D-([0-9].*)", d['snapshot'])[0]
    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d-%H-%M-%S')
    release = re.findall("([0-9].*)-\D", d['snapshot'])[0]
    if 'stage' not in d:
        d['stage'] = 'results'
    if 'branch' not in d:
        y_release = re.findall("[0-9]\.[0-9]+", release)[0]
        d['branch'] = f"{y_release}-integration"
    if 'issue_url' not in d:
        if d['failed'] == 0:
            d['issue_url'] = ''
        else:
            d['issue_url'] = 'https://github.com/stolostron/backlog/issues'
    c.execute("SELECT * FROM snapshots_staging WHERE id=%s AND acm_release=%s AND hub_platform=%s", (d['snapshot'], release, d['hub_platform']))
    if c.fetchone() is None:
        add_snapshot_to_db(d, date_time_obj, release, d['verification_level'])
    c.execute("SELECT * FROM squad_tests_staging WHERE id=%s AND acm_release=%s AND hub_platform=%s", (d['snapshot'], release, d['hub_platform']))
    if c.fetchone() is None:
        add_tests_to_db(d, date_time_obj, release, d['verification_level'])
    conn.commit()

#function to read in json to database
def add_snapshot_to_db(json_data, date, release, verification_level):
    c.execute("INSERT into snapshots_staging values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  [json_data['snapshot'], date, release, verification_level, 
                   json_data['total'], json_data['passed'], json_data['failed'], json_data['skipped'], json_data['ignored'], json_data['hub_platform'], json_data['hub_version'], json_data['stage'], json_data['branch'], json_data['issue_url']])

def add_tests_to_db(json_data, date, release, verification_level):
    squad_test_df = process_test_results(json_data)
    squad_test_df['hub_platform'] = json_data['hub_platform']
    squad_test_df['hub_version'] = json_data['hub_version']
    squad_test_df['snapshot'] = json_data['snapshot']
    squad_test_df['stage'] = json_data['stage']
    squad_test_df['branch'] = json_data['branch']
    squad_test_df['issue_url'] = json_data['issue_url']
    squad_idx = squad_test_df.columns.get_loc("squad(s)")
    pass_idx = squad_test_df.columns.get_loc("passes")
    fail_idx = squad_test_df.columns.get_loc("fails")
    skip_idx = squad_test_df.columns.get_loc("skips")
    ignore_idx = squad_test_df.columns.get_loc("ignored")
    hub_p_idx = squad_test_df.columns.get_loc("hub_platform")
    hub_v_idx = squad_test_df.columns.get_loc("hub_version")
    snapshot_idx = squad_test_df.columns.get_loc("snapshot")
    testsuite_idx = squad_test_df.columns.get_loc("testsuite")
    severity_idx = squad_test_df.columns.get_loc("severity")
    priority_idx = squad_test_df.columns.get_loc("priority")
    stage_idx = squad_test_df.columns.get_loc("stage")
    branch_idx = squad_test_df.columns.get_loc("branch")
    issue_idx = squad_test_df.columns.get_loc("issue_url")
    for row in squad_test_df.itertuples():
        c.execute("INSERT into squad_tests_staging values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                 [row[snapshot_idx+1], date, release, verification_level, row[squad_idx+1], row[testsuite_idx+1], row[pass_idx+1], row[fail_idx+1], 
                  row[skip_idx+1], row[ignore_idx+1], row[severity_idx+1], row[priority_idx+1], row[hub_p_idx+1], row[hub_v_idx+1], row[stage_idx+1], row[branch_idx+1], row[issue_idx+1]])
    
def process_test_results(data):
    json_results = data['results']
    df = pd.DataFrame.from_records(json_results)
    normalized_metadata = pd.json_normalize(df.metadata)
    if 'squad(s)' not in normalized_metadata:
        normalized_metadata['squad(s)'] = 'Unlabelled'
    if 'severity' not in normalized_metadata:
        normalized_metadata['severity']='Severity 1 - Urgent'
    if 'priority' not in normalized_metadata:
        normalized_metadata['priority']='Priority/P1'
    joined = df.join(normalized_metadata, how="left")
    joined.drop(['metadata'], axis=1, inplace=True)
    joined.rename(columns={"squad(s)":"squads"}, inplace=True)
    if "db_builder" in os.environ:
        joined["squads"] = joined["squads"].apply(lambda x: str(x).split(','))
    #print(joined)
    joined["squads"] = joined.apply(lambda x: [{"squads": i} for i in x.squads], axis=1)
    joined = (pd.concat({i: pd.json_normalize(x) for i, x in joined.pop('squads').items()})
                .reset_index(level=1, drop=True)
                .join(joined)
                .reset_index(drop=True))
    joined.rename(columns={"squads":"squad(s)"}, inplace=True)
    joined["squad(s)"].replace('nan', "Unlabelled", inplace=True)
    joined["squad(s)"].replace(np.nan, "Unlabelled", inplace=True)
    ignore_df = status_filter(joined, 'ignored', 'ignored')
    pass_df = status_filter(joined, 'passed', 'passes')
    fail_df = status_filter(joined, 'failed', 'fails')
    skip_df = status_filter(joined, 'skipped', 'skips')
    result_df = pass_df.merge(fail_df, how='outer').merge(skip_df, how='outer').merge(ignore_df, how = 'outer')
    result_df.fillna(0, inplace=True)
    return result_df

def status_filter(dataframe, filter_str, column_name):
    result_df = dataframe[(dataframe.state == filter_str)].groupby(['squad(s)', 'testsuite', 'severity', 'priority'], dropna = False, as_index = False).count()
    result_df['squad(s)'] = result_df['squad(s)'].fillna('Unlabelled')
    result_df['severity'] = result_df['severity'].fillna('Severity 1 - Urgent')
    result_df['priority'] = result_df['priority'].fillna('Priority/P1')
    result_df = result_df[['squad(s)', 'testsuite', 'state', 'severity', 'priority']]
    result_df.rename(columns={'state': column_name}, inplace = True)
    result_df[column_name] = result_df[column_name].astype('Int64')
    return result_df

#reading out of my local json files
if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        connect_to_db()
        populate_db(f)
        f.close()
        conn.close()