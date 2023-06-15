import csv
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser
import os
from django.http import FileResponse
import mysql.connector


# Connect to the database
database = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Autodrome@123',
    db='autodrome_db',
    autocommit=True
)
mycursor = database.cursor()

def process_csv(request):
    if request.method == 'POST':

        csv_file = request.FILES['csv_file']
        input_data = csv.DictReader(csv_file.read().decode('utf-8').splitlines())

        # Convert the csv.DictReader object to a list of dictionaries
        data = list(input_data)

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)

        channel_ids = df.values.flatten().tolist()

        api_key = 'AIzaSyAMB1zv6Hm5KoJEkySE9Ty3ztfBTsDjgFw'
        youtube = build('youtube', 'v3', developerKey=api_key)

        print("initiating process")

        def get_channel_stats(youtube, channel_ids):
            all_data = []

            # Create a list of 50 channel IDs at a time, to be used in each API request
            id_lists = [channel_ids[i:i + 50] for i in range(0, len(channel_ids), 50)]

            # Iterate through the list of ID lists
            for id_list in id_lists:
                # Make an API request for the current list of IDs
                request = youtube.channels().list(part='snippet,contentDetails,statistics', id=','.join(id_list))
                response = request.execute()

                # Process the API response
                for i in range(len(response['items'])):
                    data = dict(channel_name=response['items'][i]['snippet']['title'],
                                subscribers=response['items'][i]['statistics']['subscriberCount'],
                                views=response['items'][i]['statistics']['viewCount'],
                                total_video=response['items'][i]['statistics']['videoCount'],
                                playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
                    all_data.append(data)

            return all_data

        yt = get_channel_stats(youtube, channel_ids)

        yt_data = pd.DataFrame(yt)

        playlist_ids = yt_data['playlist_id']
        print("Collecting playlist_id")

        def get_video_ids(youtube, playlist_ids):
            video_ids = []
            max_results = 50  # Set the maximum number of results per API request
            # Iterate over the list of playlist IDs
            for playlist_id in playlist_ids:
                try:
                    # Make an API request to get the video IDs for the current playlist
                    request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId=playlist_id,
                        maxResults=max_results)
                    response = request.execute()

                    # Get the video IDs for the current playlist
                    video_ids.extend(
                        [response['items'][i]['contentDetails']['videoId'] for i in range(len(response['items']))])

                    next_page_token = response.get('nextPageToken')
                    more_pages = True

                    # Get the video IDs for additional pages of results (if any)
                    while more_pages:
                        if next_page_token is None:
                            more_pages = False
                        else:
                            request = youtube.playlistItems().list(
                                part='contentDetails',
                                playlistId=playlist_id,
                                maxResults=max_results,
                                pageToken=next_page_token)
                            response = request.execute()

                            video_ids.extend(
                                [response['items'][i]['contentDetails']['videoId'] for i in range(len(response['items']))])

                            next_page_token = response.get('nextPageToken')
                except HttpError:
                    # Skip the invalid playlist ID and move on to the next one
                    continue

            return video_ids

        video_ids = get_video_ids(youtube, playlist_ids)

        print("Collecting video_ids")

        def get_video_details(youtube, video_ids):
            all_video_stats = []
            video_id_chunks = [video_ids[i:i + 50] for i in range(0, len(video_ids), 50)]

            for chunk in video_id_chunks:
                request = youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(chunk)
                )
                response = request.execute()

                # Add the video statistics for each video to the all_video_stats list
                for video in response['items']:
                    video_stats = {'snippet': ['channelTitle', 'title', 'description', 'tags', 'publishedAt', 'thumbnail',
                                            'channelId'],
                                'statistics': ['viewCount', 'likeCount', 'commentCount', 'favoriteCount'],
                                'contentDetails': ['duration', 'definition', 'caption']
                                }

                    video_info = {}
                    video_info['video_id'] = video['id']

                    for k in video_stats.keys():
                        for v in video_stats[k]:
                            if v == 'thumbnail':
                                thumbnail = video['snippet']['thumbnails']['default']['url']
                                video_info[v] = thumbnail
                            else:
                                video_info[v] = video[k].get(v)

                    all_video_stats.append(video_info)

            # Return the all_video_stats list
            return all_video_stats
            # Save the video data to the database


        video_df = get_video_details(youtube, video_ids)

        video_data = pd.DataFrame(video_df)

        video_data['publishedAt'] = video_data['publishedAt'].apply(lambda x: parser.parse(x))
        video_data['publishedAt'] = video_data['publishedAt'].apply(lambda x: x.strftime("%Y-%m-%d"))

        video_data['tags'] = video_data['tags'].apply(lambda x: tuple(x) if isinstance(x, list) else x)
        video_data['tags'].unique()
        video_data['tags'] = video_data['tags'].astype(str)


        # Create a CSV file from the DataFrame
        csv_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'youtube_data.csv')
        video_data.to_csv(csv_file_path, index=False)

        data = video_data.fillna(method='ffill')


        for index, row in data.iterrows():
            video_id = row['video_id']
            channel_title = row['channelTitle']
            title = row['title']
            description = row['description']
            tags = row['tags']
            publishedAt = row['publishedAt']
            thumbnail = row['thumbnail']
            channel_id = row['channelId']
            view_count = row['viewCount']
            likes_count = row['likeCount']
            comments_count = row['commentCount']
            favorite_count = row['favoriteCount']
            duration = row['duration']
            definition = row['definition']
            caption = row['caption']
            
            sql = "INSERT IGNORE INTO youtube_scrape_youtube_data (video_id, channel_title, title, description, tags, published_at, thumbnail, channel_id, view_count, like_count, comment_count, favorite_count, duration, definition, caption) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (video_id, channel_title, title, description, tags, publishedAt, thumbnail, channel_id, view_count, likes_count, comments_count, favorite_count, duration, definition, caption)
            
            mycursor.execute(sql, val)
            
        database.commit()
        database.close()

        
        print("Process done.")

        # Return the CSV file as an HTTP response
        response = FileResponse(open(csv_file_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename="youtube_data.csv"'
        return response

    else:
        return render(request, 'files/process_csv.html')


import json

def get_status(request):
    status = {
        'message': 'Processing the CSV file. Please wait...',
        'percent_complete': 0,
        'complete': False
    }
    # Update the status object with the current status of the background process
    # ...

    return HttpResponse(json.dumps(status), content_type='application/json')