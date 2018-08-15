
def spamNotification(user, domain, percentage, channel = None):
	if channel == None:
		print(
			'+++SPAM+++ ' +
			'user: ' + user +
			'; domain: ' + domain +
			'; percentage: ' + str(percentage) + '%'
		)
	else:
		print(
			'+++SPAM+++ ' +
			'user: ' + user +
			'; domain: ' + domain +
			'; channel: ' + channel +
			'; percentage: ' + str(percentage) + '%'
		)
