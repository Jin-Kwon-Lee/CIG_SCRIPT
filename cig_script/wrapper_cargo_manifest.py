import os
from cargo_result_processing import get_cargo_result_df
from config.config_env import Config

def main_cargo() :

    if os.path.isfile(Config().cargo_path):
        get_cargo_result_df(Config().cargo_path)
    else:
        print('CARGO ,EXCEL PATH is not found !')


if __name__ == "__main__":
    main_cargo()