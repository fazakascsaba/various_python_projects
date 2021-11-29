# (c) fazakas.cs@gmail.com
# called by Pipeline job_launcher
# vi /home/ansible/jenkins/file_watcher.py
# vi /home/ansible/jenkins/watched_folders.yaml
# a2x
######################################################################################################

import os
import re
import yaml
import time
import hashlib
import urllib
import threading
import logging
from datetime import date
import sys
import random
import requests


JENKINS_URL = 'https://10.21.201.7:3043/job/File_Exchange/job/'
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

jobno='#{}'.format(sys.argv[1])
curr_date=str(date.today())
log_file='job_launcher_{}.log'.format(curr_date)
log_folder='{}//file_watcher_logs'.format(os.getcwd().split('/workspace/')[0])
logging.basicConfig(level=logging.DEBUG, filename='{}//{}'.format(log_folder,log_file), filemode='a', format='%(asctime)s %(levelname)s {0} %(threadName)s : %(message)s'.format(jobno))

def load_yaml_file(filename):
  try:
    with open(filename,'r') as stream:
      return yaml.safe_load(stream)
  except Exception as e:
    return
def md5(filename, blocksize=65536):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()
def different_checksum(file):
    first_calc=md5(file)
    time.sleep(1)
    second_calc=md5(file)
    return first_calc!=second_calc
def different_size(host,path,file,sudo):
    first_size=int(os.popen('ssh {}{}du -b {}{} | cut -f 1'.format(host,sudo,path,file)).read().split('\n')[:-1][0])
    time.sleep(3)
    second_size=int(os.popen('ssh {}{}du -b {}{} | cut -f 1'.format(host,sudo,path,file)).read().split('\n')[:-1][0])
    return first_size!=second_size
def number_of_threads():
  return len(threading.enumerate())
def launch_if_condition_met(f, print_lock,jobno):
  console_msg=[]
  if wf[f]["inactive"]:
    console_msg.append('INFO {} is not active.'.format(f))
  else:
    path=wf[f]["path"]
    mask=wf[f]["mask"]
    host=wf[f]["host"]
    job_name=wf[f]["job_name"]
    files=[]

    if host=='localhost':
      try:
        files=[x for x in os.listdir(path) if re.match(mask,x)]
      except:
        console_msg.append('ERROR {} -> directory listing failed. Make sure {} is accessible!'.format(job_name,path))
    else:

      if host=='opc@c01p1-sftp05':
        sudo=' sudo '
      else:
        sudo=' '

      path_len=len(path)
      reply_from_host=[x[path_len:] for x in os.popen('ssh {}{}find {} -type f -maxdepth 1 -print'.format(host,sudo,path)).read().split('\n')[:-1]]
      files=[x for x in reply_from_host if re.match(mask,x)]

    if files:
      time.sleep(5)
      logging.info('{} is started to process these files {}. Host={}, Location={}.'.format(job_name,files,host,path))
      console_msg.append('{} -> these object were found: {}'.format(job_name,files))

      #check if file is being written for short filelists
      if len(files) < 10:
        for ff in files:
          if host=='localhost':
            if os.path.isdir('{}{}'.format(path,ff)):
              console_msg.append('INFO {} -> {} is directory md5 validation skipped.'.format(job_name,ff))
            else:
              while different_checksum("{}{}".format(path,ff)):
                time.sleep(1)
          else:
            while different_size(host,path,ff,sudo):
              time.sleep(1)
      console_msg.append('INFO {0} -> {0} is being started.'.format(job_name))

      # new part --- uncomment
      job_name=wf[f]["job_name"]
      url = "{}{}/build".format(JENKINS_URL,job_name)
      response = requests.post(url, verify=False,
                             auth=('jenkins', '11186fb44c6cx6f9xxxx13544ce055440f'))
      console_msg.append('INFO response= {0}.'.format(response))
    else:
      console_msg.append('INFO {} -> no file was found this time. Pattern: {}{}'.format(job_name,path,mask))

  print_lock.acquire()
  for l in console_msg:
    print(l)
  print_lock.release()

wf=load_yaml_file('./watched_folders.yaml')
print_lock=threading.Lock()

threads=[]

for f in wf:
  thr=threading.Thread(target=launch_if_condition_met,args=[f,print_lock,jobno])
  thr.setDaemon(True)
  time.sleep(random.random())

  while number_of_threads() > 5:
    print('INFO thread limit reached: {}.'.format(number_of_threads()))
    time.sleep(1)

  thr.start()
  threads.append(thr)
[t.join() for t in threads]
