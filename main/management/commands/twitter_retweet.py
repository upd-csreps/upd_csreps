

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import tweepy
import os
import datetime


class Command(BaseCommand):

	help = 'Retweets from important twitter handles.'

	def handle(self, *args, **options):
		auth = tweepy.OAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
		auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_SECRET_TOKEN)

		api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, timeout=15)

		previous_tweet_time = None
		twitter_handles = ["UP_ESC", "upparser"]

		for account_name in twitter_handles:
			for status in tweepy.Cursor(api.user_timeline, id=account_name, user_id=account_name).items(7):
				status = api.get_status(status.id, tweet_mode="extended")
				retweeted = False
				lacks_time = False
				is_reply = bool(status.in_reply_to_status_id)

				 #If tweet date is > 10 days from now
				too_old = ((datetime.datetime.now() - status.created_at).days > 10)

				try:
				    if (status.retweeted_status.retweeted):
				    	retweeted = True
				except AttributeError:  # Not a Retweet from Page
				    if (status.retweeted):
				    	retweeted = True

				if previous_tweet_time:
					elapsed_minutes = (previous_tweet_time - status.created_at).total_seconds()//60
					if elapsed_minutes < 90:
						lacks_time = True 

				if not (retweeted or is_reply or lacks_time or too_old):
					status.retweet()

				previous_tweet_time = status.created_at

		self.stdout.write(self.style.SUCCESS('Retweeting task complete.'))
		return
