from audioop import mul
import pandas as pd
import numpy as np
import json
import re
from tqdm import tqdm


from common_mail_script import _remove_NBSP_df
from common_mail_script import _reset_index
from common_mail_script import _get_ship_dict
from common_mail_script import _get_df_car_con_info
from common_mail_script import _get_df_car_info
from check_valid_data import call_error_message_mail_con_acid_empty

# from cig_script.common_mail_script import _remove_NBSP_df
# from cig_script.common_mail_script import _reset_index
# from cig_script.common_mail_script import _get_ship_dict
# from cig_script.common_mail_script import _get_df_car_con_info
# from cig_script.common_mail_script import _get_df_car_info
# from cig_script.check_valid_data import call_error_message_mail_con_acid_empty

def _mul_car_decorator(func):
    def wrapper(*args, **kargs):
        print("MULTI CAR @ mail started!")
        print("Function Name : ",func.__name__)
        result = func(*args, **kargs)
        print("MULTI CAR @ mail compelete!")
        print('')
        return result
    return wrapper

def _get_mul_car_mail_in_format(mail_copy_in_path,mul_sheet):
    df = pd.read_excel(mail_copy_in_path,sheet_name=mul_sheet,header= None)
    return df

def _get_mul_car_shipper_info(df):
    init_idx = 1048000 #excel last cell index
    ship_start_idx = init_idx 
    ship_start_val = ''
    ship_end_idx = 0
    ship_cnt = 0

    ship_dict = {}

    first_col_df = df.loc[:,[0]]
    first_col_df = first_col_df.replace(np.nan," ")

    for idx, col in first_col_df.iterrows():
        val = col[0]
        if "SHIPPER" in val:
            ship_start_idx = idx
            ship_start_val = val
            ship_cnt = ship_cnt + 1
            
        elif idx > ship_start_idx:
            if val == " ":
                ship_end_idx = idx
                ship_dict = _get_ship_dict(df,ship_dict,ship_start_val,ship_start_idx,ship_end_idx,ship_cnt)            
                ship_start_idx = init_idx

    return ship_dict

def _merge_mul_car_info(total_df,df,cnt,mul_sheet):
    model_dict = {}
    year_dict = {}
    chassino_dict = {}
    model_tot_dict = {}
    year_tot_dict = {}
    chassino_tot_dict = {}

    car_cnt = 0
    for idx,col in df.iterrows():
        row = col.name + 1
        car_cnt = car_cnt + 1
        
        model = col[0]
        year = col[1]
        chassino = col[2]
        
        model_cond = bool(re.search('\w+$',model))
        yr_cond = bool(re.search('\d+',str(year)))
        chassino_cond = bool(re.search('\w+',chassino))
        
        if model_cond == False:
            idx = 1
            err_dict = {1:(row,mul_sheet,'MUL_MODEL_ERROR')}
            call_error_message_mail_con_acid_empty(err_dict)
        
        if yr_cond == False:
            idx = 1
            err_dict = {1:(row,mul_sheet,'MUL_YEAR_ERROR')}
            call_error_message_mail_con_acid_empty(err_dict)
        
        if chassino_cond == False:
            idx = 1
            err_dict = {1:(row,mul_sheet,'MUL_CHASSINO_ERROR')}
            call_error_message_mail_con_acid_empty(err_dict)


        model_dict.update({car_cnt:model})
        year_dict.update({car_cnt:int(year)})
        chassino_dict.update({car_cnt:chassino})

    model = json.dumps(model_dict)
    year = json.dumps(year_dict)
    chassino = json.dumps(chassino_dict)
    
    model_tot_dict.update({"MODEL":{cnt:model}})
    year_tot_dict.update({"YR":{cnt:year}})
    chassino_tot_dict.update({"CHASSINO":{cnt:chassino}})

    sub_model_df = pd.DataFrame.from_dict(data=model_tot_dict).reset_index()
    sub_year_df = pd.DataFrame.from_dict(data=year_tot_dict).reset_index()
    sub_cha_df = pd.DataFrame.from_dict(data=chassino_tot_dict).reset_index()

    sub_df = pd.merge(sub_model_df,sub_year_df,how='inner', on=['index'])
    sub_df = pd.merge(sub_df,sub_cha_df,how='inner', on=['index'])
    sub_df['CAR_COUNT'] = car_cnt

    total_df = pd.concat([total_df,sub_df])
    
    return total_df


