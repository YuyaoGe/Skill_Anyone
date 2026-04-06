"""Tests for the downloader module."""

from youtuber2skill.downloader.channel import _is_single_video, _is_channel_url


def test_is_single_video():
    assert _is_single_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert _is_single_video("https://youtu.be/dQw4w9WgXcQ")
    assert not _is_single_video("https://www.youtube.com/@ChannelName")
    assert not _is_single_video("https://www.youtube.com/playlist?list=PLxxx")


def test_is_channel_url():
    assert _is_channel_url("https://www.youtube.com/@ChannelName")
    assert _is_channel_url("https://www.youtube.com/channel/UCxxx")
    assert not _is_channel_url("https://www.youtube.com/watch?v=xxx")
    assert not _is_channel_url("https://www.youtube.com/playlist?list=xxx")
