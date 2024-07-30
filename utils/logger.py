from base import *


class SubprocessLogger:
    def __init__(self, logger, key_type):
        self.logger = logger
        self.stdout_thread = None
        self.stderr_thread = None
        self.stop_event = threading.Event()        
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

        date_time_prefix_pattern = re.compile(r'^\d{2}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ')
        message = date_time_prefix_pattern.sub('', message).strip()

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
        self.stderr_thread = threading.Thread(target=self.monitor_stderr, args=(process, mount_name, process_name))
        self.stderr_thread.daemon = True
        self.stderr_thread.start()

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
        self.stdout_thread = threading.Thread(target=self.log_subprocess_output, args=(process.stdout,))
        self.stdout_thread.daemon = True
        self.stdout_thread.start()

    def stop_logging_stdout(self):
        if self.stdout_thread:
            self.stop_event.set()
            self.stdout_thread.join()

    def stop_monitoring_stderr(self):
        if self.stderr_thread:
            self.stop_event.set()
            self.stderr_thread.join()       

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

class CustomRotatingFileHandler(BaseRotatingHandler):
    def __init__(self, filename, when='midnight', interval=1, backupCount=0, maxBytes=0, encoding=None, delay=False, utc=False, atTime=None):
        self.when = when
        self.backupCount = backupCount
        self.maxBytes = maxBytes
        self.utc = utc
        self.atTime = atTime
        self.interval = self.computeInterval(when, interval)
        self.rolloverAt = self.computeRollover(time.time())
        self.logger = logging.getLogger('CustomRotatingFileHandler')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%b %e, %Y %H:%M:%S')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(stream_handler)               
        super().__init__(filename, 'a', encoding, delay)
    
    def computeInterval(self, when, interval):
        if when == 'S':
            return interval
        elif when == 'M':
            return interval * 60
        elif when == 'H':
            return interval * 60 * 60
        elif when == 'D' or when == 'midnight':
            return interval * 60 * 60 * 24
        elif when.startswith('W'):
            day = int(when[1])
            current_day = time.localtime().tm_wday
            days_to_wait = (day - current_day) % 7
            return interval * 60 * 60 * 24 * 7 + days_to_wait * 60 * 60 * 24
        else:
            raise ValueError("Invalid rollover interval specified: %s" % when)
    
    def computeRollover(self, currentTime):
        if self.when == 'midnight':
            t = time.localtime(currentTime)
            current_hour = t.tm_hour
            current_minute = t.tm_min
            current_second = t.tm_sec
            seconds_until_midnight = ((24 - current_hour - 1) * 3600) + ((60 - current_minute - 1) * 60) + (60 - current_second)
            rollover_time = currentTime + seconds_until_midnight + 1
        else:
            rollover_time = currentTime + self.interval        
        return rollover_time
    
    def shouldRollover(self, record):
        if self.stream is None:  
            self.stream = self._open()
        if self.maxBytes > 0:  
            self.stream.seek(0, 2)  
            if self.stream.tell() + len(self.format(record)) >= self.maxBytes:
                return 1
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0
    
    def doRollover(self):
        self.logger.debug("Performing rollover")
        if self.stream:
            self.stream.close()
        current_time = int(time.time())
        base_filename_with_path, ext = os.path.splitext(self.baseFilename)
        base_filename = os.path.basename(base_filename_with_path)
        dir_name = os.path.dirname(base_filename_with_path)    
        match = re.search(r'(\d{4}-\d{2}-\d{2})', base_filename)
        if match:
            base_date = match.group(1)
        else:
            base_date = None
        current_date = time.strftime("%Y-%m-%d", time.localtime(current_time))   
        if base_date:
            base_filename_without_date = base_filename.replace(f"-{base_date}", "")
        else:
            base_filename_without_date = base_filename    
        for i in range(self.backupCount - 1, 0, -1):
            sfn = os.path.join(dir_name, f"{base_filename_without_date}-{base_date}_{i}.log" if base_date else f"{base_filename_without_date}_{i}.log")
            dfn = os.path.join(dir_name, f"{base_filename_without_date}-{base_date}_{i + 1}.log" if base_date else f"{base_filename_without_date}_{i + 1}.log")
            if os.path.exists(sfn):
                self.logger.debug(f"Renaming {sfn} to {dfn}")
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)   
        dfn = os.path.join(dir_name, f"{base_filename_without_date}-{base_date}_1.log" if base_date else f"{base_filename_without_date}_1.log")
        self.logger.debug(f"Renaming {self.baseFilename} to {dfn}")
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)    
        if self.backupCount > 0:
            files_to_delete = self.getFilesToDelete(base_filename_without_date)
            for s in files_to_delete:
                self.logger.debug(f"Deleting old log file {s}")
                os.remove(s)
        new_log_filename = os.path.join(dir_name, f"{base_filename_without_date}-{current_date}.log")
        self.baseFilename = new_log_filename
        if not self.delay:
            self.stream = self._open()
        self.rolloverAt = self.computeRollover(current_time)

    def getFilesToDelete(self, base_filename):
        dir_name = os.path.dirname(self.baseFilename)
        file_names = os.listdir(dir_name)
        result = []
        base_filename_without_date = re.sub(r'-\d{4}-\d{2}-\d{2}', '', os.path.basename(base_filename))
        base_filename_pattern = re.escape(base_filename_without_date) + r"-\d{4}-\d{2}-\d{2}(_\d+)?\.log$"
        self.logger.debug(f"Base filename pattern: {base_filename_pattern}")
        pattern = re.compile(base_filename_pattern)
        for file_name in file_names:
            self.logger.debug(f"Checking file: {file_name}")
            if pattern.match(file_name):
                self.logger.debug(f"Matched file: {file_name}")
                result.append(os.path.join(dir_name, file_name))
        result.sort(key=lambda x: (self.extract_date(x), self.extract_index(x)))
        self.logger.debug(f"Files considered for deletion: {result}")
        if len(result) <= self.backupCount:
            return []
        else:
            files_to_delete = result[:len(result) - self.backupCount]
            self.logger.debug(f"Files to delete: {files_to_delete}")
            return files_to_delete

    @staticmethod
    def extract_date(file_path):
        file_name = os.path.basename(file_path)
        match = re.search(r"(\d{4}-\d{2}-\d{2})", file_name)
        if match:
            return match.group(1)
        return "9999-99-99"

    @staticmethod
    def extract_index(file_path):
        file_name = os.path.basename(file_path)
        match = re.search(r"_(\d+)\.log$", file_name)
        if match:
            return int(match.group(1))
        return 0

