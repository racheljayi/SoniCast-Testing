from .models import User
import requests, environ

BASE_ADDRESS = "https://api.spotify.com"
headers = {
    "Accept": "application/json",
    'Content-Type': 'application/json',
    'Authorization': "Bearer "
  }

env = environ.Env()
environ.Env.read_env()

# gets User object by user_id
def get_user(user_id):
    user = User.objects.filter(user_id=user_id)
    if user: 
        return user[0]
    else: 
        return None

# gets User object by user_spotify_id
def get_user_by_id(user_spotify_id):
    user = User.objects.filter(user_spotify_id=user_spotify_id)
    if user: 
        return user[0]
    else:
        return None

# updates or creates User object. returns user_id
    # uses user_spotify_id to determine if User exists in database
def update_user_token(token_information):
    token = token_information['access_token']
    user_spotify_id = request_user_spotify_id(token)
    user = get_user_by_id(user_spotify_id)
    if user is not None:
        user.access_token = token
        user.refresh_token = token_information['refresh_token']
        user.save()
    else:
         user = User(user_spotify_id=user_spotify_id, access_token=token, refresh_token=token_information['refresh_token'])
         user.save()
    return user.user_id

# updates User object. returns user_id
def update_user_location(location_information, user_id):
    user = get_user(user_id)
    if user is not None: 
        user.city = location_information["city"]
        user.region = location_information["region"]
        user.country = location_information["country_name"]
        user.save()
    return user_id

# make API call to retrieve current forecast from location information
def request_forecast(user_id):
    user = get_user(user_id)
    params = {
        'key': env("WEATHER_API_KEY"),
        'q': user.city + ", " + user.region + ", " + user.country
    }
    response = requests.get(url="http://api.weatherapi.com/v1/current.json", params=params)
    try:
        return response.json()['current']
    except:
        return({'Error': 'Retriving weather failed'})


# make API call to retrieve user's spotify_id from access token
def request_user_spotify_id(access_token):
    headers['Authorization'] = "Bearer " + access_token
    response = requests.get(url = BASE_ADDRESS + "/v1/me", headers=headers)
    try:
        return response.json()['id']
    except:
        return({'Error': 'Retriving user failed'})

# catch all method for making Spotify API calls
def make_API_call(access_token, endpoint, params='', post=False, put=False):
    headers['Authorization'] = "Bearer " + access_token
    if post:
       requests.post(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    if put:
        requests.put(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    
    response = requests.get(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    try:
        return response.json()
    except:
        return({'Error': 'API call failed'})

# make recoomendations for user given weather parameters. returns an array of song objects
def make_recommendations(user_id, weather_perms):
    user = get_user(user_id)

    if user is not None: 
        access_token = user.access_token

        # get top 2 artists
        endpoint = "v1/me/top/artists"
        params = {
            "offset":1
        }
        artists = make_API_call(access_token=access_token, endpoint=endpoint).items.id + "," + make_API_call(access_token
            =access_token, endpoint=endpoint, params=params).items.id

        # get top 3 tracks
        endpoint = "v1/me/top/tracks"
        offsets1 = {
            "offset":1
        }
        offsets2 = {
            "offset":2
        }
        tracks = make_API_call(access_token=access_token, endpoint=endpoint).items.id + "," + make_API_call(access_token=access_token, endpoint
            =endpoint, params=offsets1).items.id + "," + make_API_call(access_token=access_token, endpoint=endpoint, params=
            offsets2).items.id

        params = {
            #TODO
            "seed_artists": artists,
            "seed_tracks": tracks
        }
        return None
    else: return({'Error': 'User not found'})

# define parameters for track recommendations based on weather   
def make_parameters(forecast):
    parameters = {}
    acousticness = 1 - round(forecast['vis_miles'] * 0.11, 3)   # visibility = acousticness 
    tempo = round(forecast['wind_mph'] * 7, 3) + 60     # windiness = tempo
    valence = 1 - round(forecast['cloud'] * 0.007, 3) - 0.1     # more cloudiness = lower valence 

    if (forecast['is_day']):
        energy = round(forecast['uv'] * 0.2, 3) - 0.1     # uv = energy (only included if is_day)
        parameters["target_energy"] = energy
    else:
        acousticness += 0.3
    
    if (forecast['precip_in'] != 0.0):
            mode = 1    # mode is minor (only included if there is percipitation)
            parameters["target_mode"] = mode
    
    parameters["target_acousticness"] = acousticness
    parameters["target_tempo"] = tempo
    parameters["target_valence"] = valence
    
    # day of week & time => dancibility 
    return parameters

# def refresh_user_token