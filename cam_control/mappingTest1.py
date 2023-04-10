import requests
import numpy as np

auth = requests.auth.HTTPDigestAuth ('bk','habeeb12')

server = '69.209.6.206:8080'




# get status (trying to figure out how to set zoom)
url = f'http://{server}/cgi-bin/ptz.cgi?action=getStatus&channel=1'
r = requests.get(url=url, auth=auth)
r.text

#"postion[2]" seems to increase by 2.048 regardless of what "arg3" in "goToABS(...)" is.  CONFUSED
#ZoomValue goes up by 20





def urlfunc2(command, code, arg1, arg2, arg3, arg4=None):
    url = f'http://{server}/cgi-bin/ptz.cgi?action={command}&channel=1&code={code}&arg1={arg1}&arg2={arg2}&arg3={arg3}'
    if arg4:
        url += f"&arg4={arg4}"
    return url


#def goToABS(arg1, arg2, arg3, arg4=None):
def goToABS(arg1, arg2, arg3='0', arg4=None):
    r = requests.get(url=urlfunc2('start', 'PositionABS',arg1,arg2,arg3,arg4), auth=auth)










# I'd like to be able to getStatus, pull current PTZ values, and then "add" dtheta and tphi to them
# (and later adjust the zoom appropriately - that's the next step after horizontal location)

# for now, I'll start with the PTZ values after running goToABS('50','0','0') (my best effort at pointing it north)

#Postion[0]=50.000000
#Postion[1]=0.000000
#Postion[2]=5.120000



# Coords from Google maps:

# CAM:
#  37.73918773576854, -122.50640333768246

# height = 10m (?????)

# Taraval bathrooms:
#  37.74144719376465, -122.50711310279776

# RESULT SHOULD BE SAME AS goToABS('65','0','0')
# so we're looking for ~15 degree horizontal increase in angle.  

# NOTE: we should check to see whether the target is east or west of camera, and adjust sign of angle increment accordingly








# 50 degrees currently seems close to pointing North.  We need to lock the calibration down
goToABS('50','0','0')


# Camera gps coordinates
cam_gps = np.array([37.73918773576854, -122.50640333768246])

# Set target gps coordinates
def setTarget(x,y):
    return np.array([x,y])

# Some sample target gps coords
gps_sloatBR = setTarget(37.74144719376465, -122.50711310279776)
gps_vicenteSouthwestStoplight = setTarget(37.737791303817076, -122.50711462860801)
# choose your own:
gps_test = setTarget(37.89551542376183, -122.70190068362308)  # insert any coordinates here


target_gps = gps_test

# Initial PTZ coordinates for camera (MUST CALIBRATE EVENTUALLY - ie what P value corresponds to due north)
theta_0 = 50
phi_0 = 0
zoom_0 = 0

# (Rough) calculation/estimate of how many meters correspond to a change of 1 degree of lat/lon at cam location
local_lat = 37.74  # Lat of cam zone
lonStep_equater = 111.321e3
latStep_0 = 111e3  #(do we need to be more precise?  i think not...)
lonStep_0 = np.cos(np.radians(local_lat)) * lonStep_equater  #roughly 88km at lat=37.74 (ie at OB)

# Calculate the "fraction" of a degree of lat/lon between cam and target, then
# multiply those fractions by the <lon/lat>Step_0 variables to get relative horizontal distances in meters
def dhorz_calc(y, x, y0=cam_gps[0], x0=cam_gps[1], lonStep=lonStep_0, latStep=latStep_0):
    return np.array([abs(x-x0)*lonStep,abs(y-y0)*latStep])

coord_array = np.concatenate((target_gps,origin_gps))

dhorz = dhorz_calc(*target_gps)

dx = dhorz[0]
dy = dhorz[1]
dz = 8;  # Very rough guess at height (meters) of camera

dtheta = np.degrees(np.arctan(dx/dy))

# CHECK THIS
# Adjust theta depending on quadrant of target (base case is quadrant 2 (ie NW of camera), adjust for 3,4,1 in that order)
if target_gps[0] < origin_gps[0] and target_gps[1] < origin_gps[1]:
    dtheta = 180 - dtheta
elif target_gps[0] < origin_gps[0] and target_gps[1] > origin_gps[1]:
    dtheta = 180 + dtheta
elif target_gps[0] > origin_gps[0] and target_gps[1] > origin_gps[1]:
    dtheta = -dtheta

dl = np.sqrt(dx**2 + dy**2)

dphi = 90 - np.degrees(np.arctan(dl/dz))  # Subtract from 90 since 0 points flat not down, unlike my drawings

theta = theta_0 + dtheta
phi = phi_0 + dphi


goToABS(str(theta),str(phi),'0')









# get status (trying to figure out how to set zoom)
url = f'http://{server}/cgi-bin/ptz.cgi?action=getStatus&channel=1'
r = requests.get(url=url, auth=auth)
r.text



