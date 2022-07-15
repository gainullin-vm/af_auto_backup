import subprocess
import time
import logging
import re
import os
#go
os.system('chmod 600 /home/ubuntu/.ssh/dev02_access')
os.system('chmod 600 /home/ubuntu/.ssh/server460_access')
os.system('chmod 600 /home/ubuntu/.ssh/prod_af_access')

logging.basicConfig(
    filename="/home/ubuntu/backup.log",
    level=logging.INFO)

timecount = str(time.strftime("%b_%d_at_%H_%M_%S_in_%Y"))
host = "user@ip"
dev02_KeyPath_dev02 = "/home/vitaly/.ssh/dev02_access"
dev02_KeyPath_server460 = "/home/vitaly/.ssh/server460_access"
local_keyPath_server460 = "/home/ubuntu/.ssh/server460_access"
local_keyPath_dev02 = "/home/ubuntu/.ssh/dev02_access"

src = "/home/"
dest = "user@:ip/home/vitaly/"
volumeList = {
    "volumes"
}

def logError(host, command, errorElement):
    print("ERROR: ", host, " ===", command, "=== ", errorElement)
    logs_ERROR = "ERROR: " + str(host) + " ===" + str(command) + "=== " + str(errorElement)
    logging.info(logs_ERROR)

def logInfo(host, command, element):
    print("INFO: ", host, " ===", command, "=== ", element)
    log_INFO = "INFO: " + str(host) + " ===" + str(command) + "=== " + str(element)
    logging.info(log_INFO)

def logVolumes(host, command, volume, dest):
    print("INFO: ", host, " ===", command, "=== ", volume, " to ", dest)
    log_INFO = "INFO: " + str(host) + " ===" + str(command) + "=== " + str(volume) + " to " + str(dest)
    logging.info(log_INFO)


def exec(local_KeyPath_dev02, host, tag, timecount):
    commandList = [
        "docker commit " + tag + " avalancheforecast/main:" + tag + "_" + timecount,
        "docker push avalancheforecast/main:" + tag + "_" + timecount,
        "docker rmi avalancheforecast/main:" + tag + "_" + timecount,
    ]
    for command in commandList:
        ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-i", local_KeyPath_dev02, host, command],
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        error = ssh.stderr.readlines()
        if result == []:
            for errorElement in error:
                logError(host, command, errorElement)
        else:
            for element in result:
                logInfo(host, command, element)

def scpBackup(local_KeyPath_dev02, dev02_KeyPath_server460, host, volume, src, dest):
    commandList = [
        "scp -o StrictHostKeyChecking=no -i " + dev02_KeyPath_server460 + " -r " + src + volume + " " + dest,
    ]
    for command in commandList:
        ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-i", local_KeyPath_dev02, host, command],
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        result = ssh.stdout.readlines()
        error = ssh.stderr.readlines()
        if (result == []) & (error == "b'Failed to add the host to the list of known hosts (/home/ubuntu/.ssh/known_hosts).\r\n'"):
            logVolumes(host, command, volume, dest)
        else:
            for errorElement in error:
                logError(host, command, errorElement)

def execActive(local_KeyPath_dev02, host):
    commandList = [
        "docker ps -q"
    ]
    for command in commandList:
        ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-i", local_KeyPath_dev02, host, command],
                            shell=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        result = re.findall("\w\B\w*", str(ssh.stdout.readlines()))
        error = ssh.stderr.readlines()
        if result == []:
            for errorElement in error:
                logError(host, command, errorElement)
        else:
            for element in result:
                logInfo(host, command, element)
            for element in result:
                commandList = [
                    "docker inspect --format {{.Name}} " + element
                ]
                for command in commandList:
                    ssh = subprocess.Popen(
                        ["ssh", "-o", "StrictHostKeyChecking=no", "-i", local_KeyPath_dev02, host, command],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                    result = re.findall("\w\B\w*", str(ssh.stdout.readlines()))
                    if result == []:
                        error = ssh.stderr.readlines()
                        for errorElement in error:
                            logError(host, command, errorElement)
                    else:
                        for tag in result:
                            logInfo(host, command, tag)
                            exec(local_KeyPath_dev02, host, tag, timecount)

i = 0
while i < 1:
    execActive(local_keyPath_dev02, host)
    for volume in volumeList:
        scpBackup(local_keyPath_dev02, dev02_KeyPath_server460, host, volume, src, dest)
        time.sleep(86400)
