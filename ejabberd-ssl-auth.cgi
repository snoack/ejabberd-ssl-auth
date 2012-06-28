#!/usr/bin/env python

import os
import re
import cgi
import string
import random
from subprocess import Popen, call, PIPE

HOST = 'localhost'
EJABBERDCTL = '/usr/sbin/ejabberdctl'
ADMIN_URL = 'http://%s:5280/admin/' % HOST

PASSWORD_CHARS = string.letters + string.digits
PASSWORD_LENGTH = 12

VCARD_FIELDS = (
	('full-name',         ('FN',)),
	('first-name',        ('N', 'GIVEN')),
	('last-name',         ('N', 'FAMILY')),
#	('nickname',          ('NICKNAME')),
#	('url',               ('URL',)),
#	('street-address',    ('ADR', 'STREET')),
#	('extended-address',  ('ADR', 'EXTADD')),
#	('locality',          ('ADR', 'LOCALITY')),
#	('region',            ('ADR', 'REGION')),
#	('postal-code',       ('ADR', 'PCODE')),
#	('country',           ('ADR', 'CTRY')),
	('telephone',         ('TEL', 'NUMBER')),
	('email',             ('EMAIL', 'USERID')),
	('organization',      ('ORG', 'ORGNAME')),
	('organization-unit', ('ORG', 'ORGUNIT')),
	('job-title',         ('TITLE',)),
#	('role',              ('ROLE',)),
	('birthday',          ('BDAY',)),
#	('description',       ('DESC',)),
)

X509_FIELDS = {
	'full-name':         'CN',
	'email':             'Email',
	'organization':      'O',
	'organization-unit': 'OU',
}

CSS = '''\
html,body {
  background: white;
  margin: 0;
  padding: 0;
  height: 100%;
}

#container {
  padding: 0;
  margin: 0;
  min-height: 100%;
  height: 100%;
  margin-bottom: -30px;
}

#header h1 {
  width: 100%;
  height: 55px;
  padding: 0;
  margin: 0;
  background: transparent url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAYAAAA3BAMAAADdxCZzAAAAAXNSR0IArs4c6QAAAB5QTFRF1nYO/ooC/o4O/pIS/p4q/q5K/rpq/sqM/tam/ubGzn/S/AAAAEFJREFUCNdlw0sRwCAQBUE+gSRHLGABC1jAAhbWAhZwC+88XdXOXb4UlFArSmwN5ekdJY2BkudEec1QvrVQ/r3xOlK9HsTvertmAAAAAElFTkSuQmCC);
}

#header h1 a {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 55px;
  padding: 0;
  margin: 0;
  background: transparent url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAVcAAAA3CAMAAACPbPnEAAAAAXNSR0IArs4c6QAAAEtQTFRFcTIA1XcE/YsA/40E/pIH/JYc/5kg/54i/KIu/6U6/apE/61H/61P/bFX/7Vh/bda/rpq/L5s/8J2/cJ8/8qI/86Y/9aj/9mt/+bJ7EGiPwAAAZRJREFUeNrt28lug0AQhGHajrPv+/s/aVwpDlgE0gQ3tqO/DhxihMg33VJ7JmmCVKSJlVJ4bZQ93Jl/zjJv+8tzcMUVV1xxLXIlRfPAZptYrbf5YeW618PWyvG8w/g9ZwquuJ6Y6+bbdY0rrifhSmrmgUulVXbVDq3H39Zy6Cf9+8c7JNM/mXeY8+SMRmuIK6644oprkSupmQdulLhQdup1qJKmrmWmVpb5NN9LUyddu7nnLYkrrrjiimuVK6mZB+6VuFbiXJk8v/bnv0PVa+Yd5tdr/x7vCfqbgPsfV1xxxRXXKldSMw+8KPGgxJWyU7WZE538p0vOr/lOm/q7dPf+bOVKvVXiUcEVV1xxxbXMldTMA29KPCtxp7T6XpvxE6/9nm/l987mnG9l5u/8jO4Ot9uTEq8KrrjiiiuuZa6kZh74UFpli3sO61btMfyHyWGv/RMs7wB67ne32/BdwRVXXHHFtcyV1MwDn0qrbHHvyPT/Dsarla/R/1GpQydYPhf0bqC/A7jz7YkrrrjiimuVK6nIF5dWoNvcLcs/AAAAAElFTkSuQmCC) no-repeat;
  display: block;
  text-indent: -700em;
}

#navigation ul {
  position: absolute;
  top: 65px;
  left: 0;
  padding: 0 1px 1px 1px;
  margin: 0;
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 8pt;
  font-weight: bold;
  border-top: 1px solid #d47911;
  width: 17em;
}

#navigation ul li {
  list-style: none;
  margin: 0;
  text-align: left;
  display: inline;
}

#navigation ul li a {
  margin: 0;
  display: block;
  padding: 3px 6px 3px 9px;
  border-left: 1em solid #ffc78c;
  border-right: 1px solid #d47911;
  border-bottom: 1px solid #d47911;
  background: #ffe3c9;
  text-decoration: none;
}

#navigation ul li a:link {
  color: #844;
}

#navigation ul li a:visited {
 color: #766;
}

#navigation ul li a:hover {
  border-color: #fc8800;
  color: #FFF;
  background: #332;
}

ul li #navhead a {
  text-align: center;
  border-top: 1px solid #d47911;
  border-bottom: 2px solid #d47911;
  background: #FED6A6;
}

#lastactivity li {
  font-weight: bold;
  border: 1px solid #d6760e;
  background-color: #fff2e8;
  padding: 2px;
  margin-bottom: -1px;
}

input {
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 10pt;
  border: 1px solid #d6760e;
  color: #723202;
  background-color: #fff2e8;
  vertical-align: middle;
  margin-bottom: 0px;
  padding: 0.1em;
}

input[type=submit] {
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 8pt;
  font-weight: bold;
  color: #ffffff;
  background-color: #fe8a00;
  border: 1px solid #d6760e;
}

input[disabled] {
	opacity: 0.5;
}

h1 {
  color: #000044;
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 14pt;
  font-weight: bold;
  text-align: center;
  padding-top: 2px;
  padding-bottom: 2px;
  margin-top: 0px;
  margin-bottom: 0px;
}

#content a:link {
  color: #990000; 
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 10pt;
  font-weight: bold;
  text-decoration: underline;
}
#content a:visited {
  color: #990000;  
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 10pt;
  font-weight: bold;
  text-decoration: underline;
}
#content a:hover {
  color: #cc6600;  
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 10pt;
  font-weight: bold;
  text-decoration: underline;
}

#content {
  font-family: Verdana, Arial, Helvetica, sans-serif; 
  font-size: 10pt;
  padding-left: 17em;
  padding-top: 5px;
}'''


