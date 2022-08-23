import os
import pandas as pd
import json
from config.config_env import Config
from check_valid_data import call_error_message_compare_cargo_and_total
# import numpy as np

def _read_excel_df(filepath,sheet):
    df = pd.read_excel(filepath,sheet_name= sheet)
    return df

def _read_total_mail_df():
    if os.path.isfile(Config().tot_excel_from_mail):
        tot_one_car_sheet = Config().total_one_car_sheet_name
        tot_mul_car_sheet = Config().total_mul_car_sheet_name
        tot_one_car_df = _read_excel_df(Config().tot_excel_from_mail,tot_one_car_sheet)
        tot_mul_car_df = _read_excel_df(Config().tot_excel_from_mail,tot_mul_car_sheet)
    else:
        print('TOTAL MAIL EXCEL PATH is not found !')
    return tot_one_car_df,tot_mul_car_df

def _read_cargo_df():
    if os.path.isfile(Config().cargo_path):
        cargo_sheet = Config().result_carco_sheet
        df =_read_excel_df(Config().export_info_from_cargo_path,cargo_sheet)
    else:
        print('CARGO ,EXCEL PATH is not found !')
    return df

def _duplicate_cnt_dict(_list):
    count = {}
    for i in _list:
        try: count[i] += 1
        except: count[i]=1
    return count

def _compare_total_count(tot_one_car_df,tot_mul_car_df,cargo_result_df):
    cargo_one_car_df = cargo_result_df.copy().loc[(cargo_result_df['car_count'] == 1),:]
    cargo_mul_car_df = cargo_result_df.copy().loc[(cargo_result_df['car_count'] != 1),:]

    one_car_cnt = len(tot_one_car_df)
    mul_car_cnt = len(tot_mul_car_df)
    total_mail_cnt = one_car_cnt + mul_car_cnt
    
    cargo_one_cnt = len(cargo_one_car_df)
    cargo_mul_cnt = len(cargo_mul_car_df)
    cargo_cnt = len(cargo_result_df)

    if total_mail_cnt == cargo_cnt:
        if (one_car_cnt == cargo_one_cnt) and (mul_car_cnt == cargo_mul_cnt):
            same_count = True
            same_one_count,same_mul_count = True,True
        elif one_car_cnt == cargo_one_cnt:
            same_count = False
            same_one_count,same_mul_count = True,False
            print('MULTI COUNT DIFFER')
        elif mul_car_cnt == cargo_mul_cnt:
            same_count = False
            same_one_count,same_mul_count = False,True
            print('ONE COUNT DIFFER')
        else :
            same_count = False
            same_one_count,same_mul_count = False,False
            print('BOTH DIFFER')
    else:
        same_count = False
        same_one_count,same_mul_count = False,False
        print('TOTAL COUNT DIFFER')

    return same_count,same_one_count,same_mul_count

def _json_to_list(json_format):
    _dict = json.loads(json_format)
    _list = []
    for key in _dict:
        _list.append(_dict[key])
        
    return _list

def _check_mul_acid_for_chassino(cargo_mul_chassino,cargo_mul_acid,tot_mul_car_df):
    matching_possibilty = 0
    matched_df = pd.DataFrame()
    check_acid = False
    check_chassino = False
    cargo_mul_chassino_list = _json_to_list(cargo_mul_chassino)

    tot_mul_acid_df = tot_mul_car_df.copy().loc[(tot_mul_car_df['ACID NO']==cargo_mul_acid),:]    
    if tot_mul_acid_df.empty:
        check_acid = False
        check_chassino = False
    elif len(tot_mul_acid_df) == 1:
        tot_mul_chassino = tot_mul_acid_df['CHASSINO'].values[0]
        tot_mul_chassino_list = _json_to_list(tot_mul_chassino)
        common_set_list = list(set(tot_mul_chassino_list) & set(cargo_mul_chassino_list))

        if len(common_set_list) == 0: #0% matching
            check_acid = True
            check_chassino = False
        elif len(tot_mul_chassino_list) == len(common_set_list): #100% matching
            check_acid = True
            check_chassino = True
        else : 
            check_acid = True #partially matching
            check_chassino = False
    else:
        # ACID가 여러개 matching되었을 때,
        for idx in tot_mul_acid_df.index:
            tot_mul_chassino = tot_mul_acid_df._get_value(idx,'CHASSINO')
            tot_mul_chassino_list = _json_to_list(tot_mul_chassino)
            common_set_list = list(set(tot_mul_chassino_list) & set(cargo_mul_chassino_list))
            if len(common_set_list) > matching_possibilty:
                matching_possibilty = len(common_set_list)
                matched_df = tot_mul_acid_df.copy().loc[idx,:]
            
            if check_acid:
                pass
            else:
                if len(common_set_list) == 0:
                    check_acid = True #0% matching
                    check_chassino = False
                elif len(common_set_list) == matching_possibilty: 
                    check_acid = True 
                    check_chassino = True
                else:  
                    check_acid = True #0 Partially matching
                    check_chassino = False
                    
        tot_mul_acid_df = matched_df
    return check_acid,check_chassino,tot_mul_acid_df


