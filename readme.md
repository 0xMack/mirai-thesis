Mirai Botnet Traffic Anlaysis - Honours Thesis
----------------------------------------------

This repository contains scripts used for the pre-processing and analysis of attack traffic generated by mirai.
Attack traffic was generated by launching attacks in a sandbox environment, but the traffic is too large to upload here.


    
TODO
----

### IDS - Snort

- Script reporting summary for IDS detection results (count number of
alerts generated by each ruleset on each dataset)
- Better understand snort rule syntax

### Traffic Mining - Flows (Argus/Tranalyzer)

- Better understand features in argus and tranalyzer
- Include direction and state features as categorical values
- Map hex features?


### Future Problems

- Generate snort rules from decision trees
- Create dataset with legitimate traffic to test


### Completed
- ~~10-fold cross validation for 6-attack dataset~~
- ~~proper data cleaning procedure for Nan given by argus~~
- ~~Output pre-processed csv that can be used by weka~~
- ~~Repeat process-argus functionality for tranalyzer output~~


Install
-------

WEKA
----
```
export _JAVA_OPTIONS=-Xmx2048m #allocate more heap - add to ~/.bashrc
```

PYTHON
-----
```shell
python -m pip install [packagename] #pip tries to use dif python -V alone
```