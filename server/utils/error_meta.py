import os, sys

def error_meta(depth=1):
    err_type, _, err_tb = sys.exc_info()
    err_func = os.path.split(err_tb.tb_frame.f_code.co_filename)[depth]
    err_line = err_tb.tb_lineno
    return err_type, err_func, err_line
