import pandas as pd
import os
import xml.dom.minidom as minidom
import pandas as pd
import sys
import h5py
# from functions.NMEA_parser import gps_chksum, extract_GNRMC, extract_GNGGA, extract_GNGSV
# from datetime import datetime

def process_flightlog(file_path, output_folder_location):
    """
    This function read a gpx file and convert it to a pandas dataframe
    Make sure the gpx file has the fillowing structure:
    <gpx>
        <trk>
            <trkseg>
                <trkpt lat="..." lon="...">
                    <ele>...</ele>
                    <time>...</time>
                    <course>...</course>
                    <roll>...</roll>
                    <pitch>...</pitch>
                </trkpt>
            </trkseg>
        </trk>
    </gpx>

    Output is a pandas dataframe with the following columns:
    time, lat, lon, ele, course, roll, pitch
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print ('File does not exist:', file_path)
        return None
    
    try: # Try to read the gpx file using minidom parser
        xml_doc = minidom.parse(file_path)
    except: # If there is an error, print the error and continue to the next file
        print("Error Reading: "+ file_path)
        return None
    
    root = xml_doc.documentElement # Get the root element of the xml file
    trackpoints = root.getElementsByTagName('trkpt') # Get all the trackpoints tags from the xml file

    trackpt_df = pd.DataFrame() # Create an empty dataframe to store the trackpoints data

    for trackpoint in trackpoints: # Loop through each trackpoint
        # Get the latitude and longitude from the trackpoint
        lat = trackpoint.getAttribute('lat') 
        lon = trackpoint.getAttribute('lon')
        
        # Loop through each child of the trackpoint to find ele, time, course, roll, pitch
        for child in trackpoint.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                tag = child.tagName # Get the tag name
                value = child.firstChild.data if child.firstChild else None # Get the value of the tag if it exists
                # print(tag, value)
                # break

                # Store the values in the in corresponding variables
                if tag == 'ele':
                    ele = value
                elif tag == 'time':
                    t = value
                elif tag == 'course':
                    course = value
                elif tag == 'roll':
                    roll = value
                elif tag == 'pitch':
                    pitch = value

        try: # Try to save the values in the dataframe
            row_df = pd.DataFrame([[t, lat, lon, ele, course, roll, pitch]], columns=['time','lat','lon','ele','course','roll','pitch'])
            trackpt_df = pd.concat([trackpt_df, row_df])
        except:
            print ('Error saving row')
            print (row_df)
            continue 

    trackpt_df.reset_index(drop=True, inplace=True) # Reset the index of the dataframe

    # Convert the time column to datetime format
    trackpt_df['time'] = pd.to_datetime(trackpt_df['time']).dt.tz_convert('UTC').round('s')
    trackpt_df['time'] = trackpt_df['time'].dt.tz_localize(None)

    print ("Done Reading: "+ file_path)


    if "/" in file_path:
        file_name = file_path.split("/")[-1]
        file_name_stripped = file_name.split(".")[0]
    else:
        file_name = file_path.split("\\")[-1]
        file_name_stripped = file_name.split(".")[0]
    
    trackpt_df['time'] = trackpt_df['time'].astype('int64') // 10**9 # Convert the time to epoch time
    trackpt_df['lat'] = trackpt_df['lat'].astype(float)
    trackpt_df['lon'] = trackpt_df['lon'].astype(float)
    trackpt_df['ele'] = trackpt_df['ele'].astype(float)
    trackpt_df['course'] = trackpt_df['course'].astype(float)
    trackpt_df['roll'] = trackpt_df['roll'].astype(float)
    trackpt_df['pitch'] = trackpt_df['pitch'].astype(float)

    # trackpt_df.to_csv(f"{output_folder_location}/{file_name_stripped}_gpx.csv", index=False)
    
    with h5py.File(f"{output_folder_location}/{file_name_stripped}_gpx.h5", 'w') as f:
        dset = f.create_dataset(f'{file_name_stripped}_gpx', data=trackpt_df)
        dset.attrs['file_name'] = file_name_stripped
        dset.attrs['col1'] = 'time'
        dset.attrs['col2'] = 'lat'
        dset.attrs['col3'] = 'lon'
        dset.attrs['col4'] = 'ele'
        dset.attrs['col5'] = 'course'
        dset.attrs['col6'] = 'roll'
        dset.attrs['col7'] = 'pitch'
    print (f"Output: {output_folder_location}/{file_name_stripped}_gpx.h5")

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python process_flightlog.py <input_gpx_file_location>")
        sys.exit(1)

    # Get the file location from the command line argument
    input_file_location = sys.argv[1]
    output_folder_location = sys.argv[2]

    # Create the file
    process_flightlog(input_file_location, output_folder_location)