def _check_chassino(cargo_one_chassino,tot_one_car_df):
    tot_one_chassino_df = tot_one_car_df.copy().loc[(tot_one_car_df['CHASSINO']==cargo_one_chassino),:]
    if tot_one_chassino_df.empty:
        check_chassino = False
    elif len(tot_one_chassino_df) == 1:
        check_chassino = True
    else:
        check_chassino = True
        tot_one_chassino_df = tot_one_chassino_df.drop_duplicate() 

    return check_chassino,tot_one_chassino_df

def _check_con(idx,cargo_one_car_df,match_df):
    cargo_one_car_df = cargo_one_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_one_con = cargo_one_car_df._get_value(idx,'CONSIGNEE NAME')
    tot_one_con = match_df['CONSIGNEE NAME'].values[0]
    return cargo_one_con == tot_one_con

def _check_model(idx,cargo_one_car_df,match_df):
    cargo_one_car_df = cargo_one_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_one_model = cargo_one_car_df._get_value(idx,'MODEL')
    tot_one_model = match_df['MODEL'].values[0]
    return cargo_one_model == tot_one_model

def _check_year(idx,cargo_one_car_df,match_df):
    cargo_one_car_df = cargo_one_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_one_year = cargo_one_car_df._get_value(idx,'YR')
    tot_one_year = match_df['YR'].values[0]
    return cargo_one_year == tot_one_year

def _check_acid(idx,cargo_one_car_df,match_df):
    cargo_one_car_df = cargo_one_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_one_acid = cargo_one_car_df._get_value(idx,'ACID_NO')
    tot_one_acid = match_df['ACID NO'].values[0]
    return cargo_one_acid == tot_one_acid

def _check_export_id(idx,cargo_one_car_df,match_df):
    cargo_one_car_df = cargo_one_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_one_export_id = cargo_one_car_df._get_value(idx,'FREIGHT_FORWARDER_ID')
    tot_one_export_id = match_df['FREIGHT FORWARDER ID'].values[0]
    return cargo_one_export_id == tot_one_export_id

def _check_import_num(idx,cargo_one_car_df,match_df):
    cargo_one_car_df = cargo_one_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_one_import_num = cargo_one_car_df._get_value(idx,'IMPORTER_TAX_NUMBER')
    tot_one_import_num = match_df['IMPORTER TAX NUMBER'].values[0]
    return cargo_one_import_num == tot_one_import_num

def _check_mul_con(idx,cargo_mul_car_df,match_df):
    cargo_mul_car_df = cargo_mul_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_mul_con = cargo_mul_car_df._get_value(idx,'CONSIGNEE NAME')
    tot_mul_con = match_df['CONSIGNEE NAME:'].values[0]
    return cargo_mul_con == tot_mul_con

def _check_mul_model(idx,cargo_mul_car_df,match_df):
    cargo_mul_model_dict = {}
    tot_mul_model = {}
    match_cnt = 0
    tot_cnt = 0
    cargo_cnt = 0
    
    cargo_mul_car_df = cargo_mul_car_df.astype(str)
    match_df = match_df.astype(str)

    cargo_mul_model = cargo_mul_car_df._get_value(idx,'MODEL')
    tot_mul_model = match_df['MODEL'].values[0]
    
    cargo_mul_model_list = _json_to_list(cargo_mul_model)
    tot_mul_model_list = _json_to_list(tot_mul_model)
    
    cargo_mul_model_dict = _duplicate_cnt_dict(cargo_mul_model_list)
    tot_mul_model_dict = _duplicate_cnt_dict(tot_mul_model_list) 

    for key in cargo_mul_model_dict:
        cargo_model_cnt = cargo_mul_model_dict[key]
        cargo_cnt = cargo_cnt + cargo_model_cnt
        
    for key in tot_mul_model_dict:
        try:
            cargo_model_cnt = cargo_mul_model_dict[key]
        except:
            cargo_model_cnt = 0
        
        tot_model_cnt = tot_mul_model_dict[key]
        
        if cargo_model_cnt == tot_model_cnt:
            match_cnt = match_cnt+1
        else: pass
        
        tot_cnt = tot_cnt + tot_model_cnt
        
    common_set_list = list(set(tot_mul_model_list) & set(cargo_mul_model_list))
    if tot_cnt == cargo_cnt:
        if match_cnt == len(common_set_list):
            check_mul_model = True
        else:
            check_mul_model = False
    else :
        check_mul_model = False
    
    return check_mul_model

