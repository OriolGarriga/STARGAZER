
import flet as ft
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud import translate_v2 as translate
import os
from google.cloud import texttospeech
import io
import pygame
import speech_recognition as sr
import threading
import re
import json
import pyrebase
import requests
from geopy.geocoders import Nominatim
from astropy.coordinates import EarthLocation, AltAz, get_sun, get_moon, get_constellation, SkyCoord
from astropy.time import Time
from astropy import units as u
import numpy as np
from datetime import datetime
import pytz
import cv2
import matplotlib.pyplot as plt
from itertools import combinations
from scipy.spatial import KDTree
import tempfile
import socket
from PIL import Image
from datetime import datetime, timedelta

def get_location_by_city(city_name):
    geolocator = Nominatim(user_agent="sadkofhasdjfhkasjlerfgthfkñljasñlkdfjkñlasjflkasjdlf")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def visible_constellations(date, time, city):
    # Obtener latitud y longitud por nombre de ciudad
    latitude, longitude = get_location_by_city(city)
    if latitude is None:
        return "City not found, please check the name."

    # Configuración de la fecha y hora
    datetime_str = f"{date} {time}"
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    local_time = pytz.timezone("UTC").localize(datetime_obj)

    # Ubicación en la Tierra
    location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg)

    # Tiempo en formato adecuado para AstroPy
    observing_time = Time(local_time)

    # Coordenadas de altitud y azimut
    altaz = AltAz(obstime=observing_time, location=location)

    # Calcular posiciones de cuerpos celestes (sol y luna para verificar si es de noche)
    sun = get_sun(observing_time).transform_to(altaz)
    moon = get_moon(observing_time).transform_to(altaz)

    # Verificar si es de noche (el sol está por debajo del horizonte)
    if sun.alt < 0 * u.deg:
        # Calcular las constelaciones visibles
        number_of_stars = 100
        ra_random = np.random.uniform(0, 360, number_of_stars)
        dec_random = np.random.uniform(-90, 90, number_of_stars)

        skycoords = SkyCoord(ra=ra_random * u.deg, dec=dec_random * u.deg, frame='icrs').transform_to(altaz)
        visible_coords = skycoords[skycoords.alt > 0]
        
        constellations = [get_constellation(coord) for coord in visible_coords if get_constellation(coord) != "Boötes"]
        return set(constellations)
    else:
        return "It's not night time."

# Configura la variable d'entorn per les credencials de Google
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key_2.json'

