
import os
import pandas as pd
import numpy as np
import re
import json

from config.config_env import Config

from datetime import datetime
from one_car_one_bl import _get_one_mail_dict
from mul_car_one_bl import _get_mul_mail_dict
from common_mail_script import _reset_index
from excel_mail_info import _export_tot_xl_mail_info
from excel_mail_info import _export_cur_xl_mail_info


def _get_all_sheet_from_mail(mail_copy_in_path,one_sheet_list,mul_sheet_list):
    df = pd.read_excel(mail_copy_in_path,sheet_name=None,header= None)
    sheet_list = list(df.keys())
    for sheet in sheet_list:
        mul_sheet = re.search('\w+_MUL',sheet)
        if mul_sheet:
            mul_sheet_list.append(sheet)
        else:
            one_sheet_list.append(sheet)

    return one_sheet_list,mul_sheet_list

def get_mail_in_format(mail_copy_in_path):
    mul_sheet_list = []
    one_sheet_list = []
    one_result_dict = {}
    mul_result_dict = {}

    one_sheet_list,mul_sheet_list = _get_all_sheet_from_mail(mail_copy_in_path,one_sheet_list,mul_sheet_list)

    print('Do you want to merge current mail info in TOTAL sheet?')
    total_option = input('1 : Y(Yes) or  0: N(No) : ')

    if one_sheet_list and mul_sheet_list:
        one_result_dict = _get_one_mail_dict(mail_copy_in_path,one_result_dict,one_sheet_list)
        mul_result_dict = _get_mul_mail_dict(mail_copy_in_path,mul_result_dict,mul_sheet_list)
    elif one_sheet_list:
        one_result_dict = _get_one_mail_dict(mail_copy_in_path,one_result_dict,one_sheet_list)
    elif mul_sheet_list:
        mul_result_dict = _get_mul_mail_dict(mail_copy_in_path,mul_result_dict,mul_sheet_list)
    else:
        pass
    
    _export_tot_xl_mail_info(one_result_dict,mul_result_dict,total_option)
    _export_cur_xl_mail_info(one_result_dict,mul_result_dict)


            

    