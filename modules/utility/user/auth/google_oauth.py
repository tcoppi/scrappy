import json
import requests_oauthlib
import logging

from ..user import User, Account, AuthBackend, get_user, merge_accounts

oauth_logger = logging.getLogger("oauthlib")
oauth_logger.setLevel(logging.WARNING)
oauth_logger = logging.getLogger("urllib3")
oauth_logger.setLevel(logging.WARNING)
# give a URL, wait for response
# This handles OAuth specifics
class Auth(object):
    def __init__(self):

        self.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        self.scope = ['https://www.googleapis.com/auth/userinfo.profile']
        if not Account.table_exists():
            Account.create_table()
        if not User.table_exists():
            User.create_table()
        if not AuthBackend.table_exists():
            AuthBackend.create_table()

    # !auth
    # Get the challenge to the user
    def challenge(self, user, server):
        user_obj = get_user(user, server.server_name)

        oauth = requests_oauthlib.OAuth2Session(server.config["google_id"], redirect_uri=self.redirect_uri, scope=self.scope)
        authorization_url, state = oauth.authorization_url('https://accounts.google.com/o/oauth2/auth', access_type="offline", approval_prompt="auto")

        return authorization_url


    # !auth <response>
    def respond(self, user, server, auth_response):
        user_obj = get_user(user, server.server_name)

        oauth = requests_oauthlib.OAuth2Session(server.config["google_id"], redirect_uri=self.redirect_uri, scope=self.scope)
#        try:
        token = oauth.fetch_token('https://accounts.google.com/o/oauth2/token', code=auth_response, client_secret=server.config["google_secret"])
        r = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
        info = json.loads(r.content)

        try:
            backend = AuthBackend.get(AuthBackend.identifier == info["id"], AuthBackend.auth_service == "GoogleOAuth")
            merge_accounts(user_obj.acct, backend.acct)
            msg = "Successfully updated authentication information to %s"
        except AuthBackend.DoesNotExist:
            backend = AuthBackend(identifier=info["id"], auth_service="GoogleOAuth", acct=user_obj.acct)
            backend.save()

            msg = "Successfully authenticated as %s"
        user_obj.acct.name = info["name"]

        msg = msg % user_obj.acct.name

        return (True, msg)
#        except Exception as e:
#            return (False, str(e.strerror))

