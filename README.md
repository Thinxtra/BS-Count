# BS-Count
A program to comparing the number of receiving base station between two devices.

The function of the code is as follow:
- Enter the Sigfox ID of the testing device and the DUT
- Enter the start time to retrieve the message from the backend 
- Enter the end time to retrieve the message from the backend  
- Choose the Sigfox backend zone (i.e., AU, NZ, HK).
- Click count to get the average number of receiving base stations. OOB messages are removed.
- Click Compare to calculate the ratio of the average of the testing device over the average of the DUT.

The user is required to replace the credential in SigfoxCredentials.py with the real one.
