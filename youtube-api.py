from googleapiclient.discovery import build
from pytube import YouTube
from art import *
import requests 
from PIL import Image 
from io import BytesIO
from pathlib import Path
import re
import requests
import os
import threading
import pickle
import os, shutil




#api set up
api_key = "AIzaSyBS4GCfFyzZjtMSNPN7NgH99KXMbsV_I4Q" #dont not share this under any circumstances

youtube = build("youtube", "v3", developerKey=api_key)

#constants
SHOW_LAST = 3
DOWNLOADS_PATH = str(Path.home() / "Downloadsa")
if not os.path.exists(DOWNLOADS_PATH):
    DOWNLOADS_PATH = "backup_downloads"
    print("print download folder not found useing backup")
    print(DOWNLOADS_PATH)
else:
    print("downloads folder exists")
#varibles
global return_videos_titles
return_videos = []
global channel_name
channel_name = ""
channel_data = {}
return_video_titles = []



#check/load data
print("checking followed_channels.dat")
if os.path.isfile("followed_channels.dat") == False:
    print("no file creating followed_channels.dat")
    followed_channels = {}
    pickle.dump(followed_channels, open("followed_channels.dat","wb"))
print("loading followed_channels.dat")
try:
    with open("followed_channels.dat","rb") as file:
        followed_channels = pickle.load(file)
except EOFError:
    print("ERROR FILE EMPTY")
    print("assuming the worst and deleted all save data in effort to keep syncrazation")
    try:
        os.remove("channels.dat")
    except:
        print("channels.dat already removed")
    try:
        shutil.rmtree("youtube_thumbnails")
    except:
        print("thumbnail path arleady removed")
    followed_channels = {}
    followed_channels = {
    "list": [],
    }



print("checking channel.dat")
if os.path.isfile("channels.dat") == False:
    print("no file creating channel.dat")
    channels = {}
    pickle.dump(channels, open("channels.dat", "wb"))
print("loading channel.dat")
channels = pickle.load(open("channels.dat","rb"))
if os.path.isfile("channels.dat"):
    with open("channels.dat", "rb") as file:
        channel_data = pickle.load(file)

print("checking thumbnail path")
if not os.path.exists("youtube_thumbnails"):
    print("no path makeing path")
    os.makedirs("youtube_thumbnails")
print("thumbnail path exists")



#set up functions

def download_video(url,title):    
    yt = YouTube(url)
    yt.streams.filter(
        progressive=True,
        file_extension='mp4').order_by('resolution').desc().first().download(DOWNLOADS_PATH)


def get_thumbnail(url, id, ch_id):               
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    folder_path = f"youtube_thumbnails/{ch_id}"
    print("checking thumbnail sub path")
    if not os.path.exists(folder_path):
        print("no path makeing path")
        os.makedirs(folder_path)
    print("downloading thumbnails")
    img.save(os.path.join(folder_path,id))




def get_url(videoID):
    video_url = (f"https://www.youtube.com/watch?v={videoID}")
    return video_url




#urls to id
# url = "https://www.youtube.com/watch?v=6LjVqIfnbOk"
# exp = "^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
# s = re.findall(exp,url)[0][-1]
# thumbnail = f"https://i.ytimg.com/vi/{s}/maxresdefault.jpg"

#image scraping







def save_channel_settings(channel_id, settings):
    # Load existing settings from channel_settings.dat
    if os.path.isfile("channel_settings.dat"):
        try:
            with open("channel_settings.dat", "rb") as file:
                channel_settings = pickle.load(file)
        except EOFError:
            channel_settings = {}
    else:
        # If the file doesn't exist, initialize an empty dictionary
        channel_settings = {}

    # Save or update settings for the specific channel_id
    channel_settings[channel_id] = settings

    # Save the updated settings back to channel_settings.dat
    with open("channel_settings.dat", "wb") as file:
        pickle.dump(channel_settings, file)








