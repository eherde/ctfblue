## @package html
# XSS Filter
#
# methods and class for removing harmless tags
#
#  This module accepts user inputs and ensures they do not contain 
#	any inputs that may be harmful to the user.  
#  

#system modules
from html.parser import HTMLParser
from cgi import escape
from urllib.parse import urlparse
from formatter import AbstractFormatter
from html.entities import entitydefs
from xml.sax.saxutils import quoteattr

##
# @brief  Removes <,>,&,:","
#
# @ param text: the text that needs to be escaped
#
# @function escape: Escapes the user input to remove malicious inputs
#
#@return text with the malicious inputs removed
def xssEscape(text):
	return escape(text, quote=True).replace(':','&#58;')


class Xssfilter(HTMLParser):
	# @brief: Create a filter to remove any malicious inputs
	#
	# @param self create a new dictionary to store attributes
	#
	# @ return a new Xssfilter object	
	def __init__(self, fmt = AbstractFormatter):
		#initialize the base class
		HTMLParser.__init__(self, fmt)
		#Create a dictionary to hold variable tags that are allowed and disallowed
		self.result = "" #result of escaping the inputs
		self.open_tags = [] 
		self.allowed_attributes = {'a':['href','title'], 'img':['src','alt'] } 
		self.allowed_schemes = ['https']
		self.permitted_tags = ['fieldset','form']
		self.requires_no_close = ['img','br','html']
	##	
	# @brief: escapes the data and removes unwanted HTML tags
	def escapeData(self,data):
		if data:
			self.result += xssEscape(data)
	##		
	# @brief: handles any character references
	def handleCharRef(self, ref):
		if len(ref) < 7 and ref.isdigit():
			self.result += '&#%s' % ref
		else:
			self.result += xssEscape('&%s' % ref)
	##
	# @brief handles any entity references 
	#
	# @param ref: a reference object
	def handleEntityRef(self, ref):
		if ref in entitydefs:
			self.result += '&%s:' % ref
		else:
			self.result += xssEscape('&%s' % ref)
	##
	# @brief removes malicious inputs from comments
	#
	# @param comment: comments passed into the function
	def handleComment(self, comment):
		if comment:
			self.result +=("<!--%s-->" % comment)
	##		
	# @brief checks start tags in scripts for malicious inputs
	#
	# @param tag: tags identified in the user's input
	# @param attrs:  Any attribute passed into the server
	def handleStartTag(self, tag, method, attrs):
		if tag not in self.permitted_tags:
			self.result += xssEscape("<%s>" % tag)
		else:
			breakTag = "<" + tag
			if tag in self.allowed_attributes:
				attrs = dict(attrs)
				self.allowed_attributes_here = \
					[i for i in self.allowed_attributes[tag] if x in attrs and len(attrs[i]) > 0]
				for attribute in self.allowed_attributes_here:
					if attribute in ['href', 'src', 'background']:
						if self.url_is_acceptable(attrs[attribute]):
							breakTag += '%s=%s"' % (attribute, attrs[attribute])
						else:
							breakTag += '%s=%s' % (xssEscape(attribute), quoteattr(attrs[attribute]))
			if breakTag == "<a" or breakTag == "<img":
				return
		breakTag += ">"
		self.result += breakTag
		self.open_tags.insert(0,tag)
	##
	# @brief removes any malicious inputs from endtags
	#
	# @param tags, attrs: Refere to comment in handleEndTag
	def handleEndTag(self, tag, attrs):
		endTag = "</%s>" % tag
		if tag not in self.permitted_tags:
			self.result += xssEscape(endTag)
		elif tag in self.open_tags:
			self.result += endTag
			self.open_tags.remove(tag)
	##
	# @brief Removes any start tags not known to the our system
	#
	# @param attributes handles any attributes passed into the server
	def unknownStartTag(self,tag,attrbutes):
		self.handleStartTag(tag,None,attrbutes)
	##
	# @brief Checks any end tags that were for which we did not account
	def unknownEndTag(self, tag):
		self.handleEndTag(tag, None)
	##
	# @brief Ensures that URLs passed are safe
	#
	# @param url: URL passed into the server
	def urlIsAcceptable(self, url):
		parsed = urlparse(url)
		return parsed[0] in self.allowed_schemes and '.' in parsed[1]
	##
	# @brief strips the strings the arguements and removes any harmful HTML or Javascript
	#
	# @param rawstring: The original string that needs to be removed
	def stripString(self, rawstring):
		self.result=""
		self.feed(rawstring)
		for endtag in self.open_tags:
			if endtag not in self.requires_no_close:
				self.result += "</%s>" % endtag
		return self.result
	##
	# @brief cleans tags of malicious inputs
	# 
	# @return Escapes the tags passed into the method
	def cleanTags(self):
		self.permitted_tags.sort()
		tg = ""
		for x in self.permitted_tags:
			tg += "<" + x
			if x in self.allowed_attributes:
				for y in self.allowed_attributes[x]:
					tg += '%s=""' % y
			tg += ">"
		return xssEscape(tg.clean_tags())