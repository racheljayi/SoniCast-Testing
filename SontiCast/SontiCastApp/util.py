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
def make_API_call(user_id, endpoint, params='', post=False, put=False):
    user = get_user(user_id)
    headers['Authorization'] = "Bearer " + user.access_token
    if post:
       requests.post(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    if put:
        requests.put(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    
    response = requests.get(url = BASE_ADDRESS + endpoint, headers=headers, params=params)
    try:
        return response.json()
    except:
        return({'Error': 'API call failed'})
    
# def make_parameters(user_id)
    # the big boy method
    # make parameters for recommendataions
    # seed top artists, genres, & tracks, and make weather rules to add to seeded genres as well
    # as to adjust other parameters

# def refresh_user_token