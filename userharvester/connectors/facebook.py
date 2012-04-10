#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#

#import facebook_api
import urllib
import urllib2
import cgi
import gzip
import logging
import datetime

from StringIO import StringIO

import userharvester.errors as errors

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


class FacebookConnector():
    
    def __init__(self, app_id, app_secret, app_url, graph_url, oauth_url):
        """ Init app access parameters """
        self._app_id = app_id
        self._app_secret = app_secret
        self._app_url = app_url
        self._graph_url = graph_url
        self._oauth_url = oauth_url

    def _decode_response_data(self, response):
        """ Test to see if reponse data is gzipped """
        if response.info().get('Content-Encoding') == 'gzip':
            buffer = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buffer)
            data = f.read()
        else:
            data = response.read()      
        return data       
    
    def time_convert(self, time_str):
        return datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S+0000")
    
    def authorize(self, request):
        ''' FB Authorize process for OAuth 2.0... returns dict with access_token and time to exp '''
        
        # If 'code' variable is returned, then move forward with 
        if 'code' in request and 'error' not in request:
            
            
            # Build Auth Params
            auth_params = {}
            auth_params['client_id'] = self._app_id
            auth_params['redirect_uri'] = self._app_url
            auth_params['client_secret'] = self._app_secret
            auth_params['code'] = request['code']
            
            auth_param_str = urllib.urlencode(auth_params)
            
            auth_request = self._oauth_url + '?' + auth_param_str
            
            # Do the OAuth request
            try:
                response = urllib2.urlopen(auth_request)
            except urllib2.URLError, e:
                raise errors.ConnectorError('facebook',e)
            
                        
            # Validate Response
            if (response.code == 400):
                raise errors.ConnectorError('facebook','400 response code from Oauth Request')
            
            response_data = self._decode_response_data(response)      
            
            # Build dict for response
            auth_return = cgi.parse_qs(response_data)
            
        else:
            raise errors.ConnectorError('facebook','Oauth Error:' + request['error'])
        
        return auth_return['access_token']
    
    def get_authorization_url(self, permission_url, permissions=None):
        
        params = {}
        
        params['client_id'] = self._app_id
        params['redirect_uri'] = self._app_url
        params['scope'] = permissions
        
        return permission_url + '?' + urllib.urlencode(params)

    def _request(self, url, args=None, post_args=None):
        """ Access GraphAPI """
        
        # If post data is present, add it
        post_data = None if post_args is None else urllib.urlencode(post_args)
        
        url = url + "?" + urllib.urlencode(args)
        
        # Url
        file = urllib.urlopen(url, post_data)
        
        try:
            response = _parse_json(file.read())
        finally:
            file.close()
        if response.get("error"):
            #TODO: Error handling
            logging.error(url)
            raise errors.ConnectorError('facebook','error response from API request')
        
        return response  

    
    def _get_resource(self, id, resource, access_token, start_time=None, end_time=None):
        
        # Build args
        args = {}
        args['access_token'] = access_token
        
        if start_time is not None:
            args['since'] = start_time
        
        if end_time is not None:
            args['until'] = end_time
        
        if (resource is None):
            url = self._graph_url + '/' + id
        else:
            url = self._graph_url + '/' + id + '/' + resource        
        
        return self._request(url, args)
        pass    

#    def _get_paged_resource(self, id, resource, access_token, start_time=None, end_time=None):
#                
#        mo_data = True         
#        json_aggregate = []
#        s_time = start_time
#        e_time = end_time
#        
#        while mo_data:
#            json = self._get_resource(id, resource, access_token, s_time, e_time)
#              
#            # Lets check to see if we have more data / paging
#            data_count = len(json['data'])
#            
#            # No Mo Data... break
#            if (data_count == 0):
#                mo_data = False
#                break
#            
#            # Add json to aggregate
#            json_aggregate.extend(json['data'])
#                
#            # Lets setup to get more dat    
#            last_created_date = self.time_convert(json['data'][data_count-1])
#            
#            # Lets subtract or add by 1 minute.. try to pull more data
#            if (s_time != None):
#                s_time = last_created_date + datetime.timedelta(minutes=+1)
#            
#            if (e_time != None):
#                e_time = last_created_date + datetime.timedelta(minutes=-1)
#            
#                  
#        return json

    def _get_paged_resource(self, id, resource, access_token, start_time=None, end_time=None):
                
        mo_data = True         
        json_aggregate = []
        s_time = start_time
        e_time = end_time
        
        while mo_data:
            json = self._get_resource(id, resource, access_token, s_time, e_time)
              
            # Lets check to see if we have more data / paging
            data_count = len(json['data'])
            
            # No Mo Data... break
            if (data_count == 0):
                mo_data = False
                break
            
            # Add json to aggregate
            json_aggregate.extend(json['data'])
                
            # Lets setup to get more dat    
            last_created_date = self.time_convert(json['data'][data_count-1])
            
            # Lets subtract or add by 1 minute.. try to pull more data
            if (s_time != None):
                s_time = last_created_date + datetime.timedelta(minutes=+1)
            
            if (e_time != None):
                e_time = last_created_date + datetime.timedelta(minutes=-1)
            
                  
        return json   
    
    
    def get_basic_user_info(self, id, access_token):
        return self._get_resource(id, None, access_token)    
    
    def get_posts(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'posts', access_token, start_time, end_time)
    
    def get_statuses(self, id, access_token, start_time=None, end_time=None):
        return self._get_paged_resource(id, 'statuses', access_token, start_time, end_time)    

    def get_links(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'links', access_token, start_time, end_time)  
    
    def get_friends(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'friends', access_token, start_time, end_time)
        
    def get_groups(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'groups', access_token, start_time, end_time)

    def get_photo_tags(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'photos', access_token, start_time, end_time)

    def get_photo_albums(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'albums', access_token, start_time, end_time)
    
    def get_likes(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'likes', access_token, start_time, end_time)
    
    def get_events(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'events', access_token, start_time, end_time)

    def get_checkins(self, id, access_token, start_time=None, end_time=None):
        return self._get_resource(id, 'checkins', access_token, start_time, end_time)
        
    