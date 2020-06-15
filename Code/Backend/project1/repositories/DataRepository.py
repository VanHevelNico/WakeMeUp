from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

#Selects
    @staticmethod
    def read_sensor_by_id(sensorID, wekkerID):
        sql = "SELECT meting from tblMeting WHERE sensorID = %s AND wekkerID = %s ORDER BY Datum DESC"
        params = [sensorID,wekkerID]
        return Database.get_one_row(sql, params)

    @staticmethod
    def read_temperaturen(sensorID, wekkerID):
        sql = "SELECT meting,DATE_FORMAT(datum, '%Y-%m-%d %T') as datum from tblMeting WHERE sensorID = %s AND wekkerID = %s ORDER BY Datum DESC LIMIT 20"
        params = [sensorID,wekkerID]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_alarmen(wekkerID):
        sql = "SELECT idAlarm,kleur,titel,herhaling,lichteffect,status, DATE_FORMAT(tijdstip, '%H:%i') as tijdstip FROM tblProject.tblAlarm WHERE wekkerID = %s"
        params = [wekkerID]
        return Database.get_rows(sql, params)  

    @staticmethod
    def read_alarm_by_id(alarmID, wekkerID):
        sql = "SELECT idAlarm,kleur,titel,herhaling,lichteffect,deuntje,status, DATE_FORMAT(tijdstip, '%H:%i') as tijdstip, DATE_FORMAT(laatsteKeerAfgegaan, '%Y-%m-%d %T') as laatstekeer from tblAlarm WHERE idAlarm = %s AND wekkerID = %s"
        params = [alarmID,wekkerID]
        return Database.get_one_row(sql, params)              

    @staticmethod
    def read_alarmen_aan(wekkerID,vandaag):
        sql = "SELECT idAlarm,kleur,titel,herhaling,lichteffect,deuntje,status, DATE_FORMAT(tijdstip, '%H:%i') as tijdstip, DATE_FORMAT(laatsteKeerAfgegaan, '%Y-%m-%d %T') as laatstekeer FROM tblProject.tblAlarm WHERE wekkerID = %s AND status = 1 AND laatsteKeerAfgegaan < %s"
        params = [wekkerID,vandaag]
        return Database.get_rows(sql, params)   

    @staticmethod
    def read_status_lamp(wekkerID):
        sql = "SELECT * FROM tblProject.tblLedstrip where WekkerID = %s"
        params = [wekkerID]
        return Database.get_one_row(sql, params)     

    @staticmethod
    def read_muziekjes()      :
        sql = "SELECT * FROM tblProject.tblMuziek"
        return Database.get_rows(sql)
        
#Inserts
    @staticmethod
    def insert_meting(meting, Datum, sensorID, wekkerID):
        sql = "INSERT INTO tblMeting (meting,datum,sensorID,wekkerID) VALUES (%s,%s,%s,%s)"
        params = [meting, Datum, sensorID, wekkerID]
        return Database.execute_sql(sql, params)

    @staticmethod
    def insert_alarm(titel,tijdstip,herhaling,lichteffect,deuntje,wekkerID,status,kleur,kleurLedstrip):
        sql = "INSERT INTO tblAlarm (titel,tijdstip,herhaling,lichteffect,deuntje,wekkerID,status,kleur,kleurLedstrip) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [titel,tijdstip,herhaling,lichteffect,deuntje,wekkerID,status,kleur,kleurLedstrip]
        return Database.execute_sql(sql,params)

#Updates
    @staticmethod
    def update_alarm(status,id):
        sql = "UPDATE tblAlarm SET tblAlarm.status = %s WHERE idAlarm = %s"
        params = [status, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_alarm_uit(datum,id):
        sql = "UPDATE tblAlarm SET tblAlarm.laatsteKeerAfgegaan = %s WHERE idAlarm = %s"
        params = [datum, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_lamp_uit(wekkerID):
        sql = "UPDATE tblLedstrip SET status='uit' WHERE wekkerID = %s"
        params = [wekkerID]
        return Database.execute_sql(sql, params) 

    @staticmethod
    def update_lamp_status(wekkerID,status):
        sql = "UPDATE tblLedstrip SET status=%s WHERE wekkerID = %s"
        params = [status,wekkerID]
        return Database.execute_sql(sql, params)                

    @staticmethod
    def update_alarm_alles(titel,tijdstip,herhaling,lichteffect,deuntje,status,kleur,kleurLedstrip,alarmID):
        sql = "UPDATE tblAlarm SET titel=%s,tijdstip=%s,herhaling=%s,lichteffect=%s,deuntje=%s,status=%s,kleur=%s,kleurLedstrip=%s WHERE idAlarm = %s"
        params = [titel,tijdstip,herhaling,lichteffect,deuntje,status,kleur,kleurLedstrip,alarmID]
        return Database.execute_sql(sql,params)        

#Deletes
    @staticmethod
    def delete_alarm(alarmID):
        sql = "DELETE FROM tblAlarm WHERE idAlarm = %s"
        params = [alarmID]
        return Database.execute_sql(sql,params)