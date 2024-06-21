from json import load, dump
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import logging
from logging.handlers import TimedRotatingFileHandler
from packaging.version import Version, parse as parse_version
import time
import os
import requests
import zipfile
import io
import shutil
import regex
import subprocess
import schedule
import psutil
import sys
import threading
import glob
import re
import random
import zipfile
import platform
from ruamel.yaml import YAML


load_dotenv(find_dotenv('./config/.env'))

class SubprocessLogger:
    def __init__(self, logger, key_type):
        self.logger = logger
        self.key_type = key_type
        self.log_methods = {
            'DEBUG': logger.debug,
            'INFO': logger.info,
            'NOTICE': logger.debug,
            'WARNING': logger.warning,
            'ERROR': logger.error,
            'UNKNOWN': logger.info
        }
    @staticmethod
    def parse_log_level_and_message(line, process_name):
        log_levels = {'DEBUG', 'INFO', 'NOTICE', 'WARNING', 'ERROR'}
        log_level = None
        message = None
        log_level_pattern = re.compile(r'({})\s*(.*)'.format('|'.join(log_levels)))
        match = log_level_pattern.search(line)

        if match:
            log_level = match.group(1)
            message = match.group(2).strip()
            if process_name == 'rclone' and message.startswith(': '):
                message = message[2:]
        else:
            log_level = 'UNKNOWN'
            message = line
        return log_level, message

    def monitor_stderr(self, process, mount_name, process_name):
        for line in process.stderr:
            if isinstance(line, bytes):
                line = line.decode().strip()
            else:
                line = line.strip()
            if line:
                log_level, message = SubprocessLogger.parse_log_level_and_message(line, process_name)
                log_func = self.log_methods.get(log_level, self.logger.info)
                if process_name == 'rclone':
                    log_func(f"rclone mount name \"{mount_name}\": {message}") 
                else:
                    log_func(f"{process_name}: {message}")

    def start_monitoring_stderr(self, process, mount_name, process_name):
        threading.Thread(target=self.monitor_stderr, args=(process, mount_name, process_name)).start()

    def log_subprocess_output(self, pipe):
        try:
            for line in iter(pipe.readline, ''):
                if isinstance(line, bytes):
                    line = line.decode().strip()
                else:
                    line = line.strip()
                if line:
                    log_level, message = SubprocessLogger.parse_log_level_and_message(line, self.key_type)
                    log_func = self.log_methods.get(log_level, self.logger.info)
                    log_func(f"{self.key_type} subprocess: {message}")
        except ValueError as e:
            self.logger.error(f"Error reading subprocess output for {self.key_type}: {e}")

    def start_logging_stdout(self, process):
        log_thread = threading.Thread(target=self.log_subprocess_output, args=(process.stdout,))
        log_thread.daemon = True
        log_thread.start()

class MissingAPIKeyException(Exception):
    def __init__(self):
        self.message = "Please set the debrid API Key: environment variable is missing from the docker-compose file"
        super().__init__(self.message)

class MissingEnvironmentVariable(Exception):
    def __init__(self, variable_name):
        self.variable_name = variable_name
        message = f"Environment variable '{variable_name}' is missing."
        super().__init__(message)

    def log_exception(self, logger):
        logger.error(f"Missing environment variable: {self.variable_name}")

class ConfigurationError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message
        super().__init__(self.error_message)

def format_time(interval):
    interval_hours = int(interval)
    interval_minutes = int((interval - interval_hours) * 60)

    if interval_hours == 1 and interval_minutes == 0:
        return "1 hour"
    elif interval_hours == 1 and interval_minutes != 0:
        return f"1 hour {interval_minutes} minutes"
    elif interval_hours != 1 and interval_minutes == 0:
        return f"{interval_hours} hours"
    else:
        return f"{interval_hours} hours {interval_minutes} minutes"

def get_start_time():
    start_time = time.time()
    return start_time

