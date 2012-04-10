#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#
# UserHarvester class handles communicating with the connector classes for respective 
# social sites and store the returning data into the respective datamodel.
# 
# This class will be mostly called by the Task Handler portion of the application.
#

import connectors.facebook
import connectors.twitter
import connectors.yelp
import datamodel
import config

import logging
import datetime

import errors

from google.appengine.ext import db
  

class UserHarvester():
    
    def __init__(self):
        pass
    
    def run(self):
        """ Iterates thru social sites and harvest data... run this as a cron job i guess """
        
        # Lets do some good stuff
        self.harvest_facebook_all()
        self.harvest_twitter_all()
        
        pass
    
    
    def initial_harvest(self, social_account):
        """ Run this function when the users is new and you do the initial harvest """

        #### Facebook ####
        if social_account.account_type == config.SOCIAL_SITE_FACEBOOK:
            # Connect to facebook
            fb = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                       app_secret = config.FACEBOOK_API_APP_SECRET,
                                                       app_url = config.APP_URL,
                                                       graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                       oauth_url = config.FACEBOOK_API_OAUTH_URL)        
            # Get basic info..
            try:
                self.harvest_facebook_basic_info(social_account)
            except errors.ConnectorError, e:
                pass
            
            # Harvest It.
            self.harvest_facebook_all(social_account)
        
        #### Twitter ####    
        elif social_account.account_type == config.SOCIAL_SITE_TWITTER:
            tw = connectors.twitter.TwitterConnector(config.TWITTER_API_KEY,
                                                      config.TWITTER_API_SECRET,
                                                      config.TWITTER_API_CALL_BACK_URL)
            
            # Lets make sure they have a user_id
            if (social_account.user_id == '' or social_account.user_id == None):               
                user_id = tw.get_user_id(social_account.user_name,
                                         social_account.access_token,
                                         social_account.access_token_secret)
                
                social_account.user_id = user_id
                social_account.put()       
            
            # Now harvest twitter        
            self.harvest_twitter_all(social_account)
    
        #### Yelp ####
        elif social_account.account_type == config.SOCIAL_SITE_YELP:
            self.harvest_yelp_all(social_account)
            pass
        
        #### Digg ####
        elif social_account.account_type == config.SOCIAL_SITE_DELICIOUS:
            pass
        
        pass