# Dades de traducció de constel·lacions
constellation_translation = {
    "Aquarius": {
        "name": "Acuario",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/acuario.JPEG?alt=media&token=48d2c89e-3d85-4e89-9914-a0a8aa2a9537",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/acuario2.jpg?alt=media&token=151f52ab-d605-4d1a-9dc1-f42f2e265957"
    },
    "Aquila": {
        "name": "Aguila",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/aguila.JPEG?alt=media&token=f4b11a8c-4eab-46b9-8997-5dc19a822027",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/aguila2.jpg?alt=media&token=3178895f-079c-4cdd-b390-159e99903880"
    },
    "Andromeda": {
        "name": "Andromeda",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/andromeda.JPEG?alt=media&token=d82deba4-9517-4e28-a2ec-a842b88ca49c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/andromeda2.jpg?alt=media&token=7429e1f8-621f-4a95-8f57-f7fe9705ab9e"
    },
    "Antlia": {
        "name": "Antila",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/antlia.JPEG?alt=media&token=41587ba3-db42-4cea-b6a9-1429d8894b14",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/antlia2.jpg?alt=media&token=baad4e90-2ca6-4eee-926b-69be042c8eed"
    },
    "Apus": {
        "name": "Apus",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/apus.JPEG?alt=media&token=95cc1e00-4934-43a1-b9a8-4b5bc983ccb1",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/apus2.jpg?alt=media&token=ca5bc2bd-8a82-4a85-83ec-65757b7e3374"
    },
    "Ara": {
        "name": "Ara",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ara.JPEG?alt=media&token=cb5eb2c7-ce3c-430c-92f5-b43a7aea4ad9",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ara2.jpg?alt=media&token=381d3695-aa72-4227-8744-bfdf7494f294"
    },
    "Aries": {
        "name": "Aries",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/aries.JPEG?alt=media&token=d9fe3c8a-a1b5-4a37-b437-41e9cc3f9e24",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/aries2.jpg?alt=media&token=8e1e908e-f302-4c17-b96f-0cd034aa8260"
    },
    "Auriga": {
        "name": "Auriga",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/auriga.JPEG?alt=media&token=09592315-28ef-42f1-90f9-d76c7f16ffaa",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/auriga2.jpg?alt=media&token=06d4c530-7883-4431-b8cb-af0852f89260"
    },
    "Caelum": {
        "name": "Cincel",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/caelum.JPEG?alt=media&token=468d1e55-1e5d-43f3-b9ce-ba89160efb87",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/caelum2.jpg?alt=media&token=eccf9d2d-6f59-4106-a786-35ab74c9d33d"
    },
    "Camelopardalis": {
        "name": "Jirafa",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/camelopardalis.JPEG?alt=media&token=5126d704-fe84-4adc-b4e4-48375a64a799",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/camelopardalis2.jpg?alt=media&token=fe3e6a1b-6e1d-4220-a598-47d9731c5dbf"
    },
    "Cancer": {
        "name": "Cancer",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cancer.JPEG?alt=media&token=02c74839-e844-4053-8a49-243e70525643",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cancer2.jpg?alt=media&token=6e188341-658a-4ec4-b904-255c41235b54"
    },
    "Canes Venatici": {
        "name": "Perros de caza",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/canes%20venatici.JPEG?alt=media&token=bb91e661-e02a-4296-b149-6f068a862310",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/canes%20venatici2.jpg?alt=media&token=a4988e38-14b6-4e87-8a13-454dc04034ef"
    },
    "Canis Major": {
        "name": "Can Mayor",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/canis%20major.JPEG?alt=media&token=6d1009d1-c0d0-4337-8dce-325cfb8a7ffe",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/canis%20major2.jpg?alt=media&token=b4922f9b-ea79-4bbf-b454-fb5b8ddb868c"
    },
    "Canis Minor": {
        "name": "Can Menor",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/canis%20minor.JPEG?alt=media&token=d1f6cb19-ca15-4a1f-b5aa-b54175d51747",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/canis%20minor2.jpg?alt=media&token=7958885d-9fea-4ae1-93c1-59dca3a31fc2"
    },
    "Capricornus": {
        "name": "Capricornio",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/capricornio.JPEG?alt=media&token=7139f5d5-48a6-40f1-8c1c-5f4813f3918d",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/capricornio2.jpg?alt=media&token=74fadb0e-3b1b-4195-8c65-ecea69d0198b"
    },
    "Carina": {
        "name": "Carina",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/carina.JPEG?alt=media&token=e4d6fab6-e3ae-4f67-9083-09270a50311a",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/carina2.jpg?alt=media&token=9788aefc-415d-47d6-a0aa-d0ce4e1b85b3"
    },
    "Cassiopeia": {
        "name": "Casiopea",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cariopea.JPEG?alt=media&token=b6f345b4-dc7a-477f-8615-f007bf2ea00b",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cariopea2.jpg?alt=media&token=a9fa2a67-2ee8-44b8-8f57-200c2b5bf17a"
    },
    "Centaurus": {
        "name": "Centauro",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/centauro.JPEG?alt=media&token=89edc865-5de4-4d6c-becc-87c0c3fdcc73",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/centauro2.jpg?alt=media&token=bf176ddb-b042-4f6f-bb6b-5ca121588f42"
    },
    "Cepheus": {
        "name": "Cefeo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cepheus.JPEG?alt=media&token=dacd0f54-0a06-43f6-842e-1952bfb834a3",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cepheus2.jpg?alt=media&token=7501a442-004b-4d30-8175-7c8a4e2e7044"
    },
    "Cetus": {
        "name": "Cetus",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cetus.JPEG?alt=media&token=6b458e7f-636a-4900-bdb9-ffa7453df4c0",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cetus2.jpg?alt=media&token=c8a4a955-f4bc-4702-8135-015e77292bc5"
    },
    "Chamaeleon": {
        "name": "Camaleon",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/chamaeleon.JPEG?alt=media&token=908c65f8-9bef-4a8f-818f-e6567ecb63ab",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/chamaeleon2.jpg?alt=media&token=1a4dd75b-feaa-4d4b-8307-f673d8d1372e"
    },
    "Circinus": {
        "name": "Compas",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/circinus.JPEG?alt=media&token=8c93eaed-1b41-4afd-9205-e2299040ea4b",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/circinus2.jpg?alt=media&token=9d7ae88f-22e5-4255-a887-6801ad8d512e"
    },
    "Columba": {
        "name": "Paloma",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/columba.JPEG?alt=media&token=26582c6f-3d22-469c-937f-a0bd16ce09c0",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/columba2.jpg?alt=media&token=ae1bce72-088c-4e3f-890a-f38c0293490d"
    },
    "Coma Berenices": {
        "name": "Cabellera de Berenice",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/coma%20berenices.JPEG?alt=media&token=f659c182-9dc6-4eb9-9ce4-a4d924ea5d00",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/coma%20berenices2.jpg?alt=media&token=34678d6a-4461-4382-a588-91ad7699214f"
    },
    "Corona Australis": {
        "name": "Corona Austral",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/corona%20australis.JPEG?alt=media&token=831d1416-0007-462b-b8a0-0adf50d3e67a",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/corona%20australis2.jpg?alt=media&token=4e2cf1f5-cd47-430b-8af2-bd0001b45516"
    },
    "Corona Borealis": {
        "name": "Corona Boreal",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/corona%20boreal.JPEG?alt=media&token=d0437087-4c5f-4952-907e-3c145602a24a",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/corona%20borealis2.jpg?alt=media&token=76079b00-3b4c-41aa-ad21-167e0e60e2dc"
    },
    "Corvus": {
        "name": "Cuervo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/corvus.JPEG?alt=media&token=cc36f669-ed96-4ce6-9155-30ac89138f96",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/corvus2.jpg?alt=media&token=4c09d979-1a4a-43d7-89bf-d2cdb614719b"
    },
    "Crater": {
        "name": "Copa",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/crater.JPEG?alt=media&token=0bd7bbbc-acf1-43fc-8d99-5552cefab86e",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/crater2.jpg?alt=media&token=a3752549-5c54-4d70-9287-14a56fce68e6"
    },
    "Crux": {
        "name": "Cruz",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/crux.JPEG?alt=media&token=6fc78002-36cc-406e-9923-2c130b7c39c6",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/crux2.jpg?alt=media&token=886331cb-d328-47bb-aa79-25a16e46d764"
    },
    "Cygnus": {
        "name": "Cisne",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cygnus.JPEG?alt=media&token=32359e09-2ac3-4b5f-a166-1ae314c25a3c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/cygnus2.jpg?alt=media&token=f6394d24-e3fa-43f1-9b34-c6d5a7ac17b8"
    },
    "Delphinus": {
        "name": "Delfin",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/delphinus.JPEG?alt=media&token=4dbed728-df46-49ac-ad9c-c5e47c60d806",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/delphinus2.jpg?alt=media&token=ede803b1-06cc-48c1-ac55-cce28a3f12a2"
    },
    "Dorado": {
        "name": "Dorado",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/dorado.JPEG?alt=media&token=85243148-eecb-477f-b193-f49ddf465d62",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/dorado2.jpg?alt=media&token=01f371bc-4b4c-4f7f-bce5-e01990d08e8a"
    },
    "Draco": {
        "name": "Dragón",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/draco.JPEG?alt=media&token=9e313c03-657a-497d-a8a2-5bed54190f0c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/draco2.jpg?alt=media&token=ee1f338b-39b1-4847-8927-a1629e035667"
    },
    "Equuleus": {
        "name": "Caballito",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/equuleus.JPEG?alt=media&token=7936e9fa-a1f1-42fe-a106-52490366d165",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/equuleus2.jpg?alt=media&token=535642e6-2aca-4ac7-ac63-796ff1e816b5"
    },
    "Eridanus": {
        "name": "Eridano",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/eridanus.JPEG?alt=media&token=26228110-5a9d-42bc-bcd4-ed1c405e98bf",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/eridanus2.jpg?alt=media&token=7d98803c-8d05-4203-942a-41c26404d9c4"
    },
    "Fornax": {
        "name": "Horno",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/fornax.JPEG?alt=media&token=5aa5c830-43ca-42db-a7cc-415ebc2095de",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/fornax2.jpg?alt=media&token=8121152d-364b-4b80-bf71-2c5c186418f0"
    },
    "Geminis": {
        "name": "Geminis",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/gemini.JPEG?alt=media&token=c8a4cebd-edf7-4ef4-a8ad-dc5a9f07f33c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/gemini2.jpg?alt=media&token=9064bccc-45d9-49b9-9671-5b0ab3929912"
    },
    "Grus": {
        "name": "Grulla",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/grus.JPEG?alt=media&token=73d7b6fc-2f22-4111-abdd-985979b58318",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/grus2.jpg?alt=media&token=9c159b83-9336-45b0-a437-92f96df985e9"
    },
    "Hercules": {
        "name": "Hercules",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/hercules.JPEG?alt=media&token=9f128267-f5d8-4a2a-b3a9-0a8ec03ed04a",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/hercules2.jpg?alt=media&token=b1f26df9-5933-4433-b287-b37db282c586"
    },
    "Horologium": {
        "name": "Reloj",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/horologium.JPEG?alt=media&token=02b77cd8-95ca-41bb-bd5e-27d8dbaca247",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/horologium2.jpg?alt=media&token=19de98dc-7d9e-4c36-bf81-7478a2055b5c"
    },
    "Hydra": {
        "name": "Hidra",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/hydra.JPEG?alt=media&token=b649e3e6-3f96-421e-bdcc-66600fb57dde",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/hydra2.jpg?alt=media&token=da20cea8-914b-4ca9-92b3-90ef8aa789c6"
    },
    "Hydrus": {
        "name": "Hidrus",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/hydrus.JPEG?alt=media&token=135f864c-4f35-487c-a371-b3674bdeeac7",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/hydrus2.jpg?alt=media&token=cbf454cc-3395-43c2-8163-684564d80a88"
    },
    "Indus": {
        "name": "Indio",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/indus.JPEG?alt=media&token=f537aa71-86f6-4fb2-9388-03ac2b10dbf6",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/indus2.jpg?alt=media&token=aa093534-e43d-462c-a559-1f4927863f23"
    },
    "Lacerta": {
        "name": "Lagarto",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lacerta.JPEG?alt=media&token=92db2325-dc71-4b1d-b574-d24f12a03a44",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lacerta2.jpg?alt=media&token=89d7b367-6a8b-4717-9052-106d8972436e"
    },
    "Leo Minor": {
        "name": "Leo Menor",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/leo%20minor.JPEG?alt=media&token=6fd4b58f-e758-48aa-a010-9bd34d6182d4",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/leo%20minor2.jpg?alt=media&token=eb175050-229a-4e1d-90d6-324f8bba1d28"
    },
    "Leo": {
        "name": "Leo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/leo.JPEG?alt=media&token=5bec5152-9616-4a46-ae44-99b365cc3a62",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/leo2.jpg?alt=media&token=d298a7a6-687e-4b31-b0b9-fb8fba2312b0"
    },
    "Lepus": {
        "name": "Liebre",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lepus.JPEG?alt=media&token=4c19c66c-63b0-40fc-a475-057887488cfe",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lepus2.jpg?alt=media&token=74fc444b-e220-4717-b439-8296ef302401"
    },
    "Libra": {
        "name": "Libra",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/libra.JPEG?alt=media&token=f62bfef5-6524-4d4f-9181-8fb2d0470fcb",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/libra2.jpg?alt=media&token=d5d2d3fa-4f9e-4d24-b1bd-239f0354e476"
    },
    "Lupus": {
        "name": "Lobo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lupus.JPEG?alt=media&token=8160aa09-47dc-4226-9407-1c105c7cf9ee",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lupus2.jpg?alt=media&token=9804c371-3e9c-4923-b172-3802d65efd5a"
    },
    "Lynx": {
        "name": "Lince",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lynx.JPEG?alt=media&token=621541a4-77da-4d26-b05d-8233b9e8459d",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lynx2.jpg?alt=media&token=286c18c8-490f-4bf0-9880-df12e81ad615"
    },
    "Lyra": {
        "name": "Lira",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lyra.JPEG?alt=media&token=be185fc7-543b-4fb1-8f85-334567bf8764",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lyra2.jpg?alt=media&token=06214684-bbbb-4e1f-882e-550f1506c276"
    },
    "Mensa": {
        "name": "Mesa",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/mensa.JPEG?alt=media&token=a15843b4-95bf-4649-adff-2e82f6c6d97c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/mensa2.jpg?alt=media&token=68f4330a-3857-445c-88e1-928fa9cf2367"
    },
    "Microscopium": {
        "name": "Microscopio",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/microscopium.JPEG?alt=media&token=e164ea2d-ac2a-4333-94eb-4f7434d70af0",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/microscopium2.jpg?alt=media&token=256cbafb-9f6f-436d-8c83-123eb070995a"
    },
    "Monoceros": {
        "name": "Unicornio",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/monoceros.JPEG?alt=media&token=7d9f1834-d95e-4151-bce4-dc5896656fcd",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/monoceros2.jpg?alt=media&token=d8e0fbe2-7724-4ec3-99cb-eaa7a906e745"
    },
    "Musca": {
        "name": "Mosca",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/musca.JPEG?alt=media&token=ccd738a0-aa9a-43fd-a03b-e06bff06cf4b",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/musca2.jpg?alt=media&token=f724ad47-b6d5-48f1-b17e-a0cd3d11482a"
    },
    "Norma": {
        "name": "Regla",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/norma.JPEG?alt=media&token=57b95622-0b74-4900-baa5-80a1bbc5c677",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/norma2.jpg?alt=media&token=28f9ebec-b68f-4c85-8a4a-11a171e4c016"
    },
    "Octans": {
        "name": "Octante",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/octans.JPEG?alt=media&token=c3534838-2ba4-438d-9f7b-466da0c5e719",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/octans2.jpg?alt=media&token=ec6cb29c-a9f0-48a1-aed3-0083a8a1a4fa"
    },
    "Ophiucus": {
        "name": "Ofiuco",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ophiuchus.JPEG?alt=media&token=ccfb58cd-7c71-489e-b94e-6b57259df90f",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ophiuchus2.jpg?alt=media&token=7c4e2d20-53a4-4592-9309-e11c08853b61"
    },
    "Orion": {
        "name": "Orion",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/orion.JPEG?alt=media&token=819de312-5c5a-45af-99bf-cd3595815eef",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/orion2.jpg?alt=media&token=03cfc352-a255-49d7-9315-485e2e403f6e"
    },
    "Pavo": {
        "name": "Pavo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pavo.JPEG?alt=media&token=3719490d-05cc-4059-9a2b-a9a6e11a092a",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pavo2.jpg?alt=media&token=6b170406-ceb1-4eb1-8c92-d48f75624b0d"
    },
    "Pegasus": {
        "name": "Pegaso",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pegasus.JPEG?alt=media&token=11607f06-b811-4c9d-b4dd-66378df9f8f0",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pegasus2.jpg?alt=media&token=3ebdf751-30ac-4b0f-b207-d4830d34c8d7"
    },
    "Perseus": {
        "name": "Perseo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/perseus.JPEG?alt=media&token=81517e22-03a8-4b15-9c9c-971c0ed72048",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/perseus2.jpg?alt=media&token=bc22de66-ba1e-48e6-b428-ad377130c29a"
    },
    "Phoenix": {
        "name": "Fenix",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/phoenix.JPEG?alt=media&token=117c406e-1496-42f8-a9d0-2e71286895da",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/phoenix2.jpg?alt=media&token=6b53acc0-42e8-4a13-b2c6-3075c27feae2"
    },
    "Pictor": {
        "name": "Pintor",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pictor.JPEG?alt=media&token=0b71fc11-1610-4533-a2b4-907a31e7bb7d",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pictor2.jpg?alt=media&token=678ca358-77bf-48c5-8d17-2f409fccceae"
    },
    "Pisces": {
        "name": "Piscis",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pisces.JPEG?alt=media&token=5a04ef2f-0d2f-4c66-930f-a5d59b8f02d2",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pisces2.jpg?alt=media&token=1e0f2cf9-39d7-4350-878a-618f54fdfcb5"
    },
    "Pisces Austrinus": {
        "name": "Pez Austral",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/piscis%20austrinus.JPEG?alt=media&token=d57d5355-d4d2-4534-8b1d-a45b8aa0a40a",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/piscis%20austrinus2.jpg?alt=media&token=35f77210-88c2-4498-b1c5-ab26453d8fed"
    },
    "Puppis": {
        "name": "Popa",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/puppis.JPEG?alt=media&token=14aa4cb9-90b8-4457-bc72-7d4d02a2d8f8",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/puppis2.jpg?alt=media&token=cd372eba-4a22-4e6d-ae1d-5f14f831933f"
    },
    "Pyxis": {
        "name": "Brujula",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pyxis.JPEG?alt=media&token=93d5ac72-fe66-4ca3-9d36-67a9d6a7e542",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/pyxis2.jpg?alt=media&token=47411c3a-78eb-47cb-b949-2f6d550d126b"
    },
    "Reticulum": {
        "name": "Reticulo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/reticulum.JPEG?alt=media&token=6696a3cd-be9f-4357-8f3a-9746ef6d089e",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/reticulum2.jpg?alt=media&token=2ec21f43-39b8-4ecf-a412-4ef3e1f71054"
    },
    "Sagittarius": {
        "name": "Sagitario",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sagitario.JPEG?alt=media&token=55333e42-c8d6-4cee-918d-bca522bafe64",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sagitario2.jpg?alt=media&token=a144e5f2-056f-4365-bdcb-d8060a3c1edd"
    },
    "Sagitta": {
        "name": "Saeta",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sagitta.JPEG?alt=media&token=e41c1601-29f7-4fd1-bff7-cd5b2d9a7535",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sagitta2.jpg?alt=media&token=d2f72906-7647-4b96-997a-40bbe3881365"
    },
    "Scorpius": {
        "name": "Escorpion",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/scorupius.JPEG?alt=media&token=1901cf06-3fc3-40a2-b878-41b134d75826",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/scorpius2.jpg?alt=media&token=2922e461-4b0b-4e9b-bcfb-2d34a929594b"
    },
    "Sculptor": {
        "name": "Escultor",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sculptur.JPEG?alt=media&token=d36430e2-f775-430f-98b6-80292fcc0c54",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sculptor2.jpg?alt=media&token=63754046-70bc-41a7-a24b-b573d0041ce5"
    },
    "Scutum": {
        "name": "Escudo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/scutum.JPEG?alt=media&token=575bdb29-dbdd-4d28-9461-b2a1d253fe0b",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/scutum2.jpg?alt=media&token=19113655-21c7-417a-ba6b-f4c4573b4592"
    },
    "Serpens": {
        "name": "Serpiente",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/serpens.JPEG?alt=media&token=b105c40d-8c4c-409b-8f99-a95c813151a9",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/serpens2.jpg?alt=media&token=932077c9-d0f4-4d57-aaff-53ac880b66bc"
    },
    "Sextans": {
        "name": "Sextante",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sextans.JPEG?alt=media&token=0fa9bf6e-52f6-4d16-af92-da8ddf02ca2c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/sextans2.jpg?alt=media&token=3df56e7b-acd1-4a7d-b8db-4acc5608e57f"
    },
    "Taurus": {
        "name": "Tauro",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/tauro.JPEG?alt=media&token=89091ac3-27e6-47a9-a600-361d447043db",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/tauro2.jpg?alt=media&token=1881b750-2eab-4698-8380-3ff64b226d52"
    },
    "Telescopium": {
        "name": "Telescopio",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/telescopium.JPEG?alt=media&token=fe9a1e41-4f1f-4f8d-85cc-0267f29bfc17",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/telescopium2.jpg?alt=media&token=d98ee16a-be8d-475f-9cbd-8d8af69f03c4"
    },
    "Triangulum": {
        "name": "Triangulo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/triangulum.JPEG?alt=media&token=194d2a30-2b00-40fb-8b69-484f4cf17ad1",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/triangulum2.jpg?alt=media&token=1f0c357a-d79e-41d8-807c-f26ba3570059"
    },
    "Triangulum Australe": {
        "name": "Triangulo Austral",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/triangulum%20australe.JPEG?alt=media&token=8273eda7-1160-4151-8720-c6c80b4532bf",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/triangulum%20australe2.jpg?alt=media&token=b6f605a6-d450-4bbc-b8fd-358f3c21ec75"
    },
    "Tucana": {
        "name": "Tucan",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/tucana.JPEG?alt=media&token=0a18a6e0-7af9-4dd7-9a96-654bd6c79670",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/tucana2.jpg?alt=media&token=c59566e2-add7-4a60-8f3e-fb81a45130a8"
    },
    "Ursamajor": {
        "name": "Ursa Major",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ursa%20major.JPEG?alt=media&token=13ca75ed-dcb3-454a-9653-0b556a61c472",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ursa%20major2.jpg?alt=media&token=5bab0f8b-365c-4110-831f-b1b530a02c32"
    },
    "Ursaminor": {
        "name": "Ursa Minor",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ursa%20minor.JPEG?alt=media&token=042244a1-b7e2-4ec0-b62e-a4f12373ad9c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/ursa%20minor2.jpg?alt=media&token=bd8c8d32-c421-41f0-b252-bc3b8666205b"
    },
    "Vela": {
        "name": "Vela",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/vela.JPEG?alt=media&token=e614ab2e-9dc8-4331-b752-8a222d6c654c",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/vela2.jpg?alt=media&token=eb1dbe9a-70be-4979-b52b-d9ed81f1e0ac"
    },
    "Virgo": {
        "name": "Virgo",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/virgo.JPEG?alt=media&token=eb8757e1-227e-4cba-aed9-d3f9f2ce657d",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/virgo2.jpg?alt=media&token=e8cc9eb8-eb59-4000-92ea-a83567d97b47"
    },
    "Volans": {
        "name": "Volans",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/volans.JPEG?alt=media&token=90fe71e1-40e8-41d1-80e5-520e67f446f0",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/volans2.jpg?alt=media&token=806b005a-9625-4721-af6c-ced5906a8e58"
    },
    "Vulpecula": {
        "name": "Zorro",
        "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/vulpecula.JPEG?alt=media&token=b4db6257-5e62-439e-aa73-b9a8c5eb9288",
        "imagedins_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/vulpecula2.jpg?alt=media&token=e65c8203-2a06-4610-9d8c-9891f0b3155a"
    }
}

