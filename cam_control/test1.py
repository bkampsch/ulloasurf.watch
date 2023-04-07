import requests

auth = requests.auth.HTTPDigestAuth ('bk','habeeb12')

server = '69.209.6.206:8080'

url = f'http://{server}/cgi-bin/ptz.cgi?action=getPresets&channel=1'

r = requests.get(url=url, auth=auth)

r.text

command = 'start'
code = 'Right'
speed = '1'

urlfunc = lambda: f'http://{server}/cgi-bin/ptz.cgi?action={command}&channel=1&code={code}&arg1=0&arg2={speed}&arg3=0'

r = requests.get(url=urlfunc(), auth=auth)

command = 'stop'

r = requests.get(url=urlfunc(), auth=auth)

url = f'http://{server}/cgi-bin/ptz.cgi?action=getStatus'
r = requests.get(url, auth=auth)
print(r.text)




def urlfunc2(command, code, arg1, arg2, arg3, arg4=None):
    url = f'http://{server}/cgi-bin/ptz.cgi?action={command}&channel=1&code={code}&arg1={arg1}&arg2={arg2}&arg3={arg3}'
    if arg4:
        url += f"&arg4={arg4}"
    return url

## Position ABS moves specified number of degrees from current position
r = requests.get(url=urlfunc2('start', 'PositionABS','180','45','10', '8'), auth=auth)

r = requests.get(url=urlfunc2('start', 'GotoPreset','0','2','0', '0'), auth=auth)