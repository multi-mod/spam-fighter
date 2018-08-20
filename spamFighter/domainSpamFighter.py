import praw
import prawcore
from collections import deque
import yaml
from spamFighter.watcherFunctions import announce, spamCheck, getSettings
from urllib.parse import urlparse

class domainSpam(object):

	def __init__(self):
		self.log = {}

	def getDomain(self, praw_post):
		## check if domain is looked at further
		# look at google play links in more detail
		if praw_post.domain == 'play.google.com':
			# get the studio from the url
			domain = urlparse(praw_post.url).query.split('.')[2]
		## if domain is not looked at further just return the API domain
		else:
			domain = praw_post.domain
		## supply the domain as output
		return domain

	def parsePosts(self, praw_reddit, subreddit, postNumber, mode):
		# get subreddit whitelist
		settings = getSettings.retrieve(praw_reddit, subreddit)
		# get postNumber of posts from subreddit
		posts = [post for post in praw_reddit.subreddit(subreddit).new(limit=int(postNumber))]
		# go through each post and check for spam
		for post in posts:
			# check if post was already looked at
			if self.logged(subreddit, post.id, postNumber): continue
			# print which post is being checked
			print('checking: ' + post.title)
			# go to next post if the current post is a self post
			if post.is_self: continue
			# get the domain of the post
			post_domain = self.getDomain(post)
			# go to next post if the domain is in the whitelist
			if post.domain.lower() in set(settings.whitelist): continue
			if post.domain.lower() in set(['i.redd.it']): continue
			# get the newest 1000 posts from the author of the post
			try:
				author_submissions = post.author.submissions.new(limit=1000)
			except prawcore.exceptions.Forbidden:
				print("+++USER SUSPENDED+++")
				continue
			except prawcore.exceptions.NotFound:
				print("+++USER NOT FOUND+++")
				#check if post should be reported before continuing
				if mode != 'announce':
					post.report(reason='spam_watcher: user not found, check post')
				continue
			# get the domains from the posts the author submitted
			author_domains = [self.getDomain(x) for x in author_submissions]
			# get the total number of posts from the author up to 1000
			total_submissions = len(author_domains)
			# if the author has less than 5 submissions, go to the next post
			if total_submissions < 5: continue
			# get the percentage of posts that have the submitted domain
			perc = round((author_domains.count(post_domain) / len(author_domains)) * 100)
			# check if the post is spam
			if spamCheck.checkForSpam(total_submissions, settings.lower_percentage, settings.upper_percentage, perc):
				# print the post information if it is spam
				announce.spamNotification(post.author.name, post.domain, perc)
				# remove the post if the mode is set to remove
				if mode == 'remove': post.mod.remove(spam=False)
				# report the post if the mode is set to report
				elif mode == 'report':
					report_reason = 'domain spam; percentage: ' + str(perc) + '%'
					post.report(reason = report_reason)
				# go to next post if the current post is not spam
				else: continue

	def logged(self, subreddit, postID, postNum):
		# start log if subreddit doesn't have one yet
		if subreddit not in self.log:
			self.log[subreddit] = deque(maxlen=int(postNum)+50)
		# check if post has been looked at already
		if postID in self.log[subreddit]:
			return True
		# if post hasn't been looked at already, continue and add to log
		else:
			self.log[subreddit].append(postID)
			return False

