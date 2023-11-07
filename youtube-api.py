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


# Update the save_channel_data function to accumulate data for different channels.
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
            global channel_name
            channel_name = channel_title
            if auto_download == True:
                t1 = threading.Thread(target=download_video, args=(get_url(video_id),"blank"))
                t1.start()
            

        nextPageToken = pl_response.get('nextPageToken') 
  
        if not nextPageToken: 
            break
  
def delete_old_thumbnails(channel_id):
    with open("channels.dat", "rb") as file:
            save_data=(pickle.load(file))
    print(save_data[channel_id["videos"]])


#driver code
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

# delete_old_thumbnails("UCykjfgzqTHuYIhvUGz1Xezg")
            