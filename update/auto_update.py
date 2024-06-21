from base import *


class BaseUpdate:
    def __init__(self):
        self.logger = get_logger()
        self.process = None

    def start_process(self, process_name, config_dir, command, key_type):
        try:
            if key_type:
                self.logger.info(f"Starting {process_name} w/ {key_type}")
            else:
                self.logger.info(f"Starting {process_name}")
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                cwd=config_dir,
                universal_newlines=True,
                bufsize=1
            )
            self.subprocess_logger = SubprocessLogger(self.logger, f"{process_name} w/ {key_type}")
            self.subprocess_logger.start_logging_stdout(self.process)
            self.subprocess_logger.start_monitoring_stderr(self.process, key_type, process_name)
        except Exception as e:
            self.logger.error(f"Error running subprocess for {process_name} w/ {key_type}: {e}")

    def update_schedule(self):
        self.update_check()
        interval_minutes = int(self.auto_update_interval() * 60)
        schedule.every(interval_minutes).minutes.do(self.update_check)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def auto_update_interval(self):
        if os.getenv('AUTO_UPDATE_INTERVAL') is None:
            interval = 24
        else:
            interval = float(os.getenv('AUTO_UPDATE_INTERVAL'))
        return interval

    def auto_update(self, process_name, enable_update):
        if enable_update:
            self.logger.info(f"Automatic updates set to {format_time(self.auto_update_interval())} for {process_name}")
            self.schedule_thread = threading.Thread(target=self.update_schedule)
            self.schedule_thread.start()
            self.start_process(process_name)
        else:
            self.logger.info(f"Automatic update disabled for {process_name}")
            self.start_process(process_name)
