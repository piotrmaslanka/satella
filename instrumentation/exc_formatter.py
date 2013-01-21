import sys, traceback

def format_exception():
    """
    Returns last exception that occurred, alongside with all locals.

    @return: string with exception data. Newline is \\n
    """
    sbuilder = []

    tb = sys.exc_info()[2]
    while tb.tb_next:
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back

    sbuilder.append(traceback.format_exc())

    for frame in stack:
        sbuilder.append('** Frame %s at %s:%s' % (frame.f_code.co_name,
                                                 frame.f_code.co_filename,
                                                 frame.f_lineno))
        sbuilder.append('*** Locals: ')
        for key, value in frame.f_locals.items():
            try:
                f = "**** %s: %s" % (key, repr(value))
            except:
                f = "**** %s: *repr failed*" % key

            sbuilder.append(f)

        sbuilder.append('*** Globals: ')
        for key, value in frame.f_globals.items():
            try:
                f = "**** %s: %s" % (key, repr(value))
            except:
                f = "**** %s: *repr failed*" % key

            sbuilder.append(f)

    return '\n'.join(sbuilder)