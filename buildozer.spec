[app]
# (string) Title of your application
title = testemp

# (string) Package name
package.name = testemp

# (string) Package domain (needed for android packaging)
package.domain = org.test

# (list) Application requirements
# Note: pyjnius handles the java imports, while standard libraries like json, os, sys, etc., are built into python3.
requirements = python3, kivy, pyjnius, arabic_reshaper, python-bidi

# (list) Permissions 
# Internet is required as requested, and storage is included because of your Path config.
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (bool) Enable legacy storage access so it doesn't crash on Android 10+ when accessing /Download/mainemp
android.manifest.application_arguments = android:requestLegacyExternalStorage="true"
