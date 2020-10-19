"""yelpUserProfile.py: This program scrapes data from a Yelp user and the user's friends, 
then uses NLP to analyze and produce statistically meaningful data."""

import requests
from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd
import math
import re
import argparse
from google.cloud import language
from google.cloud.language import enums, types
import os
import logging


__author__ = "Peyton Wang"
__credits__ = ["Alexandra Bullen-Smith", "Marisa Papagelis", "Erez Yoeli", "Mohsen Mosleh"]


logging.basicConfig(filename="yelpUserProfile.py", level=logging.INFO)

class YelpUserProfile():
    """
    Generates data necessary to build new user profile.
    """

    def __init__(self, args):
        """
        Parameters
        ---------- 
        args : Namespace
            Namespace object with attributes (userID) from the command line
        """
        if isinstance(args, argparse.Namespace):
            self.user_id = args.user_id
        
        if isinstance(args, str):
            self.user_id = args 
        
        self.user_dict = {}
        self.user_df = pd.DataFrame()
        self.user_places_df = pd.DataFrame()
        self.friends_df = pd.DataFrame()
        self.friends_places_df = pd.DataFrame()

        self.sentiment_client = language.LanguageServiceClient()
                          
    def get_name(self):
        """
        Gets the user's name.
        """
        return self.user_dict["name"]
        
    def get_hometown(self):
        """
        Gets the user's hometown.
        """
        return self.user_dict["hometown"]
    
    def get_total_reviews(self):
        """
        Gets the user's total number of reviews written.
        """
        return self.user_dict["total reviews"]
    
    def get_total_friends(self):
        """
        Gets the user's total number of friends.
        """
        return self.user_dict["total friends"]
        
    def get_profile_pic(self):
        """
        Gets the URL path to the user's profile picture.
        """
        return self.user_dict["profile picture"]

    def get_places_info(self, is_main_user=True):
        """
        Gets the user's information on the places they visited.
        """
        user_df = self.user_df if is_main_user else self.friends_df

        places_enthusiasm = []
        for place, sentiment in zip(user_df['places'], user_df['sentiment']):
            for p in place:
                places_enthusiasm.append((p, round(sentiment, 2), 1))

        df = pd.DataFrame(places_enthusiasm, columns=['places', 'sentiment', 'frequency'])
        df = df.groupby('places').agg({'sentiment': 'mean', 'frequency': 'sum'}).reset_index() 

        if is_main_user:
            self.user_places_df = df
        else:
            self.friends_places_df = df

    def get_most_visited_places(self, is_main_user=True):
        """
        Gets the user's information on the places they visited.
        """
        user_df = self.user_places_df if is_main_user else self.friends_places_df
        
        user_df = user_df.sort_values(by=['frequency'], ascending=False, ignore_index=True)
        
        user_df = user_df.head(3)
        return [(place, frequency) for place, frequency in zip(user_df['places'], user_df['frequency'])]

    def get_most_enthusiastic_places(self, is_main_user=True):
        """
        Gets the user's top three places that they were most enthusiastic about.
        """
        user_df = self.user_places_df if is_main_user else self.friends_places_df
        
        user_df = user_df.sort_values(by=['sentiment'], ascending=False, ignore_index=True)
        user_df = user_df.head(3)

        return [(place, sentiment) for place, sentiment in zip(user_df['places'], user_df['sentiment'])]

    def get_most_visited_cities(self, is_main_user=True):
        """
        Gets the user's top three most visited cities.
        """
        user_df = self.user_df if is_main_user else self.friends_df

        cities_freq = user_df['cities'].value_counts().to_dict()

        sorted_cities = sorted(cities_freq.items(), key=lambda item: item[1], reverse=True)
        
        return sorted_cities[0:3]
    
    def get_avg_rating(self, is_main_user=True):
        """
        Gets and calculates the user's average rating given (1 to 5-star scale).
        """
        user_df = self.user_df if is_main_user else self.friends_df

        return round(user_df['ratings'].mean(), 2)
        
    def get_recent_reviews(self):
        """
        Gets the three reviews that the user most recently wrote.
        """
        return self.user_df['reviews'].tolist()[0:3]

    def get_enthusiasm_score(self, is_main_user=True):
        """
        Gets and calculates the user's enthusiasm score (1 to 10-point scale) based on sentiment analysis.
        """
        user_df = self.user_df if is_main_user else self.friends_df

        return round(user_df['sentiment'].mean(), 2)

    def scrape_basic_info(self):
        """
        Scrapes the user's basic information (e.g. name, hometown, total reviews).
        """
        address = "https://www.yelp.com/user_details_reviews_self?userid={}".format(self.user_id)
        soup = BeautifulSoup(requests.get(address).text, 'lxml')

        user_dict = {}
        user_dict["name"] = soup.find('div', {'class': "user-profile_info arrange_unit"}).find("h1").string
        user_dict["hometown"] = soup.find('div', {'class': "user-profile_info arrange_unit"}).find("h3").string
        user_dict["total reviews"] = int(soup.find('li', {'class': "review-count"}).find("strong").string)
        user_dict["total friends"] = int(soup.find('li', {'class': "friend-count"}).find("strong").string)
        user_dict["profile picture"] = soup.find('img', {'class': "photo-box-img"}).attrs['src']
        logging.info("Scraped basic user information")

        parse_only = SoupStrainer(attrs={"class": "user-display-name js-analytics-click"})
        friends_address = "https://www.yelp.com/user_details_friends?userid={}".format(self.user_id)
        soup = BeautifulSoup(requests.get(friends_address).text, 'lxml', parse_only=parse_only)

        friends = soup.findAll("a", {"class": "user-display-name js-analytics-click"})
        user_dict['friends'] = [friend['href'].split("=")[1] for friend in friends]
        logging.info("Scraped friend IDs")
        
        self.user_dict = user_dict

        return user_dict

    def scrape_review_info(self, user_id=None, is_main_user=True):
        """
        Scrapes the user's information on the reviews they wrote (e.g. content, location, sentiment).
        """
        user_id = self.user_id if is_main_user else user_id
        print(user_id)

        parse_only = SoupStrainer(attrs={'class': ["review-count", "review"]})
        address = "https://www.yelp.com/user_details_reviews_self?userid={}".format(user_id)
        soup = BeautifulSoup(requests.get(address).text, 'lxml', parse_only=parse_only)

        total_reviews = int(soup.find("strong").string) if is_main_user else 1
        
        user_df = pd.DataFrame()
        
        num_pages = math.ceil(total_reviews/10.)  # get number of pages with review content
            
        for page in range(num_pages):  # loop through all pages with reviews
            
            if page != 0:
                parse_only = SoupStrainer(attrs={'class': "review"})
                address = (("https://www.yelp.com/user_details_reviews_self?userid={}&rec_+"
                                  "pagestart={}0")).format(user_id, page)
                soup = BeautifulSoup(requests.get(address).text, 'lxml', parse_only=parse_only)
            
            reviews = soup.find_all('p', {'lang': "en"}) if is_main_user else [soup.find('p', {'lang': "en"})]
            
            user_df['reviews'] = [review.text for review in reviews]

            places = soup.find_all('span', {'class': "category-str-list"}, 'a') if is_main_user else [soup.find('span', {'class': "category-str-list"}, 'a')]
            user_df['places'] = [[p.strip() for p in place.text.split(",")] for place in places]

            locations = soup.find_all("address") if is_main_user else [soup.find("address")]
            user_df['locations'] = [[l.strip() for l in location.contents if isinstance(l, str)] for location in locations]

            user_df['cities'] = user_df['locations'].apply(lambda location: location[1][0:-6] if len(location) == 2 else location[0][0:-6])

            ratings = soup.find_all(title=re.compile("star rating")) if is_main_user else [soup.find(title=re.compile("star rating"))]
            user_df['ratings'] = [float(rating['title'][0:3]) for rating in ratings]

            user_df['sentiment'] = user_df['reviews'].apply(lambda review: 5 * (self.sentiment_client.analyze_sentiment(
            document=types.Document(content=review, type=enums.Document.Type.PLAIN_TEXT)).document_sentiment.score + 1))
        
        if is_main_user:
            self.user_df = user_df
            # logging.info("Scraped user reviews")
        else: 
            return user_df 

    def scrape_all_info(self):
        """
        Driver for scraping all user's data and their friends' data.
        """
        self.scrape_basic_info()
        self.scrape_review_info()
        self.get_places_info()

        num = 30
        for i in self.user_dict['friends'][:num]:
            df = self.scrape_review_info(i, False)
            self.friends_df = self.friends_df.append(df)
        
        logging.info("Scraped friend reviews")
        self.get_places_info(False)  

    def to_string(self):
        """
        Returns the user's data in a nicely formatted string.   
        """ 
        self.scrape_all_info()

        result = ""  # accumulate data results
    
        result += ("\n***User Data:***\n")
        result += ("""name: {}\nhometown: {}\ntotal friends: {}\ntotal reviews: {}\n\n""").format(
            self.get_name(), self.get_hometown(), self.get_total_friends(), self.get_total_reviews())

        result += ("What places did you visit the most? {}\n").format(self.get_most_visited_places())        
        result += ("What places were you most enthusiastic about? {}\n").format(
                   self.get_most_enthusiastic_places())
        result += ("What cities did you visit the most? {}\n").format(self.get_most_visited_cities())            
        result += ("average rating: {} out of 5 stars\n").format(self.get_avg_rating()) 
        result += ("enthusiasm score: {} out of 10\n\n").format(self.get_enthusiasm_score())     
        
        result += ("recent reviews:\n")
        for review in self.get_recent_reviews():
            result += "\t" + review + "\n"
        
        result += ("\n***Friend Data:***\n")
        result += ("What places did your friends visit the most? {}\n").format(self.get_most_visited_places(False))
        result += ("What places were your friends most enthusiastic about? {}\n").format(
                   self.get_most_enthusiastic_places(False))
        result += ("What cities did your friends visit the most? {}\n").format(self.get_most_visited_cities(False))
        result += ("average rating: {} out of 5 stars\n").format(self.get_avg_rating(False)) 
        result += ("enthusiasm score: {} out of 10\n\n").format(self.get_enthusiasm_score(False))
        
        return result
        
if __name__=='__main__':    
    parser = argparse.ArgumentParser()
    parser.add_argument("-user_id")
    args = parser.parse_args()

    test1 = YelpUserProfile("OuEBqrnNkhcelQ3to9HWMw")
    print(test1.to_string())
     
    # test2 = YelpUserProfile("Tq43waynkFPrcfxxtOySXA")
    # print(test2.toString())
    
    # test3 = YelpUserProfile("KnYdK3wBlp-ZSDeBClbmqg")
    # print(test3.getProfilePic())