def parse_size(size_str):
    size_str = size_str.strip().upper()
    if size_str.endswith('K'):
        return int(size_str[:-1]) * 1024
    elif size_str.endswith('M'):
        return int(size_str[:-1]) * 1024 * 1024
    elif size_str.endswith('G'):
        return int(size_str[:-1]) * 1024 * 1024 * 1024
    else:
        return int(size_str)

def get_logger(log_name='DMB', log_dir='./log'):
    current_date = time.strftime("%Y-%m-%d")
    log_filename = f"{log_name}-{current_date}.log"
    logger = logging.getLogger(log_name)
    backupCount_env = os.getenv('DMB_LOG_COUNT')
    try:
        backupCount = int(backupCount_env)
    except (ValueError, TypeError):
        backupCount = 2
    log_level_env = os.getenv('DMB_LOG_LEVEL')
    if log_level_env:
        log_level = log_level_env.upper()
        os.environ['LOG_LEVEL'] = log_level
        os.environ['RCLONE_LOG_LEVEL'] = log_level
    else:
        log_level = 'INFO'
    numeric_level = getattr(logging, log_level, logging.INFO)   
    logger.setLevel(numeric_level)  
    max_log_size_env = os.getenv('DMB_LOG_SIZE')
    try:
        max_log_size = parse_size(max_log_size_env) if max_log_size_env else 10 * 1024 * 1024
    except (ValueError, TypeError):
        max_log_size = 10 * 1024 * 1024
    
    log_path = os.path.join(log_dir, log_filename)
    handler = CustomRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=backupCount, maxBytes=max_log_size)
    os.chmod(log_path, 0o666)
    

    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%b %e, %Y %H:%M:%S')
    handler.setFormatter(file_formatter)

    enable_color_log = os.getenv('COLOR_LOG_ENABLED', 'false').lower() == 'true'
    if enable_color_log:
        color_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
            datefmt='%b %e, %Y %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
            secondary_log_colors={
                'message': {
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red',
                },
                'levelname': {
                    'DEBUG': 'blue',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red',
                },
            },
            style='%'
        )
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(color_formatter)
    else:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(file_formatter)
    
    for hdlr in logger.handlers[:]:
        logger.removeHandler(hdlr)
    logger.addHandler(handler)
    logger.addHandler(stdout_handler)
    return logger