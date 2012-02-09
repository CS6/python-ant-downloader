Open Ant Agent
===================

Experimental linux tools for extracting data from wireless (ANT) garmin GPS units. This software has been tested with a 405CX. It is possible other units will work. The software was implemented based on ANT, ANT-FS, and garmin device inteface specs, but in some cases features were undocumented, or specs were out-of-date. If a device does not work, adding support should not be too difficult, but I have no hardware to test.

My project goal is to implement functionaly similar to the Windows "Garmin Ant Agent". So far data is automatically downloaded from devices which are paried and in range. Data is saved as both raw packets and TCX (still testing). Soon, I hope to have automatic upload working.
