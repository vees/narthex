# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 14:23:31 2015

@author: rob
"""

import csv
with open('/home/rob/Dropbox/With Work/photo_md5.csv', 'rb') as photomd5:
    photomd5reader = csv.reader(photomd5, delimiter=',', quotechar='"')
    for row in photomd5reader:
        print row[0], row[1]

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exo.settings")
import django
django.setup()

from exo.models import ContentInstance, ContentContainer, ContentSignature, ContentKey

# Find something on this server we can play with
ContentInstance.objects.exclude(content_container=2).last()
ContentInstance._meta.fields[0].name
b=ContentInstance._meta.fields[0]
b.name
getattr(b,'name')


