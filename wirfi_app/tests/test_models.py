from django.test import TestCase
from wirfi_app.models import QueueTaskForWiRFiDevice


class testme(TestCase):
    def test_just_check(self):
        check = True
        self.assertTrue(check)


if 'username' not in form or 'password' not in form:
    redirectURL = "http://192.168.1.1/cgi-bin/login.html/"
    print
    "Content-type:text/html\r\n\r\n"
    print
    "<html>"
    print
    "<head>"
    print
    "<meta http-equiv='refresh' content='0;url=" + str(redirectURL) + "' />"
    print
    "</head>"
    print
    "</html"
else:
    print
    form_data['username'].value
    print
    form_data['password'].value

config = ConfigParser.RawConfigParser()
config.read('device_login_credentials.cfg')
uname = config.get('deviceLoginCredentials', 'username')
pword = config.get('deviceLoginCredentials', 'password')
if username == uname and password == pword:
    print
    "Content-type:text/html\r\n\r\n"
    print
    "<html>"
    print
    "<head>"
    print
    "<title>WiRFi Settings</title>"
    print
    "</head>"
    print
    "<body>"
    print
    "<h2>Login credentials: %s/%s</h2>" % (username, password)
    print
    "<br>"
    print
    "</body>"
    print
    "</html>"

