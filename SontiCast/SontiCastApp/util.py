from .models import User
import requests, environ, json

BASE_ADDRESS = "https://api.spotify.com"
headers = {
    "Accept": "application/json",
    'Content-Type': 'application/json',
    'Authorization': "Bearer "
  }

env = environ.Env()
environ.Env.read_env()

class Song:
    def __init__(self, name, artist, uri, cover_url):
        self.name = name
        self.artist = artist
        self.uri = uri
        self.cover_url = cover_url

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

# updates the user's SontiCast playlist, or remove if it if no longer exists
    # takes user object, array of Song objects, playlist ID, & weather tagline
def update_playlist(access_token, tracks, playlist='', weather=''):
    # unfortunately the spotify Web API doesn't currently support any way of
        # easily checking if a playlist has been deleted by the owner or not,
        # so to avoid updating already deleted playlists, this method access's
        # the user's past 50 playlists and tries to match them with the stored
        # playlist id
    if playlist=='': 
        pass
        # TODO
    else: # if playlist ID is passed in, it was just created
        endpoint = "/v1/playlists/" + playlist + "/tracks"
        uris = []
        for track in tracks:
            uris.append(track.uri)
        data = json.dumps({
            "uris":uris
        })
    return make_API_call(access_token=access_token, endpoint=endpoint, data=data, post=True)

def update_playlist_cover(access_token, playlist):
    pass
    # TODO

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
def make_API_call(access_token, endpoint, params='', data='', post=False, put=False):
    headers['Authorization'] = "Bearer " + access_token
    if post:
       response = requests.post(url = BASE_ADDRESS + endpoint, headers=headers, params=params, data=data)
    if put:
        response = requests.put(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    
    if not post and not put: 
        response = requests.get(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    try:
        print(response)
        return response.json()
    except:
        return({'Error': 'API call failed'})

# make recomendations for user given weather parameters. returns an array of Song objects
def make_recommendations(user_id, weather_perms):
    user = get_user(user_id)
    if user is not None: 
        access_token = user.access_token
        # get top 2 artists
        endpoint = "/v1/me/top/artists"
        artists = make_API_call(access_token=access_token, endpoint=endpoint)["items"][0]['id'] + "," + make_API_call(access_token
        =access_token, endpoint=endpoint)["items"][1]['id']
        # get top 3 tracks
        endpoint = "/v1/me/top/tracks"
        tracks = make_API_call(access_token=access_token, endpoint=endpoint)["items"][1]['id'] + "," + make_API_call(access_token
            =access_token, endpoint=endpoint)["items"][1]['id'] + "," + make_API_call(access_token=
            access_token, endpoint=endpoint)["items"][2]['id']
        # get recommendations
        weather_perms["seed_artists"] = artists
        weather_perms["seed_tracks"] = tracks
        endpoint = "/v1/recommendations"
        response = make_API_call(access_token=access_token, endpoint=endpoint, params=weather_perms)["tracks"]
        # clean recommendations and return as array of Song objects
        recommendations = []
        for track in response:
            name = track["name"]
            artists = []
            for artist in track["artists"]:
                artists.append(artist["name"])
            uri = track["uri"]
            url = track["album"]["images"][0]["url"]
            song = Song(name=name, artist=artists, uri=uri, cover_url=url)
            recommendations.append(song)
        return recommendations
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
            mode = 1    # mode is minor if there is percipitation
            parameters["target_mode"] = mode
    parameters["target_acousticness"] = acousticness
    parameters["target_tempo"] = tempo
    parameters["target_valence"] = valence
    # day of week & time => dancibility 
    return parameters

# make playlist for the user given an array of Song objects and a string describing the weather
def make_playlist(user_id, tracks, weather):
    user = get_user(user_id)
    if user is not None:
        access_token = user.access_token
        endpoint = "/v1/users/" + user.user_spotify_id + "/playlists"
        data = json.dumps({
            "name": "a " + weather,
            "description": "a SontiCast playlist. Updates every 3 hours.",
            "public": False
        })
        playlist = make_API_call(access_token=access_token, endpoint=endpoint, data=data, post=True)["id"]
        user.playlist_id = playlist
        print(playlist)
        #update_playlist_cover(access_token=access_token, playlist=playlist)
        update_playlist(access_token=access_token, tracks=tracks, playlist=playlist)

# def describe_weather
# def refresh_user_token