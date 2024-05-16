import requests
from get_token import get_twitch_token


def get_clip_info(clip_list: list) -> list:
    """
    Takes a clip ID.\n
    Returns the braodcaster name, language and viewcount.
    """
    CLIENT_ID = '37cirs6k7z558qen4cdu9gtigpk7vt'
    AUTH_TOKEN = get_twitch_token()
    API_URL = 'https://api.twitch.tv/helix/clips'
    clip_info_list = []

    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': AUTH_TOKEN,
    }

    for clip in clip_list:
        clip_id = clip.split('/')[-1]
        params = {
            'id':clip_id,
        }

        response = requests.get(API_URL, params=params, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract the desired values
            if data["data"]:  # Check if data is not empty
                clip_info = {
                    "broadcaster_name": data["data"][0]["broadcaster_name"],
                    "language": data["data"][0]["language"],
                    "view_count": data["data"][0]["view_count"],
                    "title": data["data"][0]["title"],
                    "url": data["data"][0]["url"]
                }

                clip_info_list.append(clip_info)
            else:
                print(f"No data found for clip ID {clip_id}")
        else:
            print(f"Failed to retrieve data for {clip}. Status code:", response.status_code)
    
    return clip_info_list