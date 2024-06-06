import pandas as pd
import sys
import numpy as np
import h5py
from functions.geo_calc import get_SP

def calculate_SP(track_df_loc, ubx_data_loc, out_dir):
    """
    SP_from_flight_logs_and_ubx
    This function calculates the Specular Point (SP) of a satellite signal
    Inputs:
    track_df: DataFrame containing the flight logs
    ubx_data: List of dictionaries containing the UBX data

    outputs:
    sp_df: DataFrame containing the SP of the satellite signals
    """
    print(f"reading files: \n{track_df_loc}, \n{ubx_data_loc}")
    # track_df = pd.read_csv(track_df_loc)

    track_df = pd.DataFrame(np.array(h5py.File(track_df_loc)[track_df_loc.split('/')[-1][:-3]]))
    track_df.columns = ['time', 'fl_lat', 'fl_lon', 'fl_alt', 'course', 'roll', 'pitch']  # Rename the columns
    # track_df['time'] = pd.to_datetime(track_df['time'])

    track_df = track_df.groupby('time', as_index=False).mean()
    # print(track_df)

    # ubx_data = pd.read_csv(ubx_data_loc)
    # ubx_data['datetime'] = pd.to_datetime(ubx_data['datetime'])
    ubx_data = pd.DataFrame(np.array(h5py.File(ubx_data_loc)[ubx_data_loc.split('/')[-1][:-3]]))
    ubx_data.columns = ['time', 'lat', 'lon', 'const', 'prn', 'band', 'ele', 'az', 'C_N0']  # Rename the columns
    
    merged_df = pd.merge(track_df, ubx_data, on = 'time', how='inner') 
    SPs = get_SP(merged_df['fl_lat'], merged_df['fl_lon'], merged_df['fl_alt'], merged_df['az'], merged_df['ele'])
    merged_df['SP_lat'] = SPs[:,0]
    merged_df['SP_lon'] = SPs[:,1]
    merged_df['time'] = merged_df['time'].astype('int64') 

    dtype = np.dtype([
        ('time', 'i8'),
        ('fl_lat', 'f8'),
        ('fl_lon', 'f8'),
        ('fl_alt', 'f8'),
        ('course', 'f8'),
        ('roll', 'f8'),
        ('pitch', 'f8'),
        ('lat', 'f8'),
        ('lon', 'f8'),
        ('const', 'S2'),
        ('prn', 'i8'),
        ('band', 'S2'),
        ('ele', 'f8'),
        ('az', 'f8'),
        ('C_N0', 'i8'),
        ('SP_lat', 'f8'),
        ('SP_lon', 'f8')
    ])
    struct_arr = np.array(list(merged_df.to_records(index=False)), dtype=dtype)
    # print(merged_df.head())


    with h5py.File(f"{out_dir}/{track_df_loc.split('/')[-1].split('.')[0][:-4]}_SP.h5", 'w') as f:
        dset = f.create_dataset(f"{track_df_loc.split('/')[-1].split('.')[0][:-4]}_SP", data=struct_arr)
    print(f"Output: {out_dir}/{track_df_loc.split('/')[-1].split('.')[0][:-4]}_SP.h5")

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 4:
        print("Usage: python calculate_SP.py <processed_gpx_file_location> <processed_ublox_file_location>")
        sys.exit(1)

    # Get the file location from the command line argument
    flight_file_location = sys.argv[1]
    ubx_file_location = sys.argv[2]
    out_dir = sys.argv[3]

    # Create the file
    calculate_SP(flight_file_location, ubx_file_location, out_dir)