#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#

import userharvester.errors as errors

#3rd party Twitter API
import lib_path
import tweepy



# Find a JSON parser
try:
    import json
    _parse_json = lambda s: json.loads(s)
except ImportError:
    try:
        import simplejson
        _parse_json = lambda s: simplejson.loads(s)
    except ImportError:
        # For Google AppEngine
        from django.utils import simplejson
        _parse_json = lambda s: simplejson.loads(s)
        

class TwitterConnector():

    def __init__(self, app_key, app_secret, app_call_back_url):
        self._app_key = app_key
        self._app_secret = app_secret
        self._app_call_back_url = app_call_back_url
        pass
    
    def authorize(self, request, request_secret):
        
        oauth_token = request.get('oauth_token')
        oauth_verifier = request.get('oauth_verifier')
        
        # Did these exist in the request?
        if (oauth_token == None or oauth_verifier == None):
            raise errors.ConnectorError('twitter','OAuth variables not set in request')
        
        auth = tweepy.OAuthHandler(self._app_key,
                                   self._app_secret,
                                   self._app_call_back_url)
        
        # Setup to get Access Token
        auth.set_request_token(oauth_token, request_secret)
        
        try:
            auth.get_access_token(oauth_verifier)
        except tweepy.TweepError, e:
            raise errors.ConnectorError('twitter',e)
        
        return {'access_token':auth.access_token.key,
                'access_secret':auth.access_token.secret}
        
    
    def get_authorization_url(self):
        auth = tweepy.OAuthHandler(self._app_key,
                                   self._app_secret,
                                   self._app_call_back_url)
        
        try:
            redirect_auth_url = auth.get_authorization_url()
        except tweepy.TweepError, e:
            raise errors.ConnectorError('twitter', e)
        
        return {'url': redirect_auth_url, 'token_secret':auth.request_token.secret}
    
    def get_basic_user_info(self, id, access_token, access_secret):
        """ Gets user information for a specific user """
        auth = tweepy.OAuthHandler(self._app_key,
                                   self._app_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth_handler=auth)

        return api.get_user(user_id=id)  
    
    
    def get_posts(self, id, access_token, access_secret, start_id=None, end_id=None):
        
        auth = tweepy.OAuthHandler(self._app_key,
                                   self._app_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth_handler=auth)
        
        # Setup Args
        args = {}
        args['user_id'] = id
        
        if (start_id):
            args['since_id'] = start_id
        
        if (end_id):
            args['max_id'] = end_id
            
        # Page through and build result set
        json_response = []
        for status in tweepy.Cursor(api.user_timeline, **args).items():
            json_response.append(status)
            
        return json_response
    
    
    def get_friends(self, id, access_token, access_secret, start_id=None, end_id=None):
        """ Gets a list of users you are following... these are in JSON format from the show user """
        
        auth = tweepy.OAuthHandler(self._app_key,
                                   self._app_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth_handler=auth)
        
        # Get Friend ids... then get User information
        friend_list = []
        for follower_id in tweepy.Cursor(api.friends_ids).items():
            friend_list.append(api.get_user(user_id=follower_id))
            
        return friend_list

    def get_user_id(self, screen_name, access_token, access_secret):
        """ Gets the user_id for a screen name """
        #json = self.get_basic_user_info(screen_name, access_token, access_secret)

        auth = tweepy.OAuthHandler(self._app_key,
                                   self._app_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth_handler=auth)
        
        results = api.user_timeline()
        
        user_id = None
        if (len(results) > 0):
            user_id = results[0].user.id_str
            
        return user_id