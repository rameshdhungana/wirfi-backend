import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('device_login_credentials.cfg')
uname = config.get('deviceLoginCredentials', 'username')
pword = config.get('deviceLoginCredentials', 'password')

