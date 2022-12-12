#!/usr/bin/python3

from influxdb import InfluxDBClient
import sys

def add_influxdb(data):
    """
    exampledata
    {'sensor': 'interior', 'value': -10.45, 'unit': 'C'}
    """
    
    # Koppla upp mot databasen
    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database('embeddedsystem')
    
    
    # Extract data from apipoll
    sensor = data['sensor']
    temperature = float(data['value'])
    unit = data['unit']
    # Skapa JSON för att uppdatera databasen
    json_body = [
            {"measurement": "sensor_data",
                "tags": {"sensor": sensor},
                "fields": {"unit": unit, "value": temperature}}
            ]

    # Skriv till DB och stäng conn
    client.write_points(json_body)
    client.close()
    

if __name__ == '__main__':
    """
    Om du startar skriptet i bg, avsluta den gärna i fg med ctr-c
    """
    pass