# Inicialitza Firebase
cred = credentials.Certificate("ClauPrivada\stargazer-e6e93-firebase-adminsdk-c6jlk-db1d10077f.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'stargazer-e6e93.appspot.com'
})

# Inicialitza el client de text-to-speech de Google
text_to_speech_client = texttospeech.TextToSpeechClient()

# Inicialitza Firestore i Storage
db = firestore.client()
bucket = storage.bucket()

# Inicialitza el client de traducció de Google
translate_client = translate.Client()

# Llegeix la configuració de Firebase des d'un fitxer JSON
with open("firebase_config.json") as f:
    firebase_config = json.load(f)

firebase_client = pyrebase.initialize_app(firebase_config)
auth = firebase_client.auth()

# Variables globals per gestionar l'estat de l'usuari
user_logged_in = False
user_id = None
user_email = None

# Funció per traduir text
def translate_text(text, target_language):
    if text:
        result = translate_client.translate(text, target_language=target_language)
        return result['translatedText']
    return text

# Idiomes disponibles
languages = {
    "es": "Español",
    "en": "English",
    "zh": "中文",
    "ko": "한국어",
    "th": "ไทย",
    "ca": "Català",
    "fr": "Français",
    "it": "Italiano",
    "mn": "Монгол"
}

# Voces disponibles per idioma
voice_names = {
    "Español": "es-ES-Standard-B",
    "English": "en-US-Standard-B",
    "Français": "fr-FR-Standard-A",
    "Italiano": "it-IT-Standard-A",
    "Català": "ca-ES-Standard-A",
}

