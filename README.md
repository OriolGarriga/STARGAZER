<img src="https://github.com/OriolGarriga/STARGAZER/assets/127389022/d1da4eb6-2b40-4248-a3be-14965086ae94" width="300" height="300" />

# STARGAZER

__Star Gazer__ is an educational robot designed to visualize stars. Using a laser and a mobile application, it displays the planets, stars, and constellations selected by the user. Star Gazer points to all the stars and planets that can be seen at the location and time when the user is using it, in addition to showing the description of everything that is pointed to in the application.

# TABLE OF CONTENTS
- [Hardware Requirements](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#hardware-requirements)
- [Software Requirements](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#software-requirements)
- [Documentation](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#documentation)
- [Project Module](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#project-module)
- [Hardware Architecture](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#hardware-architecture)
- [Images](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#images)
- [3D](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#3d)
- [Video](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#video)
- [References](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#references)
- [Authors](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#authors)

# Hardware Requirements
- Raspberry Pi 3b
- Raspberry Cam
- x2 Stepper Motor 28BYJ-48
- x2 Driver ULN2003
- Power Bank
- Laser

# Software Requirements
For development:
- Fully developed in Python

For running the code:
- flet
- firebase_admin
- credentials
- firestore
- storage
- translate_v2
- os
- texttospeech
- io
- pygame
- speech_recognition
- threading
- re
- json
- pyrebase
- requests
- Nominatim
- EarthLocation
- AltAz
- get_sun
- get_moon
- get_constellation
- SkyCoord
- Time
- units
- numpy
- datetime
- pytz
- cv2
- matplotlib.pyplot
- combinations
- KDTree
- os
- tempfile
- socket
- Image
- datetime
- timedelta

# Documentation
Software:
- [flet](https://flet.dev/)
- [firebase_admin](https://firebase.google.com/docs/reference/admin/python/firebase_admin)
- [credentials](https://firebase.google.com/docs/admin/setup?hl=es-419)
- [firestore](https://stackoverflow.com/questions/71409466/how-to-access-admin-firestore-using-firebase-admin-sdk)
- [storage](https://firebase.google.com/docs/storage/admin/start?hl=es-419)
- [translate_v2](https://cloud.google.com/translate/docs/reference/libraries/v2/python)
- [os](https://docs.python.org/es/3.10/library/os.html)
- [texttospeech](https://cloud.google.com/dotnet/docs/reference/Google.Cloud.TextToSpeech.V1/latest/Google.Cloud.TextToSpeech.V1.TextToSpeech.TextToSpeechClient?gad_source=1&gclid=CjwKCAjw-O6zBhASEiwAOHeGxZBTbt71obPANN32ZvSRi7k721C4Ogedqxap22FtLPSk349O-IZEyBoCQboQAvD_BwE&gclsrc=aw.ds)
- [io](https://docs.python.org/es/3.9/library/io.html)
- [pygame](https://www.pygame.org/docs/tut/ImportInit.html)
- [speech_recognition](https://pypi.org/project/SpeechRecognition/2.1.3/)
- [threading](https://docs.python.org/3/library/threading.html)
- [re](https://docs.python.org/3/library/re.html)
- [json](https://docs.python.org/3/library/json.html)
- [pyrebase](https://pypi.org/project/Pyrebase/)
- [requests](https://www.w3schools.com/python/module_requests.asp)
- [Nominatim](https://geopy.readthedocs.io/en/stable/)
- [EarthLocation](https://astropy-astrofrog.readthedocs.io/en/latest/coordinates/)
- [AltAz](https://astropy-astrofrog.readthedocs.io/en/latest/coordinates/)
- [get_sun](https://astropy-astrofrog.readthedocs.io/en/latest/coordinates/)
- [get_moon](https://astropy-astrofrog.readthedocs.io/en/latest/coordinates/)
- [get_constellation](https://astropy-astrofrog.readthedocs.io/en/latest/coordinates/)
- [SkyCoord](https://astropy-astrofrog.readthedocs.io/en/latest/coordinates/)
- [Time](https://docs.astropy.org/en/stable/time/)
- [units](https://docs.astropy.org/en/stable/units/)
- [numpy](https://numpy.org/doc/stable/user/absolute_beginners.html)
- [datetime](https://docs.python.org/es/3/library/datetime.html)
- [pytz](https://pypi.org/project/pytz/)
- [cv2](https://pypi.org/project/opencv-python/)
- [matplotlib.pyplot](https://matplotlib.org/2.0.2/users/pyplot_tutorial.html)
- [combinations](https://docs.python.org/3/library/itertools.html)
- [KDTree](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html)
- [tempfile](https://docs.python.org/3/library/tempfile.html)
- [socket](https://docs.python.org/3/library/socket.html)
- [Image](https://pillow.readthedocs.io/en/stable/reference/Image.html)
- [timedelta](https://docs.python.org/es/3/library/datetime.html)

Hardware:
- [Raspberry Pi 3b](https://www.raspberrypi.com/documentation/)
- [Raspberry Cam](https://github.com/OriolGarriga/STARGAZER/blob/main/Hardware/CAMV2.pdf)
- [x2 Stepper Motor 28BYJ-48](https://github.com/OriolGarriga/STARGAZER/blob/main/Hardware/Stepper%20Motor%20-%2028BYJ-48.PDF)
- [x2 Driver ULN2003](https://github.com/OriolGarriga/STARGAZER/blob/main/Hardware/Driver%20-%20ULN2003.PDF)
- Power Bank
- Laser

# Project Module
![WhatsApp Image 2024-06-26 at 11 40 23](https://github.com/OriolGarriga/STARGAZER/assets/92922777/9694a249-1c54-4d67-a081-bf3eca16fb1c)

# Hardware Architecture
![fritzing](https://github.com/OriolGarriga/STARGAZER/assets/92922777/8e495ad5-0d3c-4c73-a881-31e9ede22863)

# Images
![WhatsApp Image 2024-06-26 at 10 55 26](https://github.com/OriolGarriga/STARGAZER/assets/92922777/ced44ca8-c3d1-4f7f-adf6-934233bff591)

# 3D

# Video

# References
https://www.hackster.io/starpointer/sshs-cs-7-3-starpointer-a60eb2

https://sketchfab.com/3d-models/laser-pointer-star-finder-robot-4288273bca724799888e1a2dc5643dc5

https://www.astropractica.org/oper/cnttel/cnttel.htm

# Authors
Project developed by 
- Joan Estop Cepero
- Marçal Muñoz Salat
- Gerard Atienza Reig
- Oriol Garriga Puig
