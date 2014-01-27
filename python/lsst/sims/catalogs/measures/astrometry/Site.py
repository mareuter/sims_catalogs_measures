""" Site Class

    Class defines the attributes of the site unless overridden
    ajc@astro 2/23/2010
    
    Restoring this so that the astrometry mixin in Astrometry.py
    can inherit the site information
    danielsf 1/27/2014

"""

class Site (object):
    """ Class  describes the defintions of types of InstanceClasses"""
    def __init__(self):
        self.parameters = {"longitude":-1.2320792, "latitude" :
            -0.517781017, "height" : 2650, "xPolar" : 0., "yPolar" : 0.,
            "meanTemperature" : 284.655, "meanPressure" : 749.3,
            "meanHumidity" : 0.40, "lapseRate" : 0.0065}
