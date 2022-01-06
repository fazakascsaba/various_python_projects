import cx_Oracle
import yaml
from datetime import datetime, timedelta

def load_yaml_file(filename):
  try:
    with open(filename,'r') as stream:
      return yaml.safe_load(stream)
  except Exception as e:
    return
def connect_to_database(target):
  config_file='conn.yaml'
  conn_string=load_yaml_file(config_file)[target]
  user = conn_string['user']
  pwd = conn_string['pwd']
  host = conn_string['host']
  service_name = conn_string['service_name']
  portno = conn_string['portno']
  sid = conn_string['sid']

  try:
    if sid:
      dsn_tns = cx_Oracle.makedsn(host, portno, sid) 
      conn = cx_Oracle.connect(user=user, password=pwd, dsn=dsn_tns) 
    else:
      conn = cx_Oracle.connect(user, pwd, '{}:{}/{}'.format(host,portno,service_name))
    return conn
  except:
    print('connection failed')
    exit()

######################### INPUT START ##########################
sql='''
  select CASE v$sqltext.piece WHEN 0 THEN'alter system kill session \'\'\'||sid||','||serial#||\'\'\' immediate;' ELSE '-' END, 
  username, seconds_in_wait/60 as mint,
  v$sqltext.sql_id, v$sqltext.piece, v$sqltext.sql_text
  from v$session 
  inner join v$sqltext on v$sqltext.sql_id = v$session.sql_id
  where osuser = '{}' and v$session.sql_id is not Null
  order by v$sqltext.sql_id, v$sqltext.piece,v$sqltext.sql_text
'''.format('fazakas')
purpose='select' # purpose | update
######################### INPUT END ############################

''' 
oci_ps_prod_bo
oci_ps_prod_fe
onprem_prod_bo
onprem_prod_fe
oci_ps_uat_bo
'''

conn=connect_to_database('oci_ps_uat_bo')
c = conn.cursor()

#ui1=input('do you want to execute above sql? y/n: ')
if True:
  c.execute(sql)
  if purpose=='update':
    ui2=input('do you want to commit? y/n: ')
    if ui2=='y':
      conn.commit()
    else:
      conn.rollback()
  elif purpose=='select':
    result_set=c.fetchall()
    if result_set:
      print('{} + {} + {} + {} + {} + {}'.format('-'*50,'-'*15,'-'*25,'-'*20,'-'*5,'-'*64))
      print('{} | {} | {} | {} | {} | {}'.format('session kill cmd'.ljust(50,' '),'user'.ljust(15,' '),'time_in_wait'.ljust(25,' '),'sql_id'.ljust(20,' '),'piece'.ljust(4,' '),'sql'.ljust(64,' ')))
      print('{} + {} + {} + {} + {} + {}'.format('-'*50,'-'*15,'-'*25,'-'*20,'-'*5,'-'*64))
      for row in result_set:
        print('{} | {} | {} | {} | {} | {}'.format(row[0].ljust(50,' '),row[1].ljust(15,' '),str(row[2]).ljust(25,' '),row[3].ljust(20,' '),str(row[4]).ljust(5,' '),row[5].strip().ljust(64,' ')))
      print('{} + {} + {} + {} + {} + {}'.format('-'*50,'-'*15,'-'*25,'-'*20,'-'*5,'-'*64))

conn.close()
