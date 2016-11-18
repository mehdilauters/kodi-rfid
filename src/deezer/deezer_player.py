#!/usr/bin/env python
# coding: utf8


"""
    Deezer ``player`` module for NativeSDK
    ==========================================

    Manage music, load and play songs, reports player events.

    This is a part of the Python wrapper for the NativeSDK. This module wraps
    the deezer-player functions into several python classes. The calls to the
    C lib are done using ctypes.

    Content summary
    ---------------

    The class used to manage the player is the Player class. The others
    describe C enums to be used in callbacks (see below) and logs as
    events (like the PlayerEvent class).

"""

from deezer_connect import *


class PlayerInitFailedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PlayerRequestFailedError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PlayerActivationError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PlayerIndex:
    """
        Defines track position in queuelist

        Warning: If you happen to change the values, make sure they correspond
        to the values of the corresponding C enum
    """
    def __init__(self):
        pass

    INVALID = sys.maxsize
    PREVIOUS = sys.maxsize - 1
    CURRENT = sys.maxsize - 2
    NEXT = sys.maxsize - 3


class PlayerEvent:
    """
        Defines values associated to player events returned by get_event.
        Use it for your callbacks.

        Warning: If you happen to change the values, make sure they correspond
        to the values of the corresponding C enum
    """
    def __init__(self):
        pass

    (
        UNKNOWN,
        LIMITATION_FORCED_PAUSE,
        QUEUELIST_LOADED,
        QUEUELIST_NO_RIGHT,
        QUEUELIST_TRACK_NOT_AVAILABLE_OFFLINE,
        QUEUELIST_TRACK_RIGHTS_AFTER_AUDIOADS,
        QUEUELIST_SKIP_NO_RIGHT,
        QUEUELIST_TRACK_SELECTED,
        QUEUELIST_NEED_NATURAL_NEXT,
        MEDIASTREAM_DATA_READY,
        MEDIASTREAM_DATA_READY_AFTER_SEEK,
        RENDER_TRACK_START_FAILURE,
        RENDER_TRACK_START,
        RENDER_TRACK_END,
        RENDER_TRACK_PAUSED,
        RENDER_TRACK_SEEKING,
        RENDER_TRACK_UNDERFLOW,
        RENDER_TRACK_RESUMED,
        RENDER_TRACK_REMOVED
    ) = range(0, 19)

    @staticmethod
    def event_name(event):
        event_names = [
            u'UNKNOWN',
            u'LIMITATION_FORCED_PAUSE',
            u'QUEUELIST_LOADED',
            u'QUEUELIST_TRACK_NO_RIGHT',
            u'QUEUELIST_TRACK_NOT_AVAILABLE_OFFLINE',
            u'QUEUELIST_TRACK_RIGHTS_AFTER_AUDIOADS',
            u'QUEUELIST_SKIP_NO_RIGHT',
            u'QUEUELIST_TRACK_SELECTED',
            u'QUEUELIST_NEED_NATURAL_NEXT',
            u'MEDIASTREAM_DATA_READY',
            u'MEDIASTREAM_DATA_READY_AFTER_SEEK',
            u'RENDER_TRACK_START_FAILURE',
            u'RENDER_TRACK_START',
            u'RENDER_TRACK_END',
            u'RENDER_TRACK_PAUSED',
            u'RENDER_TRACK_SEEKING',
            u'RENDER_TRACK_UNDERFLOW',
            u'RENDER_TRACK_RESUMED',
            u'RENDER_TRACK_REMOVED'
        ]
        return event_names[event]


class PlayerCommand:
    """Defines commands to update player's state

        Warning: If you happen to change the values, make sure they correspond
        to the values of the corresponding C enum
    """

    def __init__(self):
        pass

    (
        UNKNOWN,
        START_TRACKLIST,
        JUMP_IN_TRACKLIST,
        NEXT,
        PREV,
        DISLIKE,
        NATURAL_END,
        RESUMED_AFTER_ADS
    ) = range(0, 8)


class PlayerRepeatMode:
    """Defines repeat mode to apply after a track

        Warning: If you happen to change the values, make sure they correspond
        to the values of the corresponding C enum
    """

    def __init__(self):
        pass

    (
        OFF,
        ON,
        ALL
    ) = range(0, 3)


