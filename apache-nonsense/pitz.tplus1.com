NameVirtualHost *:80
<VirtualHost *:80>

    ServerName pitz.tplus1.com

    ServerAdmin webmaster@localhost

    DocumentRoot /home/matt/checkouts/pitz/pitz/static

    # Possible values include: debug, info, notice, warn, error, crit,
    # alert, emerg.
    LogLevel info

    CustomLog /var/log/apache2/pitz-access.log combined
    ErrorLog /var/log/apache2/pitz-error.log
    ServerSignature On

    <Directory /home/matt/checkoutz/pitz/apache-nonsense>
    Order allow,deny
    Allow from all
    </Directory>

    WSGIPythonHome /home/matt/.virtualenvs/pitz
    WSGIScriptAlias /myapp /home/matt/checkouts/pitz/apache-nonsense/myapp.wsgi

    RewriteEngine on
    RewriteRule ^/static/(.*) /home/matt/checkouts/pitz/pitz/static/$1 [last]
    RewriteRule ^/favicon.ico /home/matt/checkouts/pitz/pitz/static/favicon.ico [last]
    # RewriteRule ^(.*) http://127.0.0.1:9876$1 [proxy]

</VirtualHost>
