import requests

url = 'https://api.twitch.tv/kraken/streams?game_id=33214'
params = {'Client-ID': 'r0ay47cwvzojw6yh55qojmy9nq14kx'}

r = requests.get(url, headers=params)
print(r.text)

