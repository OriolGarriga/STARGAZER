<img src="https://github.com/OriolGarriga/STARGAZER/assets/127389022/d1da4eb6-2b40-4248-a3be-14965086ae94" width="300" height="300" />

# STARGAZER

__Star Gazer__ is an educational robot designed to visualize stars. Using a laser and a mobile application, it displays the planets, stars, and constellations selected by the user. Star Gazer points to all the stars and planets that can be seen at the location and time when the user is using it, in addition to showing the description of everything that is pointed to in the application.

# TABLE OF CONTENTS
- [Hardware Requirements](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#hardware-requirements)
- [Software Requirements](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#software-requirements)
- [Documentation](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#documentation)
- [Project Module](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#project-module)
- [Hardware Architecture](https://github.com/OriolGarriga/STARGAZER/tree/main?tab=readme-ov-file#hardware-architecture)
- [Algorithms](https://github.com/OriolGarriga/STARGAZER/blob/main/README.md#algorithms)
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

# Algorithms
- Text to Speech i Speech to Text
  Implementat a l'assignatura de Sistemes Multimedia. Basicament utilitzem les APIs de Google de Text to Speech i Speech to Text per poder comunicar-nos amb el robot. És una eina essencial perquè la pantalla no ens enlluerni si estem a les fosques observant els cossos celestes.
  
- Detecció de constel·lacions a partir de punts
  Per a la identificació i emparellament de constel·lacions en imatges, vam abordar dos problemes principals. A continuació es detalla el procés i les solucions implementades per a cadascun d'ells.

1. Detecció de la Constel·lació
El primer repte consistia a identificar quina constel·lació es mostrava a la imatge presa. Per solucionar-ho, vam decidir implementar una homografia que ens permetés detectar la constel·lació més semblant, a més de determinar els graus de rotació i els ajustos d'escala necessaris per alinear-la exactament amb la constel·lació de referència.

No obstant això, vam trobar un problema amb l'algorisme RANSAC, que necessitava detectar cantonades i punts específics per fer la comparació amb les imatges de referència. Com que les imatges només contenien punts d'estrelles, no trobava prou elements de referència.

Per solucionar aquest problema, vam modificar tant les imatges de referència com la imatge d'entrada afegint totes les connexions entre els punts. D'aquesta manera, les imatges es transformaven en grafes en lloc de només punts, permetent que l'homografia funcionés perfectament.

2. Emparellament d'Estrelles
Una vegada realitzada l'homografia, el següent pas era emparellar les estrelles de la imatge d'entrada amb les estrelles de la imatge de referència. Per fer-ho, vam utilitzar l'algoritme KDTree, que ens va permetre realitzar l'emparellament de manera eficient.

Després de l'emparellament, ja sabíem quina estrella corresponia a cada punt en la imatge d'entrada. Amb aquesta informació i tenint emmagatzemades a la base de dades les connexions necessàries per dibuixar la constel·lació, vam poder traçar aquestes connexions sobre la imatge original. Així, l'usuari podia veure clarament les connexions de la constel·lació en el seu cel.

Aquest enfocament va permetre una identificació i emparellament precisos de les constel·lacions, millorant significativament la usabilitat i la precisió de les nostres eines d'observació astronòmica.

![Captura de pantalla 2024-06-26 141651](https://github.com/OriolGarriga/STARGAZER/assets/92922777/a1ab8d51-0c8c-4c05-a0cf-4882d490b0d9)

- Pas d'ubicació, temps i coordenades a angles de Stepper Motor
  Amb les coordenades, data i hora introduït per l'usuari i la RA i DEC de l'estrella que hem cercat, guardat a la base de dades de firestore, podem fer uns calculs per obtenir la azimut i la altitud, la azimut representa l'eix X i la altitud eix Y. Amb aquests calculs el robot sap on s'ha de moure per apuntar a l'estrella que l'usuari ha demanat.
  

# Images
![robot](https://github.com/OriolGarriga/STARGAZER/assets/92922777/526839d6-93e4-4e03-9687-9fa70c12348c)

# 3D
You can find a folder named [3D](https://github.com/OriolGarriga/STARGAZER/tree/main/3D) with all the 3D modeling. Here is the main 3D model:
![3dgiulytramega](https://github.com/OriolGarriga/STARGAZER/assets/92922777/f8958bb6-8eff-465c-8ec5-d2a4c90dbb47)

# Video
https://youtu.be/jfED0y5So1w

# References
https://www.hackster.io/starpointer/sshs-cs-7-3-starpointer-a60eb2

https://sketchfab.com/3d-models/laser-pointer-star-finder-robot-4288273bca724799888e1a2dc5643dc5

https://www.astropractica.org/oper/cnttel/cnttel.htm

http://www.jjrobots.com/

# Authors
Project developed by 
- Joan Estop Cepero
- Marçal Muñoz Salat
- Gerard Atienza Reig
- Oriol Garriga Puig
