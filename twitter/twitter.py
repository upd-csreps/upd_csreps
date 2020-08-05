import tweepy
import time

auth = tweepy.OAuthHandler('ZY8thfigA73kdhqeE0XnljKkH', 'jp6NAhTswXBISbl9Ja1MITUKqmTn2GpxzQlNimLer73bU1xxtu')
auth.set_access_token('865979538060197888-8Kb3cRj5idBkF80fV32c4hsxKt35Ro5', 'r9u2S1DbM8wWwOl6Oo9F7Id1blyzyVZBs7XaMZvSSOZb6')

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

print("Updating..")
api.update_status('Twitter automation test. At service - CS Reps 1920.')
print("Done")