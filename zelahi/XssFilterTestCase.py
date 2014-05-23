import html

test = html.Xssfilter()
notEscaped = "This string should not change"
comment =  "After testing this should be made into a comment"
escapeThisText = "<>!!There should be no lt or gt signs"
unacceptableURL = "http://www.myurl.com"
acceptableURL = "https://www.myurl.com"
##
class TestDB(unittest.TestCase):
	def test_init(self):
		# Initialization is already tested in setup
		pass
	## @brief test to ensure comments are passed successfully
	def test_handleComment(self, comment):
		test.handleComment(comment)
	def test_escapeData(self, data):
		test.escapeData(notEscaped) #This string should not be escaped
		test.escapeData(escapeThisText) #This string should be escaped
	def test_urlIsAcceptable(self):
		test.urlIsAcceptable(unacceptableURL) #should return false
		test.urlIsAcceptable(acceptableURL) #should return true


