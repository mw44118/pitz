<VirtualHost *>

    ServerAdmin webmaster@localhost

    DocumentRoot /home/matt/checkouts/pitz/pitz/static

    ServerName pitz.tplus1.com

    # Possible values include: debug, info, notice, warn, error, crit,
    # alert, emerg.
    LogLevel info

    CustomLog /var/log/apache2/pitz-access.log combined
    ErrorLog /var/log/apache2/pitz-error.log
    ServerSignature On

    <Directory /home/matt/checkoutz/pitz>
    Order allow,deny
    Allow from all
    </Directory>

    WSGIScriptAlias /myapp /home/matt/checkouts/pitz/apache-nonsense/myapp.wsgi

    SSLEngine on

    SSLOptions +StrictRequire

    SSLCertificateFile /home/matt/checkouts/pitz/apache-nonsense/server.crt
    SSLCertificateKeyFile /home/matt/checkouts/pitz/apache-nonsense/server.key

    RewriteEngine on
    RewriteRule ^/static/(.*) /home/matt/checkouts/pitz/pitz/static/$1 [last]
    RewriteRule ^/favicon.ico /home/matt/checkouts/pitz/pitz/static/favicon.ico [last]
    # RewriteRule ^(.*) http://127.0.0.1:9876$1 [proxy]

</VirtualHost>
