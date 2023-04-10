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

## Position ABS moves specified number of degrees from current position  WRONG - THESE ARE ABSOLUTE COORDS
r = requests.get(url=urlfunc2('start', 'PositionABS','180','45','10', '8'), auth=auth)

r = requests.get(url=urlfunc2('start', 'GotoPreset','0','2','0', '0'), auth=auth)





def urlfuncMoveDirectly(arg1, arg2, arg3 arg4):
    url = f'http://{server}/cgi-bin/ptzBase.cgi?action=moveDirectly&channel=0&startPoint[0]={arg1}&startPoint[1]=2275&endPoint[0]=7893&endPoint[1]=3034




r = requests.get(url=urlfunc2('start', 'GotoPreset','0','1','0', '0'), auth=auth)


#def goToABS(arg1, arg2, arg3='0', arg4=None):
def goToABS(arg1, arg2, arg3, arg4=None):
    r = requests.get(url=urlfunc2('start', 'PositionABS',arg1,arg2,arg3,arg4), auth=auth)

goToABS('360','90','1')

#"postion[2]" seems to increase by 2.048 regardless of what "arg3" is.  CONFUSED
#ZoomValue goes up by 20
#


# get status (trying to figure out how to set zoom)

url = f'http://{server}/cgi-bin/ptz.cgi?action=getStatus&channel=1'

r = requests.get(url=url, auth=auth)
r.text




