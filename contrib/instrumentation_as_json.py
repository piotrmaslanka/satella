"""
Module to export instrumentation information as JSON output
"""
from satella.instrumentation import CounterCollection, Counter, NoData
import json

def asval(cc):
    if isinstance(cc, CounterCollection):
        return dict(((item.name, asval(item)) for item in cc.get()))
    elif isinstance(cc, Counter):
        try:
            h = cc.get_history()
        except:
            try:
                h = cc.get_current()
            except NoData:
                h = None
            return h
        else:
            f = dict(h)
            try:
                f['value'] = cc.get_current()
            except:
                f['value'] = None
            return f

def export(insmgr):
    """Constructs a JSON string based on data from given insmgr"""
    return json.dumps(asval(insmgr))