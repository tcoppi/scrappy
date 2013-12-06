import json
import requests_oauthlib

from utility.user.user import User, Account
# give a URL, wait for response
# This handles OAuth specifics
class Auth(object):
    def __init__(self):

        self.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        self.scope = ['https://www.googleapis.com/auth/userinfo.profile']
        if not User.table_exists():
            User.create_table()
        if not Account.table_exists():
            Account.create_table()

    # !auth
    # Get the challenge to the user
    def challenge(self, nickmask, server):
        user = nickmask.user
        host = nickmask.host
        print repr(user)
        print repr(host)
        try:
            user_obj = User.get(User.user == user, User.host == host, User.server == server.server_name)
        except User.DoesNotExist:
            user_obj = User(user=user, host=host, server=server.server_name)

        user_obj.save()

        oauth = requests_oauthlib.OAuth2Session(server.config["google_id"], redirect_uri=self.redirect_uri, scope=self.scope)
        authorization_url, state = oauth.authorization_url('https://accounts.google.com/o/oauth2/auth', access_type="offline", approval_prompt="auto")

        return authorization_url


    # !auth <response>
    def respond(self, nickmask, server, auth_response):
        user = nickmask.user
        host = nickmask.host
        try:
            user_obj = User.get(User.user == user, User.host == host, User.server == server.server_name)
        except User.DoesNotExist:
            return (False, "User has not received a challenge yet")

        oauth = requests_oauthlib.OAuth2Session(server.config["google_id"], redirect_uri=self.redirect_uri, scope=self.scope)
        try:
            token = oauth.fetch_token('https://accounts.google.com/o/oauth2/token', code=auth_response, client_secret=server.config["google_secret"])
            r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
            info = json.loads(r.content)
            if user_obj.acct is not None:
                msg = "Successfully updated authentication information to %s" % info["name"]
            else:
                new_acct = Account(identifier=info["id"], name=info["name"], auth_service="Google OAuth").save()
                user_obj.acct = new_acct
                msg = "Successfully authenticated as %s" % info["name"]
            user_obj.save()

            return (True, msg)
        except Exception as e:
            return (False, e)

