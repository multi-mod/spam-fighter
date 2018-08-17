def checkForSpam(submissionNumber, lowerPercentage, upperPercentage, submissionPercentage):
	# return spam if submission number is > 10 with a percentage above upperPercentage
	if int(submissionNumber) > 10 and int(submissionPercentage) >= int(upperPercentage):
		return True
	# return spam if submission number is > 5 and < 10 wth a percentage above lowerPercentage
	elif 5 < int(submissionNumber) < 10 and int(submissionPercentage) >= int(lowerPercentage):
		return True
	# return not spam if above conditions for spam not met
	else:
		return False
