import pandas as pd
import re


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

def _get_ship_dict(df,ship_dict,ship_start_val,ship_start_idx,ship_end_idx,ship_cnt):
    ship_list = []
    ship_info_df = df.copy().loc[ship_start_idx+1:ship_end_idx-1,:]

    for idx,row in ship_info_df.iterrows():
        ship_list.append(row[0])

    ship_dict.update({ship_cnt:{ship_start_val:ship_list}})
    return ship_dict

def _get_df_car_con_info(con_df,cate,val,cnt):
    dic = {}
    cate = cate.strip()
    cate = str(re.match('\w+',cate)[0])
    
    dic.update({cate:{cnt:val}})
    df = pd.DataFrame.from_dict(data=dic)
    
    con_df = pd.concat([con_df,df])
    return con_df

def _get_df_car_info(_df,cate,val,cnt):
    dic = {}
    dic.update({cate:{cnt:val}})
    df = pd.DataFrame.from_dict(data=dic)
    
    _df = pd.concat([_df,df])
    return _df
