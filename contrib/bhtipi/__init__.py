"""
Basic HTtp Instrumentation Presentation Interface.

Presenting an instrumentation hierarchy by server process' HTTP server.
The module contains one
"""

from satella.instrumentation import CounterCollection, Counter, NoData
from satella.threads import BaseThread, Monitor

from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

# -------------------------------------------------- Nested rendering of the counter infrastructure

def render_counter(cc, nestlevel):

    try:
        val = cc.get_current()
    except NoData:
        val = '<span class="nodata">no data</span>'

    return """<div class="counter"><div class="counter_label">%s</div><div class"counter_value">%s</div></div>""" \
            % (cc.name, val)

def render_collection(cc, nestlevel):
    u = """<h%s>%s</h%s><hr><div class="indent">""" % (nestlevel, cc.name, nestlevel)
    with Monitor.acquire(cc):
        s = [render(x, nestlevel+1) for x in cc.items]
    y = "</div>"
    return ''.join([u]+s+[y])

def render(cc, nestlevel):
    if isinstance(cc, CounterCollection):
        return render_collection(cc, nestlevel)
    elif isinstance(cc, Counter):
        return render_counter(cc, nestlevel)
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
        .counter_value {
            width: 100px;
        }
        .nodata { color: gray; }
        .indent { margin-left: 10px; }
    </style>
</head>
<body>%s
</body>
</html>""" % (self.server.rootcc.name, render(self.server.rootcc, 1))

        self.wfile.write(u)


class BHTIPIServer(ThreadingMixIn, HTTPServer):
    def __init__(self, interface, port, rootcc):
        HTTPServer.__init__(self, (interface, port), BHTIPIRequestHandler)
        self.rootcc = rootcc


class BHTIPI(BaseThread):
    def __init__(self, interface, port, rootcc):
        BaseThread.__init__(self)
        self.server = BHTIPIServer(interface, port, rootcc)

    def run(self):
        while not self._terminating:
            self.server.handle_request()

    def terminate(self):
        BaseThread.terminate(self)
        self.server.server_close()
