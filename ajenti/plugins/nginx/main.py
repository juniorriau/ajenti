from ajenti.api import *
from ajenti.plugins.webserver_common.api import WebserverPlugin


@plugin
class Nginx (WebserverPlugin):
    service_name = 'nginx'
    service_buttons = [
        {
            'command': 'force-reload',
            'text': 'Reload',
            'icon': 'step-forward',
        }
    ]
    hosts_available_dir = '/etc/nginx/sites-available'
    hosts_enabled_dir = '/etc/nginx/sites-enabled'

    template = """server {
    server_name name;
    access_log /var/log/nginx/name.access.log;
    error_log  /var/log/nginx/name.error.log;

    listen 80;

    location / {
        root /var/www/name;
    }

    location ~ \.lang$ {
        include fastcgi_params;
        fastcgi_pass 127.0.0.1:port;
        fastcgi_split_path_info ^()(.*)$;
    }
}
"""

    def init(self):
        self.title = 'NGINX'
        self.category = 'Software'
        self.icon = 'globe'