import pandas as pd
import re
import json

from config.config_env import Config
from excel_mail_info import _autowidth_excel
from check_valid_data import call_error_message_from_cargo

def _get_cargo_result_df(cargo_path):
    df = pd.read_excel(cargo_path,header= None)
    return df

def _m_bl_info(m_bl_info_df,sub_df,col,idx,cnt):
    df = sub_df[col]
    m_bl_info = df.values[0]
    m_bl_info_dict = {'m_bl':m_bl_info, 'index':idx+1, 'cnt':cnt}
    sub_m_bl_info_df = pd.DataFrame([m_bl_info_dict])
    m_bl_info_df = pd.concat([m_bl_info_df,sub_m_bl_info_df])

    return m_bl_info_df

def _ship_con_info(err_row_list,ship_con_info_df,sub_df,col,idx,cnt):
    ship_con_info = ''
    
    df = sub_df[col]
    df = df.replace(r'\n',' ', regex=True)
    is_empty = df.isnull().bool()

    ship_con_info = df.values[0]
    
    if is_empty:
        err_row_list.append(idx+1)
    else :
        result = re.search('(S\/)\s(.*)\s(C\/)\s(.*)\s(N\/)',ship_con_info)
        if result == None :
            err_row_list.append(idx+1)
        else:
            if result.group(1) == 'S/':
                ship_con_info_dict = {'SHIPPER NAME':result.group(2), 'index':idx, 'cnt':cnt}
                ship_info_df = pd.DataFrame([ship_con_info_dict])

            if result.group(3) == 'C/':
                ship_con_info_dict = {'CONSIGNEE NAME':result.group(4), 'index':idx, 'cnt':cnt}
                con_info_df = pd.DataFrame([ship_con_info_dict])
        
            ship_con_merge_df = pd.merge(ship_info_df,con_info_df, how='inner', on =['index','cnt'])
            ship_con_info_df = pd.concat([ship_con_info_df,ship_con_merge_df])
    
    return ship_con_info_df,err_row_list

def _cha_num_info(err_row_list,cha_num_info_df,sub_df,col,idx,cnt):
    df = sub_df[col]
    cha_num_info = df.values[0]
    is_empty = df.isnull().bool()

    if is_empty:
        err_row_list.append(idx+1)
    else :
        result = re.search('(\d+)\s?UT',cha_num_info)
        if result == None :
            err_row_list.append(idx+1)
        else:
            cha_num_info_dict = {'car_count':result.group(1), 'index':idx, 'cnt':cnt}
            sub_cha_num_info_df = pd.DataFrame([cha_num_info_dict])
            cha_num_info_df = pd.concat([cha_num_info_df,sub_cha_num_info_df])

    return cha_num_info_df,err_row_list

def _tot_weight_info(err_row_list,tot_weight_df,sub_df,col,idx,cnt):
    df = sub_df[col]
    tot_weight_info = df.values[0]
    is_empty = df.isnull().bool()
    
    if is_empty:
        err_row_list.append(idx+1)
    else :
        tot_weight_info_dict = {'total_weight':tot_weight_info, 'index':idx, 'cnt':cnt}
        sub_tot_weight_info_df = pd.DataFrame([tot_weight_info_dict])
        tot_weight_df = pd.concat([tot_weight_df,sub_tot_weight_info_df])
    return tot_weight_df,err_row_list

def _tot_cbm_info(err_row_list,tot_cbm_df,sub_df,col,idx,cnt):
    df = sub_df[col]
    tot_cbm_info = df.values[0]
    is_empty = df.isnull().bool()

    if is_empty:
        err_row_list.append(idx+1)
    else :
        tot_cbm_info_dict = {'total_cbm':tot_cbm_info, 'index':idx, 'cnt':cnt}
        sub_tot_cbm_info_df = pd.DataFrame([tot_cbm_info_dict])
        tot_cbm_df = pd.concat([tot_cbm_df,sub_tot_cbm_info_df])
    return tot_cbm_df,err_row_list

def _check_info_if_sliced(err_row_list,cha_info,idx):
    p_1 = re.findall('FREIGHT PREPAID.*',cha_info)
    p_2 = re.findall('FREIGHT COLLECT.*',cha_info)
    if not p_1 and not p_2:
        err_row_list.append(idx+1)
    return err_row_list

def _merge_cha_info_df(cha_info_df,cha_model_yr_no_df,cha_acid_df,cha_export_id_df,cha_import_tax_df):
    cha_info_df = pd.merge(cha_model_yr_no_df,cha_acid_df,how='inner', on=['index','cnt'])
    cha_info_df = pd.merge(cha_info_df,cha_export_id_df,how='inner', on=['index','cnt'])
    cha_info_df = pd.merge(cha_info_df,cha_import_tax_df,how='inner', on=['index','cnt'])
    
    return cha_info_df

