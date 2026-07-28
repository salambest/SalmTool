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
#
# python3 is pinned to 3.11.15. python-for-android's `master` branch
# currently defaults the python3 recipe to the newest CPython release
# (3.14.x at time of writing). CPython 3.13+ ships a new remote-debugging
# module (Python/remote_debug.h, Python/remote_debugging.c) that calls
# preadv()/pwritev() unconditionally. Those functions are only declared in
# the Android NDK headers for API level 24+, so building against
# android.minapi = 23 fails with:
#   "implicit declaration of function 'preadv'"
# Pinning to the 3.11 series (which predates that module) avoids the
# problem entirely without needing to raise minapi or change the NDK.
#
# pyaxmlparser is intentionally left out: it needs an lxml recipe that
# isn't available on every python-for-android setup. The apk_analyzer
# module already falls back to a built-in heuristic parser when
# pyaxmlparser is missing, so the app stays fully functional either way.
# ---------------------------------------------------------------------------
requirements = python3==3.11.15,kivy==2.3.0,kivymd==1.2.0,pillow,requests,plyer,fpdf2

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
android.ndk_api = 23
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
