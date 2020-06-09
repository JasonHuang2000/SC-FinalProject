### Notice

If you want to use sp_official.py to generate the answer format, please put the data-set, AIcup_testset_ok, in the same folder of sp_official.py

## How to use feature_plot.py
#### Please put "MIR-ST500" at the same folder of the program.
to run the program: python3 feature_plot.py [song id] [start sec] [feature index]

[song id]: 1 - 500.

[start]: the time(in sec) in the song you want to start plotting.

[feature index]:  0 - 5, listed below.
      (0) spectral_entropy 
      (1) spectral_flux 
      (2) spectral_rolloff 
      (3) zrc 
      (4) energy 
      (5) energy_enteopy 

## Best Score of sp.py

COn = 0.312

COnP = 0.205 

COnPOff = 0.050 

Final Score = 0.196


## The Score of example.py
  
COn = 0.606 

COnP = 0.518 

COnPOff = 0.297 

Final Score = 0.492
