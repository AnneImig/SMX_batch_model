#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np

__logBase10of2 = 3.010299956639811952137388947244930267681898814621085413104274611e-1
__logBase10ofe = 1.0 / np.log(10.0)


logBase10ofe = 1.0 / np.log(10.0)

import sys,math


def normalize(inputvalue, valuemin, valuemax): 
    if valuemax == valuemin:
        print('warning: normalisation returned 0: max and min are the same')
        return 0
    else:
        return (inputvalue - valuemin) / float(valuemax - valuemin)


    
def tidy( x, n):
    
    """Return 'x' rounded to 'n' significant digits."""
    
    if np.isnan(x) == True: 
        return np.NaN
    
    y=abs(x)
    
    if y <= sys.float_info.min: 
        return 0.0
    
    return round( x, int( n-math.ceil(math.log10(y)) ) )

def RoundToSigFigs( x, sigfigs ):
    """
    Rounds the value(s) in x to the number of significant figures in sigfigs.
    Return value has the same type as x.
    Restrictions:
    sigfigs must be an integer type and store a positive value.
    x must be a real value or an array like object containing only real values.
    """
    if not ( type(sigfigs) is int or type(sigfigs) is long or
             isinstance(sigfigs, np.integer) ):
        raise TypeError( "RoundToSigFigs: sigfigs must be an integer." )

    if sigfigs <= 0:
        raise ValueError( "RoundtoSigFigs: sigfigs must be positive." )
    
    if not np.all(np.isreal( x )):
        raise TypeError( "RoundToSigFigs: all x must be real." )

    matrixflag = False
    if isinstance(x, np.matrix): #Convert matrices to arrays
        matrixflag = True
        x = np.asarray(x)
    
    xsgn = np.sign(x)
    absx = xsgn * x
    mantissas, binaryExponents = np.frexp( absx )
    
    decimalExponents = __logBase10of2 * binaryExponents
    omags = np.floor(decimalExponents)

    mantissas *= 10.0**(decimalExponents - omags)
    
    if type(mantissas) is float or isinstance(mantissas, np.floating):
        if mantissas < 1.0:
            mantissas *= 10.0
            omags -= 1.0
            
    else: #elif np.all(np.isreal( mantissas )):
        fixmsk = mantissas < 1.0
        mantissas[fixmsk] *= 10.0
        omags[fixmsk] -= 1.0

    result = xsgn * np.around( mantissas, decimals=sigfigs - 1 ) * 10.0**omags
    if matrixflag:
        result = np.matrix(result, copy=False)
    
    return result