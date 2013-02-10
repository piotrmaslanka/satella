"""
Basic HTtp Instrumentation Presentation Interface.

Presenting an instrumentation hierarchy by server process' HTTP server.
Sample usage (let rootcc be the root CounterCollection)

    from satella.contrib.bhtipi import BHTIPI
    bt = BHTIPI('localhost', 8080, rootcc).start()

    .. wait until teardown ..

    bt.terminate()      # it will close and terminate

"""

from satella.instrumentation import CounterCollection, Counter, NoData
from satella.threads import BaseThread, Monitor

from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

# -------------------------------------------------- Nested rendering of the counter infrastructure


def render_counter_tables(cc, nestlevel):
    try:
        val = cc.get_current()
    except NoData:
        val = '<span class="nodata">no data</span>'

    if cc.description != None:
        desc = cc.description if type(cc.description) == str else cc.description.encode('utf8')
    else:
        desc = ''

    if cc.units != None:
        units = cc.units if type(cc.units) == str else cc.units.encode('utf8')
    else:
        units = ''

    return '<table><tr><td class="counter_label">%s</td><td class="counter_value">%s</td><td class="counter_units">%s</td></tr></table>' % (desc, val, units)


def render_counter_div(cc, nestlevel):
    try:
        val = cc.get_current()
    except NoData:
        val = '<span class="nodata">no data</span>'

    s = ['<div class="counter"><div class="counter_label']
    if cc.description != None:
        desc = cc.description if type(cc.description) == str else cc.description.encode('utf8')
        s.append(' has_descr" title="%s"' % desc)

    s.append('">%s</div><div class="counter_value">%s</div>' % (cc.name, val))

    if cc.units != None:
        units = cc.units if type(cc.units) == str else cc.units.encode('utf8')

        s.append('<div class="counter_units">%s</div>' % units)

    s.append('</div>')

    return ''.join(s)

def render_collection(cc, nestlevel, use_tables):
    u = """<h%s>%s</h%s><hr><div class="indent">""" % (nestlevel, cc.name, nestlevel)
    with Monitor.acquire(cc):
        s = [render(x, nestlevel+1, use_tables) for x in cc.get()]
    y = "</div>"
    return ''.join([u]+s+[y])

def render(cc, nestlevel, use_tables):
    if isinstance(cc, CounterCollection):
        return render_collection(cc, nestlevel, use_tables)
    elif isinstance(cc, Counter):
        if use_tables:
            return render_counter_tables(cc, nestlevel)
        else:
            return render_counter_div(cc, nestlevel)
    else:
        raise ValueError, 'cc of unknown type'

# -------------------------------------------------- HTTP servers and other boring stuff

class BHTIPIRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/':
            self.send_response(404)
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/html')        
        self.end_headers()

        u = """<!DOCTYPE HTML>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>%s</title>
    <style type="text/css">
        .counter div { display: inline-block; }
        .counter_label {
            width: 200px;
            text-align: right;
            margin-right: 10px;
            color: #A9A9A9;
        }
            .has_descr { text-decoration: underline; }
        .counter_value {
            margin-right: 20px
        }
        .counter_units {
            color: gray;
            font-style: italic;
        }
        .nodata { color: gray; }
        .indent { margin-left: 10px; }
        .footer { text-align: center; font-size: 0.8em; }
        .footer a { color: black; }
    </style>
</head>
<body>%s
<div class="footer">powered by <a href="https://github.com/henrietta/satella/">Satella</a></div>
</body>
</html>""" % (self.server.rootcc.name, render(self.server.rootcc, 1, self.server.use_tables))

        self.wfile.write(u)


class BHTIPIServer(ThreadingMixIn, HTTPServer):
    def __init__(self, interface, port, rootcc, use_tabled_layout):
        HTTPServer.__init__(self, (interface, port), BHTIPIRequestHandler)
        self.rootcc = rootcc
        self.use_tables = use_tabled_layout


class BHTIPI(BaseThread):
    def __init__(self, interface, port, rootcc, use_tabled_layout=False):
        BaseThread.__init__(self)
        self.server = BHTIPIServer(interface, port, rootcc, use_tabled_layout)

    def run(self):
        while not self._terminating:
            self.server.handle_request()

    def terminate(self):
        BaseThread.terminate(self)
        self.server.server_close()
