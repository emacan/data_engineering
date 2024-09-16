import os

current_directory = None

def init_working_dir():
    global current_directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

def get_absolute_path(relative_path):
    if not current_directory:
        init_working_dir()
    file_path = os.path.join(current_directory, relative_path)
    return file_path