##############################################
#
#  Facebook
#
##############################################
    
    def harvest_facebook_all(self, social_account=None):
        """ Main function which Harvests all Facebook data . If passed a SocialAccount, then just pull for that account"""
        
        # Look for see if we want to do an individual social account or load off of them
        if (social_account == None):
            q = datamodel.SocialAccount.gql('WHERE account_type = :1 AND enabled = :2', 
                                            config.SOCIAL_SITE_FACEBOOK, 
                                            True)
        else:
            q = [social_account]    
            
            # Iterate through all enabled SocialAccounts
        for social_account in q:
                
            
            # Run it 
            try:
                self.harvest_facebook_posts(social_account)
            except errors.ConnectorError, e:
                pass
            
            try:
                self.harvest_facebook_friends(social_account)
            except errors.ConnectorError, e:
                pass            
            
            try:
                self.harvest_facebook_groups(social_account)
            except errors.ConnectorError, e:
                pass            
            
            try:
                self.harvest_facebook_likes(social_account)
            except errors.ConnectorError, e:
                pass
            
            try:
                self.harvest_facebook_events(social_account)
            except errors.ConnectorError, e:
                pass                              
                    
        pass
    
    def harvest_facebook_posts(self, social_account):
        
        recent_post_date = None
        start_post_date = None
            
            
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                   
        # Get most recent post date to see what date we should start pulling from
        query =  datamodel.SocialPost.gql('WHERE social_account = :1 ORDER BY original_post_date DESC', social_account)
        
        last_social_post = query.get()
        
        # If a post exists, then lets load from that last date... if not, then lets try to load everything
        if last_social_post:
            recent_post_date = last_social_post.original_post_date
        else:
            recent_post_date = None
            #start_post_date = datetime.datetime(2000,1,1)      
            
        json_posts = fb_connector.get_posts(social_account.user_id, social_account.access_token, recent_post_date,start_post_date)

        # Parse JSON returns
        for post in json_posts['data']:
            
            # If item exists, dont restore it.
            # TODO: Make this query more efficient!!! Do similar to the harvest_friends...
            query_check = datamodel.SocialPost.gql('WHERE social_account_item_id = :1', post['id'])
            if (query_check.count() < 1):
            
                post_date = datetime.datetime.strptime(post['created_time'], "%Y-%m-%dT%H:%M:%S+0000")
                if (post['type'] == 'status'):
                    social_post = datamodel.SocialPost(user=social_account.user,
                                                       social_account=social_account,
                                                       social_account_item_id=post['id'],
                                                       post_type='status',
                                                       raw_text=db.Text(post['message']),
                                                       original_post_date=post_date)
                    social_post.put()
                elif (post['type'] == 'video'):
                    social_post = datamodel.SocialPost(user=social_account.user,
                                                       social_account=social_account,
                                                       social_account_item_id=post['id'],                                                       
                                                       post_type='video',
                                                       raw_text=db.Text(post['message']),
                                                       url_list=[db.Link(post['link'])],
                                                       original_post_date=post_date)
                    social_post.put()
                else:
                    pass
    
    def harvest_facebook_statuses(self, social_account):
        recent_post_date = None
        start_post_date = None
            
            
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                   
        # Get most recent post date to see what date we should start pulling from
        query =  datamodel.SocialPost.gql('WHERE social_account = :1 AND post_type = :2 ORDER BY original_post_date DESC LIMIT 1', 
                                          social_account,
                                          'status')
        
        last_social_post = query.get()
        
        # If a post exists, then lets load from that last date... if not, then lets try to load everything
        if last_social_post:
            recent_post_date = last_social_post.original_post_date
        else:
            recent_post_date = None
            #start_post_date = datetime.datetime(2000,1,1)      


        # Lets try this...build list of all post ids on last post date
        post_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialPost WHERE social_account = :1 AND post_type = :2 AND original_post_date = :3", 
                        social_account,
                        'status',
                        recent_post_date)
        for post_key in q:
            post_id_list.append(datamodel.SocialPost.get(post_key).social_account_item_id)

            
        json_posts = fb_connector.get_statuses(social_account.user_id, social_account.access_token, recent_post_date,start_post_date)



        # Parse JSON returns
        for post in json_posts['data']:
            
            # If item exists, dont add it.
            if (post['id'] not in post_id_list):
                post_date = datetime.datetime.strptime(post['updated_time'], "%Y-%m-%dT%H:%M:%S+0000")

                social_post = datamodel.SocialPost(user=social_account.user,
                                                   social_account=social_account,
                                                   social_account_item_id=post['id'],
                                                   post_type='status',
                                                   raw_text=db.Text(post['message']),
                                                   original_post_date=post_date)
                social_post.put()
     
        pass              

    def harvest_facebook_links(self, social_account):
        recent_post_date = None
        start_post_date = None
            
            
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                   
        # Get most recent post date to see what date we should start pulling from
        query =  datamodel.SocialPost.gql('WHERE social_account = :1 AND post_type = :2 ORDER BY original_post_date DESC LIMIT 1', 
                                          social_account,
                                          'link')
        
        last_social_post = query.get()
        
        # If a post exists, then lets load from that last date... if not, then lets try to load everything
        if last_social_post:
            recent_post_date = last_social_post.original_post_date
        else:
            recent_post_date = None
            #start_post_date = datetime.datetime(2000,1,1)      


        # Lets try this...build list of all post ids on last post date
        post_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialPost WHERE social_account = :1 AND post_type = :2 AND original_post_date = :3", 
                        social_account,
                        'link',
                        recent_post_date)
        for post_key in q:
            post_id_list.append(datamodel.SocialPost.get(post_key).social_account_item_id)

            
        json_posts = fb_connector.get_statuses(social_account.user_id, social_account.access_token, recent_post_date,start_post_date)



        # Parse JSON returns
        for post in json_posts['data']:
            
            # If item exists, dont add it.
            if (post['id'] not in post_id_list):
                post_date = datetime.datetime.strptime(post['created_time'], "%Y-%m-%dT%H:%M:%S+0000")

                social_post = datamodel.SocialPost(user=social_account.user,
                                                   social_account=social_account,
                                                   social_account_item_id=post['id'],
                                                   post_type='link',
                                                   raw_text=db.Text(post['message']),
                                                   url_list = [db.Link(post['link'])],
                                                   url_description = post['description'],
                                                   original_post_date=post_date)
                social_post.put()
     
        pass

    
    def harvest_facebook_groups(self, social_account):
        """ Harvest the groups from facebook and put into socialgroup obj """
        
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                 
        
        
        json_groups = fb_connector.get_groups(social_account.user_id, social_account.access_token)

        # Lets try this...build list of all item ids
        item_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialGroup WHERE social_account = :1", social_account)
        for item_key in q:
            item_id_list.append(datamodel.SocialGroup.get(item_key).social_account_item_id)
        
        for group in json_groups['data']:
            #query_check = datamodel.SocialGroup.gql('WHERE social_account = :1 AND social_account_item_id = :2', social_account, group['id'])  
            #if (query_check.count() == 0):
            if (group['id'] not in item_id_list):
                social_group = datamodel.SocialGroup(user=social_account.user,
                                                     social_account=social_account,
                                                     social_account_item_id=group['id'],
                                                     name=group['name'])
                social_group.put()          
                
    
    def harvest_facebook_friends(self, social_account):
        """ Harvest the friends from facebook and put into SocialFriend obj """
        
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                 
        
        # Call FB
        json_friends = fb_connector.get_friends(social_account.user_id, social_account.access_token)
        
        # Lets try this...build list of all friend ids
        friend_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialFriend WHERE social_account = :1", social_account)
        for friend_key in q:
            friend_id_list.append(datamodel.SocialFriend.get(friend_key).social_account_item_id)
                    
        
        # Parse json results
        for friend in json_friends['data']:
            
            # check to see if we already have this friend
            #query_check = datamodel.SocialFriend.gql('WHERE social_account = :1 AND social_account_item_id = :2 LIMIT 1', social_account, friend['id'])
            #query_check = db.GqlQuery("SELECT __key__ FROM SocialFriend WHERE social_account = :1 AND social_account_item_id = :2 LIMIT 1", social_account, friend['id'])
            #if (query_check.get() == None):

            if friend['id'] not in friend_id_list:    
                social_friend = datamodel.SocialFriend(user=social_account.user,
                                                       social_account=social_account,
                                                       social_account_item_id=friend['id'],
                                                       display_name=friend['name'])
                social_friend.put()
                            
        
    
    def harvest_facebook_likes(self, social_account):
        """ Harvest the likes from facebook and put into SocialLike object """
        
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                 
        
        # Call FB
        json_likes = fb_connector.get_likes(social_account.user_id, social_account.access_token)
        
        
        # Lets try this...build list of all item ids
        item_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialLike WHERE social_account = :1", social_account)
        for item_key in q:
            item_id_list.append(datamodel.SocialLike.get(item_key).social_account_item_id)  
            
                  
        # Parse and put into DB
        for like in json_likes['data']:
            #query_check = datamodel.SocialLike.gql('WHERE social_account = :1 AND social_account_item_id = :2', social_account, like['id'])    
            #if (query_check.count() == 0):
            if (like['id'] not in item_id_list):
                social_like = datamodel.SocialLike(user=social_account.user,
                                                   social_account=social_account,
                                                   social_account_item_id=like['id'],
                                                   name=like['name'],
                                                   category_list=[like['category']],
                                                   original_like_date=datetime.datetime.strptime(like['created_time'], "%Y-%m-%dT%H:%M:%S+0000")) 
                social_like.put()       
        pass        
    
    def harvest_facebook_events(self, social_account):
        """ Harvest the event from facebook and put into SocialEvent object """
        
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                 
        
        # Call FB
        json_events = fb_connector.get_events(social_account.user_id, social_account.access_token)


        # Lets try this...build list of all item ids
        item_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialEvent WHERE social_account = :1", social_account)
        for item_key in q:
            item_id_list.append(datamodel.SocialEvent.get(item_key).social_account_item_id)

        
        # Parse and put into DB
        for event in json_events['data']:
            #query_check = datamodel.SocialEvent.gql('WHERE social_account = :1 AND social_account_item_id = :2', social_account, event['id'])    
            #if (query_check.count() == 0):
            if (event['id'] not in item_id_list):
                social_event = datamodel.SocialEvent(user=social_account.user,
                                                   social_account=social_account,
                                                   social_account_item_id=event['id'],
                                                   name=event['name'],
                                                   location_text=event['location'],
                                                   location_address=db.PostalAddress(event['location']),
                                                   start_time=datetime.datetime.strptime(event['start_time'], "%Y-%m-%dT%H:%M:%S+0000"),
                                                   end_time=datetime.datetime.strptime(event['end_time'], "%Y-%m-%dT%H:%M:%S+0000"),
                                                   rsvp=event['rsvp_status'])
                                                    
                social_event.put()                

    def harvest_facebook_basic_info(self, social_account):
        """ Harvest basic info from FB and populate data in SocialUser """
        
        # Connect to facebook
        fb_connector = connectors.facebook.FacebookConnector(app_id = config.FACEBOOK_API_APP_ID,
                                                             app_secret = config.FACEBOOK_API_APP_SECRET,
                                                             app_url = config.APP_URL,
                                                             graph_url = config.FACEBOOK_API_GRAPH_URL,
                                                             oauth_url = config.FACEBOOK_API_OAUTH_URL) 
                 
        
        # Call FB
        json = fb_connector.get_basic_user_info('me', social_account.access_token)
        
        # Parse Data
        social_user = social_account.user
        
        social_user.first_name = json.get('first_name')
        social_user.last_name = json.get('last_name')
        social_user.name = json.get('name')
        social_user.birth_date = datetime.datetime.strptime(json.get('birthday'),"%m/%d/%Y")
        
        if json.get('gender') == 'male':
            social_user.gender = 'M'
        elif json.get('gender') == 'female':
            social_user.gender = 'F'
        else:
            social_user.gender = 'U'  
                                        
        social_user.email = json.get('email')
        social_user.bio = json.get('bio')
        social_user.current_location = json.get('location').get('name')
        # TODO: Add logic to make a valid link
        #social_user.personal_website = db.Link(json['website'])
        
        social_user.relationship_status = json.get('relationship_status')
        
        social_user.locale = json.get('locale')
        #social_user.timezone = json['timezone']
        
        # TODO: Add Jobs
        for job in json.get('work'):
            pass        
        
        # Store user id
        social_account.user_id = json.get('id')
        
        social_user.put()
        social_account.put()
        pass   


