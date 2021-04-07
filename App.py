from flask import Flask, render_template, request
import urllib, urllib.request, json
import os, re, datetime
from Token import token
import urllib.parse

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET','POST'])

def index() : 
    #by default show Copenhagen weather
    mycity = "Copenhagen"
    now = datetime.datetime.now()
    key ="123094"
    #get weather forcast now
    resultForcast = getForcast(key)
    localTime = resultForcast[0]
    temperature = resultForcast[1]
    isDayTime = resultForcast[2]
    if isDayTime :
        isDayTime = "../static/img/day2.jpg"
    else :
        isDayTime = "../static/img/night.jpg"
    weatherIcon = resultForcast[3]
    print(weatherIcon)
    #get weather forcast next 5 days
    forcast5Days = getForcast5Days(key)
    

    if request.method == 'POST' :
        #get entered city to search weather conditions for
        resultLocation = getLocation(mycity)
        key = resultLocation[0]
        mycity = resultLocation[1]
        #get weather forcast now
        resultForcast = getForcast(key)
        localTime = resultForcast[0]
        temperature = resultForcast[1]
        isDayTime = resultForcast[2]
        if isDayTime :
            isDayTime = "../static/img/day2.jpg"
        else :
            isDayTime = "../static/img/night.jpg"
        weatherIcon = resultForcast[3]
        #get forcast next 5 days
        forcast5Days = getForcast5Days(key)

    return render_template("index.html",
        weatherIcon = "../static/img/icons/" + str(weatherIcon) + ".svg",
        isDayTime = isDayTime,
        cityName = mycity,
        temperature = temperature,
        todayIs = now.strftime("%A"),
        todayDate = now.strftime("%d/%m/%y %H:%M %p"),
        forcast5Days = forcast5Days)

#method get city ID
def getLocation(city) :
    mycity = request.form['cityEntered']
    mycity = urllib.parse.quote(mycity)
    addressURL = "http://dataservice.accuweather.com/locations/v1/cities/search?apikey=" + token + "&q=" + mycity    
    with urllib.request.urlopen(addressURL) as addressURL :
        data = json.loads(addressURL.read().decode())
        print(mycity)
        print(data)
    location_key = data[0]["Key"]
    englishName = data[0]["EnglishName"]
    return location_key, englishName
    
#method get weather forcast now
def getForcast(location_key) :
    forcastURL = "http://dataservice.accuweather.com/currentconditions/v1/" + location_key + "?apikey=" + token
    with urllib.request.urlopen(forcastURL) as forcastURL :
        data = json.loads(forcastURL.read().decode())
        print(data)
    localTime = data[0]["EpochTime"]
    temperatureMetricValue = data[0]["Temperature"]["Metric"]["Value"]
    isDayTime = data[0]["IsDayTime"]
    weatherIcon = data[0]["WeatherIcon"]
    return localTime, temperatureMetricValue, isDayTime, weatherIcon

#method get weather forcast next 5 days       
def getForcast5Days(location_key) :
    forcast5DaysURL = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + location_key + "?apikey=" + token
    with urllib.request.urlopen(forcast5DaysURL) as forcast5DaysURL :
        data = json.loads(forcast5DaysURL.read().decode())
        print(data["DailyForecasts"])
    #data manipulation
    for row in data["DailyForecasts"] :
        row["Date"] = datetime.datetime.strptime(row["Date"], '%Y-%m-%dT%H:%M:%S%z')
        row["Date"] = row["Date"].strftime("%a")
        row["Day"]["Icon"] = "../static/img/icons/" + str(row["Day"]["Icon"]) + ".svg"
        row["Temperature"]["Maximum"]["Value"] = round((row["Temperature"]["Maximum"]["Value"] - 32) * 5.0/9.0)
    return data 


if __name__ == '__main__' :
    app.run('localhost', 4449)
