import re
from datetime import datetime

def gps_chksum(rawGPS):
    """Calculate the checksum of a GPS string and compare it to the provided checksum.
    The GPS string is expected to be in the format $<message>*<checksum>
    The checksum is calculated by XORing all the bytes of the message and converting the result to hexadecimal.

    Args:
        rawGPS (str): The raw GPS string   
    returns:
        str: The calculated checksum in hexadecimal
        bool: True if the provided checksum matches the calculated checksum, False otherwise

    Example:
    >>> gps_chksum("$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47")
    ('47', True)
    """
    # Parse the GPS string using regular expression to find the message and the checksum
    match = re.search(r'\$(?P<message>.*)\*(?P<gsum>.*)', rawGPS) # search for the message and checksum

    if match:
        names = match.groupdict() 

        # Check if the message and checksum are present
        if len(names['gsum']) < 2:
            return None, False
        
        # Convert the message to bytes for checksum calculation
        msg = names['message'].encode()

        # Calculate the checksum
        chksm = msg[0]
        for b in msg[1:]:
            chksm ^= b # XOR the bytes of the message
        chksm_hex = format(chksm, '02X')

        # Compare the calculated checksum with the provided checksum
        pass_check = chksm_hex.upper() == names['gsum'].upper()

        return chksm_hex, pass_check
    else:
        return None, False

def extract_GNRMC(msg):
    """
    Extract the time, latitude and longitude from a GNRMC message
    
    Format of the message: $GNRMC,<1>,<2>,<3>,<4>,<5>,<6>,<7>,<8>,<9>,<10>,<11>,< 12>*xx<CR><LF>

    <0> $GNRMC
    <1> UTC time, the format is hhmmss.sss
    <2> Positioning status, A=effective positioning, V=invalid positioning
    <3> Latitude, the format is ddmm.mmmmmmm
    <4> Latitude hemisphere, N or S (north latitude or south latitude)
    <5> Longitude, the format is dddmm.mmmmmmm
    <6> Longitude hemisphere, E or W (east longitude or west longitude)
    <7> Ground speed
    <8> Ground heading (take true north as the reference datum)
    <9> UTC date, the format is ddmmyy (day, month, year)
    <10> Magnetic declination (000.0~180.0 degrees)
    <11> Magnetic declination direction, E (east) or W (west)
    <12> Mode indication (A=autonomous positioning, D=differential, E=estimation, N=invalid data)
    * Statement end marker
    XX XOR check value of all bytes starting from $ to *
    <CR> Carriage return, end tag
    <LF> line feed, end tag
        
    """
    parts = msg.split(',')
    if parts[3] and parts[5]:

        YMD = parts[9]  # Date
        HMS = parts[1][:6]  # Time

        if parts[4] == 'N':
            lat = .01*float(parts[3])  # Latitude
        elif parts[4] == 'S':
            lat = -.01* float(parts[3])

        if parts[6] == 'E':
            lon = 0.001*float(parts[5])  # Longitude
        elif parts[6] == 'W':
            lon = -0.01* float(parts[5])

        dt = datetime.strptime(YMD + HMS, '%y%m%d%H%M%S')

        return dt, lat, lon
      
def extract_GNGGA(msg):
    """
    Extract the time, latitude, longitude and altitude from a GNGGA message

    $GNGGA
    Format: $GNGGA,<1>,<2>,<3>,<4>,<5>,<6>,<7>,<8>,<9>,M,<10>,M,< 11>,<12>*xx<CR><LF> 
    E.g: $GNGGA,072446.00,3130.5226316,N,12024.0937010,E,4,27,0.5,31.924,M,0.000,M,2.0,*44 Field explanation:

    <0> $GNGGA
    <1> UTC time, the format is hhmmss.sss
    <2> Latitude, the format is ddmm.mmmmmmm
    <3> Latitude hemisphere, N or S (north latitude or south latitude)
    <4> Longitude, the format is dddmm.mmmmmmm
    <5> Longitude hemisphere, E or W (east longitude or west longitude)
    <6> GNSS positioning status: 0 not positioned, 1 single point positioning, 2 differential GPS fixed solution, 4 fixed solution, 5 floating point solution
    <7> Number of satellites used
    <8> HDOP level precision factor
    <9> Altitude
    <10> The height of the earth ellipsoid relative to the geoid
    <11> Differential time
    <12> Differential reference base station label
    * Statement end marker
    xx XOR check value of all bytes starting from $ to *
    <CR> Carriage return, end tag
    <LF> line feed, end tag
    """
    # print(msg)
    parts = msg.split(',')
    if parts[2] and parts[4]:
        HMS = parts[1][:6]  # Time
        if parts[3] == 'N':
            lat = .01*float(parts[2])  # Latitude
        elif parts[3] == 'S':
            lat = -.01* float(parts[2])

        if parts[5] == 'E':
            lon = 0.001*float(parts[4])  # Longitude
        elif parts[5] == 'W':
            lon = -0.01* float(parts[4])
        alt = float(parts[9]) # Altitude


        dt = datetime.strptime(HMS, '%H%M%S')
        return dt, lat, lon, alt
   

