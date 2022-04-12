"""The profile for experimenting AMD vIOMMU (r7525)
"""

import geni.portal as portal
import geni.rspec.pg as pg

pc = portal.Context()
request = pc.makeRequestRSpec()

# Add a raw PC to the request.
node = request.RawPC("node")
# Set the OS image for the node.
node.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD'
node.hardware_type = 'r7525'

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
