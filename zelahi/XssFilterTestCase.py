import html

test = html.Xssfilter()

##
# @brief This class tests the html.py file
class Testhtml(unittest.TestCase):
	def test_init(self):
		# Initialization is already tested in setup
		pass
	## @brief test to ensure comments are passed successfully
	def test_handleComment(self):
		comment =  "After testing this should be made into a comment"
		test.handleComment(comment)
	def test_escapeData(self):
		notEscaped = "This string should not change"
		escapeThisText = "<>!!There should be no lt or gt signs"
		test.escapeData(notEscaped) #This string should not be escaped
		test.escapeData(escapeThisText) #This string should be escaped
	def test_urlIsAcceptable(self):
		unacceptableURL = "http://www.myurl.com"
		acceptableURL = "https://www.myurl.com"
		test.urlIsAcceptable(unacceptableURL) #should return false
		test.urlIsAcceptable(acceptableURL) #should return true
	def test_handleEndTag(self):
		myEndTag = "</End tags are removed>"
		attribute = "html"
		test.handleEndTag(tag,attribute)
	def test_unknownEndTag(self):
		myEndTag = "</This unknown End tag should be removed>"
		test.unknownEndTag(myEndTag)
	def test_handleStartTag(self):
		myStartTag = "<script>"
		attribute = "html"
		test.handleStartTag(myStartTag, attribute, method)
	def test_unknownStartTag(self):
		myStartTag = "<This is an unknown Start tag"
		attribute = "html"
		test.unknownStartTag(myStartTag, attribute)
	def print_result(self):
		print("The results of the test are:")
		print(test.result)





