# Reddit Spam Fighter

## About

This bot reports posts from users posting a domain or media channel too often. You can add or remove your subreddit by messaging the bot, and it has a wiki configurable domain whitelist.

## Adding to Your Subreddit

To add or remove the bot to your subreddit, send a message to **/u/spam_watcher** with the message title being the subreddit, and the message body as either `add` or `remove`. You must be a moderator of the subreddit to add or remove the bot.  

To configure the whitelist, create a wiki called **spam_watcher** on your subreddit, and then add the yaml formatted line `domain_whitelist: ['domain1.com','domain2.com', 'etc.']`. This whitelist only applies to the **domain spam** bot. Because of this it's good to include general media hosting sources, such as youtube, since those are taken care of by the media spam bot.

## Spam Removal Conditions

- If a user has < 5 posts, ignore
- if a user has 5-9 posts, remove if percentage >= 50
- if a user has >= 10 posts, remove if percentage >= 25