def save_channel_data(channel_id, last_uploads, channel_title):
    # Load the existing data from "followed_channels.dat"
    if os.path.isfile("followed_channels.dat"):
        try:
            with open("followed_channels.dat", "rb") as file:
                followed_channels = pickle.load(file)
        except EOFError:
            followed_channels = {}
    else:
        # If the file doesn't exist, initialize an empty dictionary
        followed_channels = {}

    # Check if the channel_id is not in the "list" key and append it
    if channel_id not in followed_channels.get("list", []):
        followed_channels.setdefault("list", []).append(channel_id)

    # Save the updated data back to "followed_channels.dat"
    with open("followed_channels.dat", "wb") as file:
        pickle.dump(followed_channels, file)
        print("new channel added")
        print(followed_channels)


    if channel_id not in channel_data:
        channel_data[channel_id] = {"videos": {}, "channel_info": {}}

    for x in range(3):
        video_info = {
            "id": last_uploads[x],
            "title": return_video_titles[x]
        }
        channel_data[channel_id]["videos"][f"video{x}"] = video_info
    
    channel_data[channel_id]["channel_info"]["channel_name"] = channel_title


    with open("channels.dat", "wb") as file:
        pickle.dump(channel_data, file)
    return_videos.clear()
    return_video_titles.clear()
    global channel_name
    channel_name = ""

    





def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1#b

def playlist_video_links(playlistId,ChannelId,ChannelUrl,auto_download): 
    return_videos.clear()
    return_video_titles.clear()
    global channel_name
    channel_name = ""
  
    nextPageToken = None
      
    # Creating youtube resource object 
    youtube = build('youtube', 'v3',  
                    developerKey=api_key) 
  
    for x in range(SHOW_LAST): 
  
        # Retrieve youtube video results 
        pl_request = youtube.playlistItems().list( 
            part='snippet', 
            playlistId=playlistId, 
            maxResults=1, 
            pageToken=nextPageToken 
        ) 
        pl_response = pl_request.execute() 

        request = youtube.channels().list(
            part="statistics",
            id=ChannelId
        )
        response = request.execute()
        print("_____________________________________________")
        print(response)
        print("channel url:>",ChannelUrl)
        print("_____________________________________________")



        # Iterate through all response and get video description 
        for item in pl_response['items']: 
            
            title = item["snippet"]["title"]
            release_date = item["snippet"]["publishedAt"]
            description = item['snippet']['description'] 
            video_id = item["snippet"]["resourceId"]["videoId"]
            thumbnails = item['snippet']['thumbnails'] 
            channel_title = item["snippet"]["channelTitle"]
            print(x+1, " out of ",SHOW_LAST )
            print("thumbnail urls")
            if 'default' in thumbnails: 
                default = thumbnails['default']["url"]
                print(default) 
  
            if 'high' in thumbnails: 
                high = thumbnails['high']["url"]
                print(high) 
  
            if 'maxres' in thumbnails: 
                maxres = thumbnails['maxres']["url"]
                print(maxres) 
  
            if 'medium' in thumbnails: 
                medium = thumbnails['medium']["url"]
                print(medium) 
  
            if 'standard' in thumbnails: 
                standard = thumbnails['standard']["url"]
                print(standard) 
            file_name = str(video_id)+".jpg"
            get_thumbnail(medium,file_name,ChannelId)
            print("________________________________________________________________________________________________")
            print(item)
            print("________________________________________________________________________________________________")
            print(title)
            print(release_date)
            print(description)
            print(video_id)
            print(get_url(video_id))
            print(channel_title)
            print("end")
            print("________________________________________________________________________________________________")
            print("\n") 
            return_videos.append(video_id)
            return_video_titles.append(title)
            channel_name = channel_title
            if auto_download == True:
                t1 = threading.Thread(target=download_video, args=(get_url(video_id),"blank"))
                t1.start()
            

        nextPageToken = pl_response.get('nextPageToken') 
  
        if not nextPageToken: 
            break
  
