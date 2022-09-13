from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import lxml
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
load_dotenv("variables.env")

scope = "playlist-read-private playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

BILLBOARD_BASE_ENDPOINT = "https://www.billboard.com/charts/hot-100/"
full_year = input("When do you want to travel back to ? (YYYY-MM-DD format only): ")
year = full_year[0:4]

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

billboard_final = BILLBOARD_BASE_ENDPOINT + full_year

response = requests.get(billboard_final).text
soup = BeautifulSoup(response, 'html.parser')

titles = soup.select("li.o-chart-results-list__item  h3#title-of-a-story")
artists = soup.findAll(name="span", class_=["a-no-trucate", "a-font-primary-s"])

list_of_titles = [title.getText().strip() for title in titles]
list_of_artists = [artist.getText().strip() for artist in artists if artist.getText().strip() != "RIAA Certification:"]

tracks = dict(zip(list_of_titles, list_of_artists))

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

uri_list = []

for title, artist in tracks.items():
    try:
        result = sp.search(q=f"track:{title} artist:{artist}", type="track,artist")
        uri = result["tracks"]["items"][0]["uri"]
        uri_list.append(uri)
    except IndexError:
        pass

results = sp.current_user()
# pprint(results)
user_id = results['id']

sp.user_playlist_create(user=f"{user_id}", name=f"{full_year} Billboard 100", public=False)
playlists = sp.user_playlists(user=f"{user_id}")
playlist_id = playlists['items'][0]['id']


sp.playlist_add_items(playlist_id=f"{playlist_id}", items=uri_list)

