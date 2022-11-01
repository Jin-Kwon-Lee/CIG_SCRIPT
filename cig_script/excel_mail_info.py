import os
import pandas as pd
import numpy as np
import re
import json

from tqdm import tqdm
from datetime import datetime

from config.config_env import Config
from common_mail_script import _reset_index
from one_car_one_bl import _get_one_car_macro_form
from check_valid_data import call_error_message_edi_error
from check_valid_data import call_error_message_chassino_duplicate_error
from check_valid_data import call_modify_message_input_detail

# from cig_script.config.config_env import Config
# from cig_script.common_mail_script import _reset_index
# from cig_script.one_car_one_bl import _get_one_car_macro_form


def _excel_decorator(func):
    def wrapper(*args, **kargs):
        print('')
        print("SUB SHEET UPDATE started!")
        print("Function Name : ",func.__name__)
        result = func(*args, **kargs)
        print("SUB SHEET UPDATE complete!")
        print('')
        return result
    return wrapper

def _excel_total_decorator(func):
    def wrapper(*args, **kargs):
        print('')
        print("TOTAL SHEET UPDATE started!")
        print("Function Name : ",func.__name__)
        result = func(*args, **kargs)
        print("TOTAL SHEET UPDATE complete!")
        print('')
        return result
    return wrapper

def _autowidth_excel(writer,sheet_name,df):
    margin = 5
    for column in df:
        column_length = len(column) + margin
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)


def _write_or_update_excel(_file_path,_sheet,_df):
    _df = _df.astype(str)

    if not os.path.exists(_file_path):
        with pd.ExcelWriter(_file_path, mode= 'w') as writer: 
            _df.to_excel(writer,_sheet,index=False)
            _autowidth_excel(writer,_sheet,_df)
    else:
        with pd.ExcelWriter(_file_path, mode= 'a',engine='openpyxl',if_sheet_exists='overlay') as writer: 
            _df.to_excel(writer,_sheet,index=False)

def _get_BL_no_from_edi_info(tot_df,sub_car_df,edi_df):
    if sub_car_df.empty:
        pass
    else:
        edi_no_list = edi_df['EDI NO.'].dropna().drop_duplicates().values
        f_p = re.compile("\w+F\d+")
        edi_f_list = list(filter(f_p.match,edi_no_list))
        _h_bl_no = 0

        tot_h_bl_list = tot_df.H_BL_NO.tolist()
        tot_h_bl_wo_edi_list = list(set(tot_h_bl_list) - set(edi_no_list))

        missed_edi_list = list(set(edi_f_list) - set(tot_h_bl_list))
    
        for row in sub_car_df.CHASSINO.iteritems():
            idx,val = row
            mul_chassino = {}
            one_chassino = ''
            edi_no = ''
            try:
                mul_chassino = json.loads(val) 
            except:
                one_chassino = val
            if one_chassino:
                try:
                    edi_no = edi_df.loc[(edi_df['CHASSINO.'] == val),'EDI NO.'].values[0]
                    weight = edi_df.loc[(edi_df['CHASSINO.'] == val),'WEIGHT'].values[0]
                    cbm = edi_df.loc[(edi_df['CHASSINO.'] == val),'CBM'].values[0]
                except:
                    print('there is no matched EDI NUM for : ', )
            
            if mul_chassino:
                first_key = next(iter(mul_chassino))
                mul_chassino_first_value = mul_chassino[first_key]
                try:
                    edi_no = edi_df.loc[(edi_df['CHASSINO.'] == mul_chassino_first_value),'EDI NO.'].values[0]
                    weight = edi_df.loc[(edi_df['CHASSINO.'] == mul_chassino_first_value),'WEIGHT'].values[0]
                    cbm = edi_df.loc[(edi_df['CHASSINO.'] == mul_chassino_first_value),'CBM'].values[0]
                except:
                    print('there is no matched EDI NUM for : ', mul_chassino_first_value)
                    pass      
            
            max_h_bl = tot_df.loc[:,'H_BL_NO'].max()
            
            if _h_bl_no == 0:
                pass
                init_max_h_bl = max_h_bl
                
                max_edi = max(edi_no_list)
                max_edi_result = re.search('(\d+)\s?$',max_edi)
                max_edi_val = max_edi_result.group(1)
                max_edi_prefix = max_edi.split(max_edi_val)[0]
                max_edi_val = int(max_edi_val)

                init_max_result = re.search('(\d+)\s?$',init_max_h_bl)
                init_max_val = int(init_max_result.group(1))

                super_set_bl_list = list(range(max_edi_val+1,init_max_val+1))

                tot_h_bl_num_list =[int(re.search('(\d+)\s?$',li).group(1)) for li in tot_h_bl_wo_edi_list]                        
                miss_h_bl_no_list = list(set(super_set_bl_list)-set(tot_h_bl_num_list))
                
            else:
                max_h_bl = max(max_h_bl,_h_bl_no)
                
            result_edi = re.search('(\d+)\s?$',edi_no)
            result_h_bl = re.search('(\d+)\s?$',max_h_bl)
            
            if (result_edi == None) or (result_h_bl == None):
                pass
            else:
                if edi_no in missed_edi_list:
                    missed_edi_list = sorted(missed_edi_list)
                    miss_edi = edi_no
                    missed_edi_list = missed_edi_list.remove(edi_no)

                    if missed_edi_list is None:
                        missed_edi_list = ['']

                    _h_bl_no = miss_edi
                else: 
                    if not max_h_bl in edi_no_list:
                        if miss_h_bl_no_list:
                            miss_h_bl_no_list = sorted(miss_h_bl_no_list)
                            miss_no = miss_h_bl_no_list.pop(0)
                            max_h_bl = max_edi_prefix + str(miss_no).zfill(3)
                        else :
                            max_result = re.search('(\d+)\s?$',max_h_bl)
                            max_val = max_result.group(1)
                            max_prefix = max_h_bl.split(max_val)[0]
                            max_val = int(max_val) + 1
                            max_h_bl = max_prefix + str(max_val).zfill(3)
                            
                    _h_bl_no = max_h_bl

                    while max_h_bl in edi_no_list:
                        max_result = re.search('(\d+)\s?$',max_h_bl)
                        max_val = max_result.group(1)
                        max_prefix = max_h_bl.split(max_val)[0]
                        max_val = int(max_val) + 1
                        max_h_bl = max_prefix + str(max_val).zfill(3)
                    _h_bl_no = max_h_bl

                sub_car_df.loc[idx,'EDI_NO'] = edi_no
                sub_car_df.loc[idx,'H_BL_NO'] = _h_bl_no
                sub_car_df.loc[idx,'WEIGHT'] = weight
                sub_car_df.loc[idx,'CBM'] = cbm
                    
    return sub_car_df

