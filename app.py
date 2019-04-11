from src import create_app
# from flask_dance.contrib.google import make_google_blueprint, google

application = create_app()


# google_blueprint = make_google_blueprint(
#     client_id=GOOGLE_CLIENT_ID,
#     client_secret=GOOGLE_CLIENT_SECRET,
#     scope=['https://www.googleapis.com/auth/userinfo.email',
#           'https://www.googleapis.com/auth/userinfo.profile'],
#     # Indicates whether the app can refresh access tokens when the user is not present at the browser
#     # "Enable offline access so that you can refresh an access token without re-prompting the user for permission. Recommended for web server apps."
#     offline=True,
#     #Uses the offline access to automatically refresh the authorization session
#     reprompt_consent=True
# )
# application.register_blueprint(google_blueprint, url_prefix="/login")
