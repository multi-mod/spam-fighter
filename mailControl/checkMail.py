import praw
import prawcore
import os
import yaml

class manageSubreddits(object):
	
	def __init__(self, praw_reddit):
		self.reddit = praw_reddit
		# check if the subreddit list exists
		if os.path.isfile('subreddits.yaml'):
			# if the subreddit list exists load from file
			with open('subreddits.yaml') as f:
				self.subreddits = yaml.safe_load(f)
			print('existing subreddit list: ' + ', '.join(self.subreddits))
		else:
			print('no subreddits being watched yet')
			# if there is no subreddit list start from scratch
			self.subreddits = []

	def updateSubredditList(self):
		mail = self.reddit.inbox.unread()
		for m in mail:
			### get sender
			try:
				sender = m.author.name
			# go to next mail if sender account deleted, suspended, or shadow banned
			except prawcore.exceptions.NotFound:
				continue
			except prawcore.exceptions.Forbidden:
				continue
			### get subreddit from subject and check if it's an actual subreddit
			sub = m.subject
			try: 
				self.reddit.subreddit(sub).fullname
			# catch exception if subreddit doesn't exist
			except (prawcore.exceptions.Redirect, prawcore.exceptions.NotFound):
				message = '/r/' + sub + ' not found'
				print(message)
				self.reddit.redditor(sender).message('spam_watcher notification', message)
				m.mark_read()
				continue
			### check what the user wants to do with the bot
			operation = m.body.lower()
			# catch if operation is invalid
			if operation not in set(['add','remove']):
				message = operation + ' is an invalid option'
				print(message)
				self.reddit.redditor(sender).message('spam_watcher notification', message)
				m.mark_read()
				continue
			### check if sender is a moderator of the subreddit
			sender = m.author.name
			# get mods of subreddit
			subreddit_mods = [x.name for x in self.reddit.subreddit(sub).moderator()]
			# check if sender is mod
			if sender not in set(subreddit_mods):
				message = '/u/' + sender + ' is not a moderator of /r/' + sub
				print(message)
				self.reddit.redditor(sender).message('spam_watcher notification', message)
				m.mark_read()
				continue
			### add or remove subreddit from list if possible
			# subreddit not being watched and sender wants to add it
			if operation == 'add' and sub not in self.subreddits:
				self.subreddits.append(sub)
				m.mark_read()
				message = 'watcher was added to /r/' + sub
				print(message)
				self.reddit.redditor(sender).message('spam_watcher notification', message)
				modmail = '''/u/{user} asked /u/spam_watcher to start watching your subreddit\n
				This bot will report posts if a user is posting a domain or media channel too often\n
				For more information and support visit /r/spam_watcher or message /u/multi-mod\n
				To remove the bot message /u/spam_watcher with the subreddit as the title and remove as the body'''
				modmail = modmail.format(user = sender)
				self.reddit.subreddit(sub).message('spam_watcher is now watching your subreddit!', modmail)
			# subreddit already being watched and sender wants to add it
			elif operation == 'add' and sub in self.subreddits:
				m.mark_read()
				message = 'watcher is already watching /r/' + sub
				print(message)
				self.reddit.redditor(sender).message('spam_watcher notification', message)
			# subreddit is being watched and sender wants to remove it
			elif operation == 'remove' and sub in self.subreddits:
				self.subreddits.remove(sub)
				m.mark_read()
				message = 'watcher was removed from /r/' + sub
				print(message)
				self.reddit.redditor(sender).message('spam_watcher notification', message)
				modmail = '''/u/{user} told /u/spam_watcher to stop watching your subreddit\n
				For more information and support visit /r/spam-watcher or message /u/multi-mod\n
				To add the bot again message /u/spam_watcher with the subreddit as the title and add as the body'''
				modmail.format(user = sender)
				self.reddit.subreddit(sub).message('spam_watcher stopped watching your subreddit', modmail)
			# subreddit is not being watched and sender wants to remove it
			else:
				m.mark_read()
				message = 'watcher not removed because watcher was not watching /r/' + sub
				print(message)
				self.reddit.redditor(sender).message('spam_watcher notification', message)
		### write updated subreddit list to file in yaml format
		with open('subreddits.yaml', 'w') as f:
			yaml.safe_dump(self.subreddits, f)
