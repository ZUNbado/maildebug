from flask import Flask, render_template, request

app = Flask(__name__)

def telnetCheck(host, port, session, timeout = 5):
    import telnetlib
    text = str()
    tn = telnetlib.Telnet(host, port)
    for line in session:
        (i,m,t) = tn.expect([line['expect']], timeout)
        text += t+'\r\n'
        if not m: 
            text += tn.read_eager()
        if 'send' in line:
            text += line['send']+'\r\n'
            tn.write(line['send'].encode('utf-8')+'\r\n')
    text += tn.read_eager()
    return text.decode('utf-8').replace('\r\n', '<br>')

def validate_form(fields, values):
    values = {}
    for ffield in request.form:
        for field in range(len(fields)):
            if ffield == fields[field]['name'] and request.form[ffield]:
                fields[field]['value'] = request.form[ffield]
                values[ffield] = request.form[ffield]
    return fields, values

@app.route("/imap", methods=['POST', 'GET'])
def imap():
    fields = [
            { 'name' : 'server', 'label' : 'Server', 'value' : '', 'required' : True },
            { 'name' : 'port', 'label' : 'Port', 'value' : '', 'required' : True },
            { 'name' : 'user', 'label' : 'Username', 'value' : '', 'required' : True },
            { 'name' : 'passwd', 'label' : 'Password', 'value' : '', 'required' : True },
            ]
    telnet = ''
    if request.method == 'POST':
        (fields, values) = validate_form(fields, {})
        session = [ 
                { 'expect' : r'^.*ready.*\r\n$', 'send' : 'a1 LOGIN %s %s' % (values['user'], values['passwd']) },
                { 'expect' : r'a1 OK.*\r\n$', 'send' : 'a2 LIST "" "*"' },
                { 'expect' : r'a2 OK.*\r\n$', 'send' : 'a3 EXAMINE INBOX' },
                { 'expect' : r'a3 OK.*\r\n$', 'send' : 'a4 FETCH 1 BODY[]' },
                { 'expect' : r'a4 OK.*\r\n$',  },
                ]
        server = values['server']
        port = int(values['port'])
        if server and port:
            telnet = telnetCheck(server, port, session)
    return render_template('form.html', session = telnet, fields = fields)


@app.route("/pop3", methods=['POST', 'GET'])
def pop3():
    fields = [
            { 'name' : 'server', 'label' : 'Server', 'value' : '', 'required' : True },
            { 'name' : 'port', 'label' : 'Port', 'value' : '', 'required' : True },
            { 'name' : 'user', 'label' : 'Username', 'value' : '', 'required' : True },
            { 'name' : 'passwd', 'label' : 'Password', 'value' : '', 'required' : True },
            ]
    telnet = ''
    if request.method == 'POST':
        (fields, values) = validate_form(fields, {})
        session = [ 
                { 'expect' : r'^\+OK.*\r\n$', 'send' : 'USER %s' % values['user'] },
                { 'expect' : r'^\+OK.*\r\n$', 'send' : 'PASS %s' % values['passwd'] },
                { 'expect' : r'^\+OK.*\r\n$', 'send' : 'LIST' },
                { 'expect' : r'^.\r\n$', 'send' : 'RETR 1' },
                { 'expect' : r'^.\r\n$' },
                ]
        server = values['server']
        port = int(values['port'])
        if server and port:
            telnet = telnetCheck(server, port, session)
    return render_template('form.html', session = telnet, fields = fields)


@app.route("/smtp", methods=['POST', 'GET'])
def smtp():
    fields = [
            { 'name' : 'server', 'label' : 'Server', 'value' : '', 'required' : True },
            { 'name' : 'port', 'label' : 'Port', 'value' : '', 'required' : True },
            { 'name' : 'ehlo', 'label' : 'HELO', 'value' : '', 'required' : True },
            { 'name' : 'from', 'label' : 'From', 'value' : '', 'required' : True },
            { 'name' : 'to', 'label' : 'To', 'value' : '', 'required' : True },
            { 'name' : 'data', 'label' : 'Body', 'value' : 'Text message', 'required' : True },
            ]
    telnet = ''
    if request.method == 'POST':
        (fields, values) = validate_form(fields, {})

        session = [ 
                { 'expect' : r'220.*$', 'send' : 'EHLO %s' % values['ehlo'] },
                { 'expect' : r'250 .*$', 'send' : 'mail from: %s' % values['from'] },
                { 'expect' : r'250 .*$', 'send' : 'rcpt to: %s' % values['to'] },
                { 'expect' : r'250 .*$', 'send' : 'data' },
                { 'expect' : r'354 .*$', 'send' : '%s\r\n.' % values['data'] },
                { 'expect' : r'250 .*$' },
                ]
        server = values['server']
        port = int(values['port'])
        if server and port:
            telnet = telnetCheck(server, port, session)
    return render_template('form.html', session = telnet, fields = fields)

urls = []
for url in app.url_map.iter_rules():
    static = '/static/'
    if url.rule != '/' and url.rule[:len(static)] != static:
        urls.append( url )

@app.route("/")
def client():
    return render_template('index.html', urls = urls)
