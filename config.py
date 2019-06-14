# Thingsboard platform credentials
PUBLISH_THINGSBOARD = True                  # change to False if not needed
THINGSBOARD_HOST = 'demo.thingsboard.io'    # Thingsboard host address
ACCESS_TOKEN = ''                           # Your device Access Token of Thingsboard

PUBLISH_OPEN_SENSE_MAP = True                   # change to False if not needed
SENSEBOX_ID = ''                                # Your Sensebox Token
SENSEBOX_PM25_ID = ''                           # Your Sensebox PM25 Token
SENSEBOX_PM10_ID = ''                           # Your Sensebox PM10 Token

PM_USB = '/dev/ttyUSB0'

MEASURE_TIME = 15 # after x seconds the data will be published, to avoid traffic
MEASURE_INTERVAL = 2 # every x seconds PM will be meaured

DEVICE_NAME = 'MyRPI-PM_Sensor'
MEASURE_ON_START = True