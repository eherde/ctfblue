#! /usr/bin/env python

from htmllib import HTMLParser
from cgi import escape
from urlparse import urlparse
from formatter import AbstractFormatter
from htmlentitydefs import entitydefs
from xml.sax.saxutils import quoteattr

#Removes <,>,&,:","
def xssEscape(text):
	return escape(text, quote=True).replace(':','&#58;')


class Xssfilter(HTMLParser):
	#initializes a dictionary to store tags allowed and not allowed
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

	#escapes the data and removes unwanted HTML tags
	def escape_data(self,data):
		if data:
			self.result += xssEscape(data)
	#handles any character references
	def handle_charref(self, ref):
		if len(ref) < 7 and ref.isdigit():
			self.result += '&#%s' % ref
		else:
			self.result += xssEscape('&%s' % ref)
	#handles any entity references 
	def handle_entityref(self, ref):
		if ref in entitydefs:
			self.result += '&%s:' % ref
		else:
			self.result += xssEscape('&%s' % ref)
	#removes malicious inputs from comments
	def handle_comment(self, comment):
		if comment:
			self.result +=("<!--%s-->" % comment)
	#removes malicious inputs from start tags
	def handle_starttag(self, tag, method, attrs):
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
	#removes any malicious inputs from endtags
	def handle_endtag(self, tag, attrs):
		endTag = "</%s>" % tag
		if tag not in self.permitted_tags:
			self.result += xssEscape(endTag)
		elif tag in self.open_tags:
			self.result += endTag
			self.open_tags.remove(tag)
	#Removes any start tags that is not known
	def unknown_starttag(self,tag,attrbutes):
		self.handle_starttag(tag,None,attrbutes)
	#Checks any end tags that were for which we did not account
	def unknown_endtage(self, tag):
		self.handle_endtag(tag, None)
	# Ensures that URLs passed are safe
	def url_is_acceptable(self, url):
		parsed = urlparse(url)
		return parsed[0] in self.allowed_schemes and '.' in parsed[1]
	#Strings the arguements and removes any harmful HTML or Javascript
	def strip_string(self, rawstring):
		self.result=""
		self.feed(rawstring)
		for endtag in self.open_tags:
			if endtag not in self.requires_no_close:
				self.result += "</%s>" % endtag
		return self.result
	#Returns a string telling the user which tags are allowed
	def clean_tags(self):
		self.permitted_tags.sort()
		tg = ""
		for x in self.permitted_tags:
			tg += "<" + x
			if x in self.allowed_attributes:
				for y in self.allowed_attributes[x]:
					tg += '%s=""' % y
			tg += ">"
		return xssEscape(tg.clean_tags())