def _get_first_BL_no_from_edi_info(total_sheet_df,edi_df):
    if total_sheet_df.empty:
        pass
    else:
        total_sheet_df = _reset_index(total_sheet_df)
        total_sheet_df[['EDI_NO','H_BL_NO']] = np.nan

        edi_no_list = edi_df['EDI NO.'].drop_duplicates().values

        for row in total_sheet_df.CHASSINO.iteritems():
            idx,val = row
            mul_chassino = {}
            one_chassino = ''
            edi_no = ''
            try:
                mul_chassino = json.loads(val) 
            except:
                one_chassino = val
            if one_chassino:
                try:
                    edi_no = edi_df.loc[(edi_df['CHASSINO.'] == val),'EDI NO.'].values[0]
                    weight = edi_df.loc[(edi_df['CHASSINO.'] == val),'WEIGHT'].values[0]
                    cbm = edi_df.loc[(edi_df['CHASSINO.'] == val),'CBM'].values[0]
                except:
                    print('there is no matched EDI NUM for : ', )
                    err_dict = {1:(idx,val,'EDI_MATCH_ERROR')}
                    call_error_message_edi_error(err_dict)
                    
            if mul_chassino:
                first_key = next(iter(mul_chassino))
                mul_chassino_first_value = mul_chassino[first_key]
                try:
                    edi_no = edi_df.loc[(edi_df['CHASSINO.'] == mul_chassino_first_value),'EDI NO.'].values[0]
                    weight = edi_df.loc[(edi_df['CHASSINO.'] == mul_chassino_first_value),'WEIGHT'].values[0]
                    cbm = edi_df.loc[(edi_df['CHASSINO.'] == mul_chassino_first_value),'CBM'].values[0]
                except:
                    print('there is no matched EDI NUM for : ', mul_chassino_first_value)
                    pass      

            result = re.search('(\d+)\s?$',edi_no)

            if result == None:
                pass
            else:      
                hbl_no_sr = total_sheet_df['H_BL_NO'] 
                edi_match_sr = total_sheet_df.loc[(total_sheet_df['EDI_NO']==edi_no),'H_BL_NO']
                
                if edi_match_sr.dropna().empty:
                    _h_bl_no = edi_no
                else:
                    hbl_no_max = hbl_no_sr.dropna().max()
                    if not hbl_no_max in edi_no_list:
                        max_result = re.search('(\d+)\s?$',hbl_no_max)
                        max_val = max_result.group(1)
                        max_prefix = hbl_no_max.split(max_val)[0]
                        max_val = int(max_val) + 1
                        hbl_no_max = max_prefix + str(max_val).zfill(3)
                    
                    _h_bl_no = hbl_no_max
                    while hbl_no_max in edi_no_list:
                        max_result = re.search('(\d+)\s?$',hbl_no_max)
                        max_val = max_result.group(1)
                        max_prefix = hbl_no_max.split(max_val)[0]
                        max_val = int(max_val) + 1
                        hbl_no_max = max_prefix + str(max_val).zfill(3)

                    _h_bl_no = hbl_no_max
                total_sheet_df.loc[idx,'EDI_NO'] = edi_no
                total_sheet_df.loc[idx,'H_BL_NO'] = _h_bl_no
                total_sheet_df.loc[idx,'WEIGHT'] = weight
                total_sheet_df.loc[idx,'CBM'] = cbm

    return total_sheet_df


