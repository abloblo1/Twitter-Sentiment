import folium
import tweepy
import math
from textblob import TextBlob
import preprocessor as p
from geopy.geocoders import Nominatim

class Generate_GeoipMap():
    def generate_geoipmap(self, items):
        mapvar = folium.Map(location=[45.38, -121.67], zoom_start=3)
        geolocator = Nominatim(user_agent = 'tweet_plot')

        # Row number
        i = 0
        try:
            for tweet in items:
                tweet_location = p.clean(tweet.user.location)
                try:
                    location = geolocator.geocode(tweet_location)
                except:
                    location = "NULL"
                # write in excel only if location is not null
                if location != "NULL" and tweet_location != '' and location is not None:
                    # clean tweet
                    type(tweet.text)
                tweet_text = p.clean(tweet.text)[2:]
                #print(tweet_text)
                #print("\n")

                # sentiment analysis
                feelings = TextBlob(tweet_text).sentiment.polarity
                #print(feelings)
                icon = folium.Icon()
                if feelings == 0:
                    icon = folium.Icon(color='gray')
                elif (feelings > 0 and feelings <= 0.3):
                    icon = folium.Icon(color='lightgreen')
                elif (feelings > 0.3 and feelings <= 0.6):
                    icon = folium.Icon(color='green')
                elif (feelings > 0.6 and feelings <= 1):
                    icon = folium.Icon(color='darkgreen')
                elif (feelings > -0.3 and feelings <= 0):
                    icon = folium.Icon(color='lightred')
                elif (feelings > -0.6 and feelings <= -0.3):
                    icon = folium.Icon(color='red')
                elif (feelings > -1 and feelings <= -0.6):
                    icon = folium.Icon(color='darkred')
                try:
                    folium.Marker(location=[location.latitude, location.longitude], icon=icon).add_to(mapvar)
                except:
                    pass
        except tweepy.error.TweepError:
            print("Check your credentials for correctness")
        print("printed correctly")
        mapvar.save('twittermap.html')
