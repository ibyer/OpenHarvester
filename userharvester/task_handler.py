#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#
# This will be the entry point for the tasks for harvesting individual pieces of a SocialAccount
# These will be called by CRON jobs in Google App Engine.
#
#
# Our Stuff
import userharvester.harvester as harvester
import userharvester.errors as errors
import userharvester.config as config
import userharvester.datamodel as datamodel

import logging

# Google App Enginez
from google.appengine.api import taskqueue 
from google.appengine.ext import db 
from google.appengine.ext import webapp 
from google.appengine.ext.webapp import template 
from google.appengine.ext.webapp.util import run_wsgi_app 


ALLOWED_MODES = ['all','userinfo','post','friend','bookmark','group','review','like','event']
FACEBOOK_MODES = ['userinfo','post','friend','group','like','event']
TWITTER_MODES = ['post','friend']
YELP_MODES = ['review','friend']


class FacebookHandler(webapp.RequestHandler):
    def post(self):
        
        # Why are we being called?
        mode = self.request.get('mode')
        key = self.request.get('key')
    
        uh = harvester.UserHarvester()
        social_account = datamodel.SocialAccount.get(key)        
        
        logging.debug('FB Handler: mode: ' + mode + '  key: ' + key)
        
        # Lets dooze it
        if (mode == 'post'):
            uh.harvest_facebook_statuses(social_account)

        elif (mode == 'friend'):
            uh.harvest_facebook_friends(social_account)
        
        elif (mode == 'group'):
            uh.harvest_facebook_groups(social_account)
            
        elif (mode == 'like'):
            uh.harvest_facebook_likes(social_account)
            
        elif (mode == 'event'):
            uh.harvest_facebook_events(social_account)
        else:
            pass
                
        
class TwitterHandler(webapp.RequestHandler):
    def post(self):
        
        # Why are we being called?
        mode = self.request.get('mode')
        key = self.request.get('key')
        
        uh = harvester.UserHarvester()
        social_account = datamodel.SocialAccount.get(key)        

        logging.debug('Twitter Handler: mode: ' + mode + '  key: ' + key) 
        
        # Lets dooze it
        if (mode == 'post'):
            uh.harvest_twitter_posts(social_account)
        
        elif (mode == 'friend'):
            uh.harvest_twitter_friends(social_account)
    
        else:
            pass        
        
    
class YelpHandler(webapp.RequestHandler):
    def post(self):
        
        # Why are we being called?
        mode = self.request.get('mode')
        key = self.request.get('key')
        
        uh = harvester.UserHarvester()
        social_account = datamodel.SocialAccount.get(key)        
        
        logging.debug('Yelp Handler: mode: ' + mode + '  key: ' + key)         
        
        # Lets dooze it
        if (mode == 'review'):
            uh.harvest_yelp_reviews(social_account)
        
        elif (mode == 'friend'):
            uh.harvest_yelp_friends(social_account)
    
        else:
            pass        
                
        pass    

class InitializerHandler(webapp.RequestHandler):
    """ This is the class that actually calls/distributes the individual tasks """
    def get(self):
        
        # Why are we being called?
        mode = self.request.get('mode')
  
        logging.debug('Initializer Handler: mode: ' + mode) 
                      
        # Lets check to see if that was an available mode   
        if (mode in ALLOWED_MODES):
            
            # Now add the respective task if that site allows that mode
            
            # Special 'ALL' Mode is called to load everything for a specific account
            #  It is called with 3 params... mode, key, and site
            if (mode == 'all'):
                key = self.request.get('key')
                social_site = self.request.get('site')
                
                if (social_site == config.SOCIAL_SITE_FACEBOOK):
                    for m in FACEBOOK_MODES:
                        query_params = {'mode': m,
                                        'key': key}
                        qu = taskqueue.Queue(config.TASK_QUEUE_NAME_FACEBOOK)
                        task = taskqueue.Task(url=config.TASK_FACEBOOK, params=query_params)
                        qu.add(task)                          
                        #taskqueue.add(url=config.TASK_FACEBOOK, params=query_params)   
                
                elif (social_site == config.SOCIAL_SITE_TWITTER):
                    for m in TWITTER_MODES:
                        query_params = {'mode': m,
                                        'key': key}
                        qu = taskqueue.Queue(config.TASK_QUEUE_NAME_TWITTER)
                        task = taskqueue.Task(url=config.TASK_TWITTER, params=query_params)
                        qu.add(task)                        
                        #taskqueue.add(url=config.TASK_TWITTER, params=query_params)  
                         
                elif (social_site == config.SOCIAL_SITE_YELP):
                    for m in TWITTER_MODES:
                        query_params = {'mode': m,
                                        'key': key}
                        qu = taskqueue.Queue(config.TASK_QUEUE_NAME_YELP)
                        task = taskqueue.Task(url=config.TASK_YELP, params=query_params)
                        qu.add(task)                         
                        #taskqueue.add(url=config.TASK_YELP, params=query_params)                                                                   
                else:
                    pass
                return
            
            # Facebook
            if (mode in FACEBOOK_MODES):
                fb_keys = db.GqlQuery('SELECT __key__ FROM SocialAccount WHERE account_type = :1 AND enabled = :2', 
                                      config.SOCIAL_SITE_FACEBOOK, 
                                      True)           
                        
                for key in fb_keys:
                    query_params = {'mode': mode,
                                    'key': key}
                    qu = taskqueue.Queue(config.TASK_QUEUE_NAME_FACEBOOK)
                    task = taskqueue.Task(url=config.TASK_FACEBOOK, params=query_params)
                    qu.add(task)                    
                    #taskqueue.add(url=config.TASK_FACEBOOK, params=query_params)

            # Twitter
            if (mode in TWITTER_MODES):
                twitter_keys = db.GqlQuery('SELECT __key__ FROM SocialAccount WHERE account_type = :1 AND enabled = :2', 
                                           config.SOCIAL_SITE_TWITTER, 
                                           True)                   
                for key in twitter_keys:
                    query_params = {'mode': mode,
                                    'key': key}
                    qu = taskqueue.Queue(config.TASK_QUEUE_NAME_TWITTER)
                    task = taskqueue.Task(url=config.TASK_TWITTER, params=query_params)
                    qu.add(task)                    
                    #taskqueue.add(url=config.TASK_TWITTER, params=query_params)          

            # Yelp
            if (mode in YELP_MODES):
                yelp_keys = db.GqlQuery('SELECT __key__ FROM SocialAccount WHERE account_type = :1 AND enabled = :2', 
                                        config.SOCIAL_SITE_YELP, 
                                        True)                
                for key in yelp_keys:
                    query_params = {'mode': mode,
                                    'key': key}
                    qu = taskqueue.Queue(config.TASK_QUEUE_NAME_YELP)
                    task = taskqueue.Task(url=config.TASK_YELP, params=query_params)
                    qu.add(task)                     
                    #taskqueue.add(url=config.TASK_YELP, params=query_params)  


def main():
    run_wsgi_app(webapp.WSGIApplication([
        (config.TASK_INIT, InitializerHandler), 
        (config.TASK_FACEBOOK, FacebookHandler),    
        (config.TASK_TWITTER, TwitterHandler), 
        (config.TASK_YELP, YelpHandler),                          
    ]))


if __name__ == "__main__":
    main()