def check_equal_df(cur_df,tot_gen_drop_df,tot_df,sheet_name):
    cur_cols = list(cur_df.columns)
    not_include_df = pd.DataFrame(columns=cur_cols)
    modify_info = {}

    for idx,cols in cur_df.iterrows():
        chassino_cur = cols.CHASSINO
                
        cur_chassino_df = cur_df.copy().loc[(cur_df['CHASSINO'] == chassino_cur),:]
        include_df = tot_gen_drop_df.copy().loc[(tot_gen_drop_df['CHASSINO'] == chassino_cur),:]
            
        if include_df.empty:
            not_include_df = pd.concat([not_include_df,cur_chassino_df]).set_index('YR').reset_index()
        else:
            include_rst_idx_df = include_df.copy().set_index('YR').reset_index()
            cur_temp_rst_idx_df = cur_chassino_df.copy().set_index('YR').reset_index()
            include_rst_idx_df = include_rst_idx_df[cur_cols]

            is_equal = cur_temp_rst_idx_df.equals(include_rst_idx_df)
            if is_equal:
                pass
            else:
                modify_info = call_modify_message_input_detail(cur_chassino_df,include_df,sheet_name)
                
                btnVal,modify_df = modify_info
                
                if btnVal:
                    tot_col = tot_df.columns
                    tot_df = tot_df.set_index('CHASSINO')
                    modify_df = modify_df.set_index('CHASSINO')
                    tot_df.update(modify_df)
                    tot_df = tot_df.reset_index()
                    modify_df = modify_df.reset_index()
                    tot_df = tot_df[tot_col]
                
    return not_include_df.empty,not_include_df,tot_df
        

def _check_include_df(cur_df,tot_df,gen_time,sheet_name):
    cur_df = cur_df.set_index('YR').reset_index()
    cur_df = cur_df.copy().drop(columns=['gen_time'])
    tot_gen_drop_df = tot_df.copy().drop(columns=['gen_time'])

    cur_df = cur_df.astype(str)
    tot_gen_drop_df = tot_gen_drop_df.astype(str)

    is_all_include,sub_df,tot_df = check_equal_df(cur_df,tot_gen_drop_df,tot_df,sheet_name)
    sub_df['gen_time'] = gen_time
    
    return is_all_include,sub_df,tot_df

@_excel_decorator
def _excel_write(tot_excel_from_mail,_result_dict,gen_time):
    if _result_dict:
        for _sheet,_car_df in tqdm(_result_dict.items()):
            _car_df['gen_time'] = gen_time
            try:
                tot_sub_car_df = pd.read_excel(tot_excel_from_mail,sheet_name=_sheet)
            except:
                cols = _car_df.columns
                tot_sub_car_df = pd.DataFrame(columns=cols)
    
            _is_include_car,sub_car_df,tot_sub_car_df = _check_include_df(_car_df,tot_sub_car_df,gen_time,_sheet)
            
            if _is_include_car:
                pass
            else:
                tot_sub_car_df = pd.concat([tot_sub_car_df,sub_car_df]).set_index('YR').reset_index()
                _write_or_update_excel(tot_excel_from_mail,_sheet,tot_sub_car_df)


