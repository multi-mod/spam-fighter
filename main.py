import praw
import prawcore
import yaml
from spamFighter import domainSpamFighter, mediaSpamFighter
from mailControl import checkMail
import time

class spamFighter(object):

	def __init__(self):
		self.checkers_created = False	

	def getSettings(self):
		### open global config file in yaml format
		with open('config') as config:
			self.settings = yaml.safe_load(config)

	def initializePraw(self):
		### initialize praw reddit instance
		self.reddit = praw.Reddit(
			client_id = self.settings['credentials']['client_id'],
			client_secret = self.settings['credentials']['client_secret'],
			user_agent = self.settings['credentials']['user_agent'],
			username = self.settings['credentials']['username'],
			password = self.settings['credentials']['password']
                )

	def fightSpam(self, subreddits):
		### check if spam fighter class initialized
		# create dictionary with initialized classes if this is the first time running the script
		if not self.checkers_created:
			self.spam_checkers = {
				'domain_spam': {subreddit: domainSpamFighter.domainSpam() for subreddit in subreddits},
				'media_spam': {subreddit: mediaSpamFighter.mediaSpam() for subreddit in subreddits}
			}
			self.checkers_created = True
		### update subreddit list if this is not the first time running the script
		else:
			# check for any new subreddits
			new_subreddits = [s for s in subreddits if s not in self.spam_checkers['domain_spam']]
			# if there are any new subreddits, initialize a class instance for them
			if len(new_subreddits) > 0:
				print('new subreddits detected: ' + ', '.join(new_subreddits))
				for new_subreddit in new_subreddits:
					self.spam_checkers['domain_spam'][new_subreddit] = domainSpamFighter.domainSpam()
					self.spam_checkers['media_spam'][new_subreddit] = mediaSpamFighter.mediaSpam()
			# check for subreddits that should be removed
			remove_subreddits = [s for s in self.spam_checkers['domain_spam'] if s not in subreddits]
			# if there are any subreddits to be removed, delete their class instance from the dictionary
			if len(remove_subreddits) > 0:
				print('subreddits to be removed: ' + ', '.join(remove_subreddits))
				for remove_subreddit in remove_subreddits:
					del(self.spam_checkers['domain_spam'][remove_subreddit])
					del(self.spam_checkers['media_spam'][remove_subreddit])				
	
		### perform domain and media spam checks for each subreddit in settings
		for subreddit in subreddits:
			# check for domain spam
			print('.....checking /r/' + subreddit + ' for domain spam.....') 
			self.spam_checkers['domain_spam'][subreddit].parsePosts(self.reddit, subreddit, self.settings['posts'], self.settings['mode'])
			# check for media channel spam
			print('.....checking /r/' + subreddit + ' for media spam.....')
			self.spam_checkers['media_spam'][subreddit].parseMediaPosts(self.reddit, subreddit, self.settings['posts'], self.settings['mode'])

if __name__ == "__main__":
	watcher = spamFighter()
	watcher.getSettings()
	watcher.initializePraw()
	subreddit_lister = checkMail.manageSubreddits(watcher.reddit)
	while True:
		try:
			subreddit_lister.updateSubredditList()
			watcher.fightSpam(subreddit_lister.subreddits)
			print("############# resting for 30 seconds #############")
			time.sleep(30)
		except prawcore.PrawcoreException as err:
			print('############# prawcore excpetion, resting 60 seconds ##############')
			print(err)
			time.sleep(60)
