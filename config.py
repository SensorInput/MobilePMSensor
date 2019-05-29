# Thingsboard platform credentials
PUBLISH_THINGSBOARD = True
THINGSBOARD_HOST = 'demo.thingsboard.io'       #Change IP Address
ACCESS_TOKEN = 'OCX3zXCO6ueXLgyeX00w'

PUBLISH_OPEN_SENSE_MAP = True
SENSEBOX_ID = '5cc58071facf70001a872bef'
SENSEBOX_PM25_ID = '5cc58071facf70001a872bf1'
SENSEBOX_PM10_ID = '5cc58071facf70001a872bf0'

PM_USB = '/dev/ttyUSB0'

MEASURE_TIME = 15 # after x seconds the data will be published, to avoid traffic
MEASURE_INTERVAL = 2 # every x seconds PM will be meaured

DEVICE_NAME = 'MyRPI-PM_Sensor'
MEASURE_ON_START = True