[app]

title = Employee Manager
package.name = employeemanager
package.domain = org.beaa

source.dir = .
source.include_exts = py,json,ttf,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy==2.3.1,pyjnius,arabic-reshaper,python-bidi

orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True

android.permissions = INTERNET

[buildozer]

log_level = 2
warn_on_root = 0
