import pandas as pd
from tqdm import tqdm

from common_mail_script import _remove_NBSP_df
from common_mail_script import _reset_index
from common_mail_script import _get_ship_dict
from common_mail_script import _get_df_car_con_info
from common_mail_script import _get_df_car_info
from check_valid_data import call_error_message_mail_con_acid_empty

def _one_car_decorator(func):
    def wrapper(*args, **kargs):
        print('')
        print("ONE CAR @ mail started!")
        print("Function Name : ",func.__name__)
        result = func(*args, **kargs)
        print("ONE CAR @ mail complete!")
        print('')
        return result
    return wrapper


def _get_one_car_mail_in_format(mail_copy_in_path,one_sheet):
    df = pd.read_excel(mail_copy_in_path,sheet_name=one_sheet,header= None)
    return df


def _get_one_car_macro_form(df):
    df.CAR_COUNT = df.CAR_COUNT.astype(int)
    df = df.loc[(df['CAR_COUNT'] == 1),:]
    macro_df = pd.DataFrame(index=df.index,columns=['MODEL_YR_CHASSINO','H_BL_NO','CONSIGNEE','ACID_INFO','WEIGHT','CBM'])

    for idx,cols in df.iterrows():
        model_yr_chassino_list = []
        
        model = cols.MODEL
        year = cols.YR
        chassino = cols.CHASSINO
        
        model_yr_chassino_list.append(model)
        model_yr_chassino_list.append(year)
        model_yr_chassino_list.append(chassino)
        
        model_yr_chassino = ' '.join(model_yr_chassino_list)
        
        acid = cols['ACID NO']
        import_tax = cols['IMPORTER TAX NUMBER']
        export_id = cols['FREIGHT FORWARDER ID']
        
        acid_str = 'ACID NO : ' + str(acid)
        import_tax_str = 'IMPORTER TAX NUMBER : ' + str(import_tax)
        export_id_str = 'FREIGHT FORWARDER ID : ' + str(export_id)
        
        default_detail = 'EXPORTER REGISTRATION COUNTRY : KR\nFOREIGN EXPORTER COUNTRY : South Korea'
        detail_info = acid_str + '\n' + import_tax_str + '\n' + export_id_str + '\n' + default_detail
        
        consignee = cols.CONSIGNEE
        h_bl = cols.H_BL_NO
        weight = cols.WEIGHT
        cbm = cols.CBM
        
        macro_df.at[idx,'MODEL_YR_CHASSINO'] = model_yr_chassino
        macro_df.at[idx,'H_BL_NO'] = h_bl
        macro_df.at[idx,'CONSIGNEE'] = consignee
        macro_df.at[idx,'ACID_INFO'] = detail_info
        macro_df.at[idx,'WEIGHT'] = weight
        macro_df.at[idx,'CBM'] = cbm
        
    return macro_df

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

def _get_df_one_car_chassi_info(chass_df,chassi_no,cnt):
    dic = {}
    cha_name = chassi_no.split()[0].strip()
    cha_year = chassi_no.split()[1].strip()
    cha_no = chassi_no.split()[2].strip()
    
    dic.update({'MODEL':{cnt:cha_name},'YR':{cnt:cha_year},'CHASSINO':{cnt:cha_no}})
    df = pd.DataFrame.from_dict(data=dic)
    
    chass_df = pd.concat([chass_df,df])
    return chass_df

def _get_one_con_list(df,con_start_idx,con_end_idx,con_name):
    con_list = []
    id_tel_list = []
    con_info_df = df.copy().loc[con_start_idx+1:con_end_idx-1,:]
    
    con_list.append(con_name)
    for idx,row in con_info_df.iterrows():
        if 'ID:' in row[0]:
            id_tel_list.append(row[0])
        elif 'TELEPHONE' in row[0]:
            id_tel_list.append(row[0])
        else:
            con_list.append(row[0])

    id_tel_list = ' / '.join(id_tel_list)
    con_list.append(id_tel_list)
    con_list = '\n'.join(con_list)

    return con_list

def _merge_df_one_description_info(con_df,chassi_df,acid_df,import_tax_df,export_num_df):
    con_df = con_df.reset_index()
    chassi_df = chassi_df.reset_index()
    acid_df = acid_df.reset_index()    
    import_tax_df = import_tax_df.reset_index()
    export_num_df = export_num_df.reset_index()

    total_df = pd.merge(con_df,chassi_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,acid_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,import_tax_df,how='inner', on=['index'])
    total_df = pd.merge(total_df,export_num_df,how='inner', on=['index']).set_index('index')
    
    return total_df

def _get_one_car_consignee_info(df,one_sheet):
    BL_cnt = 0
    init_idx = 1048000 
    con_start_idx = init_idx 
    con_start_val = ''
    con_end_idx = 0

    con_df = pd.DataFrame()
    chassi_df = pd.DataFrame()
    acid_df = pd.DataFrame()
    import_tax_df = pd.DataFrame()
    export_num_df = pd.DataFrame()
    err_dict = {}

    df = df.dropna()
    df = _reset_index(df)

    for idx,col in df.iterrows():
        col = col.str.upper()
        val = col[0]
        
        if 'CONSIGNEE' in val:
            BL_cnt = BL_cnt + 1
            con_name = val.split(':')[-1].strip()
            con_start_idx = idx
            con_start_val = val
            
            if idx >= 1:
                chassi_no_idx = idx - 1
                chassi_no = df.loc[chassi_no_idx,:][0]
                chassi_df = _get_df_one_car_chassi_info(chassi_df,chassi_no,BL_cnt)
        
        elif idx > con_start_idx:        
            if 'ACID' in val:
                con_end_idx = idx
                con_info = _get_one_con_list(df,con_start_idx,con_end_idx,con_name)
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
    
        if 'FREIGHT FORWARDER ID' in val:
            export_num_list = val.split(':')
            cate = 'FREIGHT FORWARDER ID'
            export_num = export_num_list[1].strip()
            export_num_df = _get_df_car_info(export_num_df,cate,export_num,BL_cnt)

    if con_df.empty :
        err_dict = {1:(idx,one_sheet,'ONE_CONSIGNEE_EMPTY')}
        call_error_message_mail_con_acid_empty(err_dict)
    else:
        total_df = _merge_df_one_description_info(con_df,chassi_df,acid_df,import_tax_df,export_num_df)
        total_df['CAR_COUNT'] = 1

    return total_df


def _get_one_car_one_bl(mail_copy_in_path,one_sheet):
    df = _get_one_car_mail_in_format(mail_copy_in_path,one_sheet)
    df = _remove_NBSP_df(df)
    
    ship_dict =  _get_one_car_shipper_info(df)
    df = _get_one_car_consignee_info(df,one_sheet)
    return df

@_one_car_decorator
def _get_one_mail_dict(mail_copy_in_path,one_result_dict,one_sheet_list):
    for one_sheet in tqdm(one_sheet_list):
        one_car_one_bl_df = _get_one_car_one_bl(mail_copy_in_path,one_sheet)
        if one_car_one_bl_df.empty :
            print('ONE CAR ONE BL info is EMPTY! : ', one_sheet)
        else:
            one_result_dict.update({one_sheet:one_car_one_bl_df})
    return one_result_dict