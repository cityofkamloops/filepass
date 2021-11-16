import os
import datetime

log_to_screen = os.environ.get('LOGTOSCREEN')
log_to_file = os.environ.get('LOGTOFILE')


class FPLogger:

    def __init__(self):
        self.level_name = {0: 'INFO', 1: 'WARNING', 2: 'ERROR', 3: 'CRITICAL'}
        self.event_datetime = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
        # %Y%m%d %H%M%S

    def screen_print(self, date_time, level, message):
        print('{} - {}: {}'.format(date_time, level, message))

    def file_print(self, level, message):
        pass

    def write(self, logging_level, log_message):
        if log_to_screen == 'yes':
            self.screen_print(self.event_datetime, self.level_name[logging_level], log_message)
