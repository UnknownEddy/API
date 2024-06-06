from functions.geo_calc import get_FresnelZone
import simplekml
import pandas as pd
import datetime
import sys
import numpy as np
import h5py

def calculate_FZone_KML(df_loc, sat_prn, band, out_dir):
    """
    This function calculates the Fresnel Zone of a satellite signal
    Inputs:
    sp_df: DataFrame containing the SP of the satellite signals
    sat_name: Name of the satellite

    Outputs:
    KML file containing SP and FZ of the satellite signals
    """
    # sp_df = pd.read_csv(df_loc)
    sp_df = pd.DataFrame(np.array(h5py.File(df_loc)[df_loc.split('/')[-1][:-3]]))
    # print(sp_df.columns)
    # print(sp_df.head())
    new_df = sp_df[(sp_df['prn'] == sat_prn)].reset_index(drop=True)
    # print(len(new_df))
    new_df = sp_df[(sp_df['prn'] == sat_prn) & (sp_df['band'] == band)].reset_index(drop=True)
    # print(len(new_df))

    kml = simplekml.Kml()
    for i, row in new_df.iterrows():
        lat = float(row['fl_lat'])
        lon = float(row['fl_lon'])
        alt = float(row['fl_alt'])

        el = row['el']
        az = row['az']

        if not el:
            continue
        el = float(el)
        az = float(az)
        lla_FZ = get_FresnelZone(lat, lon, alt, az, el)

        time = datetime.datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S')
        SP_lat = row['SP_lat']
        SP_lon = row['SP_lon']
        FZ_lats = lla_FZ[0]
        FZ_lons = lla_FZ[1]
        
        time_plus1 = time + datetime.timedelta(seconds=1)
        polygon_coords = list(zip(FZ_lons, FZ_lats))

        pol = kml.newpolygon()
        pol.outerboundaryis = polygon_coords
        pol.timespan.begin = time.strftime('%Y-%m-%dT%H:%M:%S')
        pol.timespan.end = time_plus1.strftime('%Y-%m-%dT%H:%M:%S')

        point = kml.newpoint()
        point.coords = [(SP_lon, SP_lat)]
        point.timespan.begin = time.strftime('%Y-%m-%dT%H:%M:%S')
        point.timespan.end = time_plus1.strftime('%Y-%m-%dT%H:%M:%S')

    kml.save(f"{out_dir}/{df_loc.split('/')[-1][:-4]}_FZ.kml")
    print(f"KML file saved: {out_dir}/{df_loc.split('/')[-1][:-4]}_FZ.kml")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python calculate_FZone.py <SP_df_loc> <sat_prn> <band> <output_folder>")
        sys.exit(1)
    calculate_FZone_KML(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
