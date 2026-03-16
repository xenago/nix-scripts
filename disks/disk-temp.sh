#!/bin/bash
# SPDX-License-Identifier: CC-BY-SA-4.0
# https://askubuntu.com/a/1478216

# Function to check if a drive exists and retrieve its temperature
get_drive_temperature() {
  local drive="$1"
  local info="$(sudo smartctl -a $drive)"
  local temp=$(echo "$info" | grep '194 Temp' | awk '{print $10}')
  if [[ $temp == '' ]]; then
    temp=$(echo "$info" | grep '190 Airflow' | awk '{print $10}')
  fi
  if [[ $temp == '' ]]; then
    temp=$(echo "$info" | grep 'Temperature Sensor 1:' | awk '{print $4}')
  fi
  if [[ $temp == '' ]]; then
    temp=$(echo "$info" | grep 'Current Drive Temperature:' | awk '{print $4}')
  fi
  if [[ $temp == '' ]]; then
    temp=$(echo "$info" | grep 'Temperature:' | awk '{print $2}')
  fi
  echo "$temp"
}

# Function to retrieve the core temperature
get_core_temperature() {
  local core_temp=$(sensors | grep 'Core 0:' | awk '{print $3}')
  echo "$core_temp"
}

# Get and print core temperature first
core_temperature=$(get_core_temperature)
echo "Core temperature: $core_temperature"

# Print drive temperatures
for drive in /dev/sd?; do
  if [ -e "$drive" ]; then
    temperature=$(get_drive_temperature "$drive")
    echo "$drive temperature: $temperature DegC"
  fi
done