def _check_mul_year(idx,cargo_mul_car_df,match_df):
    cargo_mul_year_dict = {}
    tot_mul_year = {}
    match_cnt = 0
    tot_cnt = 0
    cargo_cnt = 0
    
    cargo_mul_car_df = cargo_mul_car_df.astype(str)
    match_df = match_df.astype(str)

    cargo_mul_year = cargo_mul_car_df._get_value(idx,'YR')
    tot_mul_year = match_df['YR'].values[0]
    
    cargo_mul_year_list = _json_to_list(cargo_mul_year)
    tot_mul_year_list = _json_to_list(tot_mul_year)

    cargo_mul_year_list = list(map(float,cargo_mul_year_list))
    cargo_mul_year_list = list(map(int,cargo_mul_year_list))
    cargo_mul_year_list = list(map(str,cargo_mul_year_list))
    
    tot_mul_year_list = list(map(float,tot_mul_year_list))
    tot_mul_year_list = list(map(int,tot_mul_year_list))
    tot_mul_year_list = list(map(str,tot_mul_year_list))
    
    cargo_mul_year_dict = _duplicate_cnt_dict(cargo_mul_year_list)
    tot_mul_year_dict = _duplicate_cnt_dict(tot_mul_year_list) 

    for key in cargo_mul_year_dict:
        cargo_year_cnt = cargo_mul_year_dict[key]
        cargo_cnt = cargo_cnt + cargo_year_cnt
        
    for key in tot_mul_year_dict:
        try:
            cargo_year_cnt = cargo_mul_year_dict[key]
        except:
            cargo_year_cnt = 0
        
        tot_year_cnt = tot_mul_year_dict[key]
        
        if cargo_year_cnt == tot_year_cnt:
            match_cnt = match_cnt+1
        else: pass
        
        tot_cnt = tot_cnt + tot_year_cnt
        
    common_set_list = list(set(tot_mul_year_dict) & set(cargo_mul_year_dict))

    if tot_cnt == cargo_cnt:
        if match_cnt == len(common_set_list):
            check_mul_year = True
        else:
            check_mul_year = False
    else :
        check_mul_year = False
    
    return check_mul_year


def _check_mul_acid(idx,cargo_mul_car_df,match_df):
    cargo_mul_car_df = cargo_mul_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_mul_acid = cargo_mul_car_df._get_value(idx,'ACID_NO')
    tot_mul_acid = match_df['ACID NO'].values[0]
    return cargo_mul_acid == tot_mul_acid

def _check_mul_export_id(idx,cargo_mul_car_df,match_df):
    cargo_mul_car_df = cargo_mul_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_mul_export_id = cargo_mul_car_df._get_value(idx,'FREIGHT_FORWARDER_ID')
    tot_mul_export_id = match_df['FOREIGN EXPORTER REGISTRATION NUMBER'].values[0]
    return cargo_mul_export_id == tot_mul_export_id

def _check_mul_import_num(idx,cargo_mul_car_df,match_df):
    cargo_mul_car_df = cargo_mul_car_df.astype(str)
    match_df = match_df.astype(str)
    
    cargo_mul_import_num = cargo_mul_car_df._get_value(idx,'IMPORTER_TAX_NUMBER')
    tot_mul_import_num = match_df['EGYPTIAN IMPORTER VAT NUMBER '].values[0]
    return cargo_mul_import_num == tot_mul_import_num






