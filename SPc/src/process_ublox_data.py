from functions.NMEA_parser import gps_chksum, extract_GNRMC, extract_GNGGA, extract_GNGSV
from datetime import datetime
import sys
import pandas as pd
import numpy as np
import h5py

def process_ublox_data(file_path, def_date, out_dir):
    """
    Function to read a UBX file and extract the data
    The UBX file should be containing NMEA messages (GNRMC, GNGGA, GPGSV, GLGSV, etc.)

    The function will return a list of dictionaries, where each dictionary contains the following keys:
    datetime, latitude, longitude, SVs 
    where SVs is a list of dictionaries containing the following keys:
    SV, Elevation, Azimuth, C_N0

    Each SV represents a satellite visible at a given time

    """

    # Attempts to get a default date from the file path
    # the file path should be in the format: D:\GNSSR\USDA-NF-Ublox\2020\2020-06-15_12_inch_plate\Ublox_data
    # where the date is the 4th element in the path
    # If it fails, it will ask the user to input a date
    try:
        default_date = datetime.strptime(file_path.split("\\")[4][:10], '%Y-%m-%d')
    except:
        # inp = input('Enter a date of the flight in the format YYYY-MM-DD (e.g. 2021-04-27): ')
        inp = def_date
        default_date = datetime.strptime(inp, '%Y-%m-%d')
    data_file = open(file_path, errors="ignore") # Reading the UBX file
    lines = data_file.readlines() 

    i = 0
    dt = None
    lat = None
    lon = None
    data = []
    const = []

    # iterate through the lines
    while i < len(lines):
        
        # print(lines)
        line = lines [i]
        k1 = line.find('$G')
        k2 = line.find('*')
        if k1 == -1 or k2 == -1:
            i = i+1
            continue
        line = line[k1:k2+3]  # +3 to include '*' and the two checksum characters
    
        # Verify the checksum of the trimmed line
        _, passed = gps_chksum(line)
        if not passed:
            i = i+1
            continue
        parts = line.split(',')

        if parts[0] == "$GNRMC":
            try:
                dt, lat, lon = extract_GNRMC(line)
            except:
                # print(line)
                i = i+1
                continue
            
        elif parts[0] == "$GNGGA":
            try:
                dt, lat, lon, alt = extract_GNGGA(line)
                dt = dt.replace(year=default_date.year, month=default_date.month, day = default_date.day)
            except:
                i = i+1
                continue

        elif dt and (parts[0] in ['$GPGSV', '$GLGSV', '$GAGSV', '$GBGSV']):
            try: 
                info, _ = extract_GNGSV(line)
            except:
                i = i+1
                continue
            if  len(info) > 0:
                # data.append(instance)
                instance = {}
                instance['time'] = dt
                instance['lat'] = lat
                instance['long'] = lon
                # instance['SVs'] = []
                for sv in info:
                    # if sv['C_N0']:
                    # print (sv[:2])
                    const.append(sv[:2])
                    sv_data = sv.split('_')
                    instance['const'] = str(sv_data[0][:2])
                    instance['prn'] = int(sv_data[0][2:4]) 
                    instance['band'] = str(sv_data[1][:2])
                    instance['ele'] = int(sv_data[2]) if sv_data[2] else np.nan
                    instance['az'] = int(sv_data[3]) if sv_data[3] else np.nan
                    instance['C_N0'] = int(sv_data[4]) if sv_data[4] else np.nan
                    data.append(instance)
                    # print (instance)

        i = i+1
    # print (data[0])
    # check samples of each constellation
    # unique_const = np.unique(const)
    # for const_str in unique_const:
    #     count = const.count(const_str)
    #     print(f"{const_str}: {count} times")
    data_df = pd.DataFrame(data)
    # print (data_df)
    data_df['time'] = data_df['time'].astype('int64') // 10**9
    data_df['band'] = data_df['band'].values.astype('S')
    # print(data_df.band)
    data_df['const'] = data_df['const'].values.astype('S')
    # print(data_df.const)
    print("Done Reading: "+ file_path)
    # print(data_df.dtypes)
    # print(data_df)
    # data_df.to_csv(f"{out_dir}/{file_path.split('/')[-1].split('.')[0]}_ublox.csv", index=False)
    # print(f"Output: {out_dir}/{file_path.split('/')[-1].split('.')[0]}_ublox.csv")

    # create compound data type
    dtype = np.dtype([
    ('time', 'i8'),
    ('lat', 'f8'),
    ('long', 'f8'),
    ('const', 'S2'),
    ('prn', 'i8'),
    ('band', 'S2'),
    ('ele', 'f8'),
    ('az', 'f8'),
    ('C_N0', 'i8')
    ])
    struct_arr = np.array(list(data_df.to_records(index=False)), dtype=dtype)
    # print(struct_arr)
    with h5py.File(f"{out_dir}/{file_path.split('/')[-1].split('.')[0]}_ublox.h5", 'w') as f:
        dset = f.create_dataset(f"{file_path.split('/')[-1].split('.')[0]}_ublox", data=struct_arr)
        dset.attrs['file_name'] = file_path.split('/')[-1].split('.')[0]
        dset.attrs['col1'] = 'time'
        dset.attrs['col2'] = 'lat'
        dset.attrs['col3'] = 'long'
        dset.attrs['col4'] = 'const'
        dset.attrs['col5'] = 'prn'
        dset.attrs['col6'] = 'band'
        dset.attrs['col7'] = 'ele'
        dset.attrs['col8'] = 'az'
        dset.attrs['col9'] = 'C_N0'
    print(f"Output: {out_dir}/{file_path.split('/')[-1].split('.')[0]}_ublox.h5")

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 4:
        print("Usage: python process_ublox_data.py <input_gpx_file_location> <data collection date>")
        sys.exit(1)

    # Get the file location from the command line argument
    input_file_location = sys.argv[1]
    def_date = sys.argv[2]
    out_dir = sys.argv[3]

    # Create the file
    process_ublox_data(input_file_location, def_date, out_dir)