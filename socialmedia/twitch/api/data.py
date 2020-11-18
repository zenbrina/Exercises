import requests, json, sys

# BASE_URL = 'https://api.twitch.tv/kraken/' # depricated :(
BASE_URL = 'https://api.twitch.tv/helix/'
CLIENT_ID = 'r0ay47cwvzojw6yh55qojmy9nq14kx'
HEADERS = {'Client-ID': CLIENT_ID}
INDENT = 2

# query = 'streams?game_id=33214'
# url = BASE_URL + query
# response = requests.get(url, headers=PARAMS)
# print(json.dumps(response.json(), indent=2))
# parsed = json.loads(response.text)
# print(json.dumps(parsed, indent=2))

# Takes a custom query from user and gets the response object
def get_response(query):
  url  = BASE_URL + query
  response = requests.get(url, headers=HEADERS)
  return response

# Takes a response object and prints it on the console with proper format
def print_response(response):
  response_json = response.json()
  print_response = json.dumps(response_json, indent=INDENT)
  print(print_response)
  return response.json()

# if __name__ == "__main__":
#   user = sys.argv[1]
#   query = 'users?login={0}'.format(user)
#   print_response(get_response(query))

if __name__ == "__main__":
  login = sys.argv[1]
  # user_query = 'users?login={0}'.format(login)
  # response = get_response(user_query)
  # response_json = response.json()
  # user_id = response_json['data'][0]['id']

  streams_query = 'streams?user_login={0}'.format(login)
  response = get_response(streams_query)

  # DEBUG
  print_response(response)