def get_value_from_cert(name):
	if name in ('first-name', 'last-name'):
		cn = os.environ.get('SSL_CLIENT_S_DN_CN')
		if not cn:
			return ''
		m = re.match(r'(.+?) +((?:[a-z]|Graf).*|\S+)$', cn)
		if not m:
			return ''

		if name == 'first-name':
			return m.group(1)
		if name == 'last-name':
			return m.group(2)
	
	try:
		return os.environ['SSL_CLIENT_S_DN_' + X509_FIELDS[name]]
	except KeyError:
		return ''

def is_registered(username):
	process = Popen([EJABBERDCTL, 'registered_users', HOST], stdout=PIPE)
	return username.lower() in (line.strip().lower() for line in process.stdout)

def generate_random_password():
	return  ''.join(random.choice(PASSWORD_CHARS) for i in xrange(PASSWORD_LENGTH))

print 'Content-Type: text/html; charset=utf-8'
print

username = os.environ['SSL_CLIENT_S_DN_Email'].split('@')[0]
jid = '%s@%s' % (username, HOST)
password = None

has_account = is_registered(username)
action = 'Reset Password' if has_account else 'Create Account'

if os.environ['REQUEST_METHOD'] == 'POST':
	password = generate_random_password()

	if has_account:
		call([EJABBERDCTL, 'change-password', username, HOST, password])
	else:
		call([EJABBERDCTL, 'register', username, HOST, password], stdout=open(os.devnull, 'wb'))

		form = cgi.FieldStorage()
		for name, vCard in VCARD_FIELDS:
			val = get_value_from_cert(name) or form.getfirst(name)

			if not val:
				continue

			cmd = 'set-vcard' + ('' if len(vCard) == 1 else '2')
			call((EJABBERDCTL, cmd, username, HOST) + vCard + (val,))

print '<!DOCTYPE html>'
print '<html>'
print '<head>'
print '<title>ejabberd %s</title>' % action
print '<style type="text/css">'
print CSS
print '</style>'
print '</head>'
print '<body>'
print '<div id="container">'
print '<div id="header">'
print '<h1><a href="/"></a></h1>'
print '</div>'
print '<div id="navigation">'
print '<ul>'
print '<li><div id="navhead"><a href="/">ejabberd</a></div></li>'
print '<li><div id="navitem"><a href="/">%s</a></div></li>' % action
if ADMIN_URL:
	print '<li><div id="navitem"><a href="%s">Admin</a></div></li>' % ADMIN_URL
print '</ul>'
print '</div>'
print '<div id="content">'
print '<h1>%s</h1>' % action

if os.environ['REQUEST_METHOD'] == 'POST':
	if has_account:
		print '<p>You have successfully reset your password. Use the ',
		print 'JID and Password below to log into your XMPP client ',
		print '(e.g. <a href="http://www.pidgin.im/">Pidgin</a>).</p>'
	else:
		print '<p>Congratulations, you have successfully created your XMPP ',
		print 'account. Use the JID and Password below to log into your XMPP ',
		print 'client (e.g. <a href="http://www.pidgin.im/">Pidgin</a>).</p>'

	print '<table>'
	print '<tr><td>JID:</td><td>%s</td></tr>' % jid
	print '<tr><td>Password:</td><td>%s</td></tr>' % password
	print '</table>'
else:
	print '<form method="post">'

	if has_account:
		print '<p>Your JID is <strong>%s</strong>. If you have ' % jid,
		print 'forgotten your password, use the button below.</p>'
	else:
		print '<table>'
		for name, _ in VCARD_FIELDS:
			value = get_value_from_cert(name)

			print '<tr>'
			print '<td>%s:</td>' % name.replace('-', ' ').title()
			print '<td><input type="text" name="%s" value="%s"' % (name, value),
			if value:
				print ' disabled="disabled"',
			print '></td>'
			print '</tr>'
		print '</table>'
		print '<br>'

	print '<input type="submit" value="%s">' % action
	print '</form>'

print '</div>'
print '</div>'
print '</body>'
print '</html>'