def time_to_complete(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time

    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    time_string = ""
    if hours > 0:
        time_string += f"{hours} hour(s) "
    if minutes > 0:
        time_string += f"{minutes} minute(s) "
    if seconds > 0:
        time_string += f"{seconds} second(s)"
    return time_string

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        self.rollover_filename = filename
        TimedRotatingFileHandler.__init__(self, self.rollover_filename, when, interval, backupCount, encoding, delay, utc, atTime)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        base_file_name_without_date = self.baseFilename.rsplit('-', 3)[0]
        current_date = time.strftime("%Y-%m-%d")
        correct_filename = base_file_name_without_date + '-' + current_date + '.log'

        if self.rollover_filename != correct_filename:
            new_filename = correct_filename
        else:
            new_filename = self.rollover_filename

        filenames_to_delete = self.getFilesToDelete()
        for filename in filenames_to_delete:
            os.remove(filename)

        self.rollover_filename = new_filename
        self.baseFilename = self.rollover_filename
        self.stream = self._open()

        new_rollover_at = self.computeRollover(self.rolloverAt)
        while new_rollover_at <= time.time():
            new_rollover_at = new_rollover_at + self.interval
        if self.utc:
            dst_at_rollover = time.localtime(new_rollover_at)[-1]
        else:
            dst_at_rollover = time.gmtime(new_rollover_at)[-1]

        if time.localtime(time.time())[-1] != dst_at_rollover:
            addend = -3600 if time.localtime(time.time())[-1] else 3600
            new_rollover_at += addend
        self.rolloverAt = new_rollover_at

    def getFilesToDelete(self):
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName.split('-', 1)[0] + "-"
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if re.compile(r"^\d{4}-\d{2}-\d{2}.log$").match(suffix):
                    result.append(os.path.join(dirName, fileName))
        result.sort()
        if len(result) < self.backupCount:
            result = []
        else:
            result = result[:len(result) - self.backupCount]
        return result

def get_logger(log_name='PDZURG', log_dir='./log'):
    current_date = time.strftime("%Y-%m-%d")
    log_filename = f"{log_name}-{current_date}.log"
    logger = logging.getLogger(log_name)
    backupCount_env = os.getenv('PDZURG_LOG_COUNT')
    try:
        backupCount = int(backupCount_env)
    except (ValueError, TypeError):
        backupCount = 2
    log_level_env = os.getenv('PDZURG_LOG_LEVEL')
    if log_level_env:
        log_level = log_level_env.upper()
        os.environ['LOG_LEVEL'] = log_level
        os.environ['RCLONE_LOG_LEVEL'] = log_level
    else:
        log_level = 'INFO'
    numeric_level = getattr(logging, log_level, logging.INFO)
    logger.setLevel(numeric_level)
    log_path = os.path.join(log_dir, log_filename)
    handler = CustomTimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=backupCount)
    os.chmod(log_path, 0o666)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%b %e, %Y %H:%M:%S')
    handler.setFormatter(formatter)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    for hdlr in logger.handlers[:]:
        logger.removeHandler(hdlr)
    logger.addHandler(handler)
    logger.addHandler(stdout_handler)
    return logger

                    
def load_secret_or_env(secret_name, default=None):
    secret_file = f'/run/secrets/{secret_name}'
    try:
        with open(secret_file, 'r') as file:
            return file.read().strip()
    except IOError:
        return os.getenv(secret_name.upper(), default)

PLEXDEBRID = os.getenv("PD_ENABLED")
PLEXUSER = load_secret_or_env('plex_user')
PLEXTOKEN = load_secret_or_env('plex_token')
JFADD = load_secret_or_env('jf_address')
JFAPIKEY = load_secret_or_env('jf_api_key')
RDAPIKEY = load_secret_or_env('rd_api_key')
ADAPIKEY = load_secret_or_env('ad_api_key')
SEERRAPIKEY = load_secret_or_env('seerr_api_key')
SEERRADD = load_secret_or_env('seerr_address')
PLEXADD = load_secret_or_env('plex_address')
ZURGUSER = load_secret_or_env('zurg_user')
ZURGPASS = load_secret_or_env('zurg_pass')
SHOWMENU = os.getenv('SHOW_MENU')
LOGFILE = os.getenv('PD_LOGFILE')
PDUPDATE = os.getenv('PD_UPDATE')
DUPECLEAN = os.getenv('DUPLICATE_CLEANUP')
CLEANUPINT = os.getenv('CLEANUP_INTERVAL')
RCLONEMN = os.getenv("RCLONE_MOUNT_NAME")
ZURG = os.getenv("ZURG_ENABLED")
ZURGVERSION = os.getenv("ZURG_VERSION")
ZURGLOGLEVEL = os.getenv("ZURG_LOG_LEVEL")
ZURGUPDATE = os.getenv('ZURG_UPDATE')
PLEXREFRESH = os.getenv('PLEX_REFRESH')
PLEXMOUNT = os.getenv('PLEX_MOUNT_DIR')
NFSMOUNT = os.getenv('NFS_ENABLED')
NFSPORT = os.getenv('NFS_PORT')
ZURGPORT = os.getenv('ZURG_PORT')
RIVEN = os.getenv("RIVEN_ENABLED")
RUPDATE = os.getenv('RIVEN_UPDATE')