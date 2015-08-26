# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

class IGCompute(AM):
  def __init__ (self, name, host, url = None):
    if url is None:
      url = "https://%s:12369/protogeni/xmlrpc/am/2.0" % (host)
    super(IGCompute, self).__init__(name, url, "amapiv2", "pg")


#CaseWestern = IGCompute("ig-cwru", "boss.geni.case.edu")
Cornell = IGCompute("ig-cornell", "geni.it.cornell.edu")
CENIC = IGCompute("ig-cenic", "instageni.cenic.net")
Clemson = IGCompute("ig-clemson", "instageni.clemson.edu")
Colorado = IGCompute("ig-colorado", "instageni.colorado.edu")
Dublin = IGCompute("ig-ohmetrodc", "instageni.metrodatacenter.com")
GATech = IGCompute("ig-gatech", "instageni.rnoc.gatech.edu")
GPO = IGCompute("ig-gpo", "boss.instageni.gpolab.bbn.com")
Illinois = IGCompute("ig-illinois", "instageni.illinois.edu")
#Kansas = IGCompute("ig-kansas", "instageni.ku.gpeni.net")
Kentucky = IGCompute("ig-kentucky", "boss.lan.sdn.uky.edu")
KentuckyPKS2 = IGCompute("ig-ukypks2", "pks2.sdn.uky.edu")
Kettering = IGCompute("ig-kettering", "geni.kettering.edu")
#LSU = IGCompute("ig-lsu", "instageni.lsu.edu")
MAX = IGCompute("ig-max", "instageni.maxgigapop.net")
Missouri = IGCompute("ig-missouri", "instageni.rnet.missouri.edu")
MOXI = IGCompute("ig-moxi", "instageni.iu.edu")
Northwestern = IGCompute("ig-northwestern", "instageni.northwestern.edu")
NPS = IGCompute("ig-nps", "instageni.nps.edu")
NYSERNet = IGCompute("ig-nysernet", "instageni.nysernet.org")
NYU = IGCompute("ig-nyu", "genirack.nyu.edu")
#Princeton = IGCompute("ig-princeton", "instageni.cs.princeton.edu")
Rutgers = IGCompute("ig-rutgers", "instageni.rutgers.edu")
SOX = IGCompute("ig-sox", "instageni.sox.net")
Stanford = IGCompute("ig-stanford", "instageni.stanford.edu")
Utah = IGCompute("ig-utah", "boss.utah.geniracks.net")
UtahDDC = IGCompute("ig-utahddc", "boss.utahddc.geniracks.net")
UCLA = IGCompute("ig-ucla", "instageni.idre.ucla.edu")
UMKC = IGCompute("ig-umkc", "instageni.umkc.edu")
Wisconsin = IGCompute("ig-wisconsin", "instageni.wisc.edu")

def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