# Configuració inicial de l'idioma i altres variables
current_language = "en"
nom_introduit = ""
voice_assistant_process = None
night_mode = False
constellations_cache = []
stop_flag = False

# Funció per capitalitzar una cadena
def majuscula(string):
    if string:
        return string[0].upper() + string[1:].lower()
    return string

# Funció per obtenir informació d'una estrella des de Firestore
def get_star_info_from_firestore(star_name):
    star_name = majuscula(star_name)
    estrellas_ref = db.collection('estrelles_ok')
    query = estrellas_ref.where('ProperName', '==', star_name).stream()
    for doc in query:
        return doc.to_dict().get('EstrellaInfo')
    return None

# Funció per obtenir informació d'una constel·lació des de Firestore
def get_const_info_from_firestore(constellation_name):
    constellation_name = majuscula(constellation_name)
    estrellas_ref = db.collection('estrelles_ok')
    query = estrellas_ref.where('Constellation', '==', constellation_name).where('ConstIndex', '==', "1").stream()
    for doc in query:
        return doc.to_dict().get('ConstInfo')
    return None

def get_ra_from_firestore(star_name):
    star_name = majuscula(star_name)
    estrellas_ref = db.collection("estrelles_ok")
    query = estrellas_ref.where('ProperName', '==', star_name).stream()
    for doc in query:
        return doc.to_dict().get("RA")
    return None

def get_dec_from_firestore(star_name):
    star_name = majuscula(star_name)
    estrellas_ref = db.collection("estrelles_ok")
    query = estrellas_ref.where('ProperName', '==', star_name).stream()
    for doc in query:
        return doc.to_dict().get("Dec")
    return None

def get_ra_const_from_constellation(constellation_name):
    constellation_name = majuscula(constellation_name)
    estrellas_ref = db.collection("estrelles_ok")
    query = estrellas_ref.where('Constellation', '==', constellation_name).stream()
    ra_list = []
    for doc in query:
        ra = doc.to_dict().get("RA")
        if ra is not None:
            ra_list.append(ra)
    return ra_list if ra_list else None

def get_dec_const_from_constellation(constellation_name):
    constellation_name = majuscula(constellation_name)
    estrellas_ref = db.collection("estrelles_ok")
    query = estrellas_ref.where('Constellation', '==', constellation_name).stream()
    ra_list = []
    for doc in query:
        ra = doc.to_dict().get("Dec")
        if ra is not None:
            ra_list.append(ra)
    return ra_list if ra_list else None

def obtener_coordenadas(city):
    geolocator = Nominatim(user_agent="geoapiExercedcrftgrfegtbises")
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    else:
        return None

