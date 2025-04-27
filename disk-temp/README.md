# hddtemp

In the past, one could simply run the command `hddtemp /dev/sd?` to print out a list of disk temperatures.

Sadly, this was deemed 'too useful' by distro packagers, and abandoned.

Users such as `prynstag`, `sotirov`, `david-nidam`, and `johan-ehnberg` discussed this problem and solutions on [StackOverflow's Ask Ubuntu forum](https://askubuntu.com/a/1478216), licensed `CC BY-SA 4.0`.

Ultimately, a replacement is possible.

1. Install the `lm-sensors` package to enable the `sensors` command e.g.

       sudo apt install -y lm-sensors

2.   Enable the `drivetemp` module temporarily and test the output with the `sensors` command, i.e.

         sudo modprobe drivetemp
         sensors

3. Enable the module permanently, e.g.

       echo drivetemp | sudo tee /etc/modules-load.d/drivetemp.conf

4. Download and run the script, e.g.

       curl -sLO https://raw.githubusercontent.com/xenago/nix-scripts/refs/heads/main/disk-temp/disk-temp.sh
       cat disk-temp.sh
       chmod +x disk-temp.sh
       ./disk-temp.sh