def _check_except_case_for_import_tax(cha_list,err_row_list,upper_cha_info,idx):
    if not cha_list:
        cha_list = re.findall('IMPORTER VAT.*',upper_cha_info)

    if not cha_list:
        err_row_list.append(idx+1)
    return cha_list,err_row_list

def _check_except_case_for_export_id(cha_list,err_row_list,upper_cha_info,idx):
    if not cha_list:
        cha_list = re.findall('EXPORTER REGISTRATION NO.*',upper_cha_info)
        if not cha_list:
            cha_list = re.findall('EXPORTER REGISTRATION NUMBER.*',upper_cha_info)
            if not cha_list:
                cha_list = re.findall('FREIGHT FORWARDER.*',upper_cha_info)
    
    if not cha_list:
        err_row_list.append(idx+1)
    return cha_list,err_row_list


def _cha_info(err_row_list,cha_info_df,cha_model_yr_no_df,cha_acid_df,cha_export_id_df,cha_import_tax_df,sub_df,col,idx,cnt):
    df = sub_df[col]
    cha_info = df.values[0]

    upper_cha_info = df.values[0].upper()

    model = ''
    year = 0
    chassino = ''
    acid = 0
    export_id = 0
    import_tax = 0

    cha_model_yr_no_list = re.findall('\d+\..*',cha_info)
    cha_acid_list = re.findall('ACID.*',cha_info)

    cha_import_tax_list = re.findall('IMPORTER TAX.*',upper_cha_info)
    cha_export_id_list = re.findall('EXPORTER ID.*',upper_cha_info)
    
    # except case for cha import tax
    cha_import_tax_list,err_row_list = _check_except_case_for_import_tax(cha_import_tax_list,err_row_list,upper_cha_info,idx)
    # except case for cha_export_id
    cha_export_id_list,err_row_list = _check_except_case_for_export_id(cha_export_id_list,err_row_list,upper_cha_info,idx)

    # by using regex, extract info from string.    

    model_dict = {}
    year_dict = {}
    chassino_dict = {}

    if len(cha_model_yr_no_list) == 1:
        cha_info_result = re.search('\d+\.\s(\S+\s*?(\w+)?)\s+(\d+)\s+(\w+)',cha_model_yr_no_list[0])
        try:
            model = cha_info_result.group(1)
            year = cha_info_result.group(3)
            chassino = cha_info_result.group(4)
        except AttributeError:
            err_row_list.append(idx+1)
            print('Please check chassno info if around info is correct',model,year,chassino,idx+1)
            print('There must be white space " " among "MODEL","YEAR","CHASSINO"')
            print('or')
            print('The error might be absence of Chassino!!')
        
    elif len(cha_model_yr_no_list) > 1:
        for cha_model_yr_no in cha_model_yr_no_list:
            cha_info_result = re.search('(\d+)\.\s(\S+\s*?(\w+)?)\s+(\d+)\s+(\w+)',cha_model_yr_no)
            try:
                num = cha_info_result.group(1)
                model = cha_info_result.group(2)
                year = cha_info_result.group(4)
                chassino = cha_info_result.group(5)
            except AttributeError:
                err_row_list.append(idx+1)
                print('Please check chassno info if around info is correct',model,year,chassino,idx+1)
                print('There must be white space " " among "MODEL","YEAR","CHASSINO"')
                print('or')
                print('The error might be absence of Chassino!!')
            model_dict.update({num:model})
            year_dict.update({num:year})
            chassino_dict.update({num:chassino})
        model = json.dumps(model_dict)
        year = json.dumps(year_dict)
        chassino = json.dumps(chassino_dict)
    else:
        #print("this case should not be asserted")
        err_row_list.append(idx+1)
        pass

    cha_model_yr_no_dict = {'MODEL':model,'YR':year,'CHASSINO':chassino,'index':idx-1, 'cnt':cnt}
    sub_cha_model_yr_no_df = pd.DataFrame([cha_model_yr_no_dict])
    cha_model_yr_no_df = pd.concat([cha_model_yr_no_df,sub_cha_model_yr_no_df])
        
    for cha_acid in cha_acid_list:
        cha_acid_result = re.search('ACID NO.\s?(\d+)',cha_acid)
        try:
            acid = cha_acid_result.group(1)
        except AttributeError:
            err_row_list.append(idx+1)
            print('Please check ACID info if around info is correct',acid,idx+1)
        cha_acid_dict = {'ACID_NO':acid,'index':idx-1, 'cnt':cnt}
        sub_cha_acid_df = pd.DataFrame([cha_acid_dict])
        cha_acid_df = pd.concat([cha_acid_df,sub_cha_acid_df])

    for cha_export_id in cha_export_id_list:
        cha_export_id_result = re.search('(\d+)',cha_export_id)
        try:
            export_id = cha_export_id_result.group(1)
        except AttributeError:
            err_row_list.append(idx+1)
            print('Please check EXPORTER info if around info is correct',export_id,idx+1)
            # pass
        cha_export_id_dict = {'FREIGHT_FORWARDER_ID':export_id,'index':idx-1, 'cnt':cnt}
        sub_cha_export_id_df = pd.DataFrame([cha_export_id_dict])
        cha_export_id_df = pd.concat([cha_export_id_df,sub_cha_export_id_df])
    
    for cha_import_tax in cha_import_tax_list:
        cha_import_tax_result = re.search('(\d+)',cha_import_tax)
        try:
            import_tax = cha_import_tax_result.group(1)
        except AttributeError:
            err_row_list.append(idx+1)
            print('Please check IMPORTER TAX info if around info is correct',import_tax,idx+1)
            # pass
        cha_import_tax_dict = {'IMPORTER_TAX_NUMBER':import_tax,'index':idx-1, 'cnt':cnt}
        sub_cha_import_tax_df = pd.DataFrame([cha_import_tax_dict])
        cha_import_tax_df = pd.concat([cha_import_tax_df,sub_cha_import_tax_df])

    is_empty_model = cha_model_yr_no_df.empty
    is_empty_acid = cha_acid_df.empty
    is_empty_ex_id = cha_export_id_df.empty
    is_empty_im_tax = cha_import_tax_df.empty
    is_invalid_data = is_empty_model or is_empty_acid or is_empty_ex_id or is_empty_im_tax

    if is_invalid_data:
        err_row_list.append(idx+1)
    else:
        sub_cha_info_df = _merge_cha_info_df(cha_info_df,cha_model_yr_no_df,cha_acid_df,cha_export_id_df,cha_import_tax_df)
        cha_info_df = pd.concat([cha_info_df,sub_cha_info_df])
    return cha_info_df,err_row_list

