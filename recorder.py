#$Id: recorder.py 8436 2009-04-27 09:46:29Z hristo $


class MethodCallData( object):
    def __init__( me, name, *a, **k):
        me.name = name
        me.args = list(a) # args is tuple
        me.kargs = k

    def __str__( me):
        return '%s args=%s kargs=%s' % ( me.name, str(me.args), str(me.kargs))

class Recorder( object):
    ''' Records all requests so they can be played back later to another object.'''
    DEBUG = 0

    def __init__( me, rec_context =None):
        me.rec_context = rec_context # None if method results don't matter
        me.method_calls = []


    indent = 0
    def play_on( me, context):
        for call in me.method_calls:
            if me.DEBUG:
                if call.name == 'PopState': me.indent -= 1
                if me.DEBUG > 1:
                    a = raw_input( me.indent*'  ' + str(call) + ' press N to skip')
                    if a.upper() == 'N':
                        print 'skipping...', call
                        continue
                else:
                    print me.indent*'   ', call
                if call.name == 'PushState': me.indent += 1

            method = getattr( context, call.name)
            method( *call.args, **call.kargs)

    def record( me, name):
        def record_method_call( *a, **k):
            call_data = MethodCallData( name, *a, **k)
            me.method_calls.append( call_data)
            if me.rec_context:
                meth = getattr( me.rec_context, name)
                return meth( *a, **k)
            return None

        return record_method_call

    def __getattr__( me, name):
        return me.record( name)


# vim:ts=4:sw=4:expandtab
