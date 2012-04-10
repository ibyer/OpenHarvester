#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#
import logging
logging.basicConfig(level=logging.DEBUG)

# APP SPECIFIC
APP_URL = 'http://beta.zerson.com'

TASK_URL_BASE = '/tasks/uh'
TASK_INIT = TASK_URL_BASE + '/initialize'
TASK_FACEBOOK = TASK_URL_BASE + '/facebook'
TASK_TWITTER = TASK_URL_BASE + '/twitter'
TASK_YELP = TASK_URL_BASE + '/yelp'
TASK_QUEUE_NAME_FACEBOOK = 'HarvestFacebook'
TASK_QUEUE_NAME_TWITTER = 'HarvestTwitter'
TASK_QUEUE_NAME_YELP = 'HarvestYelp'

FACEBOOK_API_OAUTH_APP_URL = '/auth/fb'

SOCIAL_SITE_FACEBOOK = 'FACEBOOK'
SOCIAL_SITE_YELP = 'YELP'
SOCIAL_SITE_TWITTER = 'TWITTER'
SOCIAL_SITE_DELICIOUS = 'DELICIOUS'




# FACEBOOK
FACEBOOK_API_APP_ID = 'your_fb_app_id'
FACEBOOK_API_APP_SECRET = 'your_fb_app_secret'
FACEBOOK_API_APP_API_KEY = 'your_fb_app_api_key'
FACEBOOK_API_CALL_BACK_URL = APP_URL + '/auth/fb'

FACEBOOK_API_GRAPH_URL = 'https://graph.facebook.com'
FACEBOOK_API_OAUTH_URL = 'https://graph.facebook.com/oauth/access_token'

FACEBOOK_API_PERMISSION_URL = 'https://www.facebook.com/dialog/oauth'
FACEBOOK_API_REQUEST_SCOPES = 'user_about_me,user_activities,user_birthday,user_events,user_groups,user_hometown,user_interests,user_likes,user_location,user_photo_video_tags,user_photos,user_relationships,user_relationship_details,user_religion_politics,user_status,user_videos,user_website,user_work_history,email,read_friendlists,read_stream,publish_stream,offline_access'

# TWITTER
TWITTER_API_KEY = 'your_twitter_api_key'
TWITTER_API_SECRET = 'your_twitter_api_secret'
TWITTER_API_CALL_BACK_URL = APP_URL + '/auth/twitter'


# YELP
YELP_LOGIN_URL = 'https://www.yelp.com/login'
YELP_LOGIN_EMAIL = 'ayelplogin@gmail.com'
YELP_LOGIN_PASSWORD = 'ianbyeristhesht'
YELP_MEMBER_SEARCH_URL = 'http://www.yelp.com/member_search'
YELP_REVIEW_HTML_URL = 'http://www.yelp.com/user_details_reviews_self'
YELP_FRIEND_HTML_URL = 'http://www.yelp.com/user_details_friends'
