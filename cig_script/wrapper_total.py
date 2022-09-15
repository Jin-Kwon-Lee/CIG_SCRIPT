import os
from compare_and_checker import compare_total_and_cargo
from wrapper_mail_in_format import main_mail
from wrapper_cargo_manifest import main_cargo

def main() :
    
    main_mail()
    main_cargo()
    compare_total_and_cargo()

if __name__ == "__main__":
    main()