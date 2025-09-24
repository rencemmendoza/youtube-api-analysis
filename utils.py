"""
utils.py

Youtube API Analysis Personal Project Functions
Martin Mendoza
09/24/2025
"""

import pandas as pd


def get_channel_stats(youtube, channel_ids):
    """
    Retrieve statistics for a list of channel IDs.

    Parameters:
    - youtube: API client
    - channel_ids: list of channel IDs

    Returns:
    - DataFrame with channel stats (subscribers, views, total videos, etc.)
    """
    all_data = []

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics", id=",".join(channel_ids)
    )
    response = request.execute()

    for item in response["items"]:
        data = {
            "channelName": item["snippet"]["title"],
            "subscribers": item["statistics"]["subscriberCount"],
            "views": item["statistics"]["viewCount"],
            "totalVideos": item["statistics"]["videoCount"],
            "playlistId": item["contentDetails"]["relatedPlaylists"]["uploads"],
        }

        all_data.append(data)

    return pd.DataFrame(all_data)


def get_video_ids(youtube, playlist_id):
    """
    Retrieve all video IDs from a given YouTube playlist.

    Parameters:
    - youtube: YouTube API client
    - playlist_id: string ID of the playlist to extract videos from

    Returns:
    - list of video IDs (strings) contained in the playlist
    """
    video_ids = []

    request = youtube.playlistItems().list(
        part="snippet,contentDetails", playlistId=playlist_id, maxResults=50
    )
    response = request.execute()

    for item in response["items"]:
        video_ids.append(item["contentDetails"]["videoId"])

    next_page_token = response.get("nextPageToken")

    # continue past max results
    while next_page_token is not None:
        request = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()

        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")

    return video_ids


def get_video_details(youtube, video_ids):
    """
    Retrieve detailed information and statistics for a list of YouTube videos.

    Parameters:
    - youtube: YouTube API client
    - video_ids: list of video IDs (strings) to retrieve details for

    Returns:
    - pandas.DataFrame containing video metadata and statistics, including:
      video_id, channelTitle, title, description, tags, publishedAt,
      viewCount, likeCount, favouriteCount, commentCount, duration, definition, caption
    """
    all_video_info = []

    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics", id=",".join(video_ids[i : i + 50])
        )
        response = request.execute()
        response

        for video in response["items"]:
            stats_to_keep = {
                "snippet": [
                    "channelTitle",
                    "title",
                    "description",
                    "tags",
                    "publishedAt",
                ],
                "statistics": [
                    "viewCount",
                    "likeCount",
                    "favouriteCount",
                    "commentCount",
                ],
                "contentDetails": ["duration", "definition", "caption"],
            }
            video_info = {}
            video_info["video_id"] = video["id"]

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except KeyError:
                        video_info[v] = None

            all_video_info.append(video_info)

    return pd.DataFrame(all_video_info)


def get_comments_in_videos(youtube, video_ids):
    """
    Retrieve top-level comments for a list of YouTube videos.

    Parameters:
    - youtube: YouTube API client
    - video_ids: list of video IDs (strings) to extract comments from

    Returns:
    - pandas.DataFrame with columns:
        - video_id: ID of the video
        - comments: list of top-level comment texts for the video
    """
    all_comments = []

    for video_id in video_ids:
        request = youtube.commentThreads().list(
            part="snippet,replies", videoId=video_id
        )
        response = request.execute()

        comments_in_video = [
            comment["snippet"]["topLevelComment"]["snippet"]["textOriginal"]
            for comment in response.get("items", [])
        ]
        comments_in_video_info = {"video_id": video_id, "comments": comments_in_video}

        all_comments.append(comments_in_video_info)

    return pd.DataFrame(all_comments)


def format_view_count(x, pos):
    """
    Format a numeric view count into a readable string with K/M suffixes.

    Parameters:
    - x: numeric value representing the view count
    - pos: position (required by matplotlib FuncFormatter, not used)

    Returns:
    - string representing the formatted view count:
        - millions with 'M' suffix
        - thousands with 'K' suffix
        - integers if less than 1,000
    """
    if x >= 1_000_000:
        return f"{x / 1_000_000:.1f}M"
    elif x >= 1_000:
        return f"{x / 1_000:.0f}K"
    else:
        return f"{int(x)}"
