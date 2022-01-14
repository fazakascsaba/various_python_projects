# open_workbook.py
from openpyxl import load_workbook
import cx_Oracle
import yaml


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
def sql_collect_info(sting_utrno):
    sql='''
    select t1.status,t1.forw_inst_bin,t1.network_refnum,t1.oper_amount,t1.oper_request_amount,t2.id
    from opr_operation t1
    inner join (select * from opr_operation where  id > 2201120000000000) t2 on t1.id=t2.original_id
        where t1.id in (
        select id from (select * from aut_auth where id > 2201120000000000)
        where  external_auth_id in ({})
    ) and t1.is_reversal=0  and t2.is_reversal=1
    '''.format(sting_utrno)
    return sql
def sql_modify(status,forw_inst_bin,network_refnum,oper_amount,oper_requested_amount,oper_id):
    modif_sql='''
    update opr_operation o
    set o.status = 'OPST0100', 
        o.status_reason = '{}'
      , o.forw_inst_bin = {}
      , o.network_refnum = '{}'
      , o.oper_amount = {}
      , o.oper_request_amount  = {}
    where o.id = ({}) and o.is_reversal  = 1 and o.status = 'OPST0102'
    '''.format('RESP0001',forw_inst_bin,network_refnum,oper_amount,oper_requested_amount,oper_id)
    return(modif_sql)

if __name__ == "__main__":
    path="C:\\Users\\fazakas\\Downloads\\BPC_Generate_Reversals.xlsx"
    workbook = load_workbook(filename=path)
    sheet = workbook.active
    
    conn=connect_to_database('oci_ps_prod_bo')
    c = conn.cursor()

    list_utrno=[]
    start_line=2
    while sheet[f"A{start_line}"].value:
      list_utrno.append(sheet[f"A{start_line}"].value)
      start_line+=1

    buffer=900
    cursor=0
    while len(list_utrno[cursor:]) > 0:
      if len(list_utrno[cursor:]) < buffer:
        buffer=len(list_utrno[cursor:])

      sting_utrno="'"+"','".join(list_utrno[cursor:buffer+cursor])+"'"

      print(sql_collect_info(sting_utrno)) #
      c.execute(sql_collect_info(sting_utrno))
      result_set=c.fetchall()
      if result_set:
        for row in result_set:
          status=row[0]
          forw_inst_bin=row[1]
          if not forw_inst_bin:
            forw_inst_bin='Null'
          network_refnum=row[2]
          oper_amount=row[3]
          oper_requested_amount=row[4]
          oper_id=row[5]
          if not network_refnum:
            network_refnum='Null'
            c.execute(sql_modify(status,forw_inst_bin,network_refnum,oper_amount,oper_requested_amount,oper_id))
            conn.commit()

      cursor+=buffer
 
conn.close()
