import os
from mail_copy_input_format import get_mail_in_format
from cargo_result_processing import get_cargo_result_df
from compare_and_checker import compare_total_and_cargo

from config.config_env import Config

def main() :

    if os.path.isfile(Config().mail_copy_in_path):
         get_mail_in_format(Config().mail_copy_in_path)
    else:
        print('INPUT FORMAT EXCEL PATH is not found !')


    if os.path.isfile(Config().cargo_path):
        get_cargo_result_df(Config().cargo_path)
    else:
        print('CARGO ,EXCEL PATH is not found !')
    
    # compare_total_and_cargo()

if __name__ == "__main__":
    main()