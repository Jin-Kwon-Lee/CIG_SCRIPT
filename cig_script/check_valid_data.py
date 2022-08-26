import numpy as np
from tkinter import *
import warnings
import tkinter as tk
from config.config_env import Config

def warn_empty_df():
    warnings.warn('The Data is not ready in Input file', UserWarning)

def _check_if_empty_df(df):
    return df.empty

def _in_empty_error_default_labeling(window):
    #    Error message 
    lb_err_msg1 = Label(window, text="This error is caused if empty location in input file was found!")
    lb_err_msg1.place(x=10, y=10)
    
    lb_err_msg2 = Label(window, text="You should check below location of empty data in input file!")
    lb_err_msg2.place(x=10, y=30)
    
    #    Current working directory path
    working_xl_path = Config().in_xl_path 

    lb_err_working_dir = Label(window, text="Working Directory Path : ")
    lb_err_working_dir.place(x=10, y=70)
    
    ety_working_path = tk.Entry(fg="gray19", bg="snow", width=50)
    ety_working_path.place(x=10,y=90)
    ety_working_path.insert(0,working_xl_path)


def _out_total_weight_or_cbm_error_default_labeling(window):
    #    Error message 
    lb_err_msg1 = Label(window, text="Sum of weight and CBM might be mis-calculated in Output xls")
    lb_err_msg1.place(x=10, y=10)
    
    lb_err_msg2 = Label(window, text="You should check below location of fail data in output file!")
    lb_err_msg2.place(x=10, y=30)
    
    lb_err_msg2 = Label(window, text="Consider that The Input data is valid data without loss!")
    lb_err_msg2.place(x=10, y=50)

    #    Current working directory path
    working_xl_path = Config().out_xl_path 

    lb_err_working_dir = Label(window, text="Working Directory Path : ")
    lb_err_working_dir.place(x=10, y=90)
    
    ety_working_path = tk.Entry(fg="gray19", bg="snow", width=60)
    ety_working_path.place(x=10,y=110)
    ety_working_path.insert(0,working_xl_path)

def _ERROR_compare_default_labeling(window):
    #    Error message 
    lb_err_msg1 = Label(window, text="This ERROR message is triggered when total mail info differ from cargo!")
    lb_err_msg1.place(x=10, y=10)
    
    lb_err_msg2 = Label(window, text="Pleas check below error location from CARGO Result!")
    lb_err_msg2.place(x=10, y=30)

    lb_err_msg3 = Label(window, text="After fix these error, Please re-run!")
    lb_err_msg3.place(x=10, y=50)

    #    Current working directory path
    working_xl_path = Config().export_info_from_cargo_path 
    working_sheet = Config().result_carco_sheet

    lb_err_working_dir = Label(window, text="Working Directory Path : ")
    lb_err_working_dir.place(x=10, y=90)
    
    ety_working_path = tk.Entry(fg="gray19", bg="snow", width=60)
    ety_working_path.place(x=10,y=110)
    ety_working_path.insert(0,working_xl_path)

    lb_err_working_sheet = Label(window, text="Working Sheet Name : ")
    lb_err_working_sheet.place(x=10, y=130)

    ety_working_sheet = tk.Entry(fg="gray19", bg="snow", width=60)
    ety_working_sheet.place(x=10,y=150)
    ety_working_sheet.insert(0,working_sheet)

def _ERROR_mail_con_acid_empty_default_labeling(window):
    #    Error message 
    lb_err_msg1 = Label(window, text="This ERROR message is triggered when Consignee or ACID info is empty in Input mail format!")
    lb_err_msg1.place(x=10, y=10)
    
    lb_err_msg2 = Label(window, text="Pleas check below error location from Input mail format!")
    lb_err_msg2.place(x=10, y=30)

    lb_err_msg3 = Label(window, text="After fix these error, Please re-run!")
    lb_err_msg3.place(x=10, y=50)

    #    Current working directory path
    working_xl_path = Config().mail_copy_in_name 

    lb_err_working_dir = Label(window, text="Working Directory Path : ")
    lb_err_working_dir.place(x=10, y=90)
    
    ety_working_path = tk.Entry(fg="gray19", bg="snow", width=60)
    ety_working_path.place(x=10,y=110)
    ety_working_path.insert(0,working_xl_path)


