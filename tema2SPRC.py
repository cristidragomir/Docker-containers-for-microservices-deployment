from flask import Flask, request, Response
from flask.json import jsonify
import json

import psycopg2

app = Flask(__name__)

def connectToDb():
    return psycopg2.connect(host="db_container", port = 5432, database="myDb", user="postgres", password="docker")

def checkIfStringIsFloat(x):
    try:
        conversion = float(x)
    except (TypeError, ValueError):
        return False
    else:
        return True

def checkIfStringIsInteger(x):
    try:
        conversion = int(x)
    except (TypeError, ValueError):
        return False
    else:
        return True

def checkIfStringIsDate(dateStr):
    if len(dateStr) != len("AAAA-LL-ZZ"):
        return False
    substr = dateStr[0:4]
    if substr.isdigit() == False:
        return False
    if dateStr[4] != '-':
        return False
    substr = dateStr[5:7]
    if substr.isdigit() == False:
        return False
    if dateStr[7] != '-':
        return False
    substr = dateStr[8:10]
    if substr.isdigit() == False:
        return False
    return True

@app.route("/api/countries", methods=["GET"])
def getCountries():
    conn = connectToDb()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM Tari""")
    queryRes = cur.fetchall()
    cur.close()
    conn.close()
    resToRet = []
    for tupleVar in queryRes:
        tupleToList = list(tupleVar)
        resToRet.append({"id" : int(tupleToList[0]), "nume" : str(tupleToList[1]), 
            "lat" : float(tupleToList[2]), "lon" : float(tupleToList[3])})
    return jsonify(resToRet), 200

@app.route("/api/countries", methods=["POST"])
def postCountry():
    conn = connectToDb()
    cur = conn.cursor()
    
    sentJsonToServer = request.json
    codeToRet = 201
    if sentJsonToServer is not None and "nume" in sentJsonToServer and "lat" in sentJsonToServer and "lon" \
        in sentJsonToServer and sentJsonToServer["nume"] != "":
        nameToFind = sentJsonToServer['nume']
        cur.execute("""SELECT * FROM Tari WHERE nume_tara LIKE %s""", (str(nameToFind),))
        queryRes = cur.fetchall()
        if len(queryRes) == 0:
            if checkIfStringIsInteger(sentJsonToServer["lat"]) and checkIfStringIsFloat(sentJsonToServer["lon"]):
                nameToInsert = sentJsonToServer["nume"]
                latToInsert = sentJsonToServer["lat"]
                lonToInsert = sentJsonToServer["lon"]
                cur.execute("""insert into Tari (nume_tara, latitudine, longitudine) values (%s, %s, %s)""",
                    (nameToInsert, latToInsert, lonToInsert,))
                conn.commit()
            else:
                codeToRet = 400
        else:
            codeToRet = 409
    else:
        codeToRet = 400
    
    idToRet = -1
    if codeToRet == 201:
        cur.execute("""SELECT * FROM Tari WHERE nume_tara LIKE %s""", (str(sentJsonToServer["nume"]),))
        queryRes = cur.fetchall()
        idToRet = int(list(queryRes[0])[0])
        cur.close()
        conn.close()
        return jsonify({'id':idToRet}), codeToRet
    else:
        cur.close()
        conn.close()
        return Response(status=codeToRet)

@app.route("/api/countries/<int:recvId>", methods=["PUT"])
def modifyCountry(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    codeToRet = 200
    sentJsonToServer = request.json
    countryNewId = -1
    countryNewName = ""
    countryNewLat = -1
    countryNewLon = -1
    if sentJsonToServer is not None and "id" in sentJsonToServer and "nume" in sentJsonToServer \
        and "lat" in sentJsonToServer and "lon" in sentJsonToServer:
        if checkIfStringIsInteger(sentJsonToServer["id"]) and checkIfStringIsFloat(sentJsonToServer["lat"]) \
            and checkIfStringIsFloat(sentJsonToServer["lon"]):       
            countryNewId = int(sentJsonToServer["id"])
            countryNewName = str(sentJsonToServer["nume"])
            countryNewLat = float(sentJsonToServer["lat"])
            countryNewLon = float(sentJsonToServer["lon"])
        else:
            codeToRet = 400
    else:
        codeToRet = 400
    if codeToRet != 400 and recvId != -1:
        cur.execute("""SELECT * FROM Tari WHERE id = %s""", (recvId,))
        queryRes = cur.fetchall()
        if len(queryRes) > 0:
            cur.execute("""SELECT * FROM Tari WHERE id = %s""", (countryNewId,))
            queryRes = cur.fetchall()
            if len(queryRes) > 0:
                codeToRet = 409

            if codeToRet != 409:
                cur.execute("""SELECT * FROM Tari WHERE nume_tara = %s""", (countryNewName,))
                queryRes = cur.fetchall()
                if len(queryRes) > 0:
                    codeToRet = 409

            if codeToRet != 409:
                cur.execute("""UPDATE Tari SET id = %s, nume_tara = %s, latitudine = %s, longitudine = %s WHERE id = %s""", \
                    (countryNewId, countryNewName, countryNewLat, countryNewLon, recvId))
                conn.commit()
        else:
            codeToRet = 404
    
    cur.close()
    conn.close()
    return Response(status=codeToRet)

@app.route("/api/countries/<int:recvId>", methods=["DELETE"])
def deleteCountry(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    codeToRet = 200
    if type(recvId) != int:
        codeToRet = 400
    else:
        cur.execute("""SELECT * FROM Tari WHERE id = %s""", (recvId,))
        queryRes = cur.fetchall()
        if (len(queryRes) > 0):
            cur.execute("""DELETE FROM Tari WHERE id = %s""", (recvId,))
            conn.commit()
        else:
            codeToRet = 404
    
    cur.close()
    conn.close()
    return Response(status=codeToRet)

@app.route("/api/cities", methods=["GET"])
def getCities():
    conn = connectToDb()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM Orase""")
    queryRes = cur.fetchall()
    cur.close()
    conn.close()
    resToRet = []
    for tupleVar in queryRes:
        tupleToList = list(tupleVar)
        resToRet.append({"id" : int(tupleToList[0]), "idTara" : int(tupleToList[1]), "nume" : str(tupleToList[2]), \
            "lat" : float(tupleToList[3]), "lon" : float(tupleToList[4])})
    return jsonify(resToRet), 200

