from json import load, dump
from token import RBRACE
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler, BaseRotatingHandler
from packaging.version import Version, parse as parse_version
import time
import os
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
RIVENBACKENDURL = os.getenv('RIVEN_BACKEND_URL')
RIVENDATABASEHOST = os.getenv('RIVEN_DATABASE_HOST')
RBBRANCH = os.getenv('RIVEN_BACKEND_BRANCH')
RFBRANCH = os.getenv('RIVEN_FRONTEND_BRANCH')
RBVERSION = os.getenv('RIVEN_BACKEND_VERSION')
RFVERSION = os.getenv('RIVEN_FRONTEND_VERSION')
RBUPDATE = os.getenv('RIVEN_BACKEND_UPDATE')
RFUPDATE = os.getenv('RIVEN_FRONTEND_UPDATE')