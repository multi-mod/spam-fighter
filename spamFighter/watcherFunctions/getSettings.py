import yaml
import praw
import prawcore

class retrieve(object):

	def __init__(self, praw_reddit, subreddit):
		### try to get subreddit settings from wiki
		try:
			sub_settings = praw_reddit.subreddit(subreddit).wiki['spam_watcher'].content_md
			# try whitelist
			try:
				self.whitelist = yaml.load(sub_settings)['domain_whitelist']
			except KeyError:
				self.whitelist = []
			# try lower percentage
			try:
				self.lower_percentage = yaml.load(sub_settings)['lower_percentage']
			except KeyError:
				self.lower_percentage = 50
			# try upper percentage
			try:
				self.upper_percentage = yaml.load(sub_settings)['upper_percentage']
			except KeyError:
				self.upper_percentage = 25
		except prawcore.exceptions.NotFound:
			print('WARNING: settings wiki not found')
			self.whitelist = []
			self.lower_percentage = 50
			self.upper_percentage = 25
		except prawcore.exceptions.Forbidden:
			print('WARNING: the bot does not have permission to see the wiki')
			self.whitelist = []
			self.lower_percentage = 50
			self.upper_percentage = 25
