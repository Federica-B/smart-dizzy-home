# code for CUSTOM communication on our serial
# GET something start the code with 7xx
# SET something start the code with 8xx

# response to correctly recived request GET start the code with 2xx
# response to correctly recived request SET start the code with 3xx
# response to not correctly recive request start the code with 4xx

# the final two number xx represent the resorse on with an action is act uppon

# the resorse are:
    # device ID -> I -> 73
    # value of the sensing -> V -> 86
    # state of the device -> S -> 83
    # resorse on the EEPROM -> E -> 69

# In this case we have:         CODE        CODE_CORRECT_RESPONSE
    # REQUEST ID            |   773     |   273
    # REQUEST SENS VALUE    |   786     |   286
    # REQUEST CONF VALUE    |   769     |   268

    # UPDATE CONF VALUE     |   869     |   368
    # UPDATE STATE          |   883     |   383

# incorrect code:
    # ERROR_CRC             |   400
    # ERROR_STRING_TO_LONG  |   401
    # INVALID_REQUEST_CODE  |   403
    # INCORRECT_VALUE_STATE |   483
    # INCORRECT_VALUE_CONF  |   469

# CODE

CODE_REQUEST_ID = '773'
CODE_REQUEST_SENS_VALUE = '786'
CODE_REQUEST_CONF_VALUE = '769'

CODE_UPDATE_CONF_VALUE = '869'
CODE_UPDATE_STATE = '883'


# CORRECT RESPONSE
CORRECT_CODE_REQUEST_ID = '273'
CORRECT_CODE_REQUEST_SENS_VALUE = '286'
CORRECT_CODE_REQUEST_CONF_VALUE = '269'

CORRECT_CODE_UPDATE_CONF_VALUE = '369'
CORRECT_CODE_UPDATE_STATE = '383'

# ERROR CODE
ERROR_CRC = '400'
ERROR_STRING_TO_LONG = '401'
INVALID_REQUEST_CODE = '403'
INCORRECT_VALUE_STATE = '483'
INCORRECT_VALUE_CONF = '469'