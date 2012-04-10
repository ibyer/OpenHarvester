#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#

from google.appengine.ext import db

ADDRESS_FORMAT = '%(address1)s, %(address2)s, %(city)s, %(state)s, %(zip)s, %(country)s'

class SocialSource(db.Model):

    pass

class SocialUser(db.Model):
    first_name = db.StringProperty(required=True)
    last_name = db.StringProperty(required=True)
    display_name = db.StringProperty()
    
    user_entity = db.UserProperty()
    
    bio = db.TextProperty()
    
    gender = db.StringProperty(choices=set(["M","F","U"]))
    birth_date = db.DateTimeProperty()
    
    email = db.EmailProperty(required=True)
    email_alternate = db.EmailProperty()
    
    mobile_number = db.PhoneNumberProperty()
    
    mailing_address = db.PostalAddressProperty()
    
    personal_website = db.LinkProperty()
    
    hometown = db.StringProperty()
    current_location = db.StringProperty()
    
    relationship_status = db.StringProperty()
    
    locale = db.StringProperty()
    timezone = db.StringProperty()
    
    enabled = db.BooleanProperty()


class SocialAccount(db.Model):
    user = db.ReferenceProperty(SocialUser,
                                collection_name='social_accounts')
        
    account_type = db.StringProperty(required=True)
    user_name = db.StringProperty(required=True)
    password = db.StringProperty()
    
    user_id = db.StringProperty()

    access_token = db.StringProperty()
    access_token_secret = db.StringProperty()
    
    temp_auth_token_secret = db.StringProperty()
    
    enabled = db.BooleanProperty()
    
    
class SocialUserWork(db.Model):
    user = db.ReferenceProperty(SocialUser)
    employer_name = db.StringProperty()
    employer_location = db.StringProperty()
    position = db.StringProperty()


class SocialPost(db.Model):
    user = db.ReferenceProperty(SocialUser)
    social_account = db.ReferenceProperty(SocialAccount,
                                          collection_name='social_posts')
    social_account_item_id = db.TextProperty()
    
    post_type = db.StringProperty()
    raw_text = db.TextProperty()
    text_only = db.TextProperty()
    
    url_description = db.StringProperty()
    url_list = db.ListProperty(db.Link)
    hashtag_list = db.StringListProperty()
    mention_list = db.StringListProperty()
    retweet_originators = db.StringListProperty()
    
    original_post_date = db.DateTimeProperty()
    internal_retrieval_date = db.DateTimeProperty(auto_now_add=True)    


class SocialFriend(db.Model):
    user = db.ReferenceProperty(SocialUser)
    social_account = db.ReferenceProperty(SocialAccount)
    social_account_item_id = db.StringProperty()
    
    social_account_username = db.StringProperty()
    
    first_name = db.StringProperty()
    last_name = db.StringProperty()
    display_name = db.StringProperty()
    
    location = db.PostalAddressProperty()

    original_friend_date = db.DateTimeProperty()
    internal_retrieval_date = db.DateTimeProperty(auto_now_add=True)  

    #TODO: Add more attributes

class SocialBookmark(db.Model):
    user = db.ReferenceProperty(SocialUser)
    social_account = db.ReferenceProperty(SocialAccount)
    social_account_item_id = db.TextProperty()
    
    url_title = db.StringProperty()
    url = db.LinkProperty(required=True)
    tag_list = db.StringListProperty()
    
    original_post_date = db.DateTimeProperty(required=True)
    internal_retrieval_date = db.DateTimeProperty(auto_now_add=True)            


class SocialGroup(db.Model):
    user = db.ReferenceProperty(SocialUser)
    social_account = db.ReferenceProperty(SocialAccount)
    social_account_item_id = db.TextProperty()
    
    name = db.StringProperty()
         

class SocialReview(db.Model):
    user = db.ReferenceProperty(SocialUser)
    social_account = db.ReferenceProperty(SocialAccount)
    social_account_item_id = db.StringProperty()

    full_business_name = db.StringProperty()
    social_account_business_id = db.StringProperty()
    business_category_list = db.StringListProperty()
    business_address = db.PostalAddressProperty()

    review_rating = db.RatingProperty() #every rating is normalized to 1 out of 100    
    review_date = db.DateTimeProperty()
    review_text = db.TextProperty()
    
    checkin_count = db.IntegerProperty()
    
class SocialLike(db.Model):
    user = db.ReferenceProperty(SocialUser)
    social_account = db.ReferenceProperty(SocialAccount)
    social_account_item_id = db.StringProperty()
    
    name = db.StringProperty()
    category_list = db.StringListProperty()
    
    original_like_date = db.DateTimeProperty()
    internal_retrieval_date = db.DateTimeProperty(auto_now_add=True)            

class SocialEvent(db.Model):
    user = db.ReferenceProperty(SocialUser)
    social_account = db.ReferenceProperty(SocialAccount)
    social_account_item_id = db.StringProperty()
    
    name = db.StringProperty()
    start_time = db.DateTimeProperty()
    end_time = db.DateTimeProperty()
    
    location_text = db.StringProperty()
    location_address = db.PostalAddressProperty()
    
    #rsvp = db.StringProperty(required=True, choices=set(["Y","N","M"]))  # Yes, NO, or Maybe
    rsvp = db.StringProperty()
    friend_list = db.StringListProperty()


class SocialDealSource(db.Model):
    name = db.StringProperty()
    url = db.LinkProperty()
    

class SocialGroupDeal(db.Model):
    #deal_source = db.ReferenceProperty(SocialDealSource)
    source = db.StringProperty()
    
    merchant_name = db.StringProperty()
    merchant_url = db.LinkProperty()
    source_merchant_id = db.StringProperty()
    source_deal_id = db.StringProperty()
    
    title = db.StringProperty()
    text = db.TextProperty()
    url = db.LinkProperty()
    time_start = db.DateTimeProperty()
    time_end = db.DateTimeProperty()

    status = db.StringProperty()
   
    tag_list = db.StringListProperty()
    
    address_list = db.ListProperty(db.PostalAddress)
    geo_list = db.ListProperty(db.GeoPt)

class GraphEntity(db.Model):
    #name 
    pass

class GraphRelationship(db.Model):
    pass



