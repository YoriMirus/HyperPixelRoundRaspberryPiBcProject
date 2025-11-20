#!/bin/bash
patchelf --add-needed libuuid.so.1 ./bin/Debug/net8.0/runtimes/linux-arm/native/libSkiaSharp.so
patchelf --add-needed libfreetype.so.6 ./bin/Debug/net8.0/runtimes/linux-arm/native/libSkiaSharp.so 