@_excel_total_decorator
def _excel_total_sheet_update(edi_df,tot_excel_from_mail,one_result_dict,mul_result_dict,gen_time):
    tot_mail_sheet = Config().total_mail_sheet_name
    total_sheet_df = pd.read_excel(tot_excel_from_mail,sheet_name=tot_mail_sheet)
    btnVal = False

    if one_result_dict:
        for _sheet,_car_df in tqdm(one_result_dict.items()):
            _car_df['gen_time'] = gen_time
            _car_df['SHEET'] = _sheet
            _is_include_car,sub_car_df,total_sheet_df = _check_include_df(_car_df,total_sheet_df,gen_time,tot_mail_sheet)
            if _is_include_car:
                pass
            else:
                sub_edi_df = _get_BL_no_from_edi_info(total_sheet_df,sub_car_df,edi_df)
                total_sheet_df = pd.concat([total_sheet_df,sub_edi_df]).set_index('YR').reset_index()
                total_macro_format_df = _get_one_car_macro_form(total_sheet_df)
                _write_or_update_excel(tot_excel_from_mail,tot_mail_sheet,total_sheet_df)
                _write_or_update_excel(tot_excel_from_mail,Config().total_macro_sheet,total_macro_format_df)

    if mul_result_dict:
        for _sheet,_car_df in tqdm(mul_result_dict.items()):
            _car_df['gen_time'] = gen_time
            _car_df['SHEET'] = _sheet

            _is_include_car,sub_car_df,total_sheet_df = _check_include_df(_car_df,total_sheet_df,gen_time,tot_mail_sheet)

            if _is_include_car:
                pass
            else:
                sub_edi_df = _get_BL_no_from_edi_info(total_sheet_df,sub_car_df,edi_df)
                total_sheet_df = pd.concat([total_sheet_df,sub_edi_df]).set_index('YR').reset_index()
                _write_or_update_excel(tot_excel_from_mail,tot_mail_sheet,total_sheet_df)

def _total_excel_update(one_result_dict,mul_result_dict):
    
    now = datetime.now()
    gen_time = now.strftime('%Y-%m-%d %H:%M')
    tot_excel_from_mail = Config().tot_excel_from_mail
    tot_mail_sheet = Config().total_mail_sheet_name
    tot_macro_sheet = Config().total_macro_sheet
    edi_path = Config().edi_data_path
    edi_sheet = Config().edi_sheet
    edi_df = pd.read_excel(edi_path,sheet_name=edi_sheet)

    if os.path.isfile(tot_excel_from_mail):
        _excel_total_sheet_update(edi_df,tot_excel_from_mail,one_result_dict,mul_result_dict,gen_time)
        _excel_write(tot_excel_from_mail,one_result_dict,gen_time)
        _excel_write(tot_excel_from_mail,mul_result_dict,gen_time)
    else:
        print('NEW Total mail file generation started!')
        total_sheet_df = pd.DataFrame()
        if one_result_dict:
            for _sheet,_car_df in one_result_dict.items():
                _car_df['SHEET'] = _sheet
                total_sheet_df = pd.concat([total_sheet_df,_car_df])
                total_sheet_df['gen_time'] = gen_time
                
        if mul_result_dict:
            for _sheet,_car_df in mul_result_dict.items():
                _car_df['SHEET'] = _sheet
                total_sheet_df = pd.concat([total_sheet_df,_car_df])
                total_sheet_df['gen_time'] = gen_time
        
        total_sheet_df = _get_first_BL_no_from_edi_info(total_sheet_df,edi_df)
        total_macro_format_df = _get_one_car_macro_form(total_sheet_df)

        with pd.ExcelWriter(tot_excel_from_mail) as writer:
            total_macro_format_df.to_excel(writer,tot_macro_sheet,index=False)
            _autowidth_excel(writer,tot_macro_sheet,total_macro_format_df)
            
            total_sheet_df.to_excel(writer,tot_mail_sheet,index=False)
            _autowidth_excel(writer,tot_mail_sheet,total_sheet_df)

            if one_result_dict:
                for _sheet,_car_df in one_result_dict.items():
                    _car_df['gen_time'] = gen_time
                    _car_df.to_excel(writer,_sheet,index=False)
                    _autowidth_excel(writer,_sheet,_car_df)

            if mul_result_dict:
                for _sheet,_car_df in mul_result_dict.items():
                    _car_df['gen_time'] = gen_time
                    _car_df.to_excel(writer,_sheet,index=False)
                    _autowidth_excel(writer,_sheet,_car_df)

        print('NEW Total mail file generated!')


def _export_cur_xl_mail_info(one_result_dict,mul_result_dict):
    filename = Config().export_xl_gen_name_from_mail
    with pd.ExcelWriter(filename) as writer:
        if one_result_dict:
            for _sheet,_car_df in one_result_dict.items():
                _car_df.to_excel(writer,_sheet,index=False)
                _autowidth_excel(writer,_sheet,_car_df)

        if mul_result_dict:
            for _sheet,_car_df in mul_result_dict.items():
                _car_df.to_excel(writer,_sheet,index=False)
                _autowidth_excel(writer,_sheet,_car_df)


def _export_tot_xl_mail_info(one_result_dict,mul_result_dict,total_option):
    filename = Config().export_xl_gen_name_from_mail

    total_option = total_option.upper()

    if total_option in ['1', 'Y','YES']:
        _total_excel_update(one_result_dict,mul_result_dict)
    else:
        pass
