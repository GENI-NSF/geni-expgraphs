# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This file is a modified version of a script distributed with geni-lib
# It was modified by Sarah Edwards, Raytheon BBN Technologies in 2014

import os
import multiprocessing as MP
import time

import example_config
import geni.aggregate.instageni as IG
context = example_config.buildContext()

def query_aggregate (context, site, q):
  try:
    res = []
    ad = site.listresources(context)

   
    total = [node for node in ad.nodes if node.exclusive and "raw-pc" in node.sliver_types]
    avail = [node.component_id for node in ad.nodes if node.available and node.exclusive and "raw-pc" in node.sliver_types]
    out = "[%s] (%d/%d)" % (site.name, len(avail), len(total))

    avail_ips = ad.routable_addresses.available
    config_ips = ad.routable_addresses.configured
    for node in ad.nodes:
      if not node.exclusive:
        try:
          if "emulab-xen" in node.sliver_types:
            res.append((node.component_id, node.hardware_types["pcvm"], "Xen"))
          else:
            res.append((node.component_id, node.hardware_types["pcvm"], "OpenVZ"))
        except:
          continue
    q.put((site.name, res, len(total)-len(avail), len(total), avail_ips, config_ips))
  except Exception:    
#    q.put((site.name, ["OFFLINE"], None, None, None, None))
    q.put((site.name, ["OFFLINE"], 0, 0, 0, 0))


def do_parallel ():
  q = MP.Queue()
  for site in IG.aggregates():
    p = MP.Process(target=query_aggregate, args=(context, site, q))
    p.start()

  while MP.active_children():
    time.sleep(0.5)

  l = []
  while not q.empty():
    l.append(q.get())

  xen_avail = xen_total = 0
  vz_avail = vz_total = 0
  data = {}
  rack = {}
  for idx,pair in enumerate(l):
    site_vz = site_xen = 0
    entries = []
    try:
      (site_name, res, rawused, rawtotal, avail_ips, config_ips) = pair
    except:
      print pair
      raise

    if res == ["OFFLINE"]:
      updown = 0
    else:
      updown = 1
    rack[site_name]=(rawused, rawtotal, int(avail_ips), int(config_ips), updown)
    data[site_name] = {}
    if res != ["OFFLINE"]:
      for (cid, count, typ) in res:
        if typ == "Xen":
          site_xen += 100 - int(count)
          xen_avail += int(count)
          xen_total += 100
        elif typ == "OpenVZ":
          site_vz += 100 - int(count)
          vz_avail += int(count)
          vz_total += 100
        entries.append("   [%s] %s/100 (%s)" % (cid, count, typ))
        data[site_name][cid] = (100-int(count), typ)
    if updown:
      status_str = "up"
    else:
      status_str = "down"
    print "%02d %s is %s (Used: %d Xen, %d OpenVZ, Avail IPs: %s/%s)" % (idx+1, site_name, status_str, site_xen, site_vz, int(avail_ips), int(config_ips))
    for entry in entries:
      print entry

  print "OpenVZ: %d/%d" % (vz_avail, vz_total)
  print "Xen: %d/%d" % (xen_avail, xen_total)
  return xen_total-xen_avail, vz_total-vz_avail, data, rack

def report( xen, vz, data, rack, debug=False ):
  import ganglia_metric, sys
  sys.path.append('/usr/local/lib')

  gmetric = ganglia_metric.GMetric()
  if debug:
    print 'ig_xen_reserved '+str(xen)
    print 'ig_openvz_reserved '+str(vz)
  else:
    gmetric.report('ig_xen_reserved', 'int16', '%d' % xen, 'num')
    gmetric.report('ig_openvz_reserved', 'int16', '%d' % vz, 'num')
  for site, site_val in data.items():
    for key, val in site_val.items():
      count, typ = val
      location = site.split("-")[-1]
      node = key.split("+")[-1]
      rack_type = typ.lower()
      if debug:
        print '%s_ig_%s_%s_reserved %s' % (location,node,rack_type, count)
      else:
      	# Looks like this:
     	# gmetric.report('utah_ig_pc3_xen_reserved', 'int16', '%d' % count, 'num')

      	gmetric.report('%s_ig_%s_%s_reserved' % (location,node,rack_type), 'int16', '%d' % count, 'num')
  raw_used = raw_total = raw_avail = 0
  ip_avail = ip_total = 0
  for site, site_val in rack.items():
      location = site.split("-")[-1]
      reserved = int(site_val[0])
      total = int(site_val[1])
      avail = total-reserved
      raw_used += reserved
      raw_total += total
      raw_avail += avail
      avail_ips = int(site_val[2])
      config_ips = int(site_val[3])
      updown = int(site_val[4])
      ip_avail += avail_ips
      ip_total += config_ips
      if debug:
	print '%s_ig_rawpc_reserved %s'%(location, reserved)
	print '%s_ig_rawpc_available %s'%(location, avail)
        print '%s_ig_publicips_available %s' % (location,avail_ips)
        print '%s_ig_publicips_total %s' % (location,config_ips)
        print '%s_ig_status %s' % (location,updown)
      else:
        gmetric.report('%s_ig_rawpc_reserved' % (location), 'int16', '%d' % reserved, 'num')
        gmetric.report('%s_ig_rawpc_available' % (location), 'int16', '%d' % avail, 'num')
        gmetric.report('%s_ig_publicips_available' % (location), 'int16', '%d' % avail_ips, 'num')
        gmetric.report('%s_ig_publicips_total' % (location), 'int16', '%d' % config_ips, 'num')
        gmetric.report('%s_ig_status' % (location), 'int16', '%d' % updown, 'num')
  if debug:
    print 'ig_rawpc_reserved %s'%(raw_used)
    print 'ig_rawpc_available %s'%(raw_avail)
    print 'ig_rawpc_total %s'%(raw_total)
    print 'ig_publicips_available %s'%(ip_avail)
    print 'ig_publicips_total %s'%(ip_total)
  else:
    gmetric.report('ig_rawpc_reserved', 'int16', '%d' % raw_used, 'num')
    gmetric.report('ig_rawpc_available', 'int16', '%d' % raw_avail, 'num')
    gmetric.report('ig_publicips_total', 'int16', '%d' % ip_total, 'num')
    gmetric.report('ig_publicips_available', 'int16', '%d' % ip_avail, 'num')
if __name__ == '__main__':
  xen, vz, data, rack = do_parallel()
  report(xen, vz, data, rack, debug=False)
  os.remove(context.cf.key)
