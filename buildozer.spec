[app]

# ---------------------------------------------------------------------------
# App identity
# ---------------------------------------------------------------------------
title = SalmTool Ultimate
package.name = salmtoolultimate
package.domain = org.salmtool

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt,md
version = 1.0.0

# ---------------------------------------------------------------------------
# Python / Kivy requirements bundled into the APK.
# pyaxmlparser is intentionally left out of the default build: it needs an
# lxml recipe that isn't available on every python-for-android setup. The
# apk_analyzer module already falls back to a built-in heuristic parser when
# pyaxmlparser is missing, so the app stays fully functional either way.
# Uncomment the line below if your build environment supports it.
# ---------------------------------------------------------------------------
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,psutil,requests,pyjnius,plyer,fpdf2
# requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,psutil,requests,pyjnius,plyer,fpdf2,pyaxmlparser

icon.filename = %(source.dir)s/icon.png

orientation = portrait
fullscreen = 0

# ---------------------------------------------------------------------------
# Android permissions required by the feature modules:
#   INTERNET / ACCESS_NETWORK_STATE  -> Network Analyzer, AI Helper
#   ACCESS_WIFI_STATE                -> WiFi Analyzer
#   READ/WRITE_EXTERNAL_STORAGE      -> APK Analyzer, EXIF Analyzer,
#                                       File Manager, Report Generator
# ---------------------------------------------------------------------------
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 34
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