class Player:
    """A simple player load and play music.

        Attributes:
            dz_player           The ID of the player
            current_track       The track currently played
            active              True if the player has been activated
    """
    def __init__(self, context, connect_handle):
        """
        :param context: A connection object to store connection info
        :type connection: connection.Connection
        """
        self.context = context  # TODO: remove context from self
        self.handle = 0
        self.current_content = None
        self.active = False
        self.is_playing = False
        self.handle = libdeezer.dz_player_new(connect_handle)
        if not self.handle:
            raise PlayerInitFailedError(u"Player failed to init. Check that connection is established.")
        self._activate(self.context)

    def _activate(self, supervisor=None):
        """Activate the player.

        :param supervisor: An object that can be manipulated by your
            dz_player_on_event_cb to store info.
        :type supervisor: Same as userdata in dz_player_on_event_cb
        """
        context = py_object(supervisor) if supervisor else c_void_p(0)
        if libdeezer.dz_player_activate(self.handle, context):
            raise PlayerActivationError(u"Player activation failed. Check player info and your network connection.")
        self.active = True

    def set_event_cb(self, cb):
        """
        Set dz_player_on_event_cb that will be triggered anytime the player
        state changes.

        :param cb: The event callback to give.
        :type cb: dz_on_event_cb_func
        """
        if libdeezer.dz_player_set_event_cb(self.handle, cb):
            raise PlayerRequestFailedError(
                u"set_event_cb: Request failed. Check the given callback arguments and return types and/or the player.")

    def load(self, content, activity_operation_cb=None, operation_user_data=None):
        """Load the given content or the current track.

        In the first case, set the current_track to the given track.

        :param content: The track/tracklist to load
        :param activity_operation_cb: A callback triggered after operation.
        See module docstring.
        :param operation_user_data:  Any object your operation_callback can
        manipulate. Must inherit from Structure class.
        :type content: str
        :type activity_operation_cb: dz_activity_operation_cb_func
        :type operation_user_data: Same as operation_user_data in your
        callback. Must inherit from Structure as it is used by ctypes
        """
        if content:
            self.current_content = content
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_player_load(self.handle, cb, context, self.current_content):
            raise PlayerRequestFailedError(u"load: Unable to load selected track. Check connection and tracklist data.")

    def play(self, activity_operation_cb=None, operation_user_data=None, command=PlayerCommand.START_TRACKLIST,
             index=PlayerIndex.CURRENT):
        """Play the current track if loaded.
            The player gets data and renders it.

        :param command: Player command
        :param index: Index of the track to play
        :param activity_operation_cb: Called when async result is available
        :param operation_user_data: A reference to user's data
        :type command: PlayerCommand
        :type index: int
        :type activity_operation_cb: dz_activity_operation_cb_func
        :type operation_user_data: Same as operation_user_data in your callback.
            Must inherit from structure as it is used by ctypes.
        """
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_player_play(self.handle, cb, context, command, index) not in range(0, 2):
            raise PlayerRequestFailedError(u"play: Unable to play selected track. Check player commands and info.")
        self.is_playing = True

    def shutdown(self, activity_operation_cb=None, operation_user_data=None):
        """Deactivate the player"""
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if self.handle:
            libdeezer.dz_player_deactivate(self.handle, cb, context)

    def stop(self, activity_operation_cb=None, operation_user_data=None):
        """Stop the currently playing track"""
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_player_stop(self.handle, cb, context):
            raise PlayerRequestFailedError(u"play: Unable to stop track. Check player commands and info.")
        self.is_playing = False

    def pause(self, activity_operation_cb=None, operation_user_data=None):
        """Pause the track"""
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_player_pause(self.handle, cb, context):
            raise PlayerRequestFailedError(u"play: Unable to pause track. Check player commands and info.")
        self.is_playing = False

    def resume(self, activity_operation_cb=None, operation_user_data=None):
        """Resume the track if it has been paused"""
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_player_resume(self.handle, cb, context):
            raise PlayerRequestFailedError(u"play: Unable to resume track. Check player commands and info.")
        self.is_playing = True

    def set_repeat_mode(self, repeat_mode, activity_operation_cb=None, operation_user_data=None):
        """Set the repeat mode of the player.
            :param repeat_mode: The repeat mode to set
            :type repeat_mode: PlayerRepeatMode
        """
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_player_set_repeat_mode(self.handle, cb, context, repeat_mode):
            raise PlayerRequestFailedError(u"play: Unable to set repeat mode. Check player commands and info.")

    def enable_shuffle_mode(self, shuffle_mode, activity_operation_cb=None, operation_user_data=None):
        """Set the shuffle mode of the player (randomize track selection)
            :param shuffle_mode: Set to true to activate the random track
            selection
            :type shuffle_mode: bool
        """
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        print type(shuffle_mode)
        if libdeezer.dz_player_enable_shuffle_mode(self.handle, cb, context, shuffle_mode):
            raise PlayerRequestFailedError(u"play: Unable to set repeat mode. Check player commands and info.")

    def play_audio_ads(self, activity_operation_cb=None, operation_user_data=None):
        """Load and play an audio ad when required"""
        context = py_object(operation_user_data) if operation_user_data else c_void_p(0)
        cb = activity_operation_cb if activity_operation_cb else c_void_p(0)
        if libdeezer.dz_player_play_audioads(self.handle, cb, context):
            raise PlayerRequestFailedError(u"play: Unable to play audio ads. Check connection.")

    @staticmethod
    def get_queuelist_context(event, streaming_mode, idx):
        return libdeezer.dz_player_event_get_queuelist_context(c_void_p(event),
                                                               byref(c_uint(streaming_mode)),
                                                               byref(c_uint(idx)))

    @staticmethod
    def is_selected_track_preview(event_handle):
        return libdeezer.dz_player_event_track_selected_is_preview(c_void_p(event_handle))

    @staticmethod
    def event_track_selected_rights(event, can_pause_unpause, can_seek, nb_skip_allowed):
        libdeezer.dz_player_event_track_selected_rights(
            c_void_p(event),
            byref(can_pause_unpause),
            byref(can_seek),
            byref(nb_skip_allowed)
        )

    @staticmethod
    def event_track_selected_dzapiinfo(event):
        return libdeezer.dz_player_event_track_selected_dzapiinfo(c_void_p(event))

    @staticmethod
    def event_track_selected_next_track_dzapiinfo(event):
        return libdeezer.dz_player_event_track_selected_next_track_dzapiinfo(c_void_p(event))

    @staticmethod
    def get_event(event_obj):
        return libdeezer.dz_player_event_get_type(c_void_p(event_obj))

