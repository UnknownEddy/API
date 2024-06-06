import numpy as np
import pandas as pd
import navpy
from datetime import timedelta
import simplekml


def get_SP(lat, lon, alt, Az, El, hgrnd=80):
    """
    This function calculates the Specular Point (SP) of a satellite signal
    Inputs:
    lat: Latitude of the receiver
    lon: Longitude of the receiver
    Alt: Altitude of the receiver
    Az: Azimuth of the satellite signal
    El: Elevation of the satellite signal
    hgrnd: Height of the ground above the sea level

    Outputs:
    lla: Latitude, Longitude, Altitude of the SP
    """

    h = alt - hgrnd + 0
    # Convert angles from degrees to radians
    El_rad = np.radians(El)
    Az_rad = np.radians(Az)

    # Calculate distances using the tangent and sine/cosine rules
    xx = h * np.sin(Az_rad) / np.tan(El_rad)
    yy = h * np.cos(Az_rad) / np.tan(El_rad)  # North direction

    # NED (North, East, Down) coordinates of the Specular Point
    NED_loc = np.stack((yy, xx, alt), axis=-1)  # stacking along the last axis to keep (N, E, D) format

    # Convert NED coordinates to LLA (Latitude, Longitude, Altitude)
    shift_lla = np.array([navpy.ned2lla(NED_loc[i], lat[i], lon[i], alt[i]) for i in range(len(lat))])

    return shift_lla


def get_FresnelZone (lat, lon, alt, az, el,n = 1 ,hgrnd=80, freq=1575.42*1e6):
    """
    The function calculates the Fresnel Zone of a satellite signal

    Inputs:
    lat: Latitude of the receiver
    lon: Longitude of the receiver
    Alt: Altitude of the receiver
    Az: Azimuth of the satellite signal
    El: Elevation of the satellite signal
    n: Number of Fresnel Zone
    hgrnd: Height of the ground above the sea level
    freq: Frequency of the signal

    Outputs:
    lla_FZ: Latitude, Longitude, Altitude of the Fresnel Zone
    """
    h = alt - hgrnd + 0
    # Fresnel Zone calculation
    # freq = 1575.42*1e6 # L1 frequency
    c_light = 3e8
    wavelength = c_light/freq
    # n = 1

    S0x = h/np.tan(el*np.pi/180) #
  
    d  = n*wavelength/ 2 #delay for nth Fresnel zone
    b = np.sqrt(2*d* h* np.sin(el*np.pi/180))/ np.sin(el*np.pi/180) #Semi minor axis
    a = b/ np.sin(el*np.pi/180);    #Semi major axis
    # print(a, b)
    # break    
  
    C = S0x - np.sqrt(a*a - b*b) # Center of the ellipse

    # Center rotated to azimuth
    Cx = C*np.cos(az*np.pi/180)
    Cy = C*np.sin(az*np.pi/180)
  
    #Rotated Ellipse
    th = np.linspace(0, 2*np.pi)
    Ex = Cx + (a * np.cos(th) * np.cos(az*np.pi/180)) - (b * np.sin(th) * np.sin((az*np.pi/180)))
    Ey = Cy + (a * np.cos(th) * np.sin(az*np.pi/180)) + (b * np.sin(th) * np.cos((az*np.pi/180)))

    NED_loc = [Ex,Ey,0*np.ones_like(Ex)]
    lla_FZ = navpy.ned2lla(NED_loc, lat, lon, alt)
    return np.round (lla_FZ, 6)

def get_fz_from_sp_df(sp_df, sat_name):
    """
    This function calculates the Fresnel Zone of a satellite signal
    Inputs:
    sp_df: DataFrame containing the SP of the satellite signals
    sat_name: Name of the satellite

    Outputs:
    new_df: DataFrame containing the SP and Fresnel Zone of the satellite signals
    """
    new_df = sp_df[sp_df['sat'] == sat_name].reset_index(drop=True)
    new_df['FZone_lat'] = None
    new_df['FZone_lon'] = None
    new_df['FZone_alt'] = None
    for i, row in new_df.iterrows():
        lat = float(row['fl_lat'])
        lon = float(row['fl_lon'])
        alt = float(row['fl_alt'])

        el = row['Az']
        az = row['El']

        if not el:
            continue
        el = float(el)
        az = float(az)
        lla_FZ = get_FresnelZone(lat, lon, alt, az, el)
        new_df.iloc[i, 9] = pd.DataFrame(lla_FZ[0]).values
        new_df.iloc[i, 10] = pd.DataFrame(lla_FZ[1]).values
        new_df.iloc[i, 11] = pd.DataFrame(lla_FZ[2]).values
    return new_df

def gen_fz_kml(fz_df, output_file):

    kml = simplekml.Kml()
    for index, row in fz_df.iterrows():
        time = row['time']
        SP_lat = row['SP_lat']
        SP_lon = row['SP_lon']
        lats = row['FZone_lat']
        lons = row['FZone_lon']
        
        
        time_plus1 = time + timedelta(seconds=1)
        
        polygon_coords = list(zip(lons, lats))

        pol = kml.newpolygon()
        pol.outerboundaryis = polygon_coords
        pol.timespan.begin = time.strftime('%Y-%m-%dT%H:%M:%S')
        pol.timespan.end = time_plus1.strftime('%Y-%m-%dT%H:%M:%S')

        point = kml.newpoint()
        point.coords = [(SP_lon, SP_lat)]
        point.timespan.begin = time.strftime('%Y-%m-%dT%H:%M:%S')
        point.timespan.end = time_plus1.strftime('%Y-%m-%dT%H:%M:%S')

    kml.save(output_file)
