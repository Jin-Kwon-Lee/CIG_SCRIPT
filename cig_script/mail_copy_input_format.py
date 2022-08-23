
import os
import pandas as pd
import numpy as np
import json
from config.config_env import Config
from datetime import datetime

def _col_append(cols,mail_key):
    for value in mail_key:
        if value not in cols:
            cols.append(value)
    return cols

def _remove_NBSP_df(df):
    for col in df:
        col
    df[col] = df[col].str.replace("\xa0"," ")
    return df

def _reset_index(df):
    col = df.columns
    col[0]
    df = df.set_index(col[0])
    df = df.reset_index()
    return df

def _get_column_from_dict(mail_dicts,cols):

    for mail_dict in mail_dicts:
        for key in mail_dict:
            mail_key = list(mail_dict[key].keys())
            if len(mail_key) == 1:
                if mail_key[0] in cols:
                    pass
                else:
                    cols = _col_append(cols,mail_key)

            elif len(mail_key) > 1:
                for i in range(len(mail_key)):
                    if mail_key[i] in cols:
                        pass
                    else:
                        mail_key[i] = mail_key[i].strip()
                        cols.append(mail_key[i])
            else:
                print('MODEL, YR, CHASSINO might be something wrong!')
    return cols

def _get_one_car_mail_in_format(mail_copy_in_path):
    sheet = Config().one_car_sheet
    df = pd.read_excel(mail_copy_in_path,sheet_name=sheet,header= None)
    return df

def _get_mul_car_mail_in_format(mail_copy_in_path):
    sheet = Config().mul_car_sheet
    df = pd.read_excel(mail_copy_in_path,sheet_name=sheet,header= None)
    return df

def _get_ship_dict(df,ship_dict,ship_start_val,ship_start_idx,ship_end_idx,ship_cnt):
    ship_list = []
    ship_info_df = df.copy().loc[ship_start_idx+1:ship_end_idx-1,:]

    for idx,row in ship_info_df.iterrows():
        ship_list.append(row[0])

    ship_dict.update({ship_cnt:{ship_start_val:ship_list}})
    return ship_dict

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

def _get_one_car_shipper_info(df):
    df = df.dropna()
    df = _reset_index(df)
    
    init_idx = 1048000 #excel last cell index
    ship_start_idx = init_idx 

    ship_start_val = ''
    ship_end_idx = 0
    ship_cnt = 0

    ship_dict = {}

    for idx, col in df.iterrows():
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

def _merge_df_description_info(con_df,acid_df,import_tax_df,export_num_df,car_info_df):
    con_df = con_df.reset_index()
    acid_df = acid_df.reset_index()    
    import_tax_df = import_tax_df.reset_index()
    export_num_df = export_num_df.reset_index()

    total_df = pd.merge(con_df,acid_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,import_tax_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,export_num_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,car_info_df,how='inner', on=['index']).set_index('index')
    
    return total_df

def _get_dict_description_info(dic,descript_list,BL_cnt):
    if type(descript_list) == list:
        descript_cate = descript_list[0].strip()
        descript_val = descript_list[1].strip()
        dic.update({BL_cnt:{descript_cate:descript_val}})
    elif type(descript_list) == str:
        cha_name = descript_list.split()[0].strip()
        cha_year = descript_list.split()[1].strip()
        cha_no = descript_list.split()[2].strip()
        dic.update({BL_cnt:{'MODEL':cha_name,'YR':cha_year,'CHASSINO':cha_no}})
    return dic

def _get_df_mul_car_info(con_df,cate,val,cnt):
    dic = {}
    dic.update({cate:{cnt:val}})
    df = pd.DataFrame.from_dict(data=dic)
    
    con_df = pd.concat([con_df,df])
    return con_df


def _merge_mul_car_info(total_df,df,cnt):
    model_dict = {}
    year_dict = {}
    chassino_dict = {}
    model_tot_dict = {}
    year_tot_dict = {}
    chassino_tot_dict = {}

    car_cnt = 0
    for idx,col in df.iterrows():
        car_cnt = car_cnt + 1
        
        model = col[0]
        year = col[1]
        chassino = col[2]
        
        model_dict.update({car_cnt:model})
        year_dict.update({car_cnt:year})
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
    
    total_df = pd.concat([total_df,sub_df])
    
    return total_df

def _get_mul_car_info_df(df):

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
                total_info_df = _merge_mul_car_info(total_info_df,sub_df,car_info_cnt)
        
    return total_info_df

