# -*- coding: utf-8 -*-
import time
import twitter


class GachikoiManager:
    """
    GachikoiManager finds all GACHIKOI-tweets,
    and RT/fav them.
    """
    """
    self.LIST_ID int:
        self.LIST_ID is the id of the list containing only Hisa
    self.statuses list:
        self.statuses is the collection of tweets in the list of self.LIST_ID
    self.gachikoi_mode bool:
        self.gachikoi_mode shows if it is in Gachikoi-Mode
    self.temp_gachikoi_id int:
        self.temp_gachikoi_id is temporarily saved id of the Gachikoi tweet
    self.fav_status_ids list:
        self.fav_status_ids contains all tweets to be favorited
    self.rt_status_ids list:
        self.rt_status_ids contains all tweets to be retweeted
    """
    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token_key,
                 access_token_secret):

        self.api = twitter.Api(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token_key=access_token_key,
            access_token_secret=access_token_secret,
        )
        self.LIST_ID = 1344548869997166592
        
        self.statuses = []
        self.gachikoi_mode = False
        self.temp_gachikoi_id = None

        self.fav_status_ids = []
        self.rt_status_ids = []

    # **************
    #  ALL-IN-ONE  *
    # **************
    def execute_all(self, since_id=None, max_id=None,
                    count=100, src="list"):
        self.fetch_statuses(since_id=since_id, max_id=max_id,
                            count=count, src=src)
        self.search_fav_rt_status_ids()
        self.retweet_fascinators()
        self.favorite_gachikoi()

    # ******************
    #  FETCH STATUSES  *
    # ******************
    def fetch_statuses(self, since_id=None, max_id=None,
                       count=100, src="list"):
        if src == "list":
            self.statuses = \
                self.api.GetListTimeline(
                    list_id=self.LIST_ID,
                    since_id=since_id, max_id=max_id,
                    count=count,
                )
        elif src == "timeline":
            self.statuses = \
                self.api.GetUserTimeline(
                    screen_name="hisagrmf",
                    since_id=since_id, max_id=max_id,
                    count=count,
                )
        else:
            raise Exception(f"src={src} is not supported")
            
    
    # ******************
    #  PARSE STATUSES  *
    # ******************
    def search_fav_rt_status_ids(self):
        """
        search_fav_rt_status_ids parses
        self.statuses (list of statuses)
        to update self.fav_status_ids
        and self.rt_status_ids
        """
        self.fav_status_ids = []
        self.rt_status_ids = []
        self.gachikoi_mode = False

        for status in self.statuses:
            if self.gachikoi_mode:
                self.find_fascinator(status)
            if not self.gachikoi_mode:
                self.find_gachikoi(status)

    def find_gachikoi(self, status):
        if self.is_gachikoi(status):
            self.gachikoi_mode = True
            if not status.favorited:
                self.temp_gachikoi_id = status.id

    @staticmethod
    def is_gachikoi(status):
        text = status.text
        return ("ガチ恋" in text) and ("@" not in text)

    def find_fascinator(self, status):
        """
        [Case 1] found fascinator
            -->  save status_id to retweet list
                 (if it has yet retweeted),
                 and gachikoi status_id to fav list
                 (if it still exists)
        [Case 2] not found fascinator
            -->  just stop gachikoi-mode

        In both cases, temporarily saved gachikoi status_id 
        is trashed after the whole process.
        """
        if self.is_fascinator(status):
            if not status.retweeted:
                self.rt_status_ids.append(status.id)
            if self.temp_gachikoi_id is not None:
                self.fav_status_ids.append(self.temp_gachikoi_id)
        else:
            self.gachikoi_mode = False

        self.temp_gachikoi_id = None
        
    @staticmethod
    def is_fascinator(status):
        status_rt = status.retweeted_status
        return (status_rt is not None) and \
            (status_rt.media is not None)

    # ******************
    #  EXECUTE RT/FAV  *
    # ******************
    def retweet_fascinators(self):
        for status_id in self.rt_status_ids[::-1]:
            self.api.PostRetweet(status_id)
            time.sleep(5) # to avoid tweet restriction

    def favorite_gachikoi(self):
        for status_id in self.fav_status_ids[::-1]:
            self.api.CreateFavorite(status_id=status_id)
            time.sleep(5) # to avoid fav restriction
    
    
if __name__ == "__main__":
    pass

    # from access_keys import \
    #     CONSUMER_KEY, CONSUMER_SECRET, \
    #     ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

    # gm = GachikoiManager(
    #     consumer_key=CONSUMER_KEY,
    #     consumer_secret=CONSUMER_SECRET,
    #     access_token_key=ACCESS_TOKEN_KEY,
    #     access_token_secret=ACCESS_TOKEN_SECRET,
    # )
    
    # GachikoiManager(
    #     consumer_key=CONSUMER_KEY,
    #     consumer_secret=CONSUMER_SECRET,
    #     access_token_key=ACCESS_TOKEN_KEY,
    #     access_token_secret=ACCESS_TOKEN_SECRET,
    # ).execute_all()
