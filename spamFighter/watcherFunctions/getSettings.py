import yaml
import praw
import prawcore

class retrieve(object):

	def __init__(self, praw_reddit, subreddit):
		# try to get subreddit settings from wiki
		try:
			sub_settings = praw_reddit.subreddit(subreddit).wiki['spam_watcher'].content_md
			#try to parse the yaml for a whitelist
			try:
				self.whitelist = yaml.load(sub_settings)['domain_whitelist']
			except KeyError:
				self.whitelist = []
		except prawcore.exceptions.NotFound:
			print('WARNING: settings wiki not found')
			self.whitelist = []
		except prawcore.exceptions.Forbidden:
			print('WARNING: the bot does not have permission to see the wiki')
			self.whitelist = []
