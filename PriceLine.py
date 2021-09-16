import http.client,sys, os, pyodbc,json,math
from datetime import date
from datetime import datetime

#https://rapidapi.com/tipsters/api/priceline-com-provider/
def pushData(today,dest,depAirline,depFlightNo,retAirline,fare):
    try:
        con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\brend\Documents\Flights.accdb;'
        conn = pyodbc.connect(con_string)
        print("Connected To Database")
        now = datetime.now()
        time = datetime(1899, 12, 30, now.hour, now.minute)
        sql="""Insert into Flights ([Date],[time],[start],[dest],[depAirline],[depFlightNo],[retAirline],[fare]) values (?,?,?,?,?,?,?,?)"""
        conn.execute(sql,(today,time,'msp',dest,depAirline,depFlightNo,retAirline,fare))
        conn.commit() 
    except pyodbc.Error as e:
        print("Error in Connection", e)
        
def flight(where):
    conn = http.client.HTTPSConnection("priceline-com-provider.p.rapidapi.com")

    headers = {
        'x-rapidapi-host': host(------),
        'x-rapidapi-key': key(------)
        }

    conn.request("GET", "/v1/flights/search?class_type=ECO&location_departure=MSP&itinerary_type=ROUND_TRIP&location_arrival="+where+"&date_departure=2021-11-16&sort_order=PRICE&number_of_passengers=1&date_departure_return=2021-11-22&price_max=20000&duration_max=2051&price_min=100", headers=headers)

    res = conn.getresponse()
    data = res.read()
    
    print(data.decode("utf-8"))
    print("\n\n\n")
    return data.decode("utf-8")
def parseFlight(where,today):
    flightJSON = json.loads(flight(where))
    flightInfo = (flightJSON["pricedItinerary"][0]["pricingInfo"]["itineraryReference"]["token"])
    try:
        flightAirline = (flightJSON["pricedItinerary"][0]["pricingInfo"]["ticketingAirline"])
    except:#Not all Flights have a ticketing Airline section
        flightBaggage = (flightJSON["pricedItinerary"][0]["baggageURL"])
        flightAirline = flightBaggage[len(flightBaggage)-3:len(flightBaggage)-1]
    flightPrice = (flightJSON["pricedItinerary"][0]["pricingInfo"]["totalFare"])

    flightNoIndex = flightInfo.find(flightAirline)
    flightNo = flightAirline + " " + flightInfo[flightNoIndex+2:flightNoIndex +6]

    print("Flight Number " + flightNo)
    print( math.floor(flightPrice))
    print("Airline " + flightAirline)
    
    pushData(today,where,flightAirline,flightNo,flightAirline,math.floor(flightPrice))

#JFK BOS DFW
'''
ticketingAirline
B6 = jbu,AA =aal,I\ = Envoy as american eagle
DL = dal,A# = republic airline delta connection
3+ = skywest , 
totalFare


'''
dateTimeObj = datetime.now()
today =  dateTimeObj.strftime("%d-%b-%Y")
try:
    parseFlight("JFK",today)
except:
    print("JFK Couldn't record")
try:  
    parseFlight("BOS",today)
except:
    print("BOS Couldn't record")
try:
    parseFlight("DFW",today)
except:
    print("DFW Couldn't record")

