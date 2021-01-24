
# MODULES #
import pandas as pd
import math
import argparse
import numpy as np
from re import search


#######################################################################################
# HELPER FUNCTIONS
#######################################################################################

def setup_argparse():
    """set up argparse"""
    ## Input validation to check latitude and longitude of type float
    parser = argparse.ArgumentParser(description="Provides the closest library name, address and popularity for a given latitude and longitude point in the city of Chicago")
    parser.add_argument('latitude', type=float, help='Latitude of a location')
    parser.add_argument('longitude', type=float, help='Longitude of a location')
    return parser.parse_args()

# haversine formula to calculate distance in kilometers
def haversine_dist(lat1, lon1, lat2, lon2): 
      
    # distance between latitudes 
    # and longitudes 
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
  
    # convert to radians 
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
  
    # apply formulae 
    a = (pow(math.sin(dLat / 2), 2) + 
         pow(math.sin(dLon / 2), 2) * 
             math.cos(lat1) * math.cos(lat2)); 
    rad = 6371
    c = 2 * math.asin(math.sqrt(a)) 
    return rad * c 

#######################################################################################
# MAIN PROGRAM
#######################################################################################

def main():
    """main program"""
    #read command line arguments
    args = setup_argparse()
    
    #Fetch Chicago public libraries data and 2018 Visitors by location data
    libraries = pd.read_csv("https://data.cityofchicago.org/resource/x8fc-8rcq.csv")
    visitors = pd.read_csv("https://data.cityofchicago.org/resource/i7zz-iiza.csv")
    
    # Popularity has been calculated using feature scaling through min-max normalization
    #rescaling the range of features to scale the range in [1, 10] 
    #MinMax Normalization Formula used: X_std = (X - X.min) / (X.max - X.min)
    #X_scaled = X_std * (max - min) + min
    visitors['popularity'] = ((visitors['ytd']-min(visitors['ytd']))/(max(visitors['ytd'])-min(visitors['ytd']))*(10-1)+1).apply(math.ceil)
    
    #used regex on libraries data to remove paranthesis and split lat and long from location e.g.,(41.96759739182978, -87.76155426232721) to match with input args
    libraries['location'].replace('[^0-9,.-]','',regex=True, inplace = True)
    libraries[['latitude','longitude']] = libraries['location'].str.split(',',expand=True)
    
    #Calculating Haversine distance from given input to each library
    distances = []
    for row in range(len(libraries)):
        distances.append(haversine_dist(args.latitude, args.longitude, float(libraries.latitude[row]), float(libraries.longitude[row])))
    libraries['distance']= distances
    
    #Choosing the nearest library using the minimum of all the calculated Haversine distances
    nearest_library = np.array(libraries[libraries.distance == min(libraries.distance)])
    nearest_library_name = nearest_library[0][0]
    nearest_library_address = nearest_library[0][2]

    # Exact String matching was not happening between the two datasets due to junk values; hence used regex search function to match with the substring
    for idx in range(len(visitors)):
        if len(nearest_library_name) < len(visitors['location'][idx]):
            match = search(nearest_library_name, visitors['location'][idx])
        else:
            match = search(visitors['location'][idx], nearest_library_name)
             
        if match:
            popularity = visitors['popularity'][idx]
        

    try: 
        print('"{0}" "{1}" "{2}"'.format(nearest_library_name, nearest_library_address, popularity))
    # Test coverage handling mis-match library name between two datasets, so unable to calculate popularity
    except UnboundLocalError as e:
            print('Library name from Libraries dataset did not match with 2018 visitors data; hence skipping popularity')
            print('"{0}" "{1}" "Unknown"'.format(nearest_library_name, nearest_library_address))



if __name__ == "__main__":
    main()
    

