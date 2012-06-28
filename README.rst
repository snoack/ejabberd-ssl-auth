This CGI script enables users that have authentificated with an SSL client
certificate, to create an XMPP account and to reset their password at ejabberd.

The username of the created XMPP account will be the alias of the email address
given in the SSL client certificate. Information like full name and organization
will be imported from the SSL client certificate into the XMPP vCard, too.

Configuration
-------------

The script needs to be executed as the user running ejabberd. Therefore you have
to enable Apache's `suEXEC`_ mechanism. When using Debian that works like below::

	apt-get install apache2-suexec
	a2enmod suexec

Create a directory for the CGI script and copy the script into that directory.
Also make sure that both, the script and its directory is owned by ejabberd::

	mkdir /var/www/ejabberd
	cp ejabberd-ssl-auth.cgi /var/www/ejabberd
	chown -R ejabberd:ejabberd /var/www/ejabberd

Open the CGI script with your favorite editor, in order to change the constants
HOST, EJABBERDCTL and ADMIN_URL, respective your setup. Optionally you can also
modify the VCARD_FIELDS tuple, to control which vCard fields are set during
account creation::

	vim /var/www/ejabberd/ejabberd-ssl-auth.cgi

Now you have to setup the virtual host for the CGI script::

	<VirtualHost _default_:443>
		...

		SSLVerifyClient Require
		SSLOptions +StdEnvVars

		SuexecUserGroup ejabberd ejabberd
		ScriptAlias / /var/www/ejabberd/ejabberd-ssl-auth.cgi
	</VirtualHost>

The last step is optional, but when you are using ejabberd's web admin, I
recommend to secure it with SSL client certificate authentification as well.
Therefore configure your firewall to block tcp port 5280. Maybe it is also
possible to tell ejabberd to listen only locally on that port, but I couldn't
find out. Then change the ADMIN_URL constant in the CGI script to '/admin/'.
And finally add following lines to your virtual host configuration::

	ProxyPass        /admin http://127.0.0.1:5280/admin
	ProxyPassReverse /admin http://127.0.0.1:5280/admin

.. _suEXEC: http://httpd.apache.org/docs/current/suexec.html