def extract_GNGSV(msg):
    """
    Extract the information about the visible satellites from a GNGSV message

    $XXGSV
    0	Message ID
    1	Total number of messages of this type in this cycle
    2	Message number
    3	Total number of SVs visible
    4	SV PRN number
    5	Elevation, in degrees, 90° maximum
    6	Azimuth, degrees from True North, 000° through 359°
    7	SNR, 00 through 99 dB (null when not tracking)
    8–11	Information about second SV, same format as fields 4 through 7
    12–15	Information about third SV, same format as fields 4 through 7
    16–19	Information about fourth SV, same format as fields 4 through 7
    20	The checksum data, always begins with *
        
    $GPGSV,2,1,07,02,54,254,23,06,77,344,17,12,27,318,26,17,40,068,28,1*6C
    """
    # print(msg)
    info = []
    parts = msg.split(',')
    msgs_this_cycle = parts[1]
    n_th_message = parts[2]
    visible_SVs = parts[3]
    
    signal_id = parts[-1].split('*')[0]
    # print(signal_id)
    band = get_band(parts[0][1:3], signal_id)

    PRN_prefix = parts[0][1:3]
    if '*' not in parts[4] and  len(parts[7])>0:
        SV1 = PRN_prefix+parts[4]+f'_{band}'+'_'+ parts[5] +'_'+ parts[6] +'_'+parts[7]
        info.append(SV1)
        if '*' not in parts[8] and  len(parts[11])>0:
            SV2 = PRN_prefix+parts[8]+f'_{band}'+'_'+ parts[9] +'_'+ parts[10] +'_'+parts[11]
            info.append(SV2)
            if '*' not in parts[12] and   len(parts[15])>0:
                SV3 = PRN_prefix+parts[12]+f'_{band}'+'_'+ parts[13] +'_'+ parts[14] +'_'+parts[15]
                info.append(SV3)
                if '*' not in parts[16] and  len(parts[19])>0:
                    SV4 = PRN_prefix+parts[15]+f'_{band}'+'_'+ parts[17] +'_'+ parts[18] +'_'+parts[19]
                    info.append(SV4)  
    return info, msgs_this_cycle, n_th_message, visible_SVs


def get_band(constellation, signal_id):
    """
    Get the band of the signal based on the constellation and signal_id
    """
    signal_id = int(signal_id)
    if constellation == "GP":
        match signal_id:
            case 0:
                return "All"
            case 1:
                return "L1C/A"
            case 2:
                return "L1P(Y)"
            case 3:
                return "L1M"
            case 4:
                return "L2P(Y)"
            case 5:
                return "L2C-M"
            case 6:
                return "L2C-L"
            case 7:
                return "L5-I"
            case 8:
                return "L5-Q"
            case _:
                return 'None'
    elif constellation == "GL":
        match signal_id:
            case 0:
                return "All"
            case 1:
                return "L1C/A"
            case 2:
                return "L1P"
            case 3:
                return "L2C/A"
            case 4:
                return "L2P"
            case _:
                return "None"
    elif constellation == "GA":
        match signal_id:
            case 0:
                return "All"
            case 1:
                return "E5a"
            case 2:
                return "E5b"
            case 3:
                return "E5a+b"
            case 4:
                return "E6-A"
            case 5:
                return "E6-BC"
            case 6:
                return "L1-A"
            case 7:
                return "L1-BC"
            case _:
                return "None"
    elif constellation == "GB":
        match signal_id:
            case 0:
                return "All"
            case 1:
                return "B1l"
            case 2:
                return "B1Q"
            case 3:
                return "B1C"
            case 4:
                return "B1A"
            case 5:
                return "B2-a"
            case 6:
                return "B2-b"
            case 7:
                return "B2a+b"
            case 8:
                return "B3l"
            case 9:
                return "B3Q"
            case 'A':
                return "B3A"
            case 'B':
                return "B2l"
            case 'C':
                return "B2Q"
            case _:
                return "None"
