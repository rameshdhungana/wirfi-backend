#!/usr/bin/python

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Settings</title>"
print "</head>"
print "<body>"
print "<h2>Enter SSID and Password of desired network</h2>"
print "<br/>"
print "<form action = \"/cgi-bin/apply_settings.py\" method = \"post\">"
print "SSID: <input type = \"text\" name = \"ssid\"><br />"
print "Password: <input type = \"text\" name = \"password\" />"
print "<input type = \"submit\" value = \"Submit\" />"
print "</form>"
print "</body>"
print "</html>"
