[app]

# (string) Title of your application
title = testemp

# (string) Package name
package.name = testemp

# (string) Package domain (needed for android packaging)
package.domain = org.test

# (string) Source code where the main.py lives (. means current directory)
source.dir = .

# (list) Source files to include (let's include all python and kv files)
source.include_exts = py,png,jpg,kv,atlas,json

# (string) Application versioning
version = 0.1

# (list) Application requirements
# json, os, tempfile, sys, re, traceback, path, and datetime are standard built-in python libraries.
# We explicitly list the external ones you imported:
requirements = python3==3.11, kivy, pyjnius, arabic_reshaper, python-bidi

# (list) Permissions
# Added internet access along with storage layout access for your BASE_DIR path
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (bool) Enable legacy storage access so it doesn't crash on Android 10+ when reading /Download/mainemp
android.manifest.application_arguments = android:requestLegacyExternalStorage="true"

# (int) Target Android API, should be as high as possible (SDK 33 or 34)
android.api = 34

# (int) Minimum API your APK will run on
android.minapi = 21

# (string) Android NDK version to use (Buildozer handles this automatically, but keeping it default)
android.ndk = 25b

# (bool) Use private storage for data
android.private_storage = True

# (str) The orientation of the app (landscape, portrait or all)
orientation = portrait

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug and outputs everything)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