def delete_old_thumbnails(channel_id):
    with open("channels.dat", "rb") as file:
        save_data = pickle.load(file)

    if channel_id in save_data:
        saved_thumbnails = set([f"{channel_id}/" + video["id"] + ".jpg" for video in save_data[channel_id]["videos"].values()])
        thumbnail_folder = "youtube_thumbnails"

        for filename in os.listdir(thumbnail_folder):
            if filename not in saved_thumbnails:
                file_path = os.path.join(thumbnail_folder, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {filename}")
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
    else:
        print(f"Channel ID {channel_id} not found in channels.dat")

def get_video_ids_for_channel(channel_id):
    if channel_id in channel_data:
        channel_info = channel_data[channel_id]
        videos = channel_info.get("videos", {})

        video_ids = [videos.get(f"video{x}", {}).get("id") for x in range(3)]

        video_ids = [video_id for video_id in video_ids if video_id is not None]

        return video_ids

# def ask_settings(): FINISH THIS ONCE UI IS BUILT
#     print("setting excludes leave empty for none NOTICE USEING THIS WILL BLOCK YOU FROM USEING INCLUDE ONLY FEATURE")
    # excludes = []
    # while True:
    #     reply = input("add exclude or type !ext to leave or !help for more info")
    #     if reply == "!help":
    #         print("if the channel you want to follow has a series that you dont want to be notified for grap its name from the channel and add it here and it wont pop up in checks")
    #     elif reply == "!ext":
    #         break
    #     else:
    #         excludes.append(reply)
    # if len(excludes) == 0:
    #     print("setting include leave empty for none")



#driver code

while True:
    debug_action = input("type cc to check channels type ac to add channel type pd to print all data type ex to exit loop and end program:>")
    if debug_action == "cc":

        if "list" in followed_channels:
            channel_list = followed_channels["list"]

            for channel_id in channel_list:
                print("Channel ID:", channel_id)
                if channel_id in channel_data:
                    channel_info = channel_data[channel_id]
                    print("Channel Info:", channel_info)
                    y = list(channel_id)
                    print(y) 
                    y[1] = "U"
                    z = listToString(y)
                    channel_url = f'https://www.youtube.com/channel/{channel_id}'
                    playlist_video_links(z,channel_id,channel_url,False) #get download from settings also when implemeted do exclude if and inlcude if here
                    print("cross checking data")
                    old_data = get_video_ids_for_channel(channel_id)
                    for video in range(0,3):
                        new_video = return_videos[video] 
                        old_video = old_data[video]
                        print("new data:>",new_video)
                        print("old data:>",old_video)
                        if old_video != new_video:
                            print("new videos deleteing old thumbnail and saveing data")
                            save_channel_data(channel_id,return_videos,channel_name)
                            delete_old_thumbnails(channel_id)
                            break
                        else:
                            print("video not new")
                            
                else:
                    print(f"Channel ID {channel_id} not found in channel_data")
                    print
        else:
            print("'list' key does not exist in followed_channels")

    elif debug_action == "ac":

        video_url = input("to start following a channel please insert a video link from the channel:>")

        x = YouTube(video_url)
        a = str(x.channel_id)
        b = str(x.channel_url)
        print("channel id:>",x.channel_id)
        print("channel url:>",x.channel_url)
        y = list(x.channel_id)
        print(y) 
        y[1] = "U"
        z = listToString(y)
        playlist_video_links(z,a,b,False) #allow user to chooose
        save_channel_data(x.channel_id,return_videos,channel_name)

        print("_____________________________________________")

        print("driver")
        with open("channels.dat", "rb") as file:
                    save_data=(pickle.load(file))
                    # save_data = pickle.load(file)
                    # print(save_data[""])
        print(save_data)

        settings = {
            "auto_download": True,
            "exclude_keywords": ["keyword1", "keyword2"],
            "include_keywords": ["keyword3"],
            "show_shorts": True,
}
        # save_channel_settings(x.channel_id) FINISH SETTINGS ONCE UI IS BUILT


        
    elif debug_action == "ex":    
        print("exiting")
        break

    elif debug_action == "pd":
        print("channels.dat")
        print(channels)

        print("followed_channels.dat")
        print(followed_channels)

        print("thumbnails")
        thumbnail_folder = "youtube_thumbnails"
        for root, dirs, files in os.walk(thumbnail_folder):
            for file in files:
                file_path = os.path.join(root, file)
                print(file_path)

    else:
        print("unsurported action")