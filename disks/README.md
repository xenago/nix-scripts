# disks

Block device (HDD/SSD etc.) related.

## hddtemp

In the past, one could simply run the command `hddtemp /dev/sd?` to print out a list of disk temperatures.

Sadly, this was deemed 'too useful' by distro packagers, and abandoned.

Users such as `prynstag`, `sotirov`, `david-nidam`, and `johan-ehnberg` discussed this problem and solutions on [StackOverflow's Ask Ubuntu forum](https://askubuntu.com/a/1478216), licensed `CC BY-SA 4.0`.

Ultimately, a replacement is possible.

1. Install the `lm-sensors` package to enable the `sensors` command e.g.
    ```sh
    sudo apt install -y lm-sensors
    ```

2.  Enable the `drivetemp` module temporarily and test the output with the `sensors` command, i.e.
    ```sh
    sudo modprobe drivetemp
    sensors
    ```

3. Enable the module permanently, e.g.
    ```sh
    echo drivetemp | sudo tee /etc/modules-load.d/drivetemp.conf
    ```

4. Download and run the script, e.g.
    ```sh
    curl -sLO https://raw.githubusercontent.com/xenago/nix-scripts/refs/heads/main/disks/disk-temp.sh
    cat disk-temp.sh
    chmod +x disk-temp.sh
    ./disk-temp.sh
    ```

## Serials

Display the serial numbers of disks in the system.

### lsblk method

Most widely supported:
```sh
lsblk -o NAME,SERIAL
```

### hdparm method

1. Install `hdparm`, e.g.
   ```sh
   sudo apt-get install -y hdparm
   ```

2. Run the shell command:
   ```sh
   sudo hdparm -I /dev/sd? |& grep -E 'Serial Number|/dev'
   ```

Note that this command discards errors, so some disks might not show up.

## Checking disk status

Basic quick check for any failing drives.

```bash
(
  # Set threshold for SSD lifetime percentage remaining
  THRESHOLD=10
  # Exit with code 1 if there is an error
  EXIT_CODE=0

  for dev in /dev/sd[a-z] /dev/nvme[0-9]; do
      [ ! -e "$dev" ] && continue
      
      DATA=$(sudo smartctl -A "$dev" 2>/dev/null)
      INFO=$(sudo smartctl -i "$dev" 2>/dev/null)
      MODEL=$(echo "$INFO" | grep -Ei "Model Family|Device Model|Model Number" | cut -d: -f2 | sed 's/^[ \t]*//')
      SN=$(echo "$INFO" | grep "Serial Number" | awk '{print $NF}')
      
      # 1: Read Error (not Seagate)
      # 5: Reallocated
      # 7: Seek Error (not Seagate)
      # 187: Uncorrectable 
      # 188: Timeout
      # 197: Pending
      # 198: Offline Uncorrectable
      # 199: CRC
      SIGNS=$(echo "$DATA" | awk '$1 ~ /^(1|5|7|187|188|197|198|199)$/ && $10 > 0 {print $2": "$10}')
      
      # Check NAND life remaining
      LIFE=$(echo "$DATA" | awk -v t="$THRESHOLD" '$1 ~ /^(169|177|231)$/ && $4 <= t {print $2": "$4"%"}')
      # Check NVMe "Percentage Used" (use inverse logic since this tracks usage, not remaining life)
      NVME_LIFE=$(sudo smartctl -H "$dev" 2>/dev/null | grep "Percentage Used" | awk -v t="$THRESHOLD" '{u=$3; sub(/%/,"",u); if(u >= (100-t)) print "NVMe_Used: "u"%"}')

      if [ -n "$SIGNS" ] || [ -n "$LIFE" ] || [ -n "$NVME_LIFE" ]; then
          EXIT_CODE=1
          echo "=== ALERT: $dev ($MODEL) ==="
          echo "SN: $SN"
          
          # Filter out Seagate noise for IDs 1 and 7
          if [[ "$MODEL" =~ "Seagate" ]]; then
              echo "$SIGNS" | grep -Ev "Raw_Read_Error_Rate|Seek_Error_Rate"
          else
              echo "$SIGNS"
          fi
          
          [ -n "$LIFE" ] && echo "$LIFE"
          [ -n "$NVME_LIFE" ] && echo "$NVME_LIFE"
          echo "--------------------------------------"
      fi
  done

  if [ $EXIT_CODE -eq 1 ]; then 
      echo "ALERT: Multiple failing disks detected on $(hostname)"
      exit 1
  fi
)

```
