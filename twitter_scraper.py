import requests, datetime, time
import argparse
class TwitterScraper:
    API_HEADERS = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
        'x-csrf-token': '0'
    }

    def __init__(self, hashtag):
        self.hashtag = hashtag

    def set_params(self, scroll_value):
        self.params = (
            ('include_profile_interstitial_type', '1'),
            ('include_blocking', '1'),
            ('include_blocked_by', '1'),
            ('include_followed_by', '1'),
            ('include_want_retweets', '1'),
            ('include_mute_edge', '1'),
            ('include_can_dm', '1'),
            ('include_can_media_tag', '1'),
            ('skip_status', '1'),
            ('cards_platform', 'Web-12'),
            ('include_cards', '1'),
            ('include_ext_alt_text', 'true'),
            ('include_quote_count', 'true'),
            ('include_reply_count', '1'),
            ('tweet_mode', 'extended'),
            ('include_entities', 'true'),
            ('include_user_entities', 'true'),
            ('include_ext_media_color', 'true'),
            ('include_ext_media_availability', 'true'),
            ('send_error_codes', 'true'),
            ('simple_quoted_tweet', 'true'),
            ('q', self.hashtag),
            ('tweet_search_mode', 'live'),
            ('count', '20'),
            ('query_source', 'recent_search_click'),
            ('cursor', scroll_value),
            ('pc', '1'),
            ('spelling_corrections', '1'),
            ('ext', 'mediaStats,highlightedLabel'),
        )

    # Thanks Todd Birchard for his awesome json extraction method
    # https://hackersandslackers.com/extract-data-from-complex-json-python/
    def json_extract(self, obj, key):
        """Recursively fetch values from nested JSON."""
        arr = []

        def extract(obj, arr, key):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        values = extract(obj, arr, key)
        return values

    def get_xguest_token(self):
        guest_token_header = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        }

        r = requests.post("https://api.twitter.com/1.1/guest/activate.json", headers=guest_token_header)
        return r.json()["guest_token"]

    def list_reviews(self):
        print('---------------------------------Tweets Start----------------------------------------------')
        self.set_params("")
        #We need a guest token to search tweets without having a twitter account.
        #Then we'll add that guest token to the header of search request
        self.API_HEADERS["x-guest-token"] = self.get_xguest_token()
        #Initate tweets to an empty list
        tweets = {"globalObjects": {}}
        while (len(tweets) > 0):
            try:
                response = requests.get('https://twitter.com/i/api/2/search/adaptive.json', headers=self.API_HEADERS,
                                        params=self.params)
                #The tweets are located in ["globalObjects"]["tweets"] key
                tweets = response.json()["globalObjects"]["tweets"]
                #I'll also get the screen name of the user who posted that tweet. This is located in ["globalObjects"]["users"] key
                users = response.json()["globalObjects"]["users"]
                #Twitter generates scroll values on the fly and it's located in a key called "value".
                #Therefore we need to search this value until we find it.
                cursor_scroll_value = self.json_extract(response.json(), 'value')[1]
                #set this value in the params for request
                self.set_params(cursor_scroll_value)
                for tweet in tweets:
                    user_id = tweets[tweet]["user_id"]
                    #Get formatted tweet date
                    tweet_date = datetime.datetime.strftime(
                        datetime.datetime.strptime(tweets[tweet]["created_at"], '%a %b %d %H:%M:%S +0000 %Y'),
                        '%Y-%m-%d')
                    #Print tweets
                    print("Account Name:", users[str(user_id)]["screen_name"], "Tweet:", tweets[tweet]["user_id"],
                          tweets[tweet]["full_text"], "Tweet Date:", tweet_date)
            except:
                #If anything goes wrong, I'll wait for 10 secs and get a new guest token
                time.sleep(10)
                self.API_HEADERS["x-guest-token"] = self.get_xguest_token()

        print('---------------------------------Tweets End-------------------------------------------------')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for a hashtag')
    parser.add_argument('--hashtag', required=True,
                        help='Please enter a hashtag that starts with # symbol')
    args = parser.parse_args()
    hashtag = args.hashtag
    ts = TwitterScraper(hashtag)
    ts.list_reviews()
