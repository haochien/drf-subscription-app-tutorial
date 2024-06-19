from django.conf import settings
import os

env = settings.ENV

def init_log_path():
    log_file_path = os.path.join(env('LOG_FILE_FOLDER'), env('LOG_FILE_NAME'))
    if not (os.path.exists(env('LOG_FILE_FOLDER'))):
        os.makedirs(env('LOG_FILE_FOLDER'))
        open(log_file_path, 'w').close()

    return log_file_path