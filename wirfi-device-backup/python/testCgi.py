#!/usr/bin/env python

# Import modules for CGI handleing
import cgi, cgitb

# Create instance of FieldStorage
form = cgi.FieldStorage()

# Get data from fields
first_name = form.getvalue('first_name')
last_name = form.getvalue('last_name')

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>WiRFi Settings</title>"
print "</head>"
print "<body>"
print "<h2>hello %s %s lubadubadubdub!</h2>" % (first_name, last_name)
print "<br>"
print "</body>"
print "</html>"
