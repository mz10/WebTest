#!/usr/bin/env python3
# Soubor:  __init__.py
# Úloha:  Flask -- aplikace
############################################################################
from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

from . import stranky