##############################################
#
#  Twitter
#
##############################################
    
    def harvest_twitter_all(self, social_account=None):
        """ Main function to harvest Twitter Accounts... if social account is passed, pull for that"""
        
        # Look for see if we want to do an individual social account or load off of them
        if (social_account == None):
            q = datamodel.SocialAccount.gql('WHERE account_type = :1 AND enabled = :2', 
                                            config.SOCIAL_SITE_TWITTER, 
                                            True)
        else:
            q = [social_account]    
            
            # Iterate through all enabled SocialAccounts
        for social_account in q:
                           
            # Run it 
            try:
                self.harvest_twitter_posts(social_account)
            except errors.ConnectorError, e:
                pass
            
            try:
                self.harvest_twitter_friends(social_account)
            except errors.ConnectorError, e:
                pass            
            
    
    def harvest_twitter_posts(self, social_account):
        """ Harvest posts from Twitter """
        
        # Connect to twitter
        twitter_connector = connectors.twitter.TwitterConnector(config.TWITTER_API_KEY,
                                                                config.TWITTER_API_SECRET,
                                                                config.TWITTER_API_CALL_BACK_URL)        
        
        start_id = None
        end_id = None
        
        q = datamodel.SocialPost.gql('WHERE social_account = :1 ORDER BY social_account_item_id DESC LIMIT 1', social_account)
        
        last_social_post = q.get()
        
        # Do we have data... then pull from last post
        if last_social_post:
            start_id = last_social_post.social_account_item_id
        
        # Get data from Twitter    
        json = twitter_connector.get_posts(social_account.user_id,
                                           social_account.access_token,
                                           social_account.access_token_secret,
                                           start_id,
                                           end_id)

        # Lets try this...build list of all friend ids
        post_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialPost WHERE social_account = :1", social_account)
        for post_key in q:
            post_id_list.append(datamodel.SocialPost.get(post_key).social_account_item_id)
       
        
        # Parse JSON
        for tweet in json:
            # Check to see if we already have this tweet
            if tweet.id_str not in post_id_list:
                
                url_list = []
                mention_list = []
                hashtag_list = []
                
                # Build url lists, mention lists, and hashtag lists
                # TODO: Add Entity processing from Status in Twitter
