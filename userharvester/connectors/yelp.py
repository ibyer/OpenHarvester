#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#
import urllib
import urllib2
import urlparse
import cgi
import cookielib
import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

# 3rd Party
import lib_path
import BeautifulSoup

import userharvester.errors as errors
import userharvester.config as config

class YelpReview():
    def __init__(self):
        self.business_name = ''
        self.business_id = ''
        self.business_address = ''
        self.category_list = []
        self.rating = 0
        self.review_date = ''
        self.review_id = ''
        self.review = ''

class YelpFriend():
    def __init__(self):
        self.display_name = ''
        self.user_id = ''
        self.location = ''

class YelpConnector():
    
    def __init__(self):
        pass
    
    def get_user_id(self, name_search_text):
        """ Try to scrape the user id from user's email """
        
        # Get HTML
        raw_html = self._scrape_user_id(name_search_text)
        
        # Extract User Ids      
        return self._extract_user_ids_from_html(raw_html)
    
    def get_reviews(self, user_id, last_review_date=None):
        """ Return Yelp reviews for a given UserId and an option last review date """
        return self._scrape_html_reviews(user_id, last_review_date)
    
    def get_friends(self, user_id):
        """ Return Yelp friends for a given userid """
        return self._scrape_html_friends(user_id)
    
    def _scrape_user_id(self, name_search_text):
        # Request Thingyz
        login_url = config.YELP_LOGIN_URL
        opts = {
            'content':'',
            'email': config.YELP_LOGIN_EMAIL,
            'password': config.YELP_LOGIN_PASSWORD,
            'default_action': 'submit',
            'action_submit':'Log In'
        }

        # Some fake headers
        headers = {
        'Host': 'www.yelp.com',
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12',
        'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
        'Accept-Language': 'en-gb,en;q=0.5',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type' : 'application/x-www-form-urlencoded'}                

        # CookieJar
        cj = cookielib.LWPCookieJar()
        redirect_handler = urllib2.HTTPRedirectHandler()
        opener = urllib2.build_opener(redirect_handler, urllib2.HTTPCookieProcessor(cj)) 
        urllib2.install_opener(opener)
        
        # Build POST params
        params = urllib.urlencode(opts) 
        
        # Request 1st Time to get initial cookie passed when logging in
        request = urllib2.Request(login_url, None, headers)
        response1 = opener.open(request)
        
        # Request 2nd time to actually login
        request2 = urllib2.Request(login_url, params, headers)
        response2 = opener.open(request2)
        
        # Now Do the search
        query = {
        'action_search':'Search',
        'query': name_search_text        
        }
        
        # Now lets do the search
        resp = opener.open(config.YELP_MEMBER_SEARCH_URL + '?' + urllib.urlencode(query))
        
        # Extract Data
        raw_html = resp.read()
        resp.close()  
        
        return raw_html    
    
    def _extract_user_ids_from_html(self, raw_html):
        """ Here we just use all the logic to extract usernames from the HTML page """
        
        soup = BeautifulSoup.BeautifulSoup(raw_html)
        
        member_list = []
        for m in soup.findAll('ol',{'class':'members'}):
            
            # Lets find the link
            member_link_tag = m.findAll('a')
            
            # Did we have a link
            if (len(member_link_tag) > 0):
                name_dict = {}
                name_dict['name'] = member_link_tag[0].string
                link = member_link_tag[0]['href']
                query_params = urlparse.urlparse(link)[4]
                user_id = cgi.parse_qs(query_params).get('userid')[0]
                
                name_dict['user_id'] = user_id
                member_list.append(name_dict)
        
                # Get Location
                member_location_tag = m.findAll('p',{'class':'location'})
                if (len(member_location_tag) > 0):
                    name_dict['location'] = member_location_tag[0].getText()
                            
            
        return member_list
    
    def _scrape_html_reviews(self, user_id, last_review_date=None):
        """ Scrape HTML reviews from user_id and last review date """
        
        review_url = config.YELP_REVIEW_HTML_URL
        review_page_start = 0  
        review_list = []
        break_loop_early = False 
               
        # Try to load all reviews.. break when none are left or you hit the last review date
        while True:
            
            # Should we break early?
            if (break_loop_early):
                break
            
            # Query params
            query_params = {
            'userid':user_id,
            'review_sort':'time',
            'rec_pagestart':review_page_start}
            
            query_url = review_url + '?' + urllib.urlencode(query_params)        
            
            
            # Do the html initial HTML request
            try:
                response = urllib2.urlopen(query_url)
            except urllib2.URLError, e:
                raise errors.ConnectorError('yelp',e)    
            
            
            # Now, lets analyze the html
            soup = BeautifulSoup.BeautifulSoup(response.read())
            

            review_blocks = soup.findAll('div',{'class':'review clearfix'})
            
            # Break out of loop if we have no review blocks
            if (len(review_blocks) == 0):
                break
            
            # Go through review blocks
            for review_block in review_blocks:
                biz_block = review_block.findAll('div',{'class':'biz_info'})[0]
                business_name = biz_block.h4.a.getText()
                business_id = biz_block.h4.a['href']
                business_id = business_id[:business_id.find('#hrid:')]
                business_address = biz_block.address.getText()

                
                # Biz categories
                categories = []
                for a in biz_block.p.findAll('a'):
                    categories.append(a.getText())
                    
                # Rating
                rating_text = review_block.findAll('div', {'class':'rating'})[0].img['title']
                rating = rating_text[0:1]
                
                # Review Date
                review_date_str = review_block.findAll('div', {'class':'rating_info'})[0].find('em', {'class':'smaller'}).getText()
                review_date = datetime.datetime.strptime(review_date_str, '%m/%d/%Y')
                
                # Lets go ahead and check if review date is less that last_review_date, if so... 
                #   bust ooot cause we prolly already have all this shite
                if (last_review_date != None and review_date < last_review_date):
                    break_loop_early = True
                    break
                
                # Review ID
                review_id = review_block.findAll('div', {'class':'rateReview'})[0]['id']
                review_id = review_id[4:]
                    
                # Check-in
                # TODO: Checkins from Yelp
                
                # Review
                review = review_block.findAll('div',{'class':'review_comment'})[0].getText()
                
                # Build ReviewClass and add to list
                # Lets do a dict... go from there
                yelp_review = YelpReview()
                yelp_review.business_name = business_name
                yelp_review.business_id = business_id
                yelp_review.business_address = business_address
                yelp_review.category_list = yelp_review.category_list + categories
                yelp_review.rating = int(rating)
                yelp_review.review_date = review_date
                yelp_review.review_id = review_id
                yelp_review.review = review
                
                review_list.append(yelp_review) 
                        
                        
                # Increment Review counter for paging
                review_page_start = review_page_start + 1
                logging.debug('Yelp Review Count: %d' % review_page_start)                
        return review_list
    
    def _scrape_html_friends(self, user_id):
        """ Scrape HTML friends from user_id """

        friend_url = config.YELP_FRIEND_HTML_URL
        friend_page_start = 0  
        friend_list = []
        
        # Try to load all reviews.. break when none are left or you hit the last review date
        while True:
            
            # Query params
            query_params = {
            'userid':user_id,
            'sort':'first_name',
            'start':friend_page_start}
            
            query_url = friend_url + '?' + urllib.urlencode(query_params)        
            
            
            # Do the html initial HTML request
            try:
                response = urllib2.urlopen(query_url)
            except urllib2.URLError, e:
                raise errors.ConnectorError('yelp',e)    
            
            
            # Now, lets analyze the html
            soup = BeautifulSoup.BeautifulSoup(response.read())
            

            friend_blocks = soup.findAll('div',{'class':'friend_box'})
            
            # Break out of loop if we have no friend blocks
            if (len(friend_blocks) == 0):
                break
            
            # Go through friend blocks
            for friend_block in friend_blocks:
                
                # Name
                friend_name = friend_block.findAll('p', {'class':'miniRegular'})[0].a.getText()
                
                # Get user id from link
                friend_user_id_link = friend_block.findAll('p', {'class':'miniRegular'})[0].a['href']
                qs = urlparse.urlparse(friend_user_id_link)[4]
                friend_user_id = cgi.parse_qs(qs).get('userid')[0]
                
                # Location
                friend_location = friend_block.findAll('p',{'class':'user_location smaller'})[0].getText()
                
                # Build Friend Class and add to list
                yelp_friend = YelpFriend()
                yelp_friend.display_name = friend_name
                yelp_friend.user_id = friend_user_id
                yelp_friend.location = friend_location
                
                friend_list.append(yelp_friend) 
                                
                # Increment Review counter for paging
                friend_page_start = friend_page_start + 1
                logging.debug('Yelp Friend Count: %d' % friend_page_start)
        return friend_list
        
        pass