def _ERROR_CARGO_default_labeling(window):
    #    Error message 
    lb_err_msg1 = Label(window, text="This ERROR message is triggered from CARGO MANIFAST!")
    lb_err_msg1.place(x=10, y=10)
    
    lb_err_msg2 = Label(window, text="Pleas check below error location from CARGO MANIFAST!")
    lb_err_msg2.place(x=10, y=30)

    lb_err_msg3 = Label(window, text="After fix these error, Please re-run!")
    lb_err_msg3.place(x=10, y=50)

    #    Current working directory path
    working_xl_path = Config().cargo_path 

    lb_err_working_dir = Label(window, text="Working Directory Path : ")
    lb_err_working_dir.place(x=10, y=90)
    
    ety_working_path = tk.Entry(fg="gray19", bg="snow", width=60)
    ety_working_path.place(x=10,y=110)
    ety_working_path.insert(0,working_xl_path)

    
def _gen_error_win():
    window = Tk()
    window.title("Error Message!")
    return window


def _call_error_message_window(window,*err_dict):
    # label,entry location config
    default_y_row = 120
    lb_y_step_size = 30
    lb_x_row = 10
    ety_y_step_size = 60
    ety_x_row = 10
    
    dict_num = len(err_dict)

    for num in range(dict_num):
        curr_err_dict = err_dict[num]
        for err_cnt in curr_err_dict:
            error_rows,error_col = curr_err_dict[err_cnt]
            if error_rows or error_col:
                #    N th Error Row Location
                lb_y_row = default_y_row + lb_y_step_size

                lb_err_error_row = Label(window, text= "Error Row Location : ")
                lb_err_error_row.place(x=lb_x_row,y=lb_y_row)

                ety_y_row = default_y_row + ety_y_step_size 

                ety_error_row = tk.Entry(fg="gray19", bg="snow", width=15)
                ety_error_row.place(x=ety_x_row,y=ety_y_row)
                ety_error_row.insert(0,error_rows)

                #  N th  Error Column Location
                lb_err_error_col = Label(window, text= "Error Column Location : ")
                lb_err_error_col.place(x=150, y=lb_y_row)
                ety_error_col = tk.Entry(fg="gray19", bg="snow", width=15)
                ety_error_col.place(x=150,y=ety_y_row)
                ety_error_col.insert(0,error_col)

                default_y_row = ety_y_row
            else:
                continue
    window.geometry('500x600')
    
    window.mainloop()
    
def _call_error_in_out_value_message_window(window,*err_dict):
    # label,entry location config
    default_y_row = 120
    lb_y_step_size = 30
    lb_x_row = 10
    ety_y_step_size = 60
    ety_x_row = 10
    
    dict_num = len(err_dict)
    for num in range(dict_num):
        curr_err_dict = err_dict[num]
        for err_cnt in curr_err_dict:
            error_rows,error_in_val,error_out_val,error_col = curr_err_dict[err_cnt]
            if error_rows or error_in_val or error_out_val or error_col :
                #    N th Error Row Location
                lb_y_row = default_y_row + lb_y_step_size

                lb_err_error_row = Label(window, text= "Error Row Location : ")
                lb_err_error_row.place(x=lb_x_row,y=lb_y_row)

                ety_y_row = default_y_row + ety_y_step_size 

                ety_error_row = tk.Entry(fg="gray19", bg="snow", width=15)
                ety_error_row.place(x=ety_x_row,y=ety_y_row)
                ety_error_row.insert(0,error_rows)

                #  N th  Error Column Location
                lb_err_error_col = Label(window, text= "Error Column Location : ")
                lb_err_error_col.place(x=150, y=lb_y_row)
                ety_error_col = tk.Entry(fg="gray19", bg="snow", width=15)
                ety_error_col.place(x=150,y=ety_y_row)
                ety_error_col.insert(0,error_col)

                #  N th  Error input Value Location
                lb_err_error_in_val = Label(window, text= "Error input Value Location : ")
                lb_err_error_in_val.place(x=300, y=lb_y_row)
                ety_error_in_val = tk.Entry(fg="gray19", bg="snow", width=15)
                ety_error_in_val.place(x=300,y=ety_y_row)
                ety_error_in_val.insert(0,error_in_val)

                #  N th  Error output Value Location
                lb_err_error_out_val = Label(window, text= "Error output Value Location : ")
                lb_err_error_out_val.place(x=450, y=lb_y_row)
                ety_error_out_val = tk.Entry(fg="red", bg="snow", width=15)
                ety_error_out_val.place(x=450,y=ety_y_row)
                ety_error_out_val.insert(0,error_out_val)

                default_y_row = ety_y_row
            else:
                continue
    window.geometry('650x500')
    
    window.mainloop()


