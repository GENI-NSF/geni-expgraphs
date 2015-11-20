# geni-expgraphs

Feed GENI aggregate availability information to ganglia for graph generation.

This software is known to work on Ubuntu 14.04. It should work on any Linux
flavor.

# Installation

## Install geni-lib
Follow the instructions at 
http://geni-lib.readthedocs.org/en/latest/intro/ubuntu.html

## Create a config file
Copy `samples/example_config.py` from geni-lib to the geni-expgraphs
directory as `example_config.py`. Edit the sample to update `portal.cert`
and `portal.key` to the location of your GENI certificate and key.

## Test checkvmavail.py
Run `checkvmavail.py` as follows and watch for errors:

```
python checkvmavail.py 
```

If any errors occur, fix them before proceeding. The desired output will
look like this:

```
01 ig-utah is down (Used: 0 Xen, 0 OpenVZ, Avail IPs: 0/0)
02 ig-gpo is up (Used: 165 Xen, 2 OpenVZ, Avail IPs: 61/91)
   [urn:publicid:IDN+instageni.gpolab.bbn.com+node+pc5] 16/100 (Xen)
   [urn:publicid:IDN+instageni.gpolab.bbn.com+node+pc4] 19/100 (Xen)
   [urn:publicid:IDN+instageni.gpolab.bbn.com+node+pc1] 98/100 (OpenVZ)

[ more output... ]
```

## Test the wrapper script
Edit `avail.sh` to change the path to `checkvmavail.py`.

Test `avail.sh` and watch for errors:

```
./avail.sh
```

This command generates no output. Check that files were generated in `/tmp`
with names similar to these:

```
$ ls /tmp
tmpvDf80T
vmavail-20151120_124509.out
```

## Add crontab entries to run the wrapper periodically

Run the wrapper script periodically. The sample entry below runs it every
30 minutes. Also run a cron job that cleans up the temporary output.

```
# Gather aggregate availabilty and push to ganglia
*/30 * * * * /path/to/geni-expgraphs/avail.sh
# Clean up detritus from aggregate availability
5 1 * * * rm /tmp/tmp*; rm /tmp/vmavail*
```
