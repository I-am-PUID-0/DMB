from json import load, dump
from token import RBRACE
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, BaseRotatingHandler
from packaging.version import Version, parse as parse_version
import time
import os
import pwd
import grp
import ast
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
import fnmatch
import signal
from colorlog import ColoredFormatter
from ruamel.yaml import YAML


load_dotenv(find_dotenv('./config/.env'))
                    
def load_secret_or_env(secret_name, default=None):
    secret_file = f'/run/secrets/{secret_name}'
    try:
        with open(secret_file, 'r') as file:
            return file.read().strip()
    except IOError:
        return os.getenv(secret_name.upper(), default)

def get_valid_env(env_var, default):
    value = os.getenv(env_var)
    if value is None or value.strip() == "":
        return default
    try:
        if isinstance(default, int):
            return int(value)
        elif isinstance(default, float):
            return float(value)
        elif isinstance(default, bool):
            return value.lower() in ['true', '1', 'yes']
        else:
            return value
    except ValueError:
        return default

PLEXTOKEN = load_secret_or_env('plex_token')
PLEXADD = load_secret_or_env('plex_address')
RDAPIKEY = load_secret_or_env('rd_api_key')
ADAPIKEY = load_secret_or_env('ad_api_key')
ZURGUSER = load_secret_or_env('zurg_user')
ZURGPASS = load_secret_or_env('zurg_pass')
GHTOKEN = load_secret_or_env('github_token')
SEERRAPIKEY = load_secret_or_env('seerr_api_key')
SEERRADD = load_secret_or_env('seerr_address')
DUPECLEAN = os.getenv('DUPLICATE_CLEANUP')
CLEANUPINT = os.getenv('CLEANUP_INTERVAL')
RCLONEMN = os.getenv("RCLONE_MOUNT_NAME")
RCLONELOGLEVEL = os.getenv("RCLONE_LOG_LEVEL")
ZURG = os.getenv("ZURG_ENABLED")
ZURGVERSION = os.getenv("ZURG_VERSION")
ZURGLOGLEVEL = os.getenv("ZURG_LOG_LEVEL")
ZURGUPDATE = os.getenv('ZURG_UPDATE')
NFSMOUNT = os.getenv('NFS_ENABLED')
NFSPORT = os.getenv('NFS_PORT')
ZURGPORT = os.getenv('ZURG_PORT')
RIVENBACKEND = os.getenv("RIVEN_BACKEND_ENABLED")
RIVENFRONTEND = os.getenv("RIVEN_FRONTEND_ENABLED")
RIVEN = os.getenv("RIVEN_ENABLED")
RUPDATE = os.getenv('RIVEN_UPDATE')
RIVENLOGLEVEL = os.getenv('RIVEN_LOG_LEVEL')
FRONTENDLOGS = os.getenv('FRONTEND_LOGS')
BACKENDLOGS = os.getenv('BACKEND_LOGS')
RIVENBACKENDURL = os.getenv('RIVEN_BACKEND_URL')
RIVENDATABASEHOST = os.getenv('RIVEN_DATABASE_HOST')
RIVENDATABASEURL = os.getenv('RIVEN_DATABASE_URL')
RBBRANCH = os.getenv('RIVEN_BACKEND_BRANCH')
RFBRANCH = os.getenv('RIVEN_FRONTEND_BRANCH')
RBVERSION = os.getenv('RIVEN_BACKEND_VERSION')
RFVERSION = os.getenv('RIVEN_FRONTEND_VERSION')
RBUPDATE = os.getenv('RIVEN_BACKEND_UPDATE')
RFUPDATE = os.getenv('RIVEN_FRONTEND_UPDATE')
RFDIALECT = os.getenv('RIVEN_FRONTEND_DIALECT')
SYMLINKLIBRARYPATH = os.getenv('SYMLINK_LIBRARY_PATH')
SYMLINKRCLONEPATH = os.getenv('SYMLINK_RCLONE_PATH')
RCLONELOGS = os.getenv('RCLONE_LOGS')
db_host = '127.0.0.1'  
user_id = get_valid_env('PUID', 1001)
group_id = get_valid_env('PGID', 1001)
postgres_data = get_valid_env('POSTGRES_DATA', '/postgres_data')
postgres_user = get_valid_env('POSTGRES_USER', 'DMB')
postgres_password = get_valid_env('POSTGRES_PASSWORD', 'postgres')
postgres_db = get_valid_env('POSTGRES_DB', 'riven')
RCLONEDIR = get_valid_env('RCLONE_DIR', '/data')