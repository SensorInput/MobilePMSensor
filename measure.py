import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime
from requests import post
from sds011 import SDS011
from time import sleep
import gpsd
import config

# Thingsboard platform credentials
PUBLISH_THINGSBOARD = config.PUBLISH_THINGSBOARD
THINGSBOARD_HOST = config.THINGSBOARD_HOST
ACCESS_TOKEN = config.ACCESS_TOKEN

PUBLISH_OPEN_SENSE_MAP = config.PUBLISH_OPEN_SENSE_MAP
SENSEBOX_ID = config.SENSEBOX_ID
SENSEBOX_PM25_ID = config.SENSEBOX_PM25_ID
SENSEBOX_PM10_ID = config.SENSEBOX_PM10_ID
OSM_HEADERS = {"content-type": "application/json"}
osm_post_url = "https://api.opensensemap.org/boxes/" + SENSEBOX_ID + "/data"

PM_USB = config.PM_USB

MEASURE_TIME = config.MEASURE_TIME
MEASURE_INTERVAL = config.MEASURE_INTERVAL

attributes = {
    'name': config.DEVICE_NAME,
    'measuring': config.MEASURE_ON_START
}

# init PM-sensor
pm_sensor = SDS011(PM_USB, use_query_mode=True)
pm_sensor.sleep(sleep=False)
print('started PM - waiting 5 secs')
sleep(5)

# init GPS-sensor
gpsd.connect()
print('started GPS - waiting 5 secs')
sleep(5)


def measure_interval(measure_time_sec=30, measure_interval_sec=2):
    '''
    measure every measure_interval_sec for measure_time_sec (sec)
    and return payloads in json format for publishing all at once to minimize traffic
    :param measure_time_sec: seconds until publishind
    :param measure_interval_sec: measure every second
    :return: thingsboard_payload, osm_payload --> thingsboard and OSM specific payloads
    '''
    next_reading = time.time()
    stop_reading = next_reading + measure_time_sec
    thingsboard_payload = []
    osm_payload = []
    while time.time() < stop_reading:
        # get pm-sensor data
        # pm25, pm10 = round(random.uniform(5.0, 10.0), 2), round(random.uniform(7.0, 15.0), 2)
        pm25, pm10 = pm_sensor.query()
        print('PM25: {pm25}, \tPM10: {pm10}'.format(pm25=pm25, pm10=pm10))

        # get gps-sensor data
        lat, lon = None, None
        try:
            lat, lon = gpsd.get_current().position()
        except Exception as e:
            print(e)
        print('lat: {lat}, \tlon: {lon}'.format(lat=lat, lon=lon))
        timestamp = datetime.now().timestamp() * 1000  # in ms

        # publish to thingsboard
        if PUBLISH_THINGSBOARD:

            measure_data = {
                "ts": timestamp,
                "values": {
                    'PM25': pm25, 'PM10': pm10
                }
            }
            if lon or lat:
                #measure_data['location'] = {
                #    'lat': lat,
                #    'lng': lon
                #}
                measure_data['values']['lat'] = lat
                measure_data['values']['lng'] = lon

            thingsboard_payload.append(measure_data)

        # publish to opensensemap
        if PUBLISH_OPEN_SENSE_MAP:
            osm_timestamp = datetime.utcnow()
            osm_timestamp = osm_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
            pm25_osm_data = {
                "sensor": SENSEBOX_PM25_ID,
                "value": str(pm25),
                "createdAt": osm_timestamp
            }

            pm10_osm_data = {
                "sensor": SENSEBOX_PM10_ID,
                "value": str(pm10),
                "createdAt": osm_timestamp
            }

            if lon or lat:
                pm25_osm_data['location'] = {
                    'lat': lat,
                    'lng': lon
                }
                pm10_osm_data['location'] = {
                    'lat': lat,
                    'lng': lon
                }

            osm_payload.append(pm25_osm_data)
            osm_payload.append(pm10_osm_data)

        next_reading += measure_interval_sec
        sleep_time = next_reading - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
    return thingsboard_payload, osm_payload


def publishValue(client):
    '''
    if attributes['measuring'] == True: loop forever and measure, publish sensor values
    :param client: thingsboard client
    :return:
    '''

    print('Start Measuring and publishing...')
    while attributes['measuring']:
        thingsboard_payload, osm_payload = measure_interval(measure_time_sec=MEASURE_TIME, measure_interval_sec=MEASURE_INTERVAL)
        
        if PUBLISH_THINGSBOARD:
            rc = client.publish('v1/devices/me/telemetry', json.dumps(thingsboard_payload), 1)
            # print(rc)
            print('published to thingsboard')
            #print(payload)
            
        if PUBLISH_OPEN_SENSE_MAP:
            r = post(osm_post_url, json=osm_payload, headers=OSM_HEADERS)
            print('published to OpenSenseMap')
            print('OpenSenseMap HTTP Response:', r.status_code)

# MQTT on_connect callback function
def on_connect(client, userdata, flags, rc):
    '''
    get called when connecting to thingsboard
    :param client: thingsboard mqtt client
    '''
    # print("rc code:", rc)
    client.subscribe('v1/devices/me/rpc/request/+')
    client.publish('v1/devices/me/attributes', json.dumps(attributes), 1)


# MQTT on_message callback function
def on_message(client, userdata, msg):
    '''
    get called, when getting a rpc-message from thingsboard
    :param client: thingsboard mqrr client
    :param msg rpc-message
    '''
    # print('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    if msg.topic.startswith('v1/devices/me/rpc/request/'):
        requestId = msg.topic[len('v1/devices/me/rpc/request/'):len(msg.topic)]
        #get rpc-msg payload
        data = json.loads(msg.payload)
        # compare method string and do something
        # e.g. turning on/off sensor, setting measurement intervall, etc
        # todo
        '''if data['method'] == 'getValue':
            #print("getvalue request\n")
            #print("sent getValue : ", sensor_data)
            client.publish('v1/devices/me/rpc/response/' + requestId, json.dumps(sensor_data['temperature']), 1)
        if data['method'] == 'setValue':
            #print("setvalue request\n")
            params = data['params']
            setValue(params)'''


# create a thingsboard mqtt client instance
client = mqtt.Client()
if PUBLISH_THINGSBOARD:
    try:
        client.on_connect = on_connect
        client.on_message = on_message
        client.username_pw_set(ACCESS_TOKEN)
        client.connect(THINGSBOARD_HOST, 1883, 60)
        client.loop_start()
    except KeyboardInterrupt:
        client.disconnect()
    except Exception as e:
        print(e)
        print('cant connect to thingsboard. set PUBLISH_THINGSBOARD to false')
        PUBLISH_THINGSBOARD = False

# start measuring
try:
    publishValue(client)
except Exception as e:
    print(e)