def _call_cargo_error_message_window(window,*err_dict):
    # label,entry location config
    default_y_row = 190
    lb_y_step_size = 30
    lb_x_row = 10
    ety_y_step_size = 60
    ety_x_row = 10
    
    dict_num = len(err_dict)
    # {1: ([236, 1031, 1104, 1175, 1630, 1815, 1967, 2585, 2845, 3047, 3716, 3951, 14981], 'DATA_DISCONNECT')}

    for num in range(dict_num):
        curr_err_dict = err_dict[num]
        for err_cnt in curr_err_dict:
            error_rows,error_col,error_cat = curr_err_dict[err_cnt]
            if error_rows or error_col or error_cat:
                #    N th Error Row Location
                lb_y_row = default_y_row + lb_y_step_size

                lb_err_error_row = Label(window, text= "Error Row Location : ")
                lb_err_error_row.place(x=lb_x_row,y=lb_y_row)

                ety_y_row = default_y_row + ety_y_step_size 

                ety_error_row = tk.Entry(fg="gray19", bg="snow", width=70)
                ety_error_row.place(x=ety_x_row,y=ety_y_row)
                ety_error_row.insert(0,error_rows)

                #  N th  Error Column Location
                lb_err_error_col = Label(window, text= "Error Column Location : ")
                lb_err_error_col.place(x=600, y=lb_y_row)
                ety_error_col = tk.Entry(fg="gray19", bg="snow", width=5)
                ety_error_col.place(x=600,y=ety_y_row)
                ety_error_col.insert(0,error_col)

                #  N th  Error Category Location
                lb_err_error_val = Label(window, text= "Error Category : ")
                lb_err_error_val.place(x=800, y=lb_y_row)
                ety_error_val = tk.Entry(fg="red", bg="snow", width=20)
                ety_error_val.place(x=800,y=ety_y_row)
                ety_error_val.insert(0,error_cat)

                default_y_row = ety_y_row
            else:
                continue
    window.geometry('1000x400')
    
    window.mainloop()


def _call_error_input_con_acid_empty_message_window(window,*err_dict):
    # label,entry location config
    default_y_row = 190
    lb_y_step_size = 30
    lb_x_row = 10
    ety_y_step_size = 60
    ety_x_row = 10
    
    dict_num = len(err_dict)

    for num in range(dict_num):
        curr_err_dict = err_dict[num]
        for err_cnt in curr_err_dict:
            error_rows,error_col,error_cat = curr_err_dict[err_cnt]
            if error_rows or error_col or error_cat:
                #    N th Error Row Location
                lb_y_row = default_y_row + lb_y_step_size

                lb_err_error_row = Label(window, text= "Error Row Location : ")
                lb_err_error_row.place(x=lb_x_row,y=lb_y_row)

                ety_y_row = default_y_row + ety_y_step_size 

                ety_error_row = tk.Entry(fg="gray19", bg="snow", width=20)
                ety_error_row.place(x=ety_x_row,y=ety_y_row)
                ety_error_row.insert(0,error_rows)

                #  N th  Error Column Location
                lb_err_error_col = Label(window, text= "Error Sheet : ")
                lb_err_error_col.place(x=300, y=lb_y_row)
                ety_error_col = tk.Entry(fg="gray19", bg="snow", width=20)
                ety_error_col.place(x=300,y=ety_y_row)
                ety_error_col.insert(0,error_col)

                #  N th  Error Category Location
                lb_err_error_val = Label(window, text= "Error Category : ")
                lb_err_error_val.place(x=600, y=lb_y_row)
                ety_error_val = tk.Entry(fg="red", bg="snow", width=20)
                ety_error_val.place(x=600,y=ety_y_row)
                ety_error_val.insert(0,error_cat)

                default_y_row = ety_y_row
            else:
                continue
    window.geometry('1000x400')
    
    window.mainloop()





def _check_error_col(temp_df):
    df = temp_df.replace('', np.nan)
    row_index = 2
    err_cnt = 0
    err_dict = {}
    
    for col in df.columns:
        check_each_col_isnull_df = df[col].isnull()
        
        if check_each_col_isnull_df.any():
            err_cnt = err_cnt + 1
            error_index = df[check_each_col_isnull_df].index
            error_row = list(error_index + row_index)
            error_col = col
            err_dict.update({err_cnt:(error_row,error_col)}) 
        else:
            pass
    
    for col in df.columns:
        check_each_col_isnull_df = df[col].isnull()
        if check_each_col_isnull_df.any():
            window = _gen_error_win()
            _in_empty_error_default_labeling(window)
            _call_error_message_window(window,err_dict)
            break