#                for url in tweet.get('entities').get('urls'):
#                    url_list.append(db.Link(url))
#
#                for mention in tweet.get('entities').get('user_mentions'):
#                    mention_list.append(mention.get('id_str'))                    
#
#                for hashtag in tweet.get('entities').get('hashtags'):
#                    hashtag_list.append(hashtag.get('text'))      
#                
#                post_date = datetime.datetime.strptime(tweet.get('created_at'),
#                                                       '%a %b %d %H:%M:%S +0000 %Y')
                social_post = datamodel.SocialPost(user=social_account.user,
                                                   social_account=social_account,
                                                   social_account_item_id=tweet.id_str,
                                                   post_type='status',
                                                   raw_text=db.Text(tweet.text),
                                                   url_list=url_list,
                                                   mention_list=mention_list,
                                                   hashtag_list=hashtag_list,
                                                   original_post_date=tweet.created_at)
                social_post.put() 
          

    def harvest_twitter_friends(self, social_account):
        """ Harvest friend data from Twitter """

        # Connect to twitter
        twitter_connector = connectors.twitter.TwitterConnector(config.TWITTER_API_KEY,
                                                                config.TWITTER_API_SECRET,
                                                                config.TWITTER_API_CALL_BACK_URL)  


        # Lets try this...build list of all friend ids
        friend_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialFriend WHERE social_account = :1", social_account)
        for friend_key in q:
            friend_id_list.append(datamodel.SocialFriend.get(friend_key).social_account_item_id)
                   
 
        # Get data from Twitter    
        json = twitter_connector.get_friends(social_account.user_id,
                                           social_account.access_token,
                                           social_account.access_token_secret)

        # Parse JSON
        for friend in json:
            if friend.id_str not in friend_id_list:    
                social_friend = datamodel.SocialFriend(user=social_account.user,
                                                       social_account=social_account,
                                                       social_account_item_id=friend.id_str,
                                                       social_account_username=friend.screen_name,
                                                       display_name=friend.name)
                social_friend.put()      
 
    
    def harvest_twitter_basic_info(self, social_account):
        """ Here we will get basic info... mainly the user's user_id """
        
        # Connect to twitter
        twitter_connector = connectors.twitter.TwitterConnector(config.TWITTER_API_KEY,
                                                                config.TWITTER_API_SECRET,
                                                                config.TWITTER_API_CALL_BACK_URL)          
        
        user_id = twitter_connector.get_user_id(social_account.user_name,
                                                social_account.access_token,
                                                social_account.access_secret)
        
        social_account.user_id = user_id
        social_account.put()
        pass
    
