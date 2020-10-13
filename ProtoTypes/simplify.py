"""
Test file for simplifying a gpx file using gpx.simplify 
"""
import os
import utm
import requests
import sys
import gpxpy
import gpxpy.gpx
import gpxpy.geo as mod_geo
import json
import pprint
# import xml.etree.ElementTree as ET


 # pk.eyJ1IjoianVuZWJ1Z2d5IiwiYSI6ImNrY2YyMnE1eDBidmkyemsyOWZjbzU0Z24ifQ.mCT9XQLM_LyYO25qTN7xUQ 
def callMapBox(coords : list):
    """
    Takes a gpx file, opens it, simplifies, gets coords, calls mapbox, 
    outputs route generated by mapbox 


    Considerations: 
        user gives gpx
        server reads and simplifies gpx based on number of points
        one mapbox call == 25 points

        do untill processed all points
            in increments of 25 points 
                call mapbox api with coordinates
                reciveve mabox coordinates and que sheet
                compare differences between user and mapbox coordinates
                if n coordinates differ by x amount 
                    run api again on an unsimplified version of that segment
                    do untill no diff for that segment
                
                if no major differences between user gpx and mapbox coords,
                    add instructions to que sheet
        
        present que sheet to user 

    """
   
# for elem in tree.findall("{http://www.topografix.com/GPX/1/1}wpt"):
#     print elem.attrib['lon'], elem.attrib['lat']

#     pp = pprint.PrettyPrinter(indent=4)

#     gpx_file = open(sys.argv[1], 'r')
#     mygpx = gpxpy.parse(gpx_file)
    
#     mygpx.simplify(300)
#     data_dict = xmltodict.parse(mygpx.to_xml()) 

#     tree = ET.parse(mygpx.to_xml())

#     result = json.dumps(data_dict)
#     pp.pprint(result)

    print("COORDS ARE ")

    print(coords)

    coordstring = ""
    for item in coords: 
        coordstring += f"{item[0]},{item[1]}"
        if item is not coords[-1]:
            coordstring += ";"
    print(coordstring)

        #73.99090404350912%2C40.727064885724246%3B-73.98744586616424%2C40.733505271200954

    payload = {"geometries" : "geojson","steps": "true",
                "access_token" : "pk.eyJ1IjoianVuZWJ1Z2d5IiwiYSI6ImNrY2YyMnE1eDBidmkyemsyOWZjbzU0Z24ifQ.mCT9XQLM_LyYO25qTN7xUQ" }
    
    # &geometries=geojson&steps=true&access_token=YOUR_MAPBOX_ACCESS_TOKEN
    
    r = requests.get(f"https://api.mapbox.com/directions/v5/mapbox/cycling/{coordstring}", params=payload)
    # print(r.url)
    # print(r.text)
  
    return json.loads(r.text)

    #  https://api.mapbox.com/directions/v5/cycling/{coordinates} 


def giveCueSheet(mygpx=None):
    """
    Returns a cuesheet JSON object -- a list of turn instructions provided by the mapbox Navigation API 
    Cuesheet Object is of format: 
    {cuesheet:
        [{
            "number" : INSTRUCTION NUMBER, 
            "Manuver" : TURN INSTRUCTION,                                 
            "coordinate" : [LON, LAT],
            'distance' : DISTANCE (meters?) 
        }]
    """

    # TODO need to change it so that we get the file from the website
    if mygpx is None:
        gpx_file = open(sys.argv[1], 'r')
        mygpx = gpxpy.parse(gpx_file)
    

    print(f"{len(mygpx.tracks[0].segments[0].points) } Before Simplification!")
    mygpx.simplify(100)

    print(f"{len(mygpx.tracks[0].segments[0].points) } after simplification!")
    # coordlists = []    
    
    #break the track into 25 point pieces
    #each 25 coord list is stored in coordlists
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    allpoints = [(pt.longitude, pt.latitude) for pt in mygpx.tracks[0].segments[0].points]
    coordlists = [allpoints[i:i + 25] for i in range(0, len(allpoints), 25)]
    # for track in mygpx.tracks:
    #     for segment in track.segments:
    #         i = 0
    #         l = []
    #         for point in segment.points:
    #             if i >= 25: 
    #                 i = 0
    #                 coordlists.append(l)
    #                 l = []
    #                 print("API LIMIT REACHED, NEED ANOTHER CALL")
        
    #             l.append((point.longitude, point.latitude))
    #             i+=1
    #         if i is not 0:
    #             coordlists.append(l)
                

        # print(f"There were {i} many points in the gpx file after simplification")
    print(f"Coords were split into {len(coordlists)} API calls ")
    # output = open("out.gpx", "w")
    # outmb = open("out.geojson", "w")
    jsonlist = []
    #get dict of location and directions for each 25 pt segment
    cuesheet = []
    i = 0
    for routsegment in coordlists: 
        j = callMapBox(routsegment)
        
        for leg in j["routes"][0]["legs"]:
            for step in leg['steps']:

                if step["maneuver"]["type"] == "turn":
                    cuesheet.append({"number" : i, "Manuver" : step["maneuver"]["instruction"], 
                                    "coordinate" :step["maneuver"]["location"], 'distance' : step["distance"]})
                    i+=1
    cuej = {"cuesheet" : cuesheet}
    pprint.pprint(cuej)
    return cuej

    # {"cuesheet" : [{number : 0, manuver : "instruction goes here", "coordinate": [lat,long]}]}
def main():
    gpx_file = open(sys.argv[1], 'r')
    mygpx = gpxpy.parse(gpx_file)
    pprint.pprint(giveCueSheet(mygpx))

    #merge the jsons generated by the API -- dont need to do this anymore 
    # merged = {}
    # for j in jsonlist:
    #     merged.update(j)

    # create json with only location and instruction 

    # print(merged)
    # json.dump(j,outmb)
    # outmb.close()
    # output.close()



if __name__ == "__main__":
    main()