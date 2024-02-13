import os
from thsr_helper.settings import settings


def get_config_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, settings.config_file_path)