def _compare_one_car_info(tot_one_car_df,cargo_result_df):
    cargo_one_car_df = cargo_result_df.copy().loc[(cargo_result_df['car_count'] == 1),:]

    err_cnt = 0
    err_dict = {}
    err_chassino_list = []
    err_con_list = []
    err_model_list = []
    err_year_list = []
    err_acid_list = []
    err_export_id_list = []
    err_import_num_list = []


    for idx in cargo_one_car_df.index:
        cargo_one_chassino = cargo_one_car_df._get_value(idx,'CHASSINO')
        check_chassino,match_df = _check_chassino(cargo_one_chassino,tot_one_car_df)
        
        if check_chassino:

            check_con = _check_con(idx,cargo_one_car_df,match_df)
            check_model = _check_model(idx,cargo_one_car_df,match_df)
            check_year = _check_year(idx,cargo_one_car_df,match_df)
            check_acid = _check_acid(idx,cargo_one_car_df,match_df)
            check_export_id = _check_export_id(idx,cargo_one_car_df,match_df)
            check_import_num = _check_import_num(idx,cargo_one_car_df,match_df)

            if not check_con: err_con_list.append(idx+2)
            if not check_model: err_model_list.append(idx+2)
            if not check_year: err_year_list.append(idx+2)
            if not check_acid: err_acid_list.append(idx+2)
            if not check_export_id: err_export_id_list.append(idx+2)
            if not check_import_num: err_import_num_list.append(idx+2)
            
        else:
            err_chassino_list.append(idx+2)
    
    if err_chassino_list:
        err_cnt = err_cnt + 1
        err_col = 'J'
        err_chassino_dict = {err_cnt:(err_chassino_list,err_col,'CHASSINO_INFO')}
        err_dict.update(err_chassino_dict)
    if err_con_list:
        err_cnt = err_cnt + 1
        err_col = 'D'
        err_con_dict = {err_cnt:(err_con_list,err_col,'CONSIGNEE_INFO')}
        err_dict.update(err_con_dict)
    if err_model_list:
        err_cnt = err_cnt + 1
        err_col = 'H'
        err_model_dict = {err_cnt:(err_model_list,err_col,'MODEL_INFO')}
        err_dict.update(err_model_dict)
    if err_year_list:
        err_cnt = err_cnt + 1
        err_col = 'I'
        err_year_dict = {err_cnt:(err_year_list,err_col,'YEAR_INFO')}
        err_dict.update(err_year_dict)
    if err_acid_list:
        err_cnt = err_cnt + 1
        err_col = 'K'
        err_acid_dict = {err_cnt:(err_acid_list,err_col,'ACID_INFO')}
        err_dict.update(err_acid_dict)
    if err_export_id_list:
        err_cnt = err_cnt + 1
        err_col = 'L'
        err_export_id_dict = {err_cnt:(err_export_id_list,err_col,'EXPORTER_ID_INFO')}
        err_dict.update(err_export_id_dict)
    if err_import_num_list:
        err_cnt = err_cnt + 1
        err_col = 'M'
        err_import_num_dict = {err_cnt:(err_import_num_list,err_col,'IMPORTER_NUM_INFO')}
        err_dict.update(err_import_num_dict)

    return err_dict