@app.route("/api/cities/country/<int:id_Tara>", methods=["GET"])
def getCitiesByCountry(id_Tara):
    conn = connectToDb()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM Orase WHERE id_tara = %s""", (id_Tara,))
    queryRes = cur.fetchall()
    cur.close()
    conn.close()
    resToRet = []
    for tupleVar in queryRes:
        tupleToList = list(tupleVar)
        resToRet.append({"id" : int(tupleToList[0]), "idTara" : int(tupleToList[1]), "nume" : str(tupleToList[2]),
            "lat" : float(tupleToList[3]), "lon" : float(tupleToList[4])})
    return jsonify(resToRet), 200

@app.route("/api/cities", methods=["POST"])
def postCities():
    conn = connectToDb()
    cur = conn.cursor()
    
    sentJsonToServer = request.json
    codeToRet = 201
    if sentJsonToServer is not None and "idTara" in sentJsonToServer is not None:
        if checkIfStringIsInteger(sentJsonToServer["idTara"]):    
            cur.execute("""SELECT * FROM Tari WHERE id = %s""", (str(sentJsonToServer["idTara"]),))
            queryRes = cur.fetchall()
            if len(queryRes) == 0:
                codeToRet = 400
        else:
            codeToRet = 400
    else:
        codeToRet = 400

    if codeToRet != 400 and sentJsonToServer is not None and "idTara" in sentJsonToServer and "nume" in sentJsonToServer \
        and "lat" in sentJsonToServer and "lon" in sentJsonToServer and sentJsonToServer["nume"] != "":
        nameToCheck = sentJsonToServer['nume']
        countryIdToCheck = sentJsonToServer['idTara']
        cur.execute("""SELECT * FROM Orase WHERE nume_oras LIKE %s AND id_tara = %s""", (str(nameToCheck), int(countryIdToCheck),))
        queryRes = cur.fetchall()
        if len(queryRes) == 0:
            if checkIfStringIsInteger(sentJsonToServer["idTara"]) and checkIfStringIsFloat(sentJsonToServer["lat"]) \
                and checkIfStringIsFloat(sentJsonToServer["lon"]):
                countryIdToInsert = int(sentJsonToServer["idTara"])
                nameToInsert = str(sentJsonToServer["nume"])
                latToInsert = float(sentJsonToServer["lat"])
                lonToInsert = float(sentJsonToServer["lon"])
                cur.execute("""insert into Orase (id_tara, nume_oras, latitudine, longitudine) values (%s, %s, %s, %s)""", \
                    (countryIdToInsert, nameToInsert, latToInsert, lonToInsert,))
                conn.commit()
            else:
                codeToRet = 400
        else:
            codeToRet = 409
    else:
        codeToRet = 400
    
    idToRet = -1
    if codeToRet == 201:
        cur.execute("""SELECT * FROM Orase WHERE nume_oras = %s""", (str(sentJsonToServer["nume"]),))
        queryRes = cur.fetchall()
        idToRet = int(list(queryRes[0])[0])
        cur.close()
        conn.close()
        return jsonify({'id':idToRet}), codeToRet
    else:
        cur.close()
        conn.close()
        return Response(status=codeToRet)

@app.route("/api/cities/<int:recvId>", methods=["PUT"])
def modifyCity(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    codeToRet = 200
    sentJsonToServer = request.json
    cityNewId = -1
    cityNewCountryId = -1
    cityNewName = ""
    cityNewLat = -1
    cityNewLon = -1
    if sentJsonToServer is not None and "id" in sentJsonToServer and "idTara" in sentJsonToServer \
        and "nume" in sentJsonToServer and "lat" in sentJsonToServer and "lon" in sentJsonToServer:
        if checkIfStringIsInteger(sentJsonToServer["id"]) and checkIfStringIsInteger(sentJsonToServer["idTara"]) and checkIfStringIsFloat("lat") and checkIfStringIsFloat("lon"):
            cityNewId = int(sentJsonToServer["id"])
            cityNewCountryId = int(sentJsonToServer["idTara"])
            cityNewName = str(sentJsonToServer["nume"])
            cityNewLat = float(sentJsonToServer["lat"])
            cityNewLon = float(sentJsonToServer["lon"])
        else:
            codeToRet = 400
    else:
        codeToRet = 400
    if codeToRet != 400:
        cur.execute("""SELECT * FROM Orase WHERE id = %s""", (recvId,))
        queryRes = cur.fetchall()
        if (len(queryRes) > 0):
            cur.execute("""SELECT * FROM Orase WHERE id = %s""", (cityNewId,))
            queryRes = cur.fetchall()
            if (len(queryRes) > 0):
                codeToRet = 409

            if codeToRet != 409:
                cur.execute("""SELECT * FROM Orase WHERE nume_oras LIKE %s AND id_tara = %s""", (cityNewName, cityNewCountryId,))
                queryRes = cur.fetchall()
                if (len(queryRes) > 0):
                    codeToRet = 409

            cur.execute("""SELECT * FROM Tari WHERE id = %s""", (cityNewCountryId,))
            queryRes = cur.fetchall()
            if (len(queryRes) == 0):
                codeToRet = 400

            if codeToRet != 409 and codeToRet != 400:
                cur.execute("""UPDATE Orase SET id = %s, id_tara = %s, nume_oras = %s, latitudine = %s, longitudine = %s WHERE id = %s""", \
                    (cityNewId, cityNewCountryId, cityNewName, cityNewLat, cityNewLon, recvId))
                conn.commit()
        else:
            codeToRet = 404
    
    cur.close()
    conn.close()
    return Response(status=codeToRet)

@app.route("/api/cities/<int:recvId>", methods=["DELETE"])
def deleteCity(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    codeToRet = 200
    if type(recvId) != int:
        codeToRet = 400
    else:
        cur.execute("""SELECT * FROM Orase WHERE id = %s""", (recvId,))
        queryRes = cur.fetchall()
        if (len(queryRes) > 0):
            cur.execute("""DELETE FROM Orase WHERE id = %s""", (recvId,))
            conn.commit()
        else:
            codeToRet = 404
    
    cur.close()
    conn.close()
    return Response(status=codeToRet)

@app.route("/api/temperatures", methods=["POST"])
def postTemp():
    conn = connectToDb()
    cur = conn.cursor()
    
    sentJsonToServer = request.json
    codeToRet = 201
    if sentJsonToServer is not None and "idOras" in sentJsonToServer:
        cur.execute("""SELECT * FROM Orase WHERE id = %s""", (str(sentJsonToServer["idOras"]),))
        queryRes = cur.fetchall()
        print(queryRes)
        if len(queryRes) == 0:
            codeToRet = 400
    else:
        codeToRet = 400

    if codeToRet != 400 and sentJsonToServer is not None and "idOras" in sentJsonToServer and "valoare" in sentJsonToServer:
        if checkIfStringIsFloat(sentJsonToServer["valoare"]) and checkIfStringIsInteger(sentJsonToServer["idOras"]):
            cityIdToInsert = int(sentJsonToServer["idOras"])
            valToInsert = float(sentJsonToServer["valoare"])
            cur.execute("""insert into Temperaturi (id_oras, valoare) values (%s, %s)""", (str(cityIdToInsert), str(valToInsert),))
            conn.commit()
        else:
            codeToRet = 400
    else:
        codeToRet = 400
    
    idToRet = -1
    if codeToRet == 201:
        cur.execute("""SELECT id FROM Temperaturi ORDER BY timestamp DESC LIMIT 1""")
        queryRes = cur.fetchall()
        idToRet = int(list(queryRes[0])[0])
        cur.close()
        conn.close()
        return jsonify({'id':idToRet}), codeToRet
    else:
        cur.close()
        conn.close()
        return Response(status=codeToRet)

@app.route("/api/temperatures/<int:recvId>", methods=["PUT"])
def modifyTemp(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    codeToRet = 200
    sentJsonToServer = request.json
    countryNewId = -1
    countryNewName = ""
    countryNewLat = -1
    countryNewLon = -1
    if sentJsonToServer is not None and "id" in sentJsonToServer and "idOras" in sentJsonToServer and "valoare" in sentJsonToServer:
        if checkIfStringIsInteger(sentJsonToServer["idOras"]) and checkIfStringIsFloat(sentJsonToServer["valoare"]):
            tempNewId = int(sentJsonToServer["id"])
            tempNewCityId = int(sentJsonToServer["idOras"])
            tempNewVal = float(sentJsonToServer["valoare"])
        else:
            codeToRet = 400
    else:
        codeToRet = 400
    if codeToRet != 400 and recvId != -1:
        cur.execute("""SELECT * FROM Temperaturi WHERE id = %s""", (recvId,))
        queryRes = cur.fetchall()
        if len(queryRes) > 0:
            cur.execute("""SELECT * FROM Temperaturi WHERE id = %s""", (tempNewId,))
            queryRes = cur.fetchall()
            if (len(queryRes) > 0):
                codeToRet = 409

            cur.execute("""SELECT * FROM Orase WHERE id = %s""", (tempNewCityId,))
            queryRes = cur.fetchall()
            if (len(queryRes) == 0):
                codeToRet = 400

            if codeToRet != 409 and codeToRet != 400:
                cur.execute("""UPDATE Temperaturi SET id = %s, id_oras = %s, valoare = %s WHERE id = %s""", \
                 (tempNewId, tempNewCityId, tempNewVal, recvId))
                conn.commit()
        else:
            codeToRet = 404
    
    cur.close()
    conn.close()
    return Response(status=codeToRet)

@app.route("/api/temperatures/<int:recvId>", methods=["DELETE"])
def deleteTemp(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    codeToRet = 200
    if type(recvId) != int:
        codeToRet = 400
    else:
        cur.execute("""SELECT * FROM Temperaturi WHERE id = %s""", (recvId,))
        queryRes = cur.fetchall()
        if (len(queryRes) > 0):
            cur.execute("""DELETE FROM Temperaturi WHERE id = %s""", (recvId,))
            conn.commit()
        else:
            codeToRet = 404
    
    cur.close()
    conn.close()
    return Response(status=codeToRet)

@app.route("/api/temperatures/cities/<int:recvId>", methods=["GET"])
def getTempsByCity(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    fromDate = str(request.args.get('from'))
    untilDate = str(request.args.get('until'))

    sqlQuery = "SELECT * FROM Temperaturi WHERE id_oras = " + str(recvId) + " "
    if fromDate != "None" and checkIfStringIsDate(fromDate):
        sqlQuery += "AND DATE(Temperaturi.timestamp) >= '" + fromDate + "'::date "
    if untilDate != "None" and checkIfStringIsDate(untilDate):
        sqlQuery += "AND DATE(Temperaturi.timestamp) < \'" + untilDate + "\'::date + INTERVAL \'1 day\' "

    cur.execute(sqlQuery)
    queryRes = cur.fetchall()

    cur.close()
    conn.close()
    resToRet = []
    for tupleVar in queryRes:
        tupleToList = list(tupleVar)
        resToRet.append({"id" : int(tupleToList[0]), "valoare" : float(tupleToList[1]), "timestamp" : str(tupleToList[2])})
    return jsonify(resToRet), 200

@app.route("/api/temperatures/countries/<int:recvId>", methods=["GET"])
def getTempsByCountry(recvId):
    conn = connectToDb()
    cur = conn.cursor()

    fromDate = str(request.args.get('from'))
    untilDate = str(request.args.get('until'))

    sqlQuery = "SELECT Temperaturi.id, Temperaturi.valoare, DATE(Temperaturi.timestamp) FROM Temperaturi, Orase "
    sqlQuery += "WHERE Orase.id = Temperaturi.id_oras AND Orase.id_tara = " + str(recvId) + " "

    if fromDate != "None" and checkIfStringIsDate(fromDate):
        sqlQuery += "AND DATE(Temperaturi.timestamp) >= '" + fromDate + "'::date "
    if untilDate != "None" and checkIfStringIsDate(untilDate):
        sqlQuery += "AND DATE(Temperaturi.timestamp) < \'" + untilDate + "\'::date + INTERVAL \'1 day\' "

    cur.execute(sqlQuery)
    queryRes = cur.fetchall()

    cur.close()
    conn.close()
    resToRet = []
    for tupleVar in queryRes:
        tupleToList = list(tupleVar)
        resToRet.append({"id" : int(tupleToList[0]), "valoare" : float(tupleToList[1]), "timestamp" : str(tupleToList[2])})
    return jsonify(resToRet), 200

@app.route("/api/temperatures", methods=["GET"])
def getTempsByHeaders():
    conn = connectToDb()
    cur = conn.cursor()
    
    latitude = str(request.args.get('lat'))
    longitude = str(request.args.get('lon'))
    fromDate = str(request.args.get('from'))
    untilDate = str(request.args.get('until'))

    sqlQuery = "SELECT Temperaturi.id, Temperaturi.valoare, DATE(Temperaturi.timestamp) FROM Temperaturi, Orase "
    sqlQuery += "WHERE Temperaturi.id_oras = Orase.id "
    if latitude != "None" and checkIfStringIsFloat(latitude):
        sqlQuery += "AND Orase.latitudine = " + latitude + " "
    if longitude != "None" and checkIfStringIsFloat(longitude):
        sqlQuery += "AND Orase.longitudine = " + longitude + " "
    if fromDate != "None" and checkIfStringIsDate(fromDate):
        sqlQuery += "AND DATE(Temperaturi.timestamp) >= '" + fromDate + "'::date "
    if untilDate != "None" and checkIfStringIsDate(untilDate):
        sqlQuery += "AND DATE(Temperaturi.timestamp) < \'" + untilDate + "\'::date + INTERVAL \'1 day\' "

    cur.execute(sqlQuery)
    queryRes = cur.fetchall()

    cur.close()
    conn.close()
    resToRet = []
    for tupleVar in queryRes:
        tupleToList = list(tupleVar)
        resToRet.append({"id" : int(tupleToList[0]), "valoare" : float(tupleToList[1]), "timestamp" : str(tupleToList[2])})
    return jsonify(resToRet), 200

if __name__ == '__main__':
    app.run('0.0.0.0', port=6000, debug=True)
