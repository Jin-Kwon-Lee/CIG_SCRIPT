import os
from pathlib import Path
# Excel path, name, sheet, row,column configuration


class Config:
    @property
    def parent_path(self):
        parent_path = str(Path(os.getcwd()).parent)
        return parent_path

    @property
    def local_path(self):
        local_path = self.parent_path + '/data/'
        return local_path

    @property
    def mail_copy_in_name(self):
        mail_copy_in_name = 'input_mail/mail_copy_in_format' # + self.excel_gen_date
        return mail_copy_in_name

    @property
    def mail_copy_in_path(self):
        mail_copy_in_path = self.local_path + self.mail_copy_in_name + '.xlsx'
        return mail_copy_in_path

    @property
    def export_xl_gen_name_from_mail(self):
        export_xl_gen_name_from_mail = self.local_path + 'input_mail/result/' + 'current_data_from_mail.xlsx'
        return export_xl_gen_name_from_mail
    
    @property
    def total_one_car_sheet_name(self):
        total_one_car_sheet_name = 'total_one_car'
        return total_one_car_sheet_name

    @property
    def total_mul_car_sheet_name(self):
        total_mul_car_sheet_name = 'total_mul_car'
        return total_mul_car_sheet_name

    @property
    def tot_excel_from_mail(self):
        tot_excel_from_mail = self.local_path + 'input_mail/result/' + 'total_data_from_mail.xlsx'
        return tot_excel_from_mail

    @property
    def cur_one_car_sheet(self):
        cur_one_car_sheet = 'cur_one_car'
        return cur_one_car_sheet

    @property
    def cur_mul_car_sheet(self):
        cur_mul_car_sheet = 'cur_mul_car'
        return cur_mul_car_sheet

    @property
    def one_car_sheet(self):
        one_car_sheet = 'one_car'
        return one_car_sheet

    @property
    def mul_car_sheet(self):
        mul_car_sheet = 'mul_car'
        return mul_car_sheet

    @property
    def cargo_path(self):
        cargo_path = self.local_path + 'output_cargo/CARGO_MANIFAST.xls'
        return cargo_path
    
    @property
    def export_info_from_cargo_path(self):
        export_info_from_cargo_path = self.local_path + 'output_cargo/result/result_from_cargo.xlsx'
        return export_info_from_cargo_path
    
    @property
    def result_carco_sheet(self):
        result_carco_sheet = 'cargo_info'
        return result_carco_sheet
    
    @property
    def total_mail_sheet_name(self):
        total_mail_sheet_name = 'TOTAL_SUMMARY'
        return total_mail_sheet_name
    
    @property
    def total_macro_sheet(self):
        total_macro_sheet = 'TOTAL_MACRO'
        return total_macro_sheet
    
    @property
    def edi_data_path(self):
        edi_data_path = self.local_path + 'input_mail/edi_no_data.xlsx'
        return edi_data_path
    
    @property
    def edi_sheet(self):
        edi_sheet = 'EDI_LATEST'
        return edi_sheet