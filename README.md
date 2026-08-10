# Fiber-Photometry_Headache-Group
Fiber photometry scripts 

Project purpose:
Control and synchronise sensory stimulation during fiber photometry 
recordings of orexin neurons in mice using pyPhotometry.

Hardware:
-Arduino Uno R3
-pyPhotometry v1
-Foor pedal (manual stimulation marker)

Stimuli:
-Light flash 
-Air puff
-Mechanical von Frey 
-Mechanical cheek pinch

Synchonisation:
Arduino TTL outputs are recorded via pyPhotometry digital inputs.
One digital input receives TTLs related to automated stimuli and
one digital input receives TTLs related to manual stimul. Stimuli are 
disinguished by pulse duration. 