##############################################
#
#  Yelp
#
##############################################    

    def harvest_yelp_all(self, social_account=None):
        """ Main function to harvest Yelp Accounts... if social account is passed, pull for that"""
        
        # Look for see if we want to do an individual social account or load off of them
        if (social_account == None):
            q = datamodel.SocialAccount.gql('WHERE account_type = :1 AND enabled = :2', 
                                            config.SOCIAL_SITE_YELP, 
                                            True)
        else:
            q = [social_account]         
            
        
        for social_account in q:
            
            try:
                self.harvest_yelp_reviews(social_account)
            except errors.ConnectorError, e:
                pass

            try:
                self.harvest_yelp_friends(social_account)
            except errors.ConnectorError, e:
                pass            
            
        pass
    
    def harvest_yelp_reviews(self, social_account):
        """ Harvest yelp reviews and put into data model """
        
        # Build connector
        yelp_connector = connectors.yelp.YelpConnector()        
        
        last_review_date = None
        review_id_list = []
        
        # Get most recent review date
        q = datamodel.SocialReview.gql('WHERE social_account = :1 ORDER BY review_date DESC LIMIT 1', social_account)
        
        
        last_social_review = q.get()
        
        # Do we have data... then pull from last post
        if last_social_review:
            last_review_date = last_social_review.review_date
            
            # Load reviews on that review_date so we can check to see if we reloaded them in this last harvest
            q = db.GqlQuery("SELECT __key__ FROM SocialReview WHERE social_account = :1 AND review_date = :2", social_account, last_review_date)
            for review_key in q:
                review_id_list.append(datamodel.SocialReview.get(review_key).social_account_item_id)
            
            
        # Call Yelp
        review_list = yelp_connector.get_reviews(social_account.user_id, last_review_date)
        
        # Iterate through and store in db... lets check against 
        for review in review_list:
        
            if (review.review_id not in review_id_list):
                
                social_review = datamodel.SocialReview(user = social_account.user,
                                                       social_account = social_account,
                                                       social_account_item_id = review.review_id,
                                                       full_business_name = review.business_name,
                                                       business_address = db.PostalAddress(review.business_address),
                                                       social_account_business_id = review.business_id,
                                                       review_rating = db.Rating(review.rating*4),
                                                       review_date = review.review_date,
                                                       review_text = review.review)
                
                # Build category list
                for c in review.category_list:
                    social_review.business_category_list.append(c)
                
                social_review.put()
                
    def harvest_yelp_friends(self, social_account):
        """ Harvest friend data from Twitter """
        
        # Build connector
        yelp_connector = connectors.yelp.YelpConnector()           
        
        # Lets try this...build list of all friend ids
        friend_id_list = []
        q = db.GqlQuery("SELECT __key__ FROM SocialFriend WHERE social_account = :1", social_account)
        for friend_key in q:
            friend_id_list.append(datamodel.SocialFriend.get(friend_key).social_account_item_id)
                   
        # Get friends
        friend_list = yelp_connector.get_friends(social_account.user_id)
        
        # Iterate through friends
        for friend in friend_list:
             
            if (friend.user_id not in friend_id_list):
                social_friend = datamodel.SocialFriend(user=social_account.user,
                                                       social_account=social_account,
                                                       social_account_item_id=friend.user_id,
                                                       display_name=friend.display_name,
                                                       location = db.PostalAddress(friend.location))
                social_friend.put()  
        pass