def _merge_total_info(m_bl_info_df,ship_con_info_df,cha_num_info_df,tot_weight_df,tot_cbm_df,cha_info_df):
    total_df = pd.merge(m_bl_info_df,ship_con_info_df,how='inner', on=['index','cnt'])
    total_df = pd.merge(total_df,cha_num_info_df,how='inner', on=['index','cnt'])
    total_df = pd.merge(total_df,tot_weight_df,how='inner', on=['index','cnt'])
    total_df = pd.merge(total_df,tot_cbm_df,how='inner', on=['index','cnt'])
    total_df = pd.merge(total_df,cha_info_df,how='inner', on=['index','cnt'])
    total_df = total_df.set_index('index')
    return total_df

def _int2alpha(val):
    val = val + 65
    return chr(val)

def _get_info_cargo_result(df):
    info_loc_offset = 1
    cha_info_loc_offset = 2
    cnt = 0
    m_bl_col = 0

    m_bl_info_df = pd.DataFrame()
    ship_con_info_df = pd.DataFrame()
    cha_num_info_df = pd.DataFrame()
    tot_weight_df = pd.DataFrame()
    tot_cbm_df = pd.DataFrame()
    cha_info_df = pd.DataFrame()
    cha_model_yr_no_df = pd.DataFrame()
    cha_acid_df = pd.DataFrame()
    cha_export_id_df = pd.DataFrame()
    cha_import_tax_df = pd.DataFrame()

    err_cnt = 0
    err_dict = {}

    err_no_prepaid_list = []
    err_ship_con_list = []
    err_cha_num_list = []
    err_tot_weight_list = []
    err_tot_cbm_list = []
    err_empty_cha_list = []

    zero_col_df = df.copy().dropna(subset=[0])
    zero_col_df = zero_col_df[zero_col_df[0].str.contains('INPS')]
    m_bl_idx_list = list(zero_col_df.index)

    init_idx = m_bl_idx_list[0]
    col_num_list = list(df.loc[init_idx+1,:].dropna().index)
    cha_col_list = list(df.loc[init_idx+2,:].dropna().index)

    ship_con_col = col_num_list[0]
    cha_info_col = cha_col_list[0]
    cha_num_col = col_num_list[2]
    tot_weight_col = col_num_list[3]
    tot_cbm_col = col_num_list[4]


    ## ## check whether info was sliced
    for m_bl_idx in m_bl_idx_list:
        err_idx = m_bl_idx + cha_info_loc_offset
        sub_err_df = df.loc[[err_idx],:]
        err_df = sub_err_df[cha_info_col]
        err_cha_info = err_df.values[0]
        err_no_prepaid_list = _check_info_if_sliced(err_no_prepaid_list,err_cha_info,err_idx) 
     
    if err_no_prepaid_list:
        err_col = _int2alpha(cha_info_col)
        err_no_prepaid_dict = {1:(err_no_prepaid_list,err_col,'NO_FREIGHT_PREPAID_OR_COLLECT')}
        call_error_message_from_cargo(err_no_prepaid_dict)
    else:
        ## assume that all master bl exists.
        for m_bl_idx in m_bl_idx_list:
            ship_con_idx = m_bl_idx + info_loc_offset
            cha_info_idx = m_bl_idx + cha_info_loc_offset
            
            cnt = cnt + 1

            sub_m_bl_df = df.loc[[m_bl_idx],:]
            sub_ship_con_df = df.loc[[ship_con_idx],:]
            sub_cha_info_df = df.loc[[cha_info_idx],:]
            
            ## M_BL df
            m_bl_info_df = _m_bl_info(m_bl_info_df,sub_m_bl_df,m_bl_col,m_bl_idx,cnt)
            ## ship, con, weight, cbm df
            ship_con_info_df,err_ship_con_list = _ship_con_info(err_ship_con_list,ship_con_info_df,sub_ship_con_df,ship_con_col,ship_con_idx,cnt)
            cha_num_info_df,err_cha_num_list = _cha_num_info(err_cha_num_list,cha_num_info_df,sub_ship_con_df,cha_num_col,ship_con_idx,cnt)
            tot_weight_df,err_tot_weight_list = _tot_weight_info(err_tot_weight_list,tot_weight_df,sub_ship_con_df,tot_weight_col,ship_con_idx,cnt)
            tot_cbm_df,err_tot_cbm_list = _tot_cbm_info(err_tot_cbm_list,tot_cbm_df,sub_ship_con_df,tot_cbm_col,ship_con_idx,cnt)
            ## cha info df
            cha_info_df,err_empty_cha_list = _cha_info(err_empty_cha_list,cha_info_df,cha_model_yr_no_df,cha_acid_df,cha_export_id_df,cha_import_tax_df,sub_cha_info_df,cha_info_col,cha_info_idx,cnt)

        if err_ship_con_list:
            err_cnt = err_cnt + 1
            err_col = _int2alpha(ship_con_col)
            err_ship_con_dict = {err_cnt:(err_ship_con_list,err_col,'SHIP_CON_INFO')}
            err_dict.update(err_ship_con_dict)
        if err_cha_num_list:
            err_cnt = err_cnt + 1
            err_col = _int2alpha(cha_num_col)
            err_cha_num_dict = {err_cnt:(err_cha_num_list,err_col,'NUM_OF_CAR')}
            err_dict.update(err_cha_num_dict)
        if err_tot_weight_list:
            err_cnt = err_cnt + 1
            err_col = _int2alpha(tot_weight_col)
            err_tot_weight_dict = {err_cnt:(err_tot_weight_list,err_col,'TOTAL_WEIGHT')}
            err_dict.update(err_tot_weight_dict)
        if err_tot_cbm_list:
            err_cnt = err_cnt + 1
            err_col = _int2alpha(tot_cbm_col)
            err_tot_cbm_dict = {err_cnt:(err_tot_cbm_list,err_col,'TOTAL_CBM')}
            err_dict.update(err_tot_cbm_dict)
        if err_empty_cha_list:  
            err_cnt = err_cnt + 1
            err_col = _int2alpha(cha_info_col)
            err_empty_cha_dict = {err_cnt:(err_empty_cha_list,err_col,'MISSING_INFO')}
            err_dict.update(err_empty_cha_dict)

        total_df = _merge_total_info(m_bl_info_df,ship_con_info_df,cha_num_info_df,tot_weight_df,tot_cbm_df,cha_info_df)

    return total_df,err_dict

def _export_xl_from_cargo(df):
    filename = Config().export_info_from_cargo_path
    work_sheet = Config().result_carco_sheet

    with pd.ExcelWriter(filename,engine='xlsxwriter') as writer:
        df.to_excel(writer,work_sheet,index=False)
        _autowidth_excel(writer,work_sheet,df)


def get_cargo_result_df(cargo_path):
    df = _get_cargo_result_df(cargo_path)
    total_df,err_dict = _get_info_cargo_result(df)

    if err_dict:
        call_error_message_from_cargo(err_dict)
    else:
        _export_xl_from_cargo(total_df)