def _get_mul_car_consignee_info(df):
    
    BL_cnt = 0
    con_df = pd.DataFrame()
    acid_df = pd.DataFrame()
    import_tax_df = pd.DataFrame()
    export_num_df = pd.DataFrame()

    first_col_df = df.loc[:,[0]]
    first_col_df = first_col_df.dropna()
    first_col_df = _reset_index(first_col_df)

    for idx,col in first_col_df.iterrows():
        col = col.str.upper()
        val = col[0]
        if 'CONSIGNEE' in val:
            BL_cnt = BL_cnt + 1
            if idx >= 1:
                consign_idx = idx + 1
                cate = val
                con_name = first_col_df.loc[consign_idx,:][0]
                con_df = _get_df_mul_car_info(con_df,cate,con_name,BL_cnt)
                    
        elif 'ACID' in val:
                acid_no_list = val.split(':')
                cate = acid_no_list[0]
                acid_no = acid_no_list[1].strip()
                acid_df = _get_df_mul_car_info(acid_df,cate,acid_no,BL_cnt)
        
        elif 'IMPORTER VAT NUMBER' in val or 'IMPORTER TAX NUMBER' in val:
                import_tax_list = val.split(':')
                cate = import_tax_list[0]
                import_tax = import_tax_list[1].strip()
                import_tax_df = _get_df_mul_car_info(import_tax_df,cate,import_tax,BL_cnt)
        
        elif 'EXPORTER REGISTRATION NUMBER' in val:
                export_num_list = val.split(':')
                cate = export_num_list[0]
                export_num = export_num_list[1].strip()
                export_num_df = _get_df_mul_car_info(export_num_df,cate,export_num,BL_cnt)
    
    # multi car info extract
    car_info_df = _get_mul_car_info_df(df)
    total_df = _merge_df_description_info(con_df,acid_df,import_tax_df,export_num_df,car_info_df)
    
    return total_df
    
def _get_one_car_consignee_info(df):
    BL_cnt = 0
    con_dict = {}
    chassi_dict = {}
    acid_dict = {}
    import_dict = {}
    acid_dict = {}
    exp_dict = {}

    df = df.dropna()
    df = _reset_index(df)

    for idx,col in df.iterrows():
        val = col[0]
    
        if 'CONSIGNEE' in val:
            BL_cnt = BL_cnt + 1
            con_idx = idx
            con_name = val.split(':')

            if idx >= 1:
                chassi_no_idx = idx - 1
                chassi_no = df.loc[chassi_no_idx,:][0]
                chassi_dict = _get_dict_description_info(chassi_dict,chassi_no,BL_cnt)
            con_dict = _get_dict_description_info(con_dict,con_name,BL_cnt)

        elif 'ACID' in val:
            acid_idx = idx
            acid_no = val.split(':')
            acid_dict = _get_dict_description_info(acid_dict,acid_no,BL_cnt)
    
        elif 'IMPORTER TAX NUMBER' in val:
            importer_idx = idx
            importer_no = val.split(':')
            import_dict = _get_dict_description_info(import_dict,importer_no,BL_cnt)
    
        elif 'FREIGHT FORWARDER ID' in val:
            exporter_idx = idx
            exporter_no = val.split(':')
            exp_dict = _get_dict_description_info(exp_dict,exporter_no,BL_cnt)
    
    return con_dict,chassi_dict,acid_dict,import_dict,exp_dict,BL_cnt

def _get_df_one_car_mail_info(BL_cnt,*mail_dicts):
    cols = []
    cols = _get_column_from_dict(mail_dicts,cols)

    index_list = range(1,BL_cnt+1)
    df = pd.DataFrame(index= index_list, columns= cols)
    
    for mail_dict in mail_dicts:
        for cnt in mail_dict:
            temp_df = pd.DataFrame()
            mail_key = list(mail_dict[cnt].keys())
            if 'SHIPPER' in mail_key[0]:
                ship_info = mail_dict[cnt].get(mail_key[0])
                ship_info = '_'.join(ship_info)
                df.loc[cnt,mail_key[0]] = ship_info
            else:
                if cnt > 0:
                    temp_df = pd.DataFrame(mail_dict[cnt], index = [cnt])
                elif cnt == 0:
                    pass
            df.update(temp_df)
    return df