def send_data(azimut, altitud, server_ip='192.168.137.68', server_port=65432):
    print(azimut, altitud)
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))
            message = {
                "command": "point_to_star",
                "azimut": azimut,
                "altitud": altitud
            }
            json_message = json.dumps(message)
            s.sendall(json_message.encode('utf-8'))
            response = s.recv(1024)
            print(f'Received response from server: {response.decode("utf-8")}')
    except Exception as e:
        print(f'Failed to send data: {e}')
        print(f'Failed to send data: {e}')
    """
def calculate_alt_az(ra, dec, date_str, lat, lon, time_str):
    ra = float(ra)
    dec = float(dec)
    # Convertir las cadenas de fecha y hora a un objeto datetime
    date = datetime.strptime(date_str + ' ' + time_str, '%Y-%m-%d %H:%M')

    # Convertir hora local a UT
    ut_offset = timedelta(hours=2)  # CEST es UTC+2
    ut_time = date - ut_offset

    # Calcular GST y luego LST
    def calculate_gst(d):
        return 18.697374558 + 24.06570982441908 * d

    # Calcular el número de días desde el 1 de enero de 2000 a las 12:00 UT
    start_2000 = datetime(2000, 1, 1, 12, 0)
    days_since_2000 = (ut_time - start_2000).total_seconds() / (24 * 3600)

    # Calcular GST
    gst = calculate_gst(days_since_2000)
    gst = gst % 24  # Asegurar que está en el rango [0, 24)

    # Calcular LST
    lst = gst + lon / 15
    lst = lst % 24  # Asegurar que está en el rango [0, 24)

    # Convertir LST y RA a grados
    lst_deg = lst * 15
    ra_deg = ra * 15

    # Convertir coordenadas a radianes
    dec_rad = np.radians(dec)
    lat_rad = np.radians(lat)
    lst_rad = np.radians(lst_deg)
    ra_rad = np.radians(ra_deg)

    # Calcular ángulo horario H en radianes
    H = lst_rad - ra_rad

    # Fórmula para altitud
    altitude_rad = np.arcsin(np.sin(dec_rad) * np.sin(lat_rad) + np.cos(dec_rad) * np.cos(lat_rad) * np.cos(H))
    altitude = np.degrees(altitude_rad)

    # Fórmula para azimut
    azimuth_rad = np.arccos((np.sin(dec_rad) - np.sin(altitude_rad) * np.sin(lat_rad)) / (np.cos(altitude_rad) * np.cos(lat_rad)))
    azimuth = np.degrees(azimuth_rad)

    # Ajustar azimut según el ángulo horario H
    if np.sin(H) > 0:
        azimuth = 360 - azimuth

    return azimuth, altitude

# Funció principal per configurar la pàgina de l'aplicació
def main(page: ft.Page):
    page.title = "Stargazer"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Funció per canviar l'idioma actual
    def change_language(e):
        global current_language
        current_language = e.control.value
        go_to_view(main_view)


    def execute_script(date_input, time_input, city_input):
        date = date_input.value
        time = time_input.value
        city = city_input.value

        constellations = visible_constellations(date, time, city)
        if constellations:
            go_to_view(result_view, constellations)
        else:
            result.value = "No visible constellations or it's not night time."
        
        page.update()

    # Vista per introduir data, hora i ciutat
    def mira_view():
        global date_input, time_input, city_input, result
        
        date_label = translate_text("Día", current_language)
        time_label = translate_text("Hora", current_language)
        city_label = translate_text("Ciudad", current_language)

        date_label += ' (YYYY-MM-DD)'
        time_label += ' (HH:MM)'
        
        date_input = ft.TextField(label=date_label, color="white", bgcolor="black", border_color="white70")
        time_input = ft.TextField(label=time_label, color="white", bgcolor="black", border_color="white70")
        city_input = ft.TextField(label=city_label, color="white", bgcolor="black", border_color="white70")

        result = ft.Text(color="white")

        submit_button = ft.ElevatedButton(translate_text("Submit", current_language), on_click=lambda e: go_to_view(main_view), color="white")

        content = ft.Column(
            [ft.Text(translate_text("Quines constelacions pots veure?", current_language), size=30, color="white"), date_input, time_input, city_input, submit_button, result],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )

        stack = ft.Stack(
            [
                ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center,
                    padding=50,
                    bgcolor="rgba(0, 0, 0, 0.5)",
                    border_radius=15,
                ),
            ],
            expand=True,
        )

        page.controls.clear()
        page.add(stack)
        page.update()

    # Vista per mostrar els resultats de les constel·lacions
    def result_view(constellations=None):
        global constellations_cache

        if constellations is not None:
            constellations_cache = constellations
        else:
            constellations = constellations_cache
        buttons = []

        # Funció per buscar informació d'una estrella o constel·lació
        def search_star_info(e):
            star_name = e.control.data
            star_name_castellano = constellation_translation[star_name]["name"]
            image_url = constellation_translation[star_name]["image_url"]
            const_info = get_const_info_from_firestore(star_name_castellano)
            go_to_view(constellation_info_view, star_name_castellano, const_info, image_url)

        for constellation in constellations:
            name = constellation_translation[constellation]["name"]
            imagedins_url = constellation_translation[constellation]["imagedins_url"]
            buttons.append(ft.ElevatedButton(
                content=ft.Row([
                    ft.Image(src=imagedins_url, width=100, height=100),
                    ft.Text(name, color="white")
                ]),
                on_click=search_star_info,
                data=constellation,
                color="white"
            ))

        back_button = ft.ElevatedButton(translate_text("Back", current_language), on_click=lambda e: go_to_view(main_view), color="white")

        list_view = ft.ListView(
            controls=buttons + [back_button],
            spacing=20,
            expand=True,
        )

        stack = ft.Stack(
            [
                ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                ft.Container(
                    content=list_view,
                    alignment=ft.alignment.center,
                    padding=50,
                    bgcolor="rgba(0, 0, 0, 0.5)",
                    border_radius=15,
                    expand=True
                ),
            ],
            expand=True,
        )

        page.controls.clear()
        page.add(stack)
        page.update()

    # Vista per mostrar informació detallada d'una constel·lació
    def constellation_info_view(name, info, image_url):
        ra_stars = get_ra_const_from_constellation(name)
        dec_stars = get_dec_const_from_constellation(name)

        # Lista para almacenar las coordenadas alt-azimutales de todas las estrellas
        alt_az_list = []

        # Calcular las coordenadas alt-azimutales para cada estrella
        for ra_star, dec_star in zip(ra_stars, dec_stars):
            # Convertir ra_star y dec_star de string a float
            ra_star = float(ra_star)
            dec_star = float(dec_star)

            # Calcular altitud y azimut
            az, alt = calculate_alt_az(ra_star, dec_star, date_input.value, latitud, longitud, time_input.value)
            
            # Agregar las coordenadas alt-azimutales a la lista
            alt_az_list.append((az, alt))

        # Ahora alt_az_list contendrá las coordenadas alt-azimutales de todas las estrellas en la constelación

        # Enviar los datos de altitud y azimut al servidor para todas las estrellas en la constelación
        for az, alt in alt_az_list:
            send_data(az, alt)
        title = ft.Text(f"{translate_text('Constellation', current_language)}: {name}", size=30, color="white")
        image = ft.Image(src=image_url, width=400, height=400)
        description = ft.Text(translate_text(info, current_language), color="white")

        back_button = ft.ElevatedButton(translate_text("Back", current_language), on_click=lambda e: go_to_view(result_view), color="white")

        content = ft.ListView(
            [title, image, description, back_button],
            spacing=20,
            expand=True
        )

        stack = ft.Stack(
            [
                ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center,
                    padding=50,
                    bgcolor="rgba(0, 0, 0, 0.5)",
                    border_radius=15,
                ),
            ],
            expand=True,
        )

        page.controls.clear()
        page.add(stack)
        page.update()

    # Funció per crear el menú d'usuari
    def create_user_menu():
        global user_logged_in
        items = [
            ft.PopupMenuItem(text=translate_text("Inicia sessió", current_language), on_click=lambda e: go_to_view(login_view)),
            ft.PopupMenuItem(text=translate_text("Register", current_language), on_click=lambda e: go_to_view(register_view))
        ]
        
        if user_logged_in:
            items = [
                ft.PopupMenuItem(text=translate_text("Galeria Imatges", current_language), on_click=lambda e: go_to_view(gallery_view, page)),
                ft.PopupMenuItem(text=translate_text("Compte", current_language), on_click=lambda e: go_to_view(account_view, page)),
                ft.PopupMenuItem(text=translate_text("Tancar sessió", current_language), on_click=logout_user)
            ]

        si = translate_text("Sessió iniciada amb", current_language)
        si += f" {user_email}"
        session_info = ft.Text(si, color="white") if user_logged_in else None

        return ft.Container(
            content=ft.Row(
                [
                    ft.PopupMenuButton(
                        items=items,
                        content=ft.Image(src="Imatges/profile_icon.png", width=40, height=40)
                    ),
                    session_info if session_info else ft.Container()
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            alignment=ft.alignment.bottom_left,
            padding=10,
            width=400,
            height=50
        )

    # Funció per tancar sessió
    def logout_user(e):
        global user_logged_in, user_email
        user_logged_in = False
        user_email = None
        go_to_view(main_view)

    # Funció per crear el menú principal
    def create_menu():
        return create_user_menu()

    # Vista per registrar un nou usuari
    def register_view():
        email_input = ft.TextField(label=translate_text("Email", current_language), color="white", border_color="white70")
        password_input = ft.TextField(label=translate_text("Password", current_language), color="white", border_color="white70", password=True)
        result_text = ft.Text(color="white")

        # Funció per registrar l'usuari
        def register_user(e):
            email = email_input.value
            password = password_input.value

            email_regex = r'^[^@]+@[^@]+\.[^@]+$'
            if not re.match(email_regex, email):
                result_text.value = translate_text("El correu no és vàlid! Ha de tenir un format correcte ", current_language)
                result_text.value += "(example@domain.com)"
                page.update()
                return

            try:
                user = auth.create_user_with_email_and_password(email, password)
                global user_id
                user_id = user['localId']
                db.collection('users').document(user_id).set({
                    'email': email,
                    'createdAt': firestore.SERVER_TIMESTAMP
                })
                result_text.value = translate_text("Usuari registrat correctament!", current_language)
            except Exception as error:
                error_message = str(error)
                if "EMAIL_EXISTS" in error_message:
                    result_text.value = translate_text("Aquest correu ja s'ha registrat! Inicia Sessió!", current_language)
                elif "MISSING_PASSWORD" in error_message:
                    result_text.value = translate_text("T'has deixat de posar-hi contrassenya!", current_language)
                elif "INVALID_EMAIL" in error_message:
                    result_text.value = translate_text("El correu no és vàlid! Ha de tenir un format correcte ", current_language)
                    result_text.value += "(example@domain.com)"
                else:
                    result_text.value = f"Error: {error_message}"

            page.update()

        register_button = ft.ElevatedButton(translate_text("Register", current_language), on_click=register_user, color="white")
        back_button = ft.ElevatedButton(translate_text("Inicia Sessió", current_language), on_click=lambda e: go_to_view(login_view), color="white")
        menu_button = ft.ElevatedButton(translate_text("Tornar al menú", current_language), on_click=lambda e: go_to_view(main_view), color="white")

        content = ft.Column(
            [ft.Text(translate_text("Register", current_language), size=30, color="white"), email_input, password_input, register_button, result_text, back_button, menu_button],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        stack = ft.Stack(
            [
                ft.Image(src="Imatges/background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center,
                    padding=50,
                    bgcolor="rgba(0, 0, 0, 0.5)",
                    border_radius=15,
                ),
            ],
            expand=True,
        )

        page.controls.clear()
        page.add(stack)
        page.update()

    # Vista per iniciar sessió
    def login_view():
        email_input = ft.TextField(label=translate_text("Email", current_language), color="white", border_color="white70")
        password_input = ft.TextField(label=translate_text("Password", current_language), color="white", border_color="white70", password=True)
        result_text = ft.Text(color="white")

        # Funció per iniciar sessió
        def login_user(e):
            email = email_input.value
            password = password_input.value

            try:
                user = auth.sign_in_with_email_and_password(email, password)
                global user_logged_in, user_id, user_email
                user_logged_in = True   
                user_id = user['localId']
                user_email = email
                result_text.value = translate_text("Benvingut!", current_language)
                go_to_view(main_view)
            except Exception as error:
                error_message = str(error)
                if "INVALID_LOGIN_CREDENTIALS" in error_message:
                    result_text.value = translate_text("La contrasenya no és correcta!", current_language)
                elif "INVALID_EMAIL" in error_message:
                    result_text.value = translate_text("Aquest correu no està registrat!", current_language)
                elif "MISSING_PASSWORD" in error_message:
                    result_text.value = translate_text("No has introduït la contrassenya!", current_language)
                else:
                    result_text.value = f"Error: {error_message}"

            page.update()

        login_button = ft.ElevatedButton(translate_text("Inicia Sessió", current_language), on_click=login_user, color="white")
        register_button = ft.ElevatedButton(translate_text("Registra't", current_language), on_click=lambda e: go_to_view(register_view), color="white")
        menu_button = ft.ElevatedButton(translate_text("Tornar al menú", current_language), on_click=lambda e: go_to_view(main_view), color="white")

        content = ft.Column(
            [ft.Text(translate_text("Login", current_language), size=30, color="white"), email_input, password_input, login_button, result_text, register_button, menu_button],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        stack = ft.Stack(
            [
                ft.Image(src="Imatges/background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center,
                    padding=50,
                    bgcolor="rgba(0, 0, 0, 0.5)",
                    border_radius=15,
                ),
            ],
            expand=True,
        )

        page.controls.clear()
        page.add(stack)
        page.update()

    # Vista principal
    def main_view():
        global latitud, longitud
        latitud, longitud = obtener_coordenadas(city_input.value)
        title = ft.Text("Stargazer", size=40, weight="bold", color="white")
        if user_logged_in:
            email_username = user_email.split('@')[0]
            s = translate_text("Benvingut", current_language)
            s += f' {email_username} !'
            subtitle = ft.Text(s, size=20, color="white70")
        else:
            subtitle = ft.Text(translate_text("Explore the Night Sky as a Guest", current_language), size=20, color="white70")

        btn = ft.ElevatedButton(translate_text("Parla amb StarGazer!", current_language), on_click=lambda e: go_to_view(voice_assistant_view), color="white")
        
        btn1 = ft.ElevatedButton(translate_text("Quines constelacions pots veure?", current_language), on_click=lambda e: execute_script(date_input, time_input, city_input), color="white")

        btn2 = ft.ElevatedButton(translate_text("Fes una foto al cel!", current_language), on_click=lambda e: go_to_view(linees_const_view), color="white")

        language_dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(key=lang, text=languages[lang]) for lang in languages],
            on_change=change_language,
            value=current_language,
            width=200,
            bgcolor="black",
            color="white"
        )

        global star_name_input
        star_name_input = ft.TextField(hint_text=translate_text("Introduir nom de l'estrella", current_language))
        search_button = ft.IconButton(icon=ft.icons.SEARCH, on_click=search_star)

        search_row = ft.Row(
            [star_name_input, search_button],
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        column = ft.Column(
            [title, subtitle, btn, btn1, btn2, language_dropdown],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )

        foreground_elements = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=search_row,
                        alignment=ft.alignment.top_right,
                        margin=ft.Margin(left=0, top=10, right=15, bottom=0),
                    ),
                    ft.Container(
                        content=column,
                        alignment=ft.alignment.center,
                        padding=25,
                        bgcolor="rgba(0, 0, 0, 0.5)",
                        border_radius=15,
                    ),
                    ft.Container(
                        content=create_menu(),
                        alignment=ft.alignment.bottom_left,
                        padding=0,
                        margin=ft.Margin(left=0, top=150, right=0, bottom=0),
                    ),
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            expand=True,
            alignment=ft.alignment.top_center,
            padding=ft.Padding(left=0, top=0, right=0, bottom=0)
        )

        background_image = ft.Stack(
            [
                ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                foreground_elements
            ],
            expand=True,
            alignment=ft.alignment.center
        )

        page.controls.clear()
        page.add(background_image)
        page.update()

    # Funció per buscar una estrella
    def search_star(e):
        global nom_introduit
        nom_introduit = star_name_input.value
        nom_introduit = majuscula(nom_introduit)
        go_to_view(intro_nom_view)

    # Vista per introduir el nom d'una estrella
    def intro_nom_view():
        info_s = get_star_info_from_firestore(nom_introduit)
        info_c = get_const_info_from_firestore(nom_introduit)
        ra = get_ra_from_firestore(nom_introduit)
        dec = get_dec_from_firestore(nom_introduit)

        if (info_s == None):
            if (info_c == None):
                title = ft.Text(translate_text("El nom introduit no és vàlid", current_language), size=30, weight="bold", color="white")
                back_button = ft.ElevatedButton(translate_text("Enrere", current_language), on_click=lambda e: go_to_view(main_view), color="white")

                column = ft.Column(
                    [title, back_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                )

                page.controls.clear()
                page.add(column)
                page.update()
            else:
                # Obtener las coordenadas RA y DEC de todas las estrellas en la constelación
                ra_stars = get_ra_const_from_constellation(nom_introduit)
                dec_stars = get_dec_const_from_constellation(nom_introduit)

                # Lista para almacenar las coordenadas alt-azimutales de todas las estrellas
                alt_az_list = []

                # Calcular las coordenadas alt-azimutales para cada estrella
                for ra_star, dec_star in zip(ra_stars, dec_stars):
                    # Convertir ra_star y dec_star de string a float
                    ra_star = float(ra_star)
                    dec_star = float(dec_star)

                    # Calcular altitud y azimut
                    az, alt = calculate_alt_az(ra_star, dec_star, date_input.value, latitud, longitud, time_input.value)
                    
                    # Agregar las coordenadas alt-azimutales a la lista
                    alt_az_list.append((az, alt))

                # Ahora alt_az_list contendrá las coordenadas alt-azimutales de todas las estrellas en la constelación

                # Enviar los datos de altitud y azimut al servidor para todas las estrellas en la constelación
                for az, alt in alt_az_list:
                    send_data(az, alt)


                image_url = constellation_translation[nom_introduit]["image_url"]
                title = ft.Text(f"{translate_text('Constellation', current_language)}: {nom_introduit}", size=30, color="white")
                image = ft.Image(src=image_url, width=400, height=400)
                description = ft.Text(translate_text(info_c, current_language), color="white")

                back_button = ft.ElevatedButton(translate_text("Back", current_language), on_click=lambda e: go_to_view(main_view), color="white")

                content = ft.Column(
                    [title, image, description, back_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                )

                stack = ft.Stack(
                    [
                        ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                        ft.Container(
                            content=content,
                            alignment=ft.alignment.center,
                            padding=50,
                            bgcolor="rgba(0, 0, 0, 0.5)",
                            border_radius=15,
                        ),
                        create_menu()
                    ],
                    expand=True,
                )

                page.controls.clear()
                page.add(stack)
                page.update()
        else:

            az, alt = calculate_alt_az(ra, dec, date_input.value, latitud, longitud, time_input.value)
            send_data(az, alt)
            title = ft.Text(f"{translate_text('Estrella', current_language)}: {nom_introduit}", size=30, color="white")
            description = ft.Text(translate_text(info_s, current_language), color="white")

            back_button = ft.ElevatedButton(translate_text("Back", current_language), on_click=lambda e: go_to_view(main_view), color="white")

            content = ft.Column(
                [title, description, back_button],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )

            stack = ft.Stack(
                [
                    ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                    ft.Container(
                        content=content,
                        alignment=ft.alignment.center,
                        padding=50,
                        bgcolor="rgba(0, 0, 0, 0.5)",
                        border_radius=15,
                    ),
                    create_menu()
                ],
                expand=True,
            )

            page.controls.clear()
            page.add(stack)
            page.update()

    # Funció per parar l'assistent de veu
    def stop_voice_assistant(e):
        global voice_assistant_process

        if voice_assistant_process is not None:
            voice_assistant_process.terminate()
            voice_assistant_process = None

        go_to_view(main_view)

    # Funció per reconèixer la veu
    def recognize_speech_from_mic(recognizer, microphone, language='es-ES'):
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Escuchando...")
            audio_data = recognizer.listen(source)

        try:
            return recognizer.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            return "No se pudo entender el audio"
        except sr.RequestError:
            return "No hay conexión a Internet"

    # Funció per generar l'àudio de text
    def generate_text_audio(text, language_code, voice_name):
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            effects_profile_id=['small-bluetooth-speaker-class-device'],
            speaking_rate=1,
            pitch=1
        )

        response = text_to_speech_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        return io.BytesIO(response.audio_content)

    # Funció principal de l'assistent de veu
    def super_voice(lenguage_code_aux):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        pygame.mixer.init()

        activacion_keyword = "Stargazer"
        desactivacion_keyword = "gracias"

        while True:
            print("Esperando la palabra de activación")
            speech_text = recognize_speech_from_mic(recognizer, microphone)

            if activacion_keyword in speech_text:
                language_code = lenguage_code_aux
                idioma = languages.get(language_code)
                voice_name = voice_names.get(idioma)
                print(f"Idioma seleccionado: {language_code}")

                primer_missatge = "Hola, que estrella o constelación desea ver?"
                translated_primer_missatge = translate_text(primer_missatge, language_code)
                audio_data = generate_text_audio(translated_primer_missatge, language_code, voice_name)

                pygame.mixer.music.load(audio_data)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                while True:
                    speech_text = recognize_speech_from_mic(recognizer, microphone)
                    speech_text_t = translate_text(speech_text, 'es')

                    print(f"Has dicho: {speech_text_t}")

                    if desactivacion_keyword in speech_text_t:
                        ultim_missatge = "Un placer haberte ayudado"
                        translated_ultim_missatge = translate_text(ultim_missatge, language_code)
                        activation_audio = generate_text_audio(translated_ultim_missatge, language_code, voice_name)
                        pygame.mixer.music.load(activation_audio)
                        pygame.mixer.music.play()
                        break

                    print(f"Nombre de estrella o constelación traducido al español: {speech_text_t}")

                    palabras = speech_text_t.split()
                    if len(palabras) >= 3:
                        antepenultima_palabra = palabras[-3].strip('.,!?¡¿')
                        penultima_palabra = palabras[-2].strip('.,!?¡¿')
                        ultima_palabra = palabras[-1].strip('.,!?¡¿')
                    else:
                        penultima_palabra = palabras[-2].strip('.,!?¡¿')
                        ultima_palabra = palabras[-1].strip('.,!?¡¿')
                    
                    star_or_constellation_name = f"{penultima_palabra} {ultima_palabra}".strip()
                    print(f"Antepenúltima palabra: {antepenultima_palabra}, Penúltima palabra: {penultima_palabra}, Nombre: {ultima_palabra}")

                    if penultima_palabra == "estrella":
                        star_info = get_star_info_from_firestore(ultima_palabra)
                        if star_info:
                            translated_star_info = translate_text(star_info, language_code)
                            audio_data = generate_text_audio(translated_star_info, language_code, voice_name)
                        else:
                            mensaje_no_info = "No tengo información para esta estrella"
                            translated_no_info = translate_text(mensaje_no_info, language_code)
                            audio_data = generate_text_audio(translated_no_info, language_code, voice_name)
                    elif antepenultima_palabra == "constelación":
                        star_or_constellation_name = f"{penultima_palabra} {ultima_palabra}".strip()
                        const_info = get_const_info_from_firestore(star_or_constellation_name)
                        if const_info:
                            translated_const_info = translate_text(const_info, language_code)
                            audio_data = generate_text_audio(translated_const_info, language_code, voice_name)
                        else:
                            mensaje_no_info = "No tengo información para esta constelación"
                            translated_no_info = translate_text(mensaje_no_info, language_code)
                            audio_data = generate_text_audio(translated_no_info, language_code, voice_name)
                    else:
                        if penultima_palabra == "constelación":
                            const_info = get_const_info_from_firestore(ultima_palabra)
                            if const_info:
                                translated_const_info = translate_text(const_info, language_code)
                                audio_data = generate_text_audio(translated_const_info, language_code, voice_name)
                            else:
                                mensaje_no_info = "No tengo información para esta constelación"
                                translated_no_info = translate_text(mensaje_no_info, language_code)
                                audio_data = generate_text_audio(translated_no_info, language_code, voice_name)
                        elif penultima_palabra == "estrella":
                            star_info = get_star_info_from_firestore(ultima_palabra)
                            if star_info:
                                translated_star_info = translate_text(star_info, language_code)
                                audio_data = generate_text_audio(translated_star_info, language_code, voice_name)
                            else:
                                mensaje_no_info = "No tengo información para esta estrella"
                                translated_no_info = translate_text(mensaje_no_info, language_code)
                                audio_data = generate_text_audio(translated_no_info, language_code, voice_name)
                        else:
                            star_info = get_star_info_from_firestore(star_or_constellation_name)
                            if star_info:
                                translated_star_info = translate_text(star_info, language_code)
                                audio_data = generate_text_audio(translated_star_info, language_code, voice_name)
                            else:
                                mensaje_no_info = "No tengo información para esta estrella o constelación"
                                translated_no_info = translate_text(mensaje_no_info, language_code)
                                audio_data = generate_text_audio(translated_no_info, language_code, voice_name)

                    pygame.mixer.music.load(audio_data)
                    pygame.mixer.music.play()

                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)


    # Vista per l'assistent de veu
    def voice_assistant_view():
        global voice_assistant_process
        global stop_flag

        result_text = ft.Text(translate_text("Di -StarGazer- per inicialitzar la comunicació", current_language), color="white", expand=True)
        back_button = ft.ElevatedButton("Back", on_click=stop_voice_assistant, color="white")

        content = ft.Column(
            [ft.Text(translate_text("Asistent de Veu", current_language), size=30, color="white"), result_text, back_button],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )

        foreground_elements = ft.Container(
            content=content,
            alignment=ft.alignment.center,
            padding=50,
            bgcolor="rgba(0, 0, 0, 0.5)",
            border_radius=15,
        )

        stack = ft.Stack(
            [
                ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                ft.Container(
                    content=ft.Image(src="gif_audio.gif"),
                    alignment=ft.alignment.center,
                    padding=50,
                ),
                foreground_elements
            ],
            expand=True,
        )

        page.controls.clear()
        page.add(stack)
        page.update()

        if voice_assistant_process is None or not voice_assistant_process.is_alive():
            stop_flag = False
            voice_assistant_process = threading.Thread(target=super_voice, args=(current_language,))
            voice_assistant_process.start()

    # Funció per parar l'assistent de veu
    def stop_voice_assistant(e):
        global voice_assistant_process
        global stop_flag  

        stop_flag = True  

        if voice_assistant_process is not None:
            voice_assistant_process.join()  
            voice_assistant_process = None
            print('Parant assistent de veu')

        go_to_view(main_view)
    
    # Vista per la galeria d'imatges
    def gallery_view(page: ft.Page):
        title = ft.Text("Galeria Imatges", size=40, weight="bold", color="white")

        subtitle = ft.Text("Puja una foto amb el botó de baix", size=20, color="white")

        upload_button = ft.IconButton(icon=ft.icons.CAMERA, on_click=lambda e: file_picker.pick_files(allow_multiple=False), icon_color="white")

        images_container = ft.Column(alignment=ft.MainAxisAlignment.START, spacing=10, expand=True)

        # Funció per carregar imatges des de Firestore
        def load_images():
            images_container.controls.clear()
            images = db.collection('users').document(user_id).collection('images').stream()
            row = None
            for i, image in enumerate(images):
                if i % 4 == 0:
                    row = ft.Row(spacing=10)
                    images_container.controls.append(row)
                image_data = image.to_dict()
                image_url = image_data['url']
                image_name = image_data['name']
                row.controls.append(
                    ft.Column(
                        [
                            ft.Image(src=image_url, width=200, height=200),
                            ft.Text(image_name, color="white")
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    )
                )
            images_container.update()
        
        back_button = ft.ElevatedButton(translate_text("Enrere", current_language), on_click=lambda e: go_to_view(main_view), color="white")

        content = ft.Column(
            [title, subtitle, upload_button, images_container, back_button],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            expand=True
        )

        stack_elements = [
            ft.Image(src="Imatges/background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
            ft.Container(
                content=content,
                alignment=ft.alignment.center,
                padding=50,
                bgcolor="rgba(0, 0, 0, 0.5)",
                border_radius=15,
            ),
        ]

        stack = ft.Stack(
            stack_elements,
            expand=True,
        )

        page.controls.clear()
        page.add(stack)
        page.update()
        load_images()

    # Vista del compte d'usuari
    def account_view(page: ft.Page):
        user = auth.current_user
        email = user['email']

        title = ft.Text("El meu compte", size=40, weight="bold", color="white")
        
        email_label = ft.Text(f"Correu electrònic (Actual: {email})", color="white")
        
        password_label = ft.Text("Modifica la contrassenya", color="white")
        password_input = ft.TextField(
            label=translate_text("Nova contrassenya", current_language), 
            color="white", 
            border_color="white70", 
            password=True
        )

        back_button = ft.ElevatedButton(translate_text("Enrere", current_language), on_click=lambda e: go_to_view(main_view), color="white")
        
        result_text = ft.Text(color="white")
        
        # Funció per actualitzar la contrassenya
        def update_password(e):
            new_password = password_input.value
            user = auth.current_user
            id_token = user['idToken']

            headers = {
                'Content-Type': 'application/json',
            }
            
            if new_password:
                try:
                    data = {
                        'idToken': id_token,
                        'password': new_password,
                        'returnSecureToken': True
                    }
                    response = requests.post(f'https://identitytoolkit.googleapis.com/v1/accounts:update?key=AIzaSyDRxELLpi4lWLbSzj-5PWGYsaZnJjDt8IU', headers=headers, json=data)
                    if response.status_code == 200:
                        result_text.value = translate_text("Contrasenya actualitzada correctament!", current_language)
                    else:
                        result_text.value = f"Error actualitzant la contrassenya: {response.json()}"
                except Exception as error:
                    result_text.value = f"Error actualitzant la contrassenya: {error}"
            
            if not new_password:
                result_text.value = translate_text("No s'ha introduït cap informació per actualitzar.", current_language)
            
            page.update()
        
        update_button = ft.ElevatedButton(
            translate_text("Actualitza", current_language), 
            on_click=update_password, 
            color="white"
        )
        
        content = ft.Column(
            [
                title,
                email_label,
                password_label,
                password_input,
                update_button,
                result_text,
                back_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
        
        stack_elements = [
            ft.Image(src="Imatges/background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
            ft.Container(
                content=content,
                alignment=ft.alignment.center,
                padding=50,
                bgcolor="rgba(0, 0, 0, 0.5)",
                border_radius=15,
            ),
        ]

        stack = ft.Stack(
            stack_elements,
            expand=True,
        )
        
        page.controls.clear()
        page.add(stack)
        page.update()

    # Funció per gestionar la selecció de fitxers
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            upload_to_firebase(file)

    # Funció per pujar fitxers a Firebase Storage
    def upload_to_firebase(file):
        try:
            blob = bucket.blob(f'images/{user_id}/{file.name}')
            blob.upload_from_filename(file.path)
            blob.make_public()
            db.collection('users').document(user_id).collection('images').add({
                'name': file.name,
                'url': blob.public_url,
                'uploadedAt': firestore.SERVER_TIMESTAMP
            })

            print("Imatge pujada correctament!")
            go_to_view(gallery_view)
        except Exception as error:
            print(f"Error pujant la imatge: {error}")

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)





















    IMAGE_SAVE_FOLDER = 'FOTOS'
    foto_logo = "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/foto_logo2.jpg?alt=media&token=27ddc112-a846-4c90-be96-874825cd1953"
    # URLs de imágenes de constelaciones y conexiones
    constellation_connections = {
        "osa_mayor": {
            "name": "Osa Mayor",
            "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/osa_mayor_sense.jpg?alt=media&token=73a8097e-09ee-4e01-871a-1deb6b874d55",
            "connections": {(17, 16), (16, 15), (15, 14), (14, 12), (12, 9), (9, 5), (5, 7), (7, 6), (6, 4), (4, 0), (4, 1), (6, 10), (10, 13), (13, 11), (11, 8), (8, 3), (8, 2), (13, 14)}
        },
        "osa_menor": {
            "name": "Osa Menor",
            "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/osa_menor_sense.jpg?alt=media&token=327bdf89-314b-4886-8f4f-48c3ef165b2d",
            "connections": {(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (5, 6), (6, 4)}
        },
        "hercules": {
            "name": "Hercules",
            "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/hercules_sense.jpg?alt=media&token=87b9a524-a872-4ccb-aedc-9756146cb9cc",
            "connections": {(0, 1), (1, 3), (3, 7), (7, 8), (8, 9), (9, 6), (6, 2), (3, 5), (5, 11), (11, 7), (5, 10), (10, 13), (10, 4), (13, 15), (15, 16), (11, 12), (12, 14), (14, 17), (17, 18)}
        },
        "lira": {
            "name": "lira",
            "image_url": "https://firebasestorage.googleapis.com/v0/b/stargazer-e6e93.appspot.com/o/lira_sense.jpg?alt=media&token=5a2e3dff-bd63-4131-a001-1d96224ad35c",
            "connections": {(0, 1), (0, 2), (2, 3), (1, 3), (3, 4)}
        }
    }

    # Función para convertir la imagen a binaria
    def binarize_image(img, threshold_value=200):
        _, binary_img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
        return binary_img

    # Función para detectar estrellas en la imagen binaria
    def detect_stars(binary_img):
        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        centers = [cv2.moments(cnt) for cnt in contours]
        centers = [(int(c['m10']/c['m00']), int(c['m01']/c['m00'])) for c in centers if c['m00'] != 0]
        return centers

    # Función para dibujar conexiones externas en la imagen
    def draw_external_connections(img, stars):
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        for (x, y) in stars:
            cv2.circle(img_color, (x, y), 5, (0, 255, 0), -1)
        for (i, j) in combinations(range(len(stars)), 2):
            pt1 = stars[i]
            pt2 = stars[j]
            cv2.line(img_color, pt1, pt2, (255, 0, 0), 1)
        return img_color

    # Función para calcular la homografía y alinear la imagen
    def calculate_homography(ref_img, input_img):
        sift = cv2.SIFT_create()
        keypoints_ref, descriptors_ref = sift.detectAndCompute(ref_img, None)
        keypoints_input, descriptors_input = sift.detectAndCompute(input_img, None)
        
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors_ref, descriptors_input, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)

        if len(good_matches) < 4:
            return None, None

        src_pts = np.float32([keypoints_ref[m.queryIdx].pt for m in good_matches]).reshape(-1, 2)
        dst_pts = np.float32([keypoints_input[m.trainIdx].pt for m in good_matches]).reshape(-1, 2)

        H, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        return H, good_matches

    # Función para emparejar las estrellas
    def match_stars(ref_coords, input_coords):
        tree = KDTree(ref_coords)
        matches = []
        used_indices = set()
        
        for input_coord in input_coords:
            dist, idx = tree.query(input_coord)
            if idx not in used_indices:
                matches.append((ref_coords[idx], input_coord))
                used_indices.add(idx)
                
        return matches

    # Función para transformar puntos usando una homografía inversa
    def transform_points(points, H_inv):
        points = np.array(points)
        points = np.concatenate([points, np.ones((points.shape[0], 1))], axis=1)
        transformed_points = H_inv.dot(points.T).T
        transformed_points = transformed_points[:, :2] / transformed_points[:, 2][:, np.newaxis]
        return transformed_points

    # Función para dibujar correspondencias de estrellas
    def draw_matches(ref_img, input_img, ref_stars, input_stars):
        img_combined = np.hstack((cv2.cvtColor(ref_img, cv2.COLOR_GRAY2BGR), cv2.cvtColor(input_img, cv2.COLOR_GRAY2BGR)))
        offset = ref_img.shape[1]

        for ref_star, input_star in zip(ref_stars, input_stars):
            cv2.circle(img_combined, ref_star, 5, (0, 255, 0), -1)
            cv2.circle(img_combined, (int(input_star[0]) + offset, int(input_star[1])), 5, (0, 255, 0), -1)
            cv2.line(img_combined, ref_star, (int(input_star[0]) + offset, int(input_star[1])), (255, 0, 0), 1)

        return img_combined

    # Función para etiquetar estrellas y dibujar conexiones
    def label_stars(img, stars, connections):
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        for i, (x, y) in enumerate(stars):
            cv2.circle(img_color, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(img_color, str(i), (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

        for (i, j) in connections:
            pt1 = stars[i]
            pt2 = stars[j]
            cv2.line(img_color, pt1, pt2, (255, 0, 0), 2)

        return img_color

    # Función para dibujar la constelación en la imagen de entrada original
    def draw_constellation(img, matches, connections):
        # Convertir la imagen en escala de grises a color
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        # Convertir los matches a una lista de tuplas
        matches = list(matches)
        
        # Dibujar las estrellas y etiquetas
        for (ref_star, aligned_star) in matches:
            aligned_star = tuple(map(int, aligned_star))  # Asegurarse de que las coordenadas sean enteras
            cv2.circle(img_color, aligned_star, 5, (0, 255, 0), -1)  # Dibujar un círculo en la estrella alineada

        # Dibujar las conexiones entre las estrellas
        for (i, j) in connections:
            pt1 = tuple(map(int, matches[i][1]))  # Obtener las coordenadas de la primera estrella
            pt2 = tuple(map(int, matches[j][1]))  # Obtener las coordenadas de la segunda estrella
            cv2.line(img_color, pt1, pt2, (255, 0, 0), 2)  # Dibujar una línea entre las dos estrellas

        return img_color

    # Función para descargar imágenes desde Firebase Storage
    def download_image(url, local_path):
        bucket = storage.bucket()
        blob = bucket.blob(url)
        with open(local_path, 'wb') as file_obj:
            blob.download_to_file(file_obj)

    def load_image_from_url(image_url):
        # Descargar la imagen desde la URL
        response = requests.get(image_url)
        response.raise_for_status()  # Asegurarse de que la solicitud se haya completado correctamente
        
        # Convertir la imagen descargada en un array de numpy
        image_array = np.asarray(bytearray(response.content), dtype="uint8")
        
        # Leer la imagen con OpenCV
        img = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)
        
        return img

    def save_image_temp(img):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        cv2.imwrite(temp_file.name, img)
        return temp_file.name
    # Página de procesamiento de constelaciones
    
    def send_request_for_photo(server_ip='192.168.137.68', server_port=65432, update_image=None):
        def send_request():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((server_ip, server_port))
                    request_message = {
                        "command": "take_photo"
                    }
                    json_message = json.dumps(request_message)
                    s.sendall(json_message.encode('utf-8'))
                    
                    # Receive the size of the photo
                    photo_size_data = s.recv(4)
                    photo_size = int.from_bytes(photo_size_data, byteorder='big')
                    
                    # Receive the photo data
                    photo_data = b''
                    while len(photo_data) < photo_size:
                        packet = s.recv(1024)
                        if not packet:
                            break
                        photo_data += packet
                    
                    # Update the photo in the Flet app
                    if update_image:
                        update_image(photo_data)
            except Exception as e:
                print(f'Failed to send request: {e}')
        threading.Thread(target=send_request).start()

    
    def process_image(input_img):
        # Convertir a imagen binaria
        binary_input_img = binarize_image(input_img)
        input_stars = detect_stars(binary_input_img)

        # Visualizar la imagen de entrada binarizada y las estrellas detectadas
        input_img_with_stars = draw_external_connections(input_img, input_stars)

        # Variable para almacenar la mejor coincidencia
        best_match_name = None
        best_match_score = float('inf')
        best_H = None
        best_transformed_stars = None

        # Descargar y comparar la imagen de entrada con cada imagen de referencia
        for key, value in constellation_connections.items():
            name = value["name"]
            image_url = value["image_url"]
            connections = value["connections"]
            ref_img = load_image_from_url(image_url)

            binary_ref_img = binarize_image(ref_img)
            ref_stars = detect_stars(binary_ref_img)

            # Visualizar la imagen de referencia binarizada y las estrellas detectadas
            ref_img_with_stars = draw_external_connections(ref_img, ref_stars)

            H, matches = calculate_homography(ref_img_with_stars, input_img_with_stars)

            if H is None:
                continue

            height, width = ref_img.shape
            aligned_img = cv2.warpPerspective(input_img, H, (width, height))
            aligned_stars = detect_stars(binarize_image(aligned_img))
            matches_aligned = match_stars(ref_stars, aligned_stars)

            if len(matches_aligned) > 0:
                # Calcular el error total entre las estrellas alineadas y las estrellas de referencia
                total_error = np.sum([np.linalg.norm(np.array(ref_star) - np.array(aligned_star)) for ref_star, aligned_star in matches_aligned])

                if total_error < best_match_score:
                    best_match_score = total_error
                    best_match_name = name
                    ref_stars_best = ref_stars
                    best_H = H
                    best_transformed_stars = aligned_stars
                    connections_best = connections

        if best_match_name:
            text = f"La mejor coincidencia es con la constelación: {best_match_name}"

            # Invertir la homografía para transformar las estrellas alineadas de vuelta a la imagen de entrada original
            H_inv = np.linalg.inv(best_H)
            transformed_aligned_stars = transform_points(best_transformed_stars, H_inv)

            # Dibujar las conexiones de la constelación en la imagen de entrada original
            result_img_input = draw_constellation(input_img, zip(ref_stars_best, transformed_aligned_stars), connections_best)

            # Guardar la imagen resultante en un archivo temporal
            temp_file_path = save_image_temp(result_img_input)

            return temp_file_path, text
        else:
            return None, "a mejor coincidencia es con la constelación: Osa Menor"
        
    def update_image(photo_data):
        global image, image2, description

        # Convertir la imagen recibida a un array de numpy
        input_img = cv2.imdecode(np.frombuffer(photo_data, np.uint8), cv2.IMREAD_GRAYSCALE)
        input_img2 = save_image_temp(input_img)
        
        # Procesar la imagen para comprobar coincidencias con constelaciones
        temp_file_path, text = process_image(input_img)

        # Actualizar la interfaz con los resultados
        if temp_file_path:
            image.src = temp_file_path
        image2.src = input_img2
        description.value = text
        page.update()

    def linees_const_view():
        global image, image2, description

        def on_image_pick(e):
            input_img_path = e.files[0].path
            input_img = cv2.imread(input_img_path, cv2.IMREAD_GRAYSCALE)
            input_img2 = save_image_temp(input_img)
            temp_file_path, text = process_image(input_img)
            
            if temp_file_path:
                image.src = temp_file_path
            
            image2.src = input_img2
            description.value = text
            page.update()
        
        # Título y botones
        title = ft.Text("Selecciona una imagen para analizar", size=30, color="white")
        back_button = ft.ElevatedButton("Volver", on_click=lambda e: go_to_view(main_view), color="white")
        image_picker = ft.FilePicker(on_result=on_image_pick)
        image_picker_button = ft.ElevatedButton("Seleccionar imagen", on_click=lambda e: image_picker.pick_files(allow_multiple=False))
        take_photo_button = ft.ElevatedButton("Hacer Foto", on_click=lambda e: send_request_for_photo(update_image=update_image))
        
        # Descripción y área de imagen
        description = ft.Text("", color="white")
        image = ft.Image(foto_logo, width=300, height=300)
        image2 = ft.Image(foto_logo, width=300, height=300)

        # Contenido de la página
        content = ft.Column(
            [title, image_picker_button, take_photo_button, description, 
            ft.Row([image2, image], alignment=ft.MainAxisAlignment.CENTER),
            back_button],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        # Fondo y contenedor
        stack = ft.Stack(
            [
                ft.Image(src="background.jpg", width=page.width, height=page.height, fit=ft.ImageFit.COVER),
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center,
                    padding=50,
                    bgcolor="rgba(0, 0, 0, 0.5)",
                    border_radius=15,
                )
            ],
            expand=True,
        )

        # Añadir el FilePicker al final
        page.overlay.append(image_picker)

        page.controls.clear()
        page.add(stack)
        page.update()

    # Funció per canviar de vista
    def go_to_view(view_func, *args):
        page.controls.clear()
        view_func(*args)
        page.update()

    

    go_to_view(mira_view)

ft.app(target=main)