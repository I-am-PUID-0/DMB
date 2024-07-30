from base import *
from utils.logger import *
from utils.processes import ProcessHandler

class Update(ProcessHandler):
    def __init__(self):
        logger = get_logger()
        super().__init__(logger)

    def update_schedule(self, process_name):
        #self.update_check(process_name)
        interval_minutes = int(self.auto_update_interval() * 60)
        schedule.every(interval_minutes).minutes.do(self.update_check, process_name)

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
            initial_update = self.update_check(process_name)
            self.schedule_thread = threading.Thread(target=self.update_schedule, args=(process_name,))
            self.schedule_thread.start()
            if not initial_update:
                self.start_process(process_name)
        else:
            self.logger.info(f"Automatic update disabled for {process_name}")
            self.start_process(process_name)

