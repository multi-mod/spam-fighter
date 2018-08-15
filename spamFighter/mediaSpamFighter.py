import praw
import prawcore
from collections import deque
from spamFighter.watcherFunctions import announce, spamCheck, getSettings
import yaml

class mediaSpam(object):
	
	def __init__(self):
		self.log = {}

	def checkMatch(self, submitted_channel, submitted_domain, post):
		# defining matching or special case domains
		soundcloud = set(['m.soundcloud.com', 'soundcloud.com'])
		youtube = set(['youtube.com', 'youtu.be', 'm.youtube.com'])
		facebook = set(['facebook.com'])
		# check for channel matches for soundcloud
		if post.domain == 'm.soundcloud.com' and submitted_domain in soundcloud:
			try:
				# grab the channel name from the url
				channel = post.url.split('/')[3]
				# check if the channel is the submitted channel
				if channel == submitted_channel: return True
				else: return False
			except Exception:
				return False
		# check for a facebook channel
		elif post.domain in facebook and submitted_domain in facebook:
			try:
				# grab the channel name from the url
				channel = post.url.split('/')[3]
				# check of the channel is the submitted channel
				if channel == submitted_channel: return True
				else: return False
			except Exception:
				return False
		# check for a youtube channel
		elif submitted_domain in youtube and post.domain in youtube:
			try:
				# try to grab the youtube channel
				channel = post.media['oembed']['author_name']
				# check if the channel is the submitted channel
				if channel == submitted_channel: return True
				else: return False
			except (KeyError, TypeError):
				return False
		# domain not listed above and doesn't match submitted domain
		elif post.domain != submitted_domain:
			return False
		# domain not listed above but matches submitted domain
		else:
			try:
				# try to grab the media channel
				channel = post.media['oembed']['author_name']
				# check if the channel is the submitted channel
				if channel == submitted_channel: return True
				else: return False
			except (KeyError, TypeError):
				return False

	def parseMediaPosts(self, reddit_praw, subreddit, postNumber, mode):
		# get subreddit settings (not used for mediaSpamFighter atm)
		settings = getSettings.retrieve(reddit_praw, subreddit)
		# grab posts from the subreddit
		posts = [post for post in reddit_praw.subreddit(subreddit).new(limit=int(postNumber))]
		# start checking the submitted posts
		for post in posts:
			# check if post has been looked at already
			if self.logged(subreddit, post.id, postNumber): continue
			print("checking: " + post.title)
			# skip self posts
			if post.is_self: continue
			# get the post domain
			domain = post.domain
			# check if the domain has the channel in the url
			if domain in set(['m.soundcloud.com', 'facebook.com']):
				# if channel in url grab channel name
				channel = post.url.split('/')[3]
			else:
				try:
					# for other posts try grabbing the channel name
					channel = post.media['oembed']['author_name']
				except (KeyError, TypeError):
					continue
			try:
				# try getting the submissions from the author
				author_submissions = [x for x in post.author.submissions.new(limit=1000)]
			except prawcore.exceptions.Forbidden:
				# go to next post if user is suspended
				print('+++USER SUSPENDED+++')
				continue
			except prawcore.exceptions.NotFound:
				# go to next post if user is deleted or shadow banned
				print('+++USER NOT FOUND+++')
				# check whether to report the post first before continuing
				if mode != 'announce':
					post.report(reason = 'spamer_watcher: user not found, check post')
				continue
			# get total submissions from user
			total_submissions = len(author_submissions)
			# go to next post if submitter has less than 5 posts
			if total_submissions < 5: continue
			# look for channels matching the submitted channel in the author's submission history
			matching_channels = [x for x in author_submissions if self.checkMatch(channel, domain, x)]
			# get percentage of posts where they submitted channel
			perc = round((len(matching_channels) / len(author_submissions)) * 100)
			if perc < 25: continue
			# check if the user is spamming channel
			if spamCheck.checkForSpam(total_submissions, perc):
				announce.spamNotification(post.author.name, post.domain, perc, channel)
				# remove post if mode set to remove
				if mode == 'remove': post.mod.remove(spam=False)
				# report post if mode is set to report
				elif mode == 'report':
					report_reason = 'media spam; percentage: ' + str(perc)
					post.report(reason = report_reason)
				else: continue

	def logged(self, subreddit, postID, postNum):
		# start a log for each subreddit
                if subreddit not in self.log:
                        self.log[subreddit] = deque(maxlen=int(postNum)+50)
		# check if post has been looked at already
                if postID in self.log[subreddit]:
                        return True
		# add post to log if it hasn't been looked at
                else:
                        self.log[subreddit].append(postID)
                        return False

