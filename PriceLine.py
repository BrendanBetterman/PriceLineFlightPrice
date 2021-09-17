import sys, os, pyodbc, json, math , http.client
from datetime import date
from datetime import datetime

#This Project was Created By Brendan
#https://rapidapi.com/tipsters/api/priceline-com-provider/
#Register account through rapidapi

Flights = ["JFK","BOS","DFW"] #Airports
Key = "key"
DataDir = r'directory'
StartAirport = "MSP"
def connectDB():
    con_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+ DataDir +';'
    conn = pyodbc.connect(con_string)
    print("Connected To Database")
    return conn
def disconnectDB(conn):
    conn.close()
    print("Discconected From Database")
def pushDB(conn,today,dest,depAirline,depFlightNo,retAirline,fare):
    now = datetime.now()
    time = datetime(1899, 12, 30, now.hour, now.minute)
    sql="""Insert into Flights ([Date],[time],[start],[dest],[depAirline],[depFlightNo],[retAirline],[fare]) values (?,?,?,?,?,?,?,?)"""
    conn.execute(sql,(today,time,StartAirport,dest,depAirline,depFlightNo,retAirline,fare))
def flight(where):
    try:
        conn = http.client.HTTPSConnection("priceline-com-provider.p.rapidapi.com")
        headers = {
            'x-rapidapi-host': "priceline-com-provider.p.rapidapi.com",
            'x-rapidapi-key': Key
            }
        conn.request("GET", "/v1/flights/search?class_type=ECO&location_departure="+StartAirport+"&itinerary_type=ROUND_TRIP&location_arrival="+where+"&date_departure=2021-11-16&sort_order=PRICE&number_of_passengers=1&date_departure_return=2021-11-22&price_max=20000&duration_max=2051&price_min=100", headers=headers)
        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8")
    except:
        print("Couldn't record" + where)
def parseFlight(conn,where,today):
    flightJSON = json.loads(flight(where))
    flightInfo = (flightJSON["pricedItinerary"][0]["pricingInfo"]["itineraryReference"]["token"])
    flightPrice = (flightJSON["pricedItinerary"][0]["pricingInfo"]["totalFare"])
    try:
        flightAirline = (flightJSON["pricedItinerary"][0]["pricingInfo"]["ticketingAirline"])
    except:
        flightBaggage = (flightJSON["pricedItinerary"][0]["baggageURL"])
        flightAirline = flightBaggage[len(flightBaggage)-3:len(flightBaggage)-1]
    flightNoIndex = flightInfo.find(flightAirline)
    if (flightInfo[flightNoIndex+6] == "-"):
        flightNo = flightAirline + " " + flightInfo[flightNoIndex+2:flightNoIndex +5]
    else:
        flightNo = flightAirline + " " + flightInfo[flightNoIndex+2:flightNoIndex +6]
    print("Flight Number " + flightNo)
    print( math.floor(flightPrice))
    print("Airline " + flightAirline)
    pushDB(conn,today,where,flightAirline,flightNo,flightAirline,math.floor(flightPrice))
def main():
    dateTimeObj = datetime.now()
    today =  dateTimeObj.strftime("%d-%b-%Y")
    conn = connectDB()
    for i in Flights:
        parseFlight(conn,i,today)
    disconnectDB(conn)
main()
