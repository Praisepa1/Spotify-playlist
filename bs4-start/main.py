from bs4 import BeautifulSoup
import requests
import datetime as dt
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Step 1: Get the date input from the user
date = input("What year would you like to travel to in YYY-MM-DD format? ")

# Step 2: Scrape the Billboard Hot 100 songs
url = f"https://www.billboard.com/charts/hot-100/{date}/"
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"
}

response = requests.get(url, headers=header)
website_html = response.text

soup = BeautifulSoup(website_html, 'html.parser')
song_elements = soup.find_all("h3", class_="a-no-trucate")
song_titles = [songs.getText(strip=True) for songs in song_elements]
print(f"Top 100 Songs on {date}:\n", song_titles)

# Step 3: Authenticate with Spotify using Spotipy
CLIENT_ID = "c4b7da02a2f247efbd5f7247a9d11f2d"
CLIENT_SECRET = "15b954db0fbc485da0fbb4a664b63be6"
REDIRECT_URI = "http://localhost:8888/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-modify-private"
))

# Step 4: Get the current user ID
user = sp.current_user()
user_id = user['id']

# Step 5: Create a new Spotify playlist
playlist_name = f"Billboard Hot 100 - {date}"
playlist_description = f"Top 100 songs on Billboard for {date}"
new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, description=playlist_description, public=False)
print(f"Created Playlist: {new_playlist['name']} (ID: {new_playlist['id']})")

# Step 6: Search for each song on Spotify and add to the playlist
track_uris = []
for song in song_titles:
    result = sp.search(q=f"track:{song}", type="track", limit=1)
    try:
        track_uri = result['tracks']['items'][0]['uri']
        track_uris.append(track_uri)
    except IndexError:
        print(f"{song} not found on Spotify. Skipping.")

# Add all found tracks to the playlist
if track_uris:
    sp.playlist_add_items(playlist_id=new_playlist['id'], items=track_uris)
    print(f"Added {len(track_uris)} songs to the playlist.")
else:
    print("No songs were added to the playlist.")
