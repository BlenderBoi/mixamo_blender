import bpy, sys, linecache, ast

def get_error_message():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    error_message = 'Error in ({}\nLine {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
    return error_message


def get_addon_preferences():
    return bpy.context.preferences.addons[__package__].preferences