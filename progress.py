import os
import platform

import time

from config import Config


def kill():
    sys = platform.system()
    if sys == "Linux":
        print("OS is Linux!!!")
    else:
        print("OS is not Linux! %s"%sys)
        return
    print('-------BEGIN-KILL------')
    stop_run_time = 300
    stop_cpu_time_ratio = 0.25
    # a = 'ps -eo "pid,etime,time,command" | grep chrome| grep -v grep'
    #96022 chromedriver       0:00.10
    ## linux
    a = 'ps -eo "%p|%t|%x|%c" | grep chromedriver | grep -v grep'
    # PID | ELAPSED | TIME | COMMAND
    # 2486 | 26: 24 | 00:00: 00 | bash
    # 2639 | 00: 00 | 00:00: 00 | ps
    b = os.popen(a,'r',1)
    shuchu = b.read()
    b.close()
    s = shuchu.split("\n")   # 切割换行
    new = [x for x in s if x != '']  # 去掉空''
    print('********%d**********'%len(new))
    for index in range(0,len(new)):
        print('------%d---------'%(index+1))
        i =  new[index]
        # list = i.split(' ')
        # linux
        list = i.split('|')
        pid_index = 0
        etime_index = 0
        etime_int = 0
        cpu_time_int = 0
        # pid = list[0].replace(' ','')
        for index in range(0,len(list)):
            if ( len(list[index]) > 1 ):
                pid = list[index].replace(' ','')
                pid_index = index
                break
        print('pid=%s'%pid)
        # pids.append(pid)
        for index in range(pid_index+1,len(list)):
            if ( len(list[index]) > 1 ):
                etime = list[index].replace(' ','')
                etime_index = index
                break
        for index in range(etime_index+1,len(list)):
             if ( len(list[index]) > 1 ):
                time_command = list[index]
                break
        print('etime=%s'%etime)
        # print('time_command=%s'%time_command)
        etime_list = etime.split(':')
        if (len(etime_list) == 3):
            etime_int += 60*60*int(etime_list[0])
            etime_int += 60*int(etime_list[1])
            etime_int += int(etime_list[2])
        elif (len(etime_list) == 2):
            etime_int += 60*int(etime_list[0])
            etime_int += int(etime_list[1])
        # print(etime_int)
        if (time_command):
            time = time_command.split(' ')[0]
            time_list = time.split(':')
            if ( len(time_list) == 3 ) :
                cpu_time_int+=int(time_list[0])*60*60
                cpu_time_int+=int(time_list[1])*60
                cpu_time_int+=int(time_list[2])
            elif( len(time_list) == 2 ) :
                cpu_time_int+=int(time_list[0])*60
                cpu_time_int+=int(time_list[1])
            print('time=%s'%time)
            # print('cpu_time_int=%s'%cpu_time_int)
        print('pid:'+pid+'|runTime:%d'%etime_int+'|cpu_time:%f'%cpu_time_int)
        if  (etime_int > stop_run_time and cpu_time_int/etime_int > stop_cpu_time_ratio):
            cmd = "kill -9 %d" % int(pid)
            rc = os.system(cmd)
            if rc == 0 :
                print("stop \"%s\" success!!"%pid)
            else:
                print("stop \"%s\" failed!!"%pid)
def get_pids_by_comm(comm):
    pids = []
    a = 'ps -eo pid,comm |grep '+comm+' | grep -v grep'
     # PID | ELAPSED | TIME | COMMAND
     # 2486 | 26: 24 | 00:00: 00 | bash
     # 2639 | 00: 00 | 00:00: 00 | ps
    b = os.popen(a,'r',1)
    shuchu = b.read()
    b.close()
    s = shuchu.split("\n")   # 切割换行
    new = [x for x in s if x != '']  # 去掉空''
    # print('********%d**********'%len(new))
    for i in range(0,len(new)):
        # print('------%d---------'%(i+1))
         # pid = list[0].replace(' ','')
        list = new[i].split(' ')
        pid_index = 0
        pid = None
        for index in range(0,len(list)):
            if ( len(list[index]) > 1 ):
                pid = list[index].replace(' ','')
                pids.append(pid.replace(' ',''))
                pid_index = index
                break
        # print(pid)
    return pids
def kill_ids(ids):
    for id in ids:
         cmd = "kill -9 %d" % int(id)
         os.system(cmd)
def find_pids(old,new):
    old_len = len(old)
    new_len = len(new)
    pids = []
    if (new_len >= old_len):
        for n in new :
            for o in old:
                if (o == n):
                    break;
        pids.append(n)
    else:
        for o in old:
            for n in new:
                if (o == n):
                    break;
        pids.append(o)
    print(pids)
    return pids
if __name__ =='__main__':
    old = get_pids_by_comm('chromedriver')
    time.sleep(15)
    new = get_pids_by_comm('chromedriver')
    find_pids(old,new)