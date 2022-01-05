import cx_Oracle
import yaml
from datetime import datetime, timedelta

def load_yaml_file(filename):
  try:
    with open(filename,'r') as stream:
      return yaml.safe_load(stream)
  except Exception as e:
    return
def compile_bo_sql(id_list,phone_number,purpose):
  id_list[0]='\'{}'.format(id_list[0])
  id_list[-1]='{}\''.format(id_list[-1])
  id_string='\',\''.join(id_list)
  if purpose=='update':
    sql='''
      update MCW_FIN
      set p0170 = {}, status = 'CLMS0010'
      where de022_5 = '2'
      and id in ({})
      '''.format(phone_number,id_string)
  elif purpose=='select':
    sql='''
      select * from MCW_FIN
      where id in ({})
      and de022_5 = '2'
      '''.format(id_string)
  print(sql)
  return sql
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
  
id_list=['2112300098409030','2112300098409031']
phone_number='9058320600'
purpose='select' # update | select

''' 
oci_ps_prod_bo
oci_ps_prod_fe
onprem_prod_bo
onprem_prod_fe
'''
conn=connect_to_database('onprem_prod_bo')
c = conn.cursor()
c.execute(compile_bo_sql(id_list,phone_number,purpose))
if purpose=='update':
  conn.commit()
elif purpose=='select':
  result_set=c.fetchall()
  if result_set:
    for row in result_set:
      print(row)

conn.close()
