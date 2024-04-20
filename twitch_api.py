import requests
import youtube_dl
#from datetime import datetime, timedelta
import datetime

# Constants
CLIENT_ID = '37cirs6k7z558qen4cdu9gtigpk7vt'
AUTH_TOKEN = 'Bearer 7u952e7nrxzx2wtyj724iihiq8ghfl'
API_URL = 'https://api.twitch.tv/helix/clips'

def twitch_api_request(params):
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': AUTH_TOKEN,
    }

    response = requests.get(API_URL, params=params, headers=headers)

    ## Output get Errors
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        print("Token invalid.")
        return None
    elif response.status_code == 400:
        print("Bad Request: One and only one parameter of type id is required.")
        return None
    elif response.status_code == 404:
        print("Not Found")
        return None
    else:
        return None

## Validates userinput
def get_input(prompt, validator):
    while True:
        user_input = input(prompt)
        if validator(user_input):
            return user_input
        else:
            print("Invalid input. Please try again.")

if __name__ == '__main__':
    # User Inputs
    #iGame_id = get_input("Please enter the Game ID (numeric): ",
    #                                             lambda x: x.isdigit() and int(x) > 0)
    iGame_id = int(21779)
    iNum_days = get_input("Please enter the past x days (max. 7): ",
                                                 lambda x: x.isdigit() and 0 < int(x) < 8)
    iNum_vids = get_input("Please Enter the number of Videos you want to get (between 1 and 10): ",
                                                   lambda x: x.isdigit() and 0 < int(x) < 11)
    
    start = (datetime.datetime.now() - datetime.timedelta(days=int(iNum_days))).strftime('%Y-%m-%dT%H:%M:%SZ')
    print(start)

    params = {
        'game_id': iGame_id,
        'started_at': start,
        'first': iNum_vids,
    }

    result = twitch_api_request(params)

    if result:
        videos = result.get('data', [])
        video_urls = [item['url'] for item in result.get('data', [])]  # Extract video URLs from the Twitch API response

        for video in videos:
            if video.get('viewable') == 'public':
                video_urls.append(video['url'])
            else:
                print(f"Video with ID {video['id']} is not publicly viewable and will not be downloaded.")

        if not video_urls:
            print("No publicly viewable videos found.")
        else:
            # Proceed with downloading the publicly viewable videos
            def my_hook(d):
                if d['status'] == 'finished':
                    print('Done downloading')


            ydl_opts = {
                'format': 'best',  # Best Quality available
                'progress_hooks': [my_hook],
                'outtmpl': f"/Videos/%(title)s.%(ext)s"
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download(video_urls)

            if result == 0:  # Check if download was successful
                print("Download successful.")
            else:
                print("Download failed.")
    else:
        print("Error fetching data.")