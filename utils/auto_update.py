from base import *
from utils.global_logger import logger
from utils.logger import format_time


class Update:
    _scheduler_initialized = False
    _jobs = {}

    def __init__(self, process_handler):
        self.process_handler = process_handler
        self.logger = process_handler.logger
        self.updating = threading.Lock()

        if not Update._scheduler_initialized:
            self.scheduler = schedule.Scheduler()
            Update._scheduler_initialized = True
        else:
            self.scheduler = schedule.default_scheduler

    def update_schedule(self, process_name):
        interval_minutes = int(self.auto_update_interval() * 60)
        self.logger.debug(
            f"Scheduling automatic update check every {interval_minutes} minutes for {process_name}"
        )

        if process_name not in Update._jobs:
            self.scheduler.every(interval_minutes).minutes.do(
                self.scheduled_update_check, process_name
            )
            Update._jobs[process_name] = True
            self.logger.debug(f"Scheduled automatic update check for {process_name}")

        while True:
            self.scheduler.run_pending()
            time.sleep(1)

    def auto_update_interval(self):
        if os.getenv("AUTO_UPDATE_INTERVAL") is None:
            interval = 24
        else:
            interval = float(os.getenv("AUTO_UPDATE_INTERVAL"))
        return interval

    def auto_update(self, process_name, enable_update):
        if enable_update:
            self.logger.info(
                f"Automatic updates set to {format_time(self.auto_update_interval())} for {process_name}"
            )
            self.schedule_thread = threading.Thread(
                target=self.update_schedule, args=(process_name,)
            )
            self.schedule_thread.start()
            self.initial_update_check(process_name)
        else:
            self.logger.info(f"Automatic update disabled for {process_name}")
            self.start_process(process_name)

    def initial_update_check(self, process_name):
        with self.updating:
            if not self.update_check(process_name):
                self.start_process(process_name)

    def scheduled_update_check(self, process_name):
        with self.updating:
            self.update_check(process_name)
