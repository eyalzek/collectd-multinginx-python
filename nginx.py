#! /usr/bin/env python


import re
import urllib2

import collectd


class Nginx(object):

    def __init__(self):
        self.pattern = re.compile("([A-Z][\w]*).+?(\d+)")
        self.urls = {}

    def do_nginx_status(self):
        for instance, url in self.urls.items():
            try:
                response = urllib2.urlopen(url)
            except urllib2.HTTPError, e:
                collectd.error(str(e))
            except urllib2.URLError, e:
                collectd.error(str(e))
            else:
                data = response.read()
                m = self.pattern.findall(data)
                for key, value in m:
                    self.dispatch_metric(instance, 'connections', key, value)

                try:
                    server_headers = data.split('\n')[2].split()
                    server_values = data.split('\n')[1].split()
                    server_values.pop(0)

                    for key, value in zip(server_headers, server_values):
                        self.dispatch_metric(instance, 'server', key, value)
                except IndexError:
                    collectd.error(str(e))

    def dispatch_metric(self, instance, metric_type, key, value):
        metric = collectd.Values()
        metric.plugin = 'nginx-%s' % instance
        metric.type = 'nginx_%s' % metric_type
        metric.type_instance = key.lower()
        metric.values = [value]
        metric.dispatch()

    def config(self, obj):
        self.urls = dict((node.key, node.values[0]) for node in obj.children)


nginx = Nginx()
collectd.register_config(nginx.config)
collectd.register_read(nginx.do_nginx_status)