def _compare_mul_car_info(tot_mul_car_df,cargo_result_df):
    cargo_mul_car_df = cargo_result_df.copy().loc[(cargo_result_df['car_count'] != 1),:]

    err_mul_cnt = 0
    err_mul_dict = {}
    err_mul_chassino_list = []
    err_mul_con_list = []
    err_mul_model_list = []
    err_mul_year_list = []
    err_mul_acid_list = []
    err_mul_export_id_list = []
    err_mul_import_num_list = []


    for idx in cargo_mul_car_df.index:
        cargo_mul_chassino = cargo_mul_car_df._get_value(idx,'CHASSINO')
        cargo_mul_acid = cargo_mul_car_df._get_value(idx,'ACID_NO')
        check_acid,check_chassino,match_df = _check_mul_acid_for_chassino(cargo_mul_chassino,cargo_mul_acid,tot_mul_car_df)        

        if check_chassino:
            check_mul_con = _check_mul_con(idx,cargo_mul_car_df,match_df)
            check_mul_model = _check_mul_model(idx,cargo_mul_car_df,match_df)
            check_mul_year = _check_mul_year(idx,cargo_mul_car_df,match_df)
            check_mul_acid = _check_mul_acid(idx,cargo_mul_car_df,match_df)
            check_mul_export_id = _check_mul_export_id(idx,cargo_mul_car_df,match_df)
            check_mul_import_num = _check_mul_import_num(idx,cargo_mul_car_df,match_df)

            
            if not check_mul_con: err_mul_con_list.append(idx+2)
            if not check_mul_model: err_mul_model_list.append(idx+2)
            if not check_mul_year: err_mul_year_list.append(idx+2)
            if not check_mul_acid: err_mul_acid_list.append(idx+2)
            if not check_mul_export_id: err_mul_export_id_list.append(idx+2)
            if not check_mul_import_num: err_mul_import_num_list.append(idx+2)

        elif check_acid:
            err_mul_chassino_list.append(idx+2)
        else:
            err_mul_acid_list.append(idx+2)
            
            
    if err_mul_chassino_list:
        err_mul_cnt = err_mul_cnt + 1
        err_mul_col = 'J'
        err_chassino_dict = {err_mul_cnt:(err_mul_chassino_list,err_mul_col,'MUL_CHASSINO_INFO')}
        err_mul_dict.update(err_chassino_dict)
    if err_mul_con_list:
        err_mul_cnt = err_mul_cnt + 1
        err_mul_col = 'D'
        err_con_dict = {err_mul_cnt:(err_mul_con_list,err_mul_col,'MUL_CONSIGNEE_INFO')}
        err_mul_dict.update(err_con_dict)
    if err_mul_model_list:
        err_mul_cnt = err_mul_cnt + 1
        err_mul_col = 'H'
        err_model_dict = {err_mul_cnt:(err_mul_model_list,err_mul_col,'MUL_MODEL_INFO')}
        err_mul_dict.update(err_model_dict)
    if err_mul_year_list:
        err_mul_cnt = err_mul_cnt + 1
        err_mul_col = 'I'
        err_year_dict = {err_mul_cnt:(err_mul_year_list,err_mul_col,'MUL_YEAR_INFO')}
        err_mul_dict.update(err_year_dict)
    if err_mul_acid_list:
        err_mul_cnt = err_mul_cnt + 1
        err_mul_col = 'K'
        err_acid_dict = {err_mul_cnt:(err_mul_acid_list,err_mul_col,'MUL_ACID_INFO')}
        err_mul_dict.update(err_acid_dict)
    if err_mul_export_id_list:
        err_mul_cnt = err_mul_cnt + 1
        err_mul_col = 'L'
        err_export_id_dict = {err_mul_cnt:(err_mul_export_id_list,err_mul_col,'MUL_EXPORTER_ID_INFO')}
        err_mul_dict.update(err_export_id_dict)
    if err_mul_import_num_list:
        err_mul_cnt = err_mul_cnt + 1
        err_mul_col = 'M'
        err_import_num_dict = {err_mul_cnt:(err_mul_import_num_list,err_mul_col,'MUL_IMPORTER_NUM_INFO')}
        err_mul_dict.update(err_import_num_dict)
    return err_mul_dict



def _compare_total_and_cargo():
    tot_one_car_df,tot_mul_car_df = _read_total_mail_df()
    cargo_result_df = _read_cargo_df()

    same_count,same_one_count,same_mul_count = _compare_total_count(tot_one_car_df,tot_mul_car_df,cargo_result_df)

    if same_count:
        err_one_car_dict = _compare_one_car_info(tot_one_car_df,cargo_result_df)
        err_mul_car_dict = _compare_mul_car_info(tot_mul_car_df,cargo_result_df)

        if err_one_car_dict:
            call_error_message_compare_cargo_and_total(err_one_car_dict)
        else:
            print("Same Total Count : One Car One BL All Matched")
        
        if err_mul_car_dict:
            call_error_message_compare_cargo_and_total(err_mul_car_dict)
        else:
            print("Same Total Count : Multi Car One BL All Matched")
    else:
        if same_one_count:
            err_one_car_dict = _compare_one_car_info(tot_one_car_df,cargo_result_df)

            if err_one_car_dict:
                call_error_message_compare_cargo_and_total(err_one_car_dict)
            else:
                print("Same One Count : Multi Car One BL All Matched")

        elif same_mul_count:
            err_mul_car_dict = _compare_mul_car_info(tot_mul_car_df,cargo_result_df)

            if err_mul_car_dict:
                call_error_message_compare_cargo_and_total(err_mul_car_dict)
            else:
                print("Same Multi Count : Multi Car One BL All Matched")
        else :
            print("Differ Total Count")


def compare_total_and_cargo():
    
    print('Do you want to check and compare between total_data_from_mail and result_cargo?')
    compare_option = input('1 : Y(Yes) or  0: N(No) : ')
    compare_option = compare_option.upper()

    if compare_option in ['1', 'Y','YES']:
        _compare_total_and_cargo()
    else:
        pass

    