def _get_mul_car_info_df(df,mul_sheet):

    second_col_df = df.loc[:,[1]]

    empty = pd.DataFrame(index=range(0,1), columns=second_col_df.columns)
    col = list(second_col_df.columns)
    second_col_df = pd.concat([second_col_df,empty]).set_index(col[0]).reset_index()
    second_col_df = second_col_df.replace(np.nan,"")

    init_idx = 100000
    start_idx = init_idx
    end_idx = 0

    car_info_cnt = 0
    total_info_df = pd.DataFrame()

    for idx, col in second_col_df.iterrows():
        val = col.values[0] 
        if val != "":
            if idx < start_idx :
                start_idx = idx
                
        elif idx > start_idx:
            if val == "" :
                car_info_cnt = car_info_cnt + 1
                end_idx = idx
                sub_df = df.iloc[start_idx:end_idx,:]
                start_idx = init_idx
                total_info_df = _merge_mul_car_info(total_info_df,sub_df,car_info_cnt,mul_sheet)
        
    return total_info_df

def _merge_df_mul_description_info(con_df,acid_df,import_tax_df,export_num_df,car_info_df):
    con_df = con_df.reset_index()
    acid_df = acid_df.reset_index()    
    import_tax_df = import_tax_df.reset_index()
    export_num_df = export_num_df.reset_index()

    total_df = pd.merge(con_df,acid_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,import_tax_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,export_num_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,car_info_df,how='inner', on=['index']).set_index('index')
    
    return total_df


def _get_mul_con_list(df,con_start_idx,con_end_idx):
    con_list = []
    id_tel_list = []
    con_info_df = df.copy().loc[con_start_idx+1:con_end_idx-1,:]
    
    for idx,row in con_info_df.iterrows():
        con_list.append(row[0])

    con_list = '\n'.join(con_list)

    return con_list


def _get_mul_car_consignee_info(df,mul_sheet):
    
    BL_cnt = 0
    init_idx = 1048000 
    con_start_idx = init_idx 
    con_start_val = ''
    con_end_idx = 0

    con_df = pd.DataFrame()
    acid_df = pd.DataFrame()
    import_tax_df = pd.DataFrame()
    export_num_df = pd.DataFrame()
    err_dict = {}

    first_col_df = df.loc[:,[0]]
    first_col_df = first_col_df.dropna()
    first_col_df = _reset_index(first_col_df)

    for idx,col in first_col_df.iterrows():
        col = col.str.upper()
        val = col[0]
    
        if 'CONSIGNEE' in val:
            BL_cnt = BL_cnt + 1
            con_start_idx = idx
            con_start_val = val

        elif idx > con_start_idx:        
            if 'NOTIFY' in val:
                con_end_idx = idx
                con_info = _get_mul_con_list(first_col_df,con_start_idx,con_end_idx)
                con_df = _get_df_car_con_info(con_df,con_start_val,con_info,BL_cnt)
                con_start_idx = init_idx
                
        if 'ACID' in val:
                acid_no_list = val.split(':')
                cate = acid_no_list[0]
                acid_no = acid_no_list[1].strip()
                acid_df = _get_df_car_info(acid_df,cate,acid_no,BL_cnt)

        if 'IMPORTER VAT NUMBER' in val or 'IMPORTER TAX NUMBER' in val:
                import_tax_list = val.split(':')
                cate = 'IMPORTER TAX NUMBER'
                import_tax = import_tax_list[1].strip()
                import_tax_df = _get_df_car_info(import_tax_df,cate,import_tax,BL_cnt)
        
        if 'EXPORTER REGISTRATION NUMBER' in val:
                export_num_list = val.split(':')
                cate = 'FREIGHT FORWARDER ID'
                export_num = export_num_list[1].strip()
                export_num_df = _get_df_car_info(export_num_df,cate,export_num,BL_cnt)
        
    if con_df.empty :
        err_dict = {1:(idx,mul_sheet,'MUL_CONSIGNEE_EMPTY')}
        call_error_message_mail_con_acid_empty(err_dict)
    else:
        # multi car info extract
        car_info_df = _get_mul_car_info_df(df,mul_sheet)
        total_df = _merge_df_mul_description_info(con_df,acid_df,import_tax_df,export_num_df,car_info_df)
    
    return total_df

def _get_mul_car_one_bl(mail_copy_in_path,mul_sheet):
    df = _get_mul_car_mail_in_format(mail_copy_in_path,mul_sheet)
    df = _remove_NBSP_df(df)

    ship_dict = _get_mul_car_shipper_info(df)
    df = _get_mul_car_consignee_info(df,mul_sheet)
    return df


@_mul_car_decorator
def _get_mul_mail_dict(mail_copy_in_path,mul_result_dict,mul_sheet_list):
    for mul_sheet in tqdm(mul_sheet_list):
        mul_car_one_bl_df = _get_mul_car_one_bl(mail_copy_in_path,mul_sheet)
        if mul_car_one_bl_df.empty:
            print('MULTI CAR ONE BL info is EMPTY! : ', mul_sheet)
        else:
            mul_result_dict.update({mul_sheet:mul_car_one_bl_df})
    return mul_result_dict
