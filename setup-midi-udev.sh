#!/bin/bash
# Setup script for MIDI device udev rules

echo "Setting up udev rules for MIDI devices..."

# Copy rules file to udev directory
sudo cp config/99-midi-devices.rules /etc/udev/rules.d/

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=sound

echo "Done! The following symlinks will be created when devices are connected:"
echo "  /dev/midi-xtouch -> X-TOUCH MINI"
echo "  /dev/midi-um1    -> EDIROL UM-1"
echo ""
echo "You may need to reconnect your MIDI devices for the changes to take effect."