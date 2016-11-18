#!/usr/bin/env python
# coding: utf8


"""
    Deezer ``connection`` module for NativeSDK
    ==========================================

    Manage connection operations and the session info.

    This is a part of the Python wrapper for the NativeSDK. This module wraps
    the deezer-connect functions into several python classes. The calls to the
    C lib are done using ctypes.

    Globals
    -------

    libdeezer: The lib object loaded to perform the function calls to the C SDK
    *_func types: C func types declared to translate python functions to
        callbacks when required. See section Callback types below.

    Content summary
    ---------------

    The class used to manage connection is the Connection class. The others
    describe C enums to be used in callbacks (see below) and logs.



"""

from deezer_import import *


class DZConnectConfiguration(Structure):
    """Contains the connection info used by the sdk."""
    _fields_ = [(u'app_id', c_char_p),
                (u'product_id', c_char_p),
                (u'product_build_id', c_char_p),
                (u'user_profile_path', c_char_p),
                (u'dz_connect_on_event_cb', dz_on_event_cb_func),
                (u'anonymous_blob', c_void_p),
                (u'dz_connect_crash_reporting_delegate', dz_connect_crash_reporting_delegate_func)]


class ConnectionInitFailedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConnectionRequestFailedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConnectionActivationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConnectionEvent:
    """Defines values associated to connection events.
        In the on_event_callbacks you define, you can convert the event object
        to an integer corresponding to a value of this class using get_event

        Warning: If you happen to change the values, make sure they correspond
        to the values of the corresponding C enum
    """

    def __init__(self):
        pass

    (
        UNKNOWN,
        USER_OFFLINE_AVAILABLE,
        USER_ACCESS_TOKEN_OK,
        USER_ACCESS_TOKEN_FAILED,
        USER_LOGIN_OK,
        USER_LOGIN_FAIL_NETWORK_ERROR,
        USER_LOGIN_FAIL_BAD_CREDENTIALS,
        USER_LOGIN_FAIL_USER_INFO,
        USER_LOGIN_FAIL_OFFLINE_MODE,
        USER_NEW_OPTIONS,
        ADVERTISEMENT_START,
        ADVERTISEMENT_STOP
    ) = range(0, 12)

    @staticmethod
    def event_name(event):
        event_names = [
            u'UNKNOWN',
            u'USER_OFFLINE_AVAILABLE',
            u'USER_ACCESS_TOKEN_OK',
            u'USER_ACCESS_TOKEN_FAILED',
            u'USER_LOGIN_OK',
            u'USER_LOGIN_FAIL_NETWORK_ERROR',
            u'USER_LOGIN_FAIL_BAD_CREDENTIALS',
            u'USER_LOGIN_FAIL_USER_INFO',
            u'USER_LOGIN_FAIL_OFFLINE_MODE',
            u'USER_NEW_OPTIONS',
            u'ADVERTISEMENT_START',
            u'ADVERTISEMENT_STOP'
        ]
        return event_names[event]


class ConnectionStreamingMode:
    """Defines values associated to the streaming mode

    Warning: If you happen to change the values, make sure they correspond
    to the values of the corresponding C enum
    """

    def __init__(self):
        pass

    (
        UNKNOWN,
        ON_DEMAND,
        RADIO
    ) = range(0, 3)