def _autowidth_excel(writer,sheet_name,df):
    margin = 5
    for column in df:
        column_length = len(column) + margin
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheet_name].set_column(col_idx, col_idx, column_length)

def _check_include_df(cur_df,tot_df,gen_time):
    exist_dup = False
    
    cur_df = cur_df.set_index('YR').reset_index()
    cur_df = cur_df.copy().drop(columns=['gen_time'])
    tot_df = tot_df.copy().drop(columns=['gen_time'])
    
    cols = list(cur_df.columns)
    
    cur_df = cur_df.astype(str)
    tot_df = tot_df.astype(str)

    common_df = pd.merge(cur_df,tot_df, on=cols)
    is_include = cur_df.equals(common_df)  
    
    cur_idx_set = set(cur_df.index)
    common_idx_set = set(common_df.index)
    sub_idx_list = list(cur_idx_set - common_idx_set)
    
    sub_df = cur_df.copy().iloc[sub_idx_list,:]
    sub_df['gen_time'] = gen_time
    
    if is_include:
        pass
    else:
        if len(cur_df) != len(common_df):
            exist_dup = True
        else:
            exist_dup = False
    
    return is_include,exist_dup,sub_df


def _total_excel_update(one_car_df,mul_car_df):
    now = datetime.now()
    gen_time = now.strftime('%Y-%m-%d %H:%M')
    
    tot_excel_from_mail = Config().tot_excel_from_mail
    tot_one_car_sheet = Config().total_one_car_sheet_name
    tot_mul_car_sheet = Config().total_mul_car_sheet_name
    
    one_car_df['gen_time'] = gen_time
    mul_car_df['gen_time'] = gen_time
    

    if os.path.isfile(tot_excel_from_mail):
        tot_one_car_df = pd.read_excel(tot_excel_from_mail,sheet_name=tot_one_car_sheet)
        tot_mul_car_df = pd.read_excel(tot_excel_from_mail,sheet_name=tot_mul_car_sheet)
        
        _is_include_one_car,exist_dup_one_car,sub_one_car_df = _check_include_df(one_car_df,tot_one_car_df,gen_time)
        _is_include_mul_car,exist_dup_mul_car,sub_mul_car_df = _check_include_df(mul_car_df,tot_mul_car_df,gen_time)
        
        if _is_include_one_car and _is_include_mul_car:
            pass
            # both already included.
        elif _is_include_mul_car:
            # multi car already included, one car should be updated
            if exist_dup_one_car:
                tot_one_car_df = pd.concat([tot_one_car_df,sub_one_car_df]).set_index('YR').reset_index()
            else:
                tot_one_car_df = pd.concat([tot_one_car_df,one_car_df]).set_index('YR').reset_index()
            
            tot_one_car_df = tot_one_car_df.astype(str)
            tot_mul_car_df = tot_mul_car_df.astype(str)
            
            with pd.ExcelWriter(tot_excel_from_mail,engine='xlsxwriter') as writer:
                tot_one_car_df.to_excel(writer,tot_one_car_sheet,index=False)
                _autowidth_excel(writer,tot_one_car_sheet,tot_one_car_df)
                tot_mul_car_df.to_excel(writer,tot_mul_car_sheet,index=False)
                _autowidth_excel(writer,tot_mul_car_sheet,tot_mul_car_df)
                
        elif _is_include_one_car:
            # one car already included, multi car should be updated
            if exist_dup_mul_car:
                tot_mul_car_df = pd.concat([tot_mul_car_df,sub_mul_car_df]).set_index('YR').reset_index()
            else:
                tot_mul_car_df = pd.concat([tot_mul_car_df,mul_car_df]).set_index('YR').reset_index()
            
            tot_one_car_df = tot_one_car_df.astype(str)
            tot_mul_car_df = tot_mul_car_df.astype(str)
            
            with pd.ExcelWriter(tot_excel_from_mail,engine='xlsxwriter') as writer:
                tot_one_car_df.to_excel(writer,tot_one_car_sheet,index=False)
                _autowidth_excel(writer,tot_one_car_sheet,tot_one_car_df)
                tot_mul_car_df.to_excel(writer,tot_mul_car_sheet,index=False)
                _autowidth_excel(writer,tot_mul_car_sheet,tot_mul_car_df)
            
        else:
            if exist_dup_one_car and exist_dup_mul_car:
                tot_one_car_df = pd.concat([tot_one_car_df,sub_one_car_df]).set_index('YR').reset_index()
                tot_mul_car_df = pd.concat([tot_mul_car_df,sub_mul_car_df]).set_index('YR').reset_index()
            elif exist_dup_one_car:
                tot_one_car_df = pd.concat([tot_one_car_df,sub_one_car_df]).set_index('YR').reset_index()
                tot_mul_car_df = pd.concat([tot_mul_car_df,mul_car_df]).set_index('YR').reset_index()
            elif exist_dup_mul_car:
                tot_one_car_df = pd.concat([tot_one_car_df,one_car_df]).set_index('YR').reset_index()
                tot_mul_car_df = pd.concat([tot_mul_car_df,sub_mul_car_df]).set_index('YR').reset_index()
            else:
                tot_one_car_df = pd.concat([tot_one_car_df,one_car_df]).set_index('YR').reset_index()
                tot_mul_car_df = pd.concat([tot_mul_car_df,mul_car_df]).set_index('YR').reset_index()
            
            tot_one_car_df = tot_one_car_df.astype(str)
            tot_mul_car_df = tot_mul_car_df.astype(str)
            
            with pd.ExcelWriter(tot_excel_from_mail,engine='xlsxwriter') as writer:
                tot_one_car_df.to_excel(writer,tot_one_car_sheet,index=False)
                _autowidth_excel(writer,tot_one_car_sheet,tot_one_car_df)
                tot_mul_car_df.to_excel(writer,tot_mul_car_sheet,index=False)
                _autowidth_excel(writer,tot_mul_car_sheet,tot_mul_car_df)
        
    else:
        with pd.ExcelWriter(tot_excel_from_mail,engine='xlsxwriter') as writer:
            
            one_car_df.to_excel(writer,tot_one_car_sheet,index=False)
            _autowidth_excel(writer,tot_one_car_sheet,one_car_df)

            mul_car_df.to_excel(writer,tot_mul_car_sheet,index=False)
            _autowidth_excel(writer,tot_mul_car_sheet,mul_car_df)
    


