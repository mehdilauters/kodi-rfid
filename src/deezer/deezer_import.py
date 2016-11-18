#! /usr/bin/env python
# coding: utf8

"""
    Imports from the C NativeSDK
    ============================

    Loads libdeezer shared library and translate its functions' prototypes. Sets
    platform-specific globals.

    Callback types
    --------------

    A bunch of this package's functions use callbacks to react to some
    connection events or to process some data. you are free to pass your funcs
    as callbacks, they are then translated to C functions and passed to the SDK
    functions. Here is a description of their parameters:

        dz_connect_on_event_cb:
            Called after connection activation and when the connection state
            changes. The callback must take 3 parameters:
            -   The handle (player or connection handle)
            -   An event object used to get the event that has been caught.
                In your callback, use the static method get_event to convert the
                event object to a ConnectionEvent index.
            -   A user_data that is an object you can pass through some
                functions and that can be manipulated by the callback.

        dz_activity_operation_cb:
            Can be set in some functions to be called after the operation. The
            callback must take 4 parameters:
            -   A delegate that is the context object to store and change info
                in the callback.
            -   An operation_userdata that is the object you can pass to the
                calling function
            -   The error status used to get the index of the error enum
            -   An event object used to get the event that has been caught

        dz_connect_crash_reporting_delegate:
            Takes nothing an returns a boolean.
            Use this to call your own crash reporting system. If left to None,
            the SDK will use its own crash reporting system.

"""
import sys
import platform
from ctypes import *

lib_path = u"./NativeSDK/Bins/Platforms"
import os
print os.path.realpath(lib_path)

# Import lib
if platform.system() == u'Darwin':
    lib_name = u'libdeezer'
    lib_path += u"/MacOSX/libdeezer.framework/Versions/Current/"
    libdeezer = cdll.LoadLibrary(lib_path+lib_name)
elif platform.system() == u'Windows':
    lib_path += u"/Windows/DLLs/"
    import os
    lib_path = os.path.abspath(os.pardir)
    lib_path = os.path.join(lib_path, u'NativeSDK', u'Bins', u'Platforms', u'Windows', u'DLLs')
    lib_name = u'libdeezer.'
    lib_name += u'x64.dll' if sys.maxsize > 2**32 else u'x86.dll'
    lib_path = os.path.join(lib_path, lib_name)
    print lib_path
    libdeezer = cdll.LoadLibrary(lib_path)
else:
    lib_name = u'libdeezer.so'
    lib_path += u"/Linux/"
    if u"arm" in platform.machine():
        lib_path += u"arm/"
    elif u"x86" in platform.machine() or u"x64" in platform.machine():
        lib_path += u"x86_64/"
    else:
        lib_path += u"i386/"
    libdeezer = cdll.LoadLibrary(lib_path+lib_name)
p_type = c_uint64 if sys.maxsize > 2**32 else c_uint32

# Callbacks
dz_on_event_cb_func = CFUNCTYPE(c_int, p_type, c_void_p, c_void_p)
dz_connect_crash_reporting_delegate_func = CFUNCTYPE(c_bool)
dz_activity_operation_cb_func = CFUNCTYPE(c_int, c_void_p, c_void_p, p_type, p_type)

# Connect functions
libdeezer.dz_connect_new.restype = p_type
libdeezer.dz_connect_get_device_id.argtypes = [p_type]
libdeezer.dz_connect_debug_log_disable.argtypes = [p_type]
libdeezer.dz_connect_activate.argtypes = [p_type, py_object]
libdeezer.dz_connect_cache_path_set.argtypes = [p_type, c_void_p, py_object, c_char_p]
libdeezer.dz_connect_set_access_token.argtypes = [p_type, c_void_p, py_object, c_char_p]
libdeezer.dz_connect_offline_mode.argtypes = [p_type, c_void_p, py_object, c_bool]
libdeezer.dz_connect_deactivate.argtypes = [p_type, c_void_p, py_object]

# Player functions
libdeezer.dz_player_new.argtypes = [p_type]
libdeezer.dz_player_new.restype = p_type
libdeezer.dz_player_activate.argtypes = [p_type, py_object]
libdeezer.dz_player_set_event_cb.argtypes = [p_type, dz_on_event_cb_func]
libdeezer.dz_player_load.argtypes = [p_type, c_void_p, py_object, c_char_p]
libdeezer.dz_player_play.argtypes = [p_type, c_void_p, py_object, c_int, c_int]
libdeezer.dz_player_deactivate.argtypes = [p_type, c_void_p, py_object]
libdeezer.dz_player_event_get_type.argtypes = [c_void_p]
libdeezer.dz_player_event_get_type.restype = c_int
libdeezer.dz_player_stop.argtypes = [p_type, c_void_p, py_object]
libdeezer.dz_player_pause.argtypes = [p_type, c_void_p, py_object]
libdeezer.dz_player_resume.argtypes = [p_type, c_void_p, py_object]
libdeezer.dz_player_event_get_queuelist_context.argtypes = [c_void_p, c_void_p, c_void_p]
libdeezer.dz_player_set_repeat_mode.argtypes = [p_type, c_void_p, py_object]
libdeezer.dz_player_enable_shuffle_mode.argtypes = [p_type, c_void_p, py_object, p_type]
libdeezer.dz_player_play_audioads.argtypes = [p_type, c_void_p, py_object]