class Connection:
    """Manage connection and user session"""

    def __init__(self, context, app_id, product_id, product_build_id, user_profile_path, dz_connect_on_event_cb=None,
                 anonymous_blob=None, dz_connect_crash_reporting_delegate=None):
        """
        :param app_id: The ID of the application
        :param product_id: The name of your application
        :param product_build_id: The version number
        :param user_profile_path: The cache path of the user. Deprecated.
        :param dz_connect_on_event_cb: The event listener to connection
            operations
        :param anonymous_blob: Deprecated
        :param dz_connect_crash_reporting_delegate: The error callback
        :type app_id: unicode
        :type product_id: unicode
        :type product_build_id: unicode
        :type user_profile_path: unicode
        :type dz_connect_on_event_cb: function
        :type dz_connect_crash_reporting_delegate: function
        """
        self.context = context
        self.app_id = app_id
        self.product_id = product_id
        self.product_build_id = product_build_id
        self.user_profile_path = user_profile_path
        self.dz_connect_on_event_cb = dz_on_event_cb_func(dz_connect_on_event_cb)
        self.anonymous_blob = anonymous_blob
        self.dz_connect_crash_reporting_delegate = dz_connect_crash_reporting_delegate_func(
            dz_connect_crash_reporting_delegate)
        self.handle = 0
        self.active = False
        self.set_event_cb(dz_connect_on_event_cb)
        config = DZConnectConfiguration(c_char_p(self.app_id),
                                        c_char_p(self.product_id),
                                        c_char_p(self.product_build_id),
                                        c_char_p(self.user_profile_path),
                                        self.dz_connect_on_event_cb,
                                        c_void_p(self.anonymous_blob),
                                        self.dz_connect_crash_reporting_delegate)
        self.handle = libdeezer.dz_connect_new(byref(config))
        if not self.handle:
            raise ConnectionInitFailedError(u'Connection handle failed to initialize. Check connection info you gave.')
        self._activate(context)

    def set_event_cb(self, callback):
        """
        Set dz_connect_on_event_cb, a callback called after each state change.
        See "callbacks" section in the module documentation.

        :param callback: The event callback to give.
        :type callback: function
        """
        self.dz_connect_on_event_cb = dz_on_event_cb_func(callback)

    def get_device_id(self):
        """
        :return: The device ID for logs
        """
        return libdeezer.dz_connect_get_device_id(self.handle)

    def debug_log_disable(self):
        """
        Mute all API logs for readability's sake
        """
        if libdeezer.dz_connect_debug_log_disable(self.handle):
            raise ConnectionRequestFailedError(u'debug_log_disable: Request failed.')

    def _activate(self, user_data=None):
        """Launch the connection. Call this after init_handle.

        Calls self.dz_connect_on_event_cb after activation. You can provide any
        object you want through user_data as long as it is managed by this
        callback.

        :param user_data: An object you want to pass to dz_connect_on_event_cb.
        :type user_data: The type of the object you want to manipulate
        """
        context = py_object(user_data) if user_data else c_void_p(0)
        if libdeezer.dz_connect_activate(self.handle, context):
            raise ConnectionActivationError(u'Failed to activate connection. Check your network connection.')
        self.active = True

    def cache_path_set(self, user_cache_path, activity_operation_cb=None, operation_userdata=None):
        """Set the cache path for debug purposes and logs.

        Cache will be stored in the specified path. Calls
        activity_operation_cb after the operation.

        :param user_cache_path: The desired path
        :param activity_operation_cb: The callback to this function.
        :param operation_userdata: An object you want to pass to
            activity_operation_cb.
        :type user_cache_path: str
        :type activity_operation_cb: dz_activity_operation_cb_func
        :type operation_userdata: The type of the object you want to manipulate
        """
        context = py_object(operation_userdata) if operation_userdata else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_connect_cache_path_set(self.handle, cb, context,
                                               c_char_p(user_cache_path)):
            raise ConnectionRequestFailedError(
                u'cache_path_set: Request failed. Check connection and/or path validity.')

    def set_access_token(self, user_access_token, activity_operation_cb=None, operation_user_data=None):
        """
        Set the user access token given by OAuth process.
        Mandatory to allow connection.

        :param user_access_token: The token given by OAuth 2 process.
            Refer to the API documentation.
        :param activity_operation_cb: The callback to this function.
        :param operation_user_data: An object you want to pass to
            activity_operation_cb.
        :type user_access_token: unicode
        :type activity_operation_cb: dz_activity_operation_cb_func
        :type operation_user_data: The type of the object you want to manipulate
        """
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_connect_set_access_token(self.handle, cb, context,
                                                 c_char_p(user_access_token)):
            raise ConnectionRequestFailedError(u'set_access_token: Request failed. Check access token or update it.')

    def set_offline_mode(self, offline_mode_forced, activity_operation_cb=None, operation_user_data=None):
        """Force offline mode in lib.

        Calling this function is mandatory to force user login.

        :param activity_operation_cb: The callback of the operation.
        :param operation_user_data: An object you want to pass to
            activity_operation_cb.
        :param offline_mode_forced: Force offline mode. Leave to False
            if just to allow connection.
        :type activity_operation_cb: dz_activity_operation_cb_func
        :type operation_user_data: The type of the object you want to manipulate
        :type offline_mode_forced: bool
        """
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_connect_offline_mode(self.handle, cb, context, c_bool(offline_mode_forced)):
            raise ConnectionRequestFailedError(
                u'connect_offline_mode: Request failed. Check connection and callbacks if used.')

    def shutdown(self, activity_operation_cb=None, operation_user_data=None):
        """Deactivate connection associated to the handle."""
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if self.handle:
            libdeezer.dz_connect_deactivate(self.handle, cb, context)
            self.active = False

    @staticmethod
    def get_event(event_obj):
        """Get the event value from the event_obj given by the SDK."""
        return int(libdeezer.dz_player_event_get_type(c_void_p(event_obj)))

    @staticmethod
    def get_build_id():
        """Return the build id of libdeezer"""
        return int(libdeezer.dz_connect_get_build_id())

