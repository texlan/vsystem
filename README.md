# vsystem
A python 3 module for communicating with Valence batteries over RS485.

Running vsystem.py on it's own will connect to the com port with the configuration defined in the __main__ section at the end, 
by default a 4-series-2-parallel system (8 batteries) on COM7. Currently the series-parallel information is used only to 
calculate the number of batteries to look for but should be expanded on.
