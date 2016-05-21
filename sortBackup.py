#!/usr/bin/python3

import os
import syslog
import re
import datetime
import shutil
import argparse

args = argparse.ArgumentParser()
args.add_argument('source_dir')
args.add_argument('--keep_days', default=30)

def log(msg):
    syslog.syslog(msg)

def createDirs(sourceDir):
    log('create dirs')
    backupDir_weekly = os.path.join(sourceDir, 'weekly')
    backupDir_montly = os.path.join(sourceDir, 'monthly')
    backupDir_yearly = os.path.join(sourceDir, 'yearly')

    if(not os.path.exists(backupDir_weekly)):
       os.mkdir(backupDir_weekly)

    if(not os.path.exists(backupDir_montly)):
        os.mkdir(backupDir_montly)

    if(not os.path.exists(backupDir_yearly)):
        os.mkdir(backupDir_yearly)


def findBackups(source):
    backupFiles = []
    for root, dirs, files in os.walk(source):
        for f in files:
            log(f)
            backupFiles.append({'fileName': f, 'date': '', 'folder': ''})

    return backupFiles

def parseDate(backupList):
    reg = re.compile('backup_mail.grischawen.de_(\d{4})(\d{2})(\d{2})_.*')
    for backup in backupList:
        if(backup['fileName'] != ''):
            print(backup['fileName'])
            res = reg.match(backup['fileName'])
            if(res):
                backup['date'] = datetime.date(int(res.group(1)), int(res.group(2)), int(res.group(3)))

    return backupList


def copyBackups(sourceDir, backups):
    for back in backups:
        print("{}\t WeekDay: {}".format(back['date'], back['date'].weekday()))

        if(back['date'].weekday() == 0):
            log('got weekly: {}'.format(back['fileName']))
            src = os.path.join(sourceDir, back['fileName'])
            dst = os.path.join(sourceDir, 'weekly', back['fileName'])

            if(not os.path.exists(dst)):
                log('move backup {} to {}'.format(src, dst))
                shutil.copy(src, dst)
            else:
                log('backup already moved')

        if(back['date'].day == 1):
            log('got monthly: {}'.format(back['fileName']))

            src = os.path.join(sourceDir, back['fileName'])
            dst = os.path.join(sourceDir, 'monthly', back['fileName'])

            if(not os.path.exists(dst)):
                log('move backup {} to {}'.format(src, dst))
                shutil.copy(src, dst)
            else:
                log('backup already moved')

        if(back['date'].day == 1 and back['date'].month == 6):
            log('got yearly: {}'.format(back['fileName']))

            src = os.path.join(sourceDir, back['fileName'])
            dst = os.path.join(sourceDir, 'yearly', back['fileName'])

            if(not os.path.exists(dst)):
                log('move backup {} to {}'.format(src, dst))
                shutil.copy(src, dst)
            else:
                log('backup already moved')

def deleteOldBackups(sourceDir, backups, days):
    diff = datetime.timedelta(days=int(days))
    today = datetime.date.today()

    for backup in backups:
        dDiff = today - backup['date']
        print("Global diff: {}, current diff for filename {} is {} - in Days: {}".format(diff, backup['fileName'], dDiff, dDiff.days))
        if(dDiff.days >= int(days)):
            log("Remove {}".format(backup['fileName']))
            if(os.path.exists(os.path.join(sourceDir, backup['fileName']))):
                os.remove(os.path.join(sourceDir, backup['fileName']))


def main():
    syslog.openlog()
    arguments = args.parse_args()
    if(arguments.source_dir):
        log('START')
        log('Looking for backups in ' + arguments.source_dir)

        backups = findBackups(arguments.source_dir)
        backups = parseDate(backups)
        createDirs(arguments.source_dir)
        copyBackups(arguments.source_dir, backups)
        deleteOldBackups(arguments.source_dir, backups, arguments.keep_days)
        log('DONE')

if __name__ == "__main__":
    main()