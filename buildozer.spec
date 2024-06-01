[app]
# (str) Title of your application
title = BabyWardrobe

# (str) Package name
package.name = babywardrobe

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = src

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*, assets/iconos/*, src/bbdd/*

# (str) Application versioning (method 1)
version = 0.1

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,sqlite3

# (str) presplash filename
presplash.filename = %(source.dir)s/assets/iconos/splash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/iconos/armario.png

# (str) Android logcat filters to use
logcat.filters = *:S python:D

# (str) Android NDK version to use
android.ndk = 25b

# Añadir la ruta del NDK
android.ndk_path = /home/fonsi/Escritorio/android-ndk-r25b

# (list) whitelisted architectures (default is armeabi-v7a)
android.archs = armeabi-v7a,arm64-v8a

# (str) Bootstrap to use for android builds
android.bootstrap = sdl2

# (str) Build command to use (one of release, debug, pgo_profile)
buildozer -v android debug deploy run

# Añadir la siguiente línea para deshabilitar los errores de cast de función estrictos
android.ndk_cflags = -Wno-cast-function-type-strict
