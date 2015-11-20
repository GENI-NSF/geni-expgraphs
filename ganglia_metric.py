##### Python module to report data via ganglia

import socket
import string
import subprocess
import sys
import syslog

# ASCII characters which are legal in metric names
METRIC_NAME_VALID_CHARS = string.ascii_lowercase + \
                          string.ascii_uppercase + \
                          string.digits + \
                          '.,_+=:-'

# This address should always be resolvable.  If it isn't, monitoring
# should fail silently on the assumption that we have no DNS.
# N.B. We're only going to look this up, not ping it, so it need not
# actually be reachable, only resolvable.
DNS_TEST_HOSTNAME = 'monitor.gpolab.bbn.com'

class GMetric:

  # Try to find a real IP and hostname for localhost, even if /etc/hosts
  # is configured to translate the FQDN as 127.0.0.1
  def _set_localhost_ipaddr(self):
    self.spoof_ipaddr = '127.0.0.1'
    self.spoof_hostname = socket.gethostname()
    hostaddr_re = re.compile('%s has address ([0-9\.]+)' % hostname)
    p = subprocess.Popen(['/usr/bin/host', self.spoof_hostname],
                         stdout=subprocess.PIPE)
    output = p.communicate()[0]
    if p.returncode == 0:
      mobj = hostaddr_re.match(output)
      if mobj:
        ipaddr = mobj.group(1)

  # Actually invoke gmetric
  def _run_gmetric_command(self, args):
    cmdargs = [x for x in self.gmetric_args]
    cmdargs.extend(args)
    p = subprocess.Popen(cmdargs,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    [output, errout] = p.communicate()
    if p.returncode != 0:
      if self.use_syslog:
        syslog.syslog(syslog.LOG_ERR, 'gmetric command (%s) failed: %s' % \
                      (' '.join(cmdargs), errout))
      return (False, errout)

    successout = output
    if self.use_syslog == 'debug':
      syslog.syslog(syslog.LOG_DEBUG, 'gmetric command (%s) reported: %s' % \
                    (' '.join(cmdargs), successout))
    return (True, successout)

  def __init__(self, gmetric='/usr/bin/gmetric', spoofhost=None,
               use_syslog=False):
    self.spoof_hostname = spoofhost
    self.gmetric_args = [ gmetric, ]
    self.use_syslog = use_syslog

    # On FreeBSD, override gmetric's default config file
    if sys.platform.startswith('freebsd'):
      self.gmetric_args.extend([
        '-c',
        '/etc/gmond.conf'
      ])
    # Set up a translation map which can be used for metric names
    self.metric_name_trans = ''
    full_ascii_map = string.maketrans('', '')
    for chr in full_ascii_map:
      if chr not in METRIC_NAME_VALID_CHARS: chr = '_'
      self.metric_name_trans += chr

    if self.spoof_hostname:
      if self.spoof_hostname == 'localhost':
        self._set_localhost_ipaddr()
      else:
        try:
          self.spoof_ipaddr = socket.gethostbyname(self.spoof_hostname)
        except Exception, e:
          raise OSError, \
            "Could not lookup IP address of requested hostname %s" % \
            self.spoof_hostname
      self.gmetric_args.extend([
        '-S',
        "%s:%s" % (self.spoof_ipaddr, self.spoof_hostname)
      ])

    # Even if we're not spoofing a hostname, DNS is still an easy way
    # to verify that we're connected to a network right now.  Do a
    # DNS lookup of a host which should always be resolvable in our
    # infrastructure.
    else:
      try:
        socket.gethostbyname(DNS_TEST_HOSTNAME)
      except Exception, e:
        raise OSError, \
          "Could not lookup IP address of test hostname %s" % DNS_TEST_HOSTNAME

  def heartbeat(self):
    return self._run_gmetric_command(['-H'])

  def report(self, metric, type, value, units):
    report_metric = metric.encode('ascii').translate(self.metric_name_trans)
    return self._run_gmetric_command([
      '-n', '%s' % report_metric,
      '-t', '%s' % type,
      '-v', '%s' % value,
      '-u', '%s' % units
    ])

