import attr
import jwt

from inbox.basicauth import OAuthError
from inbox.config import config
from inbox.models import Namespace
from inbox.models.backends.outlook import OutlookAccount
from inbox.models.secret import SecretType
from inbox.util.url import url_concat

from .oauth import OAuthAuthHandler


@attr.s
class MicrosoftAccountData(object):
    email = attr.ib()

    secret_type = attr.ib()
    secret_value = attr.ib()

    client_id = attr.ib()
    scope = attr.ib()

    sync_email = attr.ib()


class MicrosoftAuthHandler(OAuthAuthHandler):
    OAUTH_CLIENT_ID = config.get_required("MICROSOFT_OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET = config.get_required("MICROSOFT_OAUTH_CLIENT_SECRET")
    OAUTH_REDIRECT_URI = config.get_required("MICROSOFT_OAUTH_REDIRECT_URI")

    OAUTH_AUTHENTICATE_URL = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    )
    OAUTH_ACCESS_TOKEN_URL = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    )
    # Not used with Exchange tokens, which are JWTs.
    OAUTH_USER_INFO_URL = None

    OAUTH_SCOPE = " ".join(
        [
            "https://outlook.office.com/IMAP.AccessAsUser.All",
            "https://outlook.office.com/SMTP.Send",
            "offline_access",
        ]
    )

    def create_account(self, account_data):
        namespace = Namespace()
        account = OutlookAccount(namespace=namespace)
        account.create_emailed_events_calendar()
        account.sync_should_run = False
        return self.update_account(account, account_data)

    def update_account(self, account, account_data):
        account.email_address = account_data.email

        if account_data.secret_type:
            account.set_secret(account_data.secret_type, account_data.secret_value)

        if not account.secret:
            raise OAuthError("No valid auth info.")

        account.sync_email = account_data.sync_email

        account.client_id = account_data.client_id
        account.scope = account_data.scope

        return account

    def _get_user_info(self, session_dict):
        # Since we can't use an Exchange token to access the Graph API's
        # userinfo endpoint we're going to use the access_token, which is a
        # JWT, to determine the email address.
        id_token = session_dict["access_token"]
        id_data = jwt.decode(id_token, verify=False)
        return {
            "email": id_data["upn"],
        }

    def interactive_auth(self, email_address=None):
        url_args = {
            "redirect_uri": self.OAUTH_REDIRECT_URI,
            "client_id": self.OAUTH_CLIENT_ID,
            "response_type": "code",
            "scope": self.OAUTH_SCOPE,
            "prompt": "select_account",
        }
        if email_address:
            url_args["login_hint"] = email_address
        url = url_concat(self.OAUTH_AUTHENTICATE_URL, url_args)

        print "To authorize Nylas, visit this URL and follow the directions:"
        print "\n{}".format(url)

        while True:
            auth_code = raw_input("Enter authorization code: ").strip()
            try:
                auth_response = self._get_authenticated_user(auth_code)
                return MicrosoftAccountData(
                    email=auth_response["email"],
                    secret_type=SecretType.Token,
                    secret_value=auth_response["refresh_token"],
                    client_id=self.OAUTH_CLIENT_ID,
                    scope=auth_response["scope"],
                    sync_email=True,
                )
            except OAuthError:
                print "\nInvalid authorization code, try again...\n"
