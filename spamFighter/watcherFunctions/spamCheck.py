def checkForSpam(submissionNumber, percentage):
	# return not spam if percentage < 25
	if percentage < 25:
		return False
	# return spam if submission number is > 5 and < 10 wth a percentage above 50
	elif 5 < submissionNumber < 10 and percentage >= 50:
		return True
	# return spam if submission number >= 10 with a percentage >= 25
	else:
		return True
