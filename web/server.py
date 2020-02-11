from flask import Flask
from flask import request, session, redirect
import requests
import random
import json
from os import environ as env

import sys
sys.path.append('./')  # Expose parent level of project in order to be able to to import 'auth_core'

from core import environment, service, auth

app = Flask(__name__)
@app.route('/')
def homepage():
    if 'user' in session:
        header = '<h1>Identified as: {name} ({user})</h1>'.format(user=session['user'], name=session['user_name'])
        page = header + '<p>' + '</p><p>'.join(build_url_list()) + '</p>'
    else:
        state = random.getrandbits(32)
        btn_url = 'https://slack.com/oauth/authorize?scope=identity.basic' \
                  '&client_id={client_id}&state={state}&redirect_uri={redirect_uri}/callback'\
            .format(client_id=env['SLACK_CLIENT_ID'], state=state, redirect_uri=env['CALLBACK_URI'])
        page = '<a href="' + btn_url + '">' \
               '<img alt=""Sign in with Slack"" height="40" width="172" src="https://platform.slack-edge.com/img/sign_in_with_slack.png" ' \
               'srcset="https://platform.slack-edge.com/img/sign_in_with_slack.png 1x, https://platform.slack-edge.com/img/sign_in_with_slack@2x.png 2x" />' \
               '</a>'
        session['state'] = state
    return page


@app.route('/<service>-callback')
def auth_callback(service: str):
    error = request.args.get('error', '')
    if error:
        return "Error: " + error
    # state = request.args.get('state', '')
    # if not is_valid_state(state):
    #    abort(403)
    verifier = request.args.get('oauth_verifier')
    token = request.args.get('oauth_token')
    code = request.args.get('code')
    if auth.finish_auth(oauth_token=token, verifier=verifier, code=code, user=session['user'], service=service):
        return redirect('/')
    else:
        return 'Authentication error, please try again later!'


@app.route('/callback')
def callback():
    if int(request.args.get('state')) > 0:
        response = requests.get(
            url=env['SLACK_OAUTH_ACCESS_URL'],
            params={
                'client_id': env['SLACK_CLIENT_ID'],
                'client_secret': env['SLACK_CLIENT_SECRET'],
                'code': request.args.get('code'),
            }
        )
        error = request.args.get('error', '')

        if error:
            return "Error: " + error
        elif int(response.status_code) == 200:
            content = json.loads(response.content)
            if content.get('ok') is False:
                return 'Slack authentication error: {}'.format(content.get('error'))
            else:
                user = auth.set_user_identity(response.content)
                session['user'] = user.user
                session['team'] = user.team
                session['user_name'] = user.name
                session['access_token'] = user.access_token
                return redirect('/')
        else:
            return 'Authentication error, please try again later!'
    else:
        return 'Wrong session state, please retry!'


def build_url_list():
    url_list = []
    connectors = service.get_connectors_meta().values()
    services = set(map(lambda item: item.service, auth.get_user_identity(user=session['user']).service))
    for connector in connectors:
        connector = connector['meta']
        if connector['service'] in services:
            row = '<a href="{url}">Revoke Auth - {friendly_name}</a>'\
                .format(url='#', friendly_name=connector['friendly_name'])
        else:
            url = auth.start_auth(connector=connector, user=session['user'])
            row = '<a href="{url}">{friendly_name}</a>'\
                .format(url=url, friendly_name=connector['friendly_name'])
        url_list.append(row)
    return url_list


if __name__ == '__main__':
    environment.configure()
    app.secret_key = env['FLASK_SECRET_KEY']
    app.run(debug=False, port=65010, host='0.0.0.0')
