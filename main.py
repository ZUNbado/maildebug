from flask import Flask, render_template, request
import base64

app = Flask(__name__)

urls = [ 'imap', 'pop3', 'smtp', 'ftp' ]

def telnetCheck(host, port, session, timeout = 5):
    import telnetlib
    text = str()
    tn = telnetlib.Telnet(host, port)
    exit = False
    for line in session:
        if not exit:
            (i,m,t) = tn.expect([line['expect']], timeout)
            text += t+'\r\n'
            print t
            if not m: 
                text += tn.read_eager()
                exit = True
                continue
            if 'send' in line:
                print line['send']
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

    return render_template('form.html', session = telnet, fields = fields, urls = urls, current_url = request.url_rule.rule[1:])

@app.route("/ftp", methods=['POST', 'GET'])
def ftp():
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
                { 'expect' : r'220 .*$', 'send' : 'USER %s' % values['user'] },
                { 'expect' : r'331 .*$', 'send' : 'PASS %s' % values['passwd'] },
                { 'expect' : r'230.*$', 'send' : 'LIST' },
                { 'expect' : r'^.\r\n$' },
                ]
        server = values['server']
        port = int(values['port'])
        if server and port:
            telnet = telnetCheck(server, port, session)
    return render_template('form.html', session = telnet, fields = fields, urls = urls, current_url = request.url_rule.rule[1:])

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
    return render_template('form.html', session = telnet, fields = fields, urls = urls, current_url = request.url_rule.rule[1:])


@app.route("/smtp", methods=['POST', 'GET'])
def smtp():
    fields = [
            { 'name' : 'server', 'label' : 'Server', 'value' : '', 'required' : True },
            { 'name' : 'port', 'label' : 'Port', 'value' : '25', 'required' : True },
            { 'name' : 'ehlo', 'label' : 'HELO', 'value' : '', 'required' : True },
            { 'name' : 'username', 'label' : 'Username', 'value' : ''  },
            { 'name' : 'password', 'label' : 'Password', 'value' : '' },
            { 'name' : 'login', 'label' : 'Login Type', 'value' : 'PLAIN', 'choices' : [ 'PLAIN', 'LOGIN' ] },
            { 'name' : 'from', 'label' : 'From', 'value' : '', 'required' : True },
            { 'name' : 'to', 'label' : 'To', 'value' : '', 'required' : True },
            { 'name' : 'data', 'label' : 'Body', 'value' : 'Text message', 'required' : True },
            ]
    telnet = ''
    if request.method == 'POST':
        (fields, values) = validate_form(fields, {})
        print values

        session = [ 
                { 'expect' : r'^220.*\r\n$', 'send' : 'EHLO %s' % values['ehlo'] },
                ]
        nextcode = 250
        if 'username' in values and 'password' in values:
            nextcode = 235
            if values['login'] == 'PLAIN':
                session += { 'expect' : r'250 .*\r\n$', 'send' : 'AUTH PLAIN %s' % base64.b64encode('\0%s\0%s' % ( values['username'], values['password'] )) },
            elif values['login'] == 'LOGIN':
                session += [
                        { 'expect' : r'250 .*\r\n$', 'send' : 'AUTH LOGIN' },
                        { 'expect' : r'334 .*\r\n$', 'send' : base64.b64encode(values['username']) },
                        { 'expect' : r'334 .*\r\n$', 'send' : base64.b64encode(values['password']) },
                        ]
        session += [
                { 'expect' : r'%s .*\r\n$' % nextcode, 'send' : 'mail from: %s' % values['from'] },
                { 'expect' : r'^250 .*\r\n$', 'send' : 'rcpt to: %s' % values['to'] },
                { 'expect' : r'^250 .*\r\n$', 'send' : 'data' },
                { 'expect' : r'^354 .*\r\n$', 'send' : '%s\r\n.' % values['data'] },
                { 'expect' : r'^250 .*\r\n$' },
                ] 
        print session
        server = values['server']
        port = int(values['port'])
        if server and port:
            telnet = telnetCheck(server, port, session)
    return render_template('form.html', session = telnet, fields = fields, urls = urls, current_url = request.url_rule.rule[1:])


@app.route("/")
def client():
    return render_template('index.html', urls = urls)

if __name__ == '__main__':
    app.run(host='0.0.0.0')

