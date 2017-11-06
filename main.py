from ftplib import FTP
import argparse
import os
import datetime
from os import listdir


def connect(user, password):
    ftpNrb.login(user=user, passwd=password)


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("ftpHost", help="host ip")
    parser.add_argument("ftpUser", help="ftp user")
    parser.add_argument("ftpPassword", help="ftp password")
    parser.add_argument("nrb_path", help="path of the remote monitored folder")
    parser.add_argument("erp_path", help="path of the erp folder where the files will be saved")
    args = parser.parse_args()
    v_host = args.ftpHost.split('=')[1]
    v_user = args.ftpUser.split('=')[1]
    v_password = args.ftpPassword.split('=')[1]
    v_erp_ftp_monitored_folders = {'FolderMonitored': args.erp_path.split('=')[1]}
    v_ftp_nrb_monitored_folders = {'FolderMonitored': args.nrb_path.split('=')[1]}
    return v_host, v_user, v_password, v_erp_ftp_monitored_folders, v_ftp_nrb_monitored_folders


def convert_timestamp_to_epoch(timestamp):
    year = int(timestamp[0:4])
    month = int(timestamp[4:6])
    day = int(timestamp[6:8])
    hour = int(timestamp[8:10])
    minute = int(timestamp[10:12])
    return (datetime.datetime(year, month, day, hour, minute) - datetime.datetime(1970, 1,
                                                                                  1)).total_seconds()


def remove_file_on_erp_from_nrb_master():
    differences_erp = list(set(erpFtpErrorFilesList) - set(ftpNrbErrorFilesList))
    for difference in differences_erp:
        os.remove(erpFtpMonitoredFolders[folderKey] + '/' + difference)


def create_file_on_erp_from_nrb_master():
    differences_nrb = list(set(ftpNrbErrorFilesList) - set(erpFtpErrorFilesList))
    ls = []
    ftpNrb.retrlines('MLSD ' + ftpNrbMonitoredFolders[folderKey], ls.append)
    for entry in ls:
        if 'Size' in entry:
            erp_filename = entry.split(';')[3].strip()
            if erp_filename in differences_nrb:
                for e in entry.split(';'):
                    if 'Modify' in e:
                        erp_file_epoch = convert_timestamp_to_epoch(timestamp=e.split('=')[1])
                        fp = open(erpFtpMonitoredFolders[folderKey] + '/' + erp_filename, 'w')
                        fp.close()
                        os.utime(erpFtpMonitoredFolders[folderKey] + '/' + erp_filename,
                                 (erp_file_epoch, erp_file_epoch))


if __name__ == '__main__':
    ftpNrbHost, ftpNrbUser, ftpNrbPassword, erpFtpMonitoredFolders, ftpNrbMonitoredFolders = parse_command_line()
    ftpNrb = FTP(ftpNrbHost)

    connect(ftpNrbUser, ftpNrbPassword)

    for folderKey in ftpNrbMonitoredFolders.keys():
        ftpNrbErrorFilesList = set(ftpNrb.nlst(ftpNrbMonitoredFolders[folderKey]))
        erpFtpErrorFilesList = set(listdir(erpFtpMonitoredFolders[folderKey]))

        remove_file_on_erp_from_nrb_master()
        create_file_on_erp_from_nrb_master()
