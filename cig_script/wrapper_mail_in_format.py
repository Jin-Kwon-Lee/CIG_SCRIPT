import os
from mail_copy_input_format import get_mail_in_format
from config.config_env import Config


def main_mail() :
    if os.path.isfile(Config().mail_copy_in_path):
         get_mail_in_format(Config().mail_copy_in_path)
    else:
        print('INPUT FORMAT EXCEL PATH is not found !')

if __name__ == "__main__":
    main_mail()