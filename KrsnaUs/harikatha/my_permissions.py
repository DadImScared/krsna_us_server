
from rest_framework import permissions

from .models import Playlists


class CanWriteOrDeletePlaylist(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.creator == request.user


class CanWriteOrDeletePlaylistItem(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if view.action == 'create':
                playlist = Playlists.objects.get(playlist_id=request.query_params.get('playlist_id'))
                return playlist and playlist.creator == request.user
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.playlist.creator == request.user