def _find_location(out_xl_df,hbl,out_data,category):
    row_index = 4
    if category == 'weight':
        match_df = out_xl_df.copy().loc[((out_xl_df['HOUSE NO'] == hbl) & (out_xl_df['G.W/T'] == out_data)),:]
    elif category == 'cbm':
        match_df = out_xl_df.copy().loc[((out_xl_df['HOUSE NO'] == hbl) & (out_xl_df['CBM'] == out_data)),:]
    elif category == 'pkg':
        match_df = out_xl_df.copy().loc[((out_xl_df['HOUSE NO'] == hbl) & (out_xl_df['P`KGS'] == out_data)),:]    
    fail_index = match_df.index
    fail_row = list(row_index + fail_index)
    
    return fail_row

def _find_fail_loc_out(out_xl_df,fail):
    in_w_val,in_c_val,in_p_val = 0,0,0
    out_w_val,out_c_val,out_p_val = 0,0,0
    find_w_loc_dict,find_c_loc_dict,find_p_loc_dict = {},{},{}
    fail_w_row,fail_c_row,fail_p_row = [],[],[]
    
    fail_w_data,fail_c_data,fail_p_data,fail_w_info,fail_c_info,fail_p_info = fail

    w_cat = (lambda fall_info_dic:'' if not fall_info_dic else fall_info_dic['category'])(fail_w_info)
    c_cat = (lambda fall_info_dic:'' if not fall_info_dic else fall_info_dic['category'])(fail_c_info)
    p_cat = (lambda fall_info_dic:'' if not fall_info_dic else fall_info_dic['category'])(fail_p_info)
    
    cat_num = 0
    for hbl in fail_w_data:
        
        w_cnt = fail_w_info[hbl]
        in_w_val,out_w_val = fail_w_data[hbl]
        fail_w_row = fail_w_row + (_find_location(out_xl_df,hbl,out_w_val,w_cat))
        
    cat_num = cat_num + 1
    find_w_loc_dict.update({cat_num:(fail_w_row,in_w_val,out_w_val,w_cat)})
        
    for hbl in fail_c_data:
        
        c_cnt = fail_c_info[hbl]
        in_c_val,out_c_val = fail_c_data[hbl]
        fail_c_row = fail_c_row + (_find_location(out_xl_df,hbl,out_c_val,c_cat))
    
    cat_num = cat_num + 1
    find_c_loc_dict.update({cat_num:(fail_c_row,in_c_val,out_c_val,c_cat)})

    for hbl in fail_p_data:
        
        p_cnt = fail_p_info[hbl]
        in_p_val,out_p_val = fail_p_data[hbl]
        fail_p_row = fail_p_row + (_find_location(out_xl_df,hbl,out_p_val,p_cat))
    
    cat_num = cat_num + 1
    find_p_loc_dict.update({cat_num:(fail_p_row,in_p_val,out_p_val,p_cat)})

    return find_w_loc_dict,find_c_loc_dict,find_p_loc_dict

def _find_err_info_loc(err_dict):
    loc_dict={}
    cnt = 0
    # {1: ([236, 1031, 1104, 1175, 1630, 1815, 1967, 2585, 2845, 3047, 3716, 3951, 14981], 'DATA_DISCONNECT')}

    for li in err_dict: 
        cnt = cnt + 1
        row,col,cat = err_dict[li]
        loc_dict.update({cnt:(row,col,cat)})

    return loc_dict

def check_valid_df(df):
    if _check_if_empty_df(df):
        warn_empty_df()
    else:
        _check_error_col(df)

def call_fail_message(out_xl_df,*fail):
    find_w_loc_dict,find_c_loc_dict,find_p_loc_dict = {},{},{}
    
    find_w_loc_dict,find_c_loc_dict,find_p_loc_dict = _find_fail_loc_out(out_xl_df,fail)
    
    window = _gen_error_win()
    _out_total_weight_or_cbm_error_default_labeling(window)
    _call_error_in_out_value_message_window(window,find_w_loc_dict,find_c_loc_dict,find_p_loc_dict)
    
def call_error_message_from_cargo(err_dict):
    loc_dict = {}
    loc_dict = _find_err_info_loc(err_dict)
    
    window = _gen_error_win()
    _ERROR_CARGO_default_labeling(window)
    _call_cargo_error_message_window(window,loc_dict)
    

def call_error_message_compare_cargo_and_total(err_dict):
    loc_dict = {}
    loc_dict = _find_err_info_loc(err_dict)
    
    window = _gen_error_win()
    _ERROR_compare_default_labeling(window)
    _call_cargo_error_message_window(window,loc_dict)


def call_error_message_mail_con_acid_empty(err_dict):
    loc_dict = {}
    loc_dict = _find_err_info_loc(err_dict)
    
    window = _gen_error_win()
    _ERROR_mail_con_acid_empty_default_labeling(window)
    _call_error_input_con_acid_empty_message_window(window,loc_dict)