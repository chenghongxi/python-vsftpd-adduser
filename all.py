#!/usr/bin/python
# -*- coding:utf-8 -*-
import pymysql
import xlrd
import time
from subprocess import Popen, PIPE, STDOUT
import sys,os



class ExcelOperation(object):
    #封装excel内容读取方法'''
    def __init__(self, file_name="", sheet_id=0):
        self.file_name = file_name
        self.sheet_id = sheet_id
        self.data = self.get_data()

    '''获取excel内容'''

    def get_data(self):
        workbook = xlrd.open_workbook(self.file_name)
        data = workbook.sheets()[self.sheet_id]
        return data

    '''获取总行数'''

    def get_nrows(self):
        return self.data.nrows

    '''获取总列数'''

    def get_ncols(self):
        return self.data.ncols

    '''获取单元格内容'''

    def get_cell_values(self, row, col):
        return self.data.cell_value(row, col)


def mkdirs(path):
    # 引入模块
    import os

    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)

    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        print(path + ' 创建成功')
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
        return False

def Insert_mysql(user,passwd):
    conn = pymysql.connect(host='***', port=8635, user='root', passwd='*****', db='vsftpdvu')
    cur = conn.cursor()
    cur.execute("insert into users(name,passwd) VALUES ('{0}','{1}')".format(user,passwd))
    conn.commit()
    cur.close()
    conn.close()

#执行命令
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = p.communicate()
    return p.returncode, stdout.strip()

#写文件
def Write_Text(file_name,contant):
    # file_name = 'test.txt'
    with open(file_name,"a+") as f:
        f.writelines(contant)
        f.writelines("\n")
def mkdirFunc():
    operation = ExcelOperation('changbai.xlsx')
    for i in range(operation.get_nrows()):
        if i==0 :
            continue
        user=operation.get_cell_values(i, 0)
        password=operation.get_cell_values(i, 1)
        print(user,password)
        #Write_Text("login.txt",user)
        #Write_Text("login.txt", password)
        #Insert_mysql(user,password)
        #uploaddir="/sftp/{0}/upload/".format(user)
        #downloaddir = "/sftp/{0}/download/".format(user)
        #mkdirs(uploaddir)
        #mkdirs(downloaddir)
        run_cmd('touch /etc/vsftpd/vuser.conf.d/{0}'.format(user))
        run_cmd('''cat >/etc/vsftpd/vuser.conf.d/{0}<<-EOF
local_root=/sftp/{0}
anon_world_readable_only=NO
anon_umask=022
write_enable=YES
anon_mkdir_write_enable=YES
anon_upload_enable=YES
anon_other_write_enable=YES
'''.format(user))
    time.sleep(1)
    #run_cmd("chown -R www.www /www/ftpsite/")
    run_cmd("chown -R www.root /sftp/")
    run_cmd('chmod -R 700 /sftp/')
    print("-------------------------")
    print("       用户创建完成        ")
    print("-------------------------")


def scpFileToRemoteNode(user, ip, password, localsource, remotedest, port=22):
    print(user,ip,password,localsource,remotedest,port)
    SCP_CMD_BASE = r'''
      expect -c "
      set timeout -1 ;
      spawn  scp -P {port} -r {username}@{host}:{remotedest} {localsource};
      expect *yes* {{{{ send yes\r }}}} ;
      expect *assword* {{{{ send {password}\r }}}} ;
      expect eof
      " > file.out 2>&1 &
  '''.format(username=user, password=password, host=ip, localsource=localsource, remotedest=remotedest, port=port)
    SCP_CMD = SCP_CMD_BASE.format(localsource=localsource)
    p = Popen(SCP_CMD, stdout=PIPE, stderr=PIPE, shell=True)
    p.communicate()
    run_cmd("chown -R www.root /sftp/")
    run_cmd('chmod -R 700 /sftp/')
    print("-------------------------")
    print("       文件拷贝完成        ")
    print("-------------------------")

def scpFile():
    operation = ExcelOperation('changbai.xlsx',1)
    for i in range(operation.get_nrows()):
        if i==0 :
            continue
        ip = operation.get_cell_values(i, 0)
        password = operation.get_cell_values(i, 1)
        scpFileToRemoteNode("centos", ip, password, "/sftp/", "/ftp01/*", 22)

if __name__ == '__main__':
    sys.stdout.write('功能菜单:  \n')
    sys.stdout.write('1：创建用户\n')
    sys.stdout.write('2：拷贝文件')
    while True:
        str = input("\n请输入数字：选择功能\n");
        if int(str)==1:
            mkdirFunc()
        elif int(str)==2:
            scpFile()
        elif str=="exit":
            break
        else:
            print("输入错误请重新输入")
