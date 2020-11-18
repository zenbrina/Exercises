from flask import Flask, request, render_template, redirect, url_for
from flask_ngrok import run_with_ngrok
from wtforms import Form, StringField, validators
import twitch_integration
import json, time, datetime

app = Flask(__name__)
app.debug = True
# run_with_ngrok(app)

class InputForm(Form):
  user_login = StringField(validators=[validators.InputRequired()])

@app.route('/', methods=['POST', 'GET'])
def home():
  form = InputForm(request.form)
  user_login = form.user_login.data

  user_query = twitch_integration.get_user_query(user_login)
  user_info = twitch_integration.get_response(user_query)

  twitch_integration.print_response(user_info)

  try:
    user_id = user_info.json()['data'][0]['id']
    img_url = user_info.json()['data'][0]['profile_image_url']

    user_videos_query = twitch_integration.get_user_videos_query(user_id)
    videos_info = twitch_integration.get_response(user_videos_query)

    twitch_integration.print_response(videos_info)

    videos_info_json = videos_info.json()

    videos_info_json_data = videos_info_json['data']
    print('BEFORE!!!', videos_info_json_data)
    # videos_info_json_data = list(videos_info_json_data.reverse())
    videos_info_json_data_reversed = videos_info_json_data[::-1]
    print('AFTER!!!', videos_info_json_data_reversed)


    # sorted_video_data = videos_info_json_data.sort((a, b))
    # videos_info_json_data_sorted = sorted(videos_info_json_data, key=lambda x: (videos_info_json_data[]))

    line_labels = []
    line_values = []
    title = user_login + '\'s Video Stats'

    for item in videos_info_json_data_reversed:
      if (len(item['title']) == 0):
        line_labels.append('No Name')
      elif (len(item['title']) > 20):
        line_labels.append(item['title'][:20] + '...')
      else:
        line_labels.append(item['title'])
      line_values.append(item['view_count'])


    return render_template('line_chart.html', title=title, max=max(line_values) + 10, labels=line_labels,values=line_values, img_url=img_url)
  except:
    return render_template("display.html", form=form)

  # user_videos_query = twitch_integration.get_response(user_info['data']['user_id'])
  # response = twitch_integration.get_response(user_videos_query)

  # response_json = response.json()
  # twitch_integration.print_response(response)
  # return render_template("display.html", form=form, response_json=videos_info.json())


@app.route('/dfdf', methods=['POST', 'GET'])
def main():
  form = InputForm(request.form)
  user_login = form.user_login.data
  # if request.method == 'POST':
  #   return redirect(url_for('graph', user_login=user_login))
  query = twitch_integration.get_user_streams_query(user_login)
  # query = twitch_integration.get_games_query()
  response = twitch_integration.get_response(query)
  response_json = response.json()
  twitch_integration.print_response(response)
  return render_template("display.html", form=form, response_json=response_json)

@app.route('/graph', methods=['POST', 'GET'])
def graph():
  user_login = request.args.get('user_login')
  query = twitch_integration.get_user_streams_query(user_login)
  response = twitch_integration.get_response(query)
  response_json = response.json()

  twitch_integration.print_response(response)

  line_labels = []
  line_values = []
  title = None

  # return render_template("display.html", form=form, response_json=response_json)

  for i in range(5):
    query = twitch_integration.get_user_streams_query(user_login)
    response = twitch_integration.get_response(query)
    response_json = response.json()
    current_time = datetime.datetime.now()
    time_list = [current_time.hour,current_time.minute,current_time.second]

  #   try:
  #     print(response_json['data'][0]['viewer_count'])
  #     viewer_count = response_json['data'][0]['viewer_count']
  #     if title is None:
  #       title = response_json['data'][0]['user_name'] + ' - ' + response_json['data'][0]['title']
  #     t = ':'.join(str(e) for e in time_list)
  #     line_labels.append(t)
  #     line_values.append(viewer_count)
  #   except:
  #     pass
  #   # line_values.append(response_json['data'][0]['viewer_count'])
  #   # line_values.append(i * 1000)
  #   time.sleep(2)

  # print(line_labels, line_values)

  return render_template('line_chart.html', title=title, max=max(line_values) + 10, labels=line_labels,values=line_values)


  # if len(response_json['data']) > 0:
  #   line_labels=['time', 'time']
  #   line_values=['1', '1000']
  #   return render_template('line_chart.html', title='Twitch Live Stream Info', max=17000, labels=line_labels, values=line_values)
  # return render_template("display.html", form=form, response_json=response_json)

if __name__ == '__main__':
   app.run()