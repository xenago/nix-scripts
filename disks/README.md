# disks

Block device (HDD/SSD etc.) related.

## Checking disk status

Basic quick check for any failing drives.

Long version:
```bash
(
  # Set threshold for SSD lifetime percentage remaining
  THRESHOLD=10
  # Exit with code 1 if there is an error
  EXIT_CODE=0
  for dev in /dev/sd[a-z] /dev/nvme[0-9]; do
      [ ! -e "$dev" ] && continue
      DATA=$(sudo smartctl -A "$dev" 2>/dev/null)
      # Check for critical sector errors
      ERRORS=$(echo "$DATA" | awk '$1 ~ /^(5|197|198|181)$/ && $10 > 0 {print $2": "$10}')
      # Check NAND life remaining
      LIFE=$(echo "$DATA" | awk -v t="$THRESHOLD" '$1 ~ /^(169|177|231)$/ && $4 <= t {print $2": "$4"%"}')
      # Check NVMe "Percentage Used" (inverse logic - this tracks usage, not remaining life)
      NVME_LIFE=$(sudo smartctl -H "$dev" 2>/dev/null | grep "Percentage Used" | awk -v t="$THRESHOLD" '{u=$3; sub(/%/,"",u); if(u >= (100-t)) print "NVMe_Used: "u"%"}')
      if [ -n "$ERRORS" ] || [ -n "$LIFE" ] || [ -n "$NVME_LIFE" ]; then
          EXIT_CODE=1
          echo "=== [!] ISSUE: $dev ==="
          sudo smartctl -i "$dev" | grep -E "Model Family|Device Model|Serial Number"
          [ -n "$ERRORS" ] && echo "$ERRORS"
          [ -n "$LIFE" ] && echo "$LIFE"
          [ -n "$NVME_LIFE" ] && echo "$NVME_LIFE"
          echo "--------------------------------------"
      fi
  done
  if [ $EXIT_CODE -eq 0 ]; then 
      echo "No disks appear to be failing, but that doesn't mean they are OK."
      exit 0
  else 
      echo "Failing disks detected!"
      exit 1
  fi
)

```