def _export_xl_mail_info(one_df,mul_df,total_option):
    filename = Config().export_xl_gen_name_from_mail
    cur_one_car_sheet = Config().cur_one_car_sheet
    cur_mul_car_sheet = Config().cur_mul_car_sheet
    
    total_option = total_option.upper()

    if total_option in ['1', 'Y','YES']:
        _total_excel_update(one_df,mul_df)
    else:
        pass

    with pd.ExcelWriter(filename,engine='xlsxwriter') as writer:
        one_df.to_excel(writer,cur_one_car_sheet,index=False)
        _autowidth_excel(writer,cur_one_car_sheet,one_df)

        mul_df.to_excel(writer,cur_mul_car_sheet,index=False)
        _autowidth_excel(writer,cur_mul_car_sheet,mul_df)


def _get_one_car_one_bl(mail_copy_in_path):
    df = _get_one_car_mail_in_format(mail_copy_in_path)
    df = _remove_NBSP_df(df)
    
    ship_dict =  _get_one_car_shipper_info(df)
    con_dict,chassi_dict,acid_dict,import_dict,exp_dict,BL_cnt = _get_one_car_consignee_info(df)
    mail_df = _get_df_one_car_mail_info(BL_cnt,ship_dict,con_dict,chassi_dict,acid_dict,import_dict,exp_dict)
    return mail_df

def _get_mul_car_one_bl(mail_copy_in_path):
    df = _get_mul_car_mail_in_format(mail_copy_in_path)
    df = _remove_NBSP_df(df)

    ship_dict = _get_mul_car_shipper_info(df)
    df = _get_mul_car_consignee_info(df)
    return df

def get_mail_in_format(mail_copy_in_path):
    
    one_car_one_bl_df = _get_one_car_one_bl(mail_copy_in_path)
    mul_car_one_bl_df = _get_mul_car_one_bl(mail_copy_in_path)

    if one_car_one_bl_df.empty :
        print('one car one bl info is EMPTY!')
    elif mul_car_one_bl_df.empty :
        print('multi car one bl info is EMPTY!')
    else:
        print("Both info Parsing from mail are SUCCESSFUL !")

        print('Do you want to merge current mail info in TOTAL sheet?')
        total_option = input('1 : Y(Yes) or  0: N(No) : ')
        
        _export_xl_mail_info(one_car_one_bl_df,mul_car_one_bl_df,total_option)