# Simulating VLAN Networks with Mininet

## Introduction
The `vlanhost.py` script defines a custom Mininet host class called `VLANHost` which uses a VLAN tag for the default interface. This allows for the creation of virtual networks where hosts are segmented into different VLANs, providing network isolation and security. The script also includes example topologies demonstrating the use of `VLANHost`.

## Task Description
The task is to simulate a network with two VLANs, each having 2 hosts. Hosts within the same VLAN should be able to communicate with each other, while hosts in different VLANs should not be able to communicate.

## Solution Code with Explanation

### VLANHost Class
The `VLANHost` class is a subclass of Mininet's `Host` class. It configures a host to use a VLAN tag for its default interface.

```python
from mininet.node import Host

class VLANHost(Host):
    "Host connected to VLAN interface"

    def config(self, vlan=100, **params):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super(VLANHost, self).config(**params)

        intf = self.defaultIntf()
        self.cmd('ifconfig %s inet 0' % intf)  # remove IP from default interface
        self.cmd('vconfig add %s %d' % (intf, vlan))  # create VLAN interface
        self.cmd('ifconfig %s.%d inet %s' % (intf, vlan, params['ip']))  # assign IP to VLAN interface
        
        newName = '%s.%d' % (intf, vlan)
        intf.name = newName
        self.nameToIntf[newName] = intf

        return r

hosts = {'vlan': VLANHost}
```

### VLANStarTopo Class
The `VLANStarTopo` class defines a topology with a single switch and multiple VLANs. Each VLAN has a specified number of hosts.

```python
from mininet.topo import Topo

class VLANStarTopo(Topo):
    """Example topology that uses host in multiple VLANs
       The topology has a single switch. There are k VLANs with
       n hosts in each, all connected to the single switch."""

    def build(self, k=2, n=2, vlanBase=100):
        s1 = self.addSwitch('s1')
        for i in range(k):
            vlan = vlanBase + i
            for j in range(n):
                name = 'h%d-%d' % (j+1, vlan)
                h = self.addHost(name, cls=VLANHost, vlan=vlan)
                self.addLink(h, s1)
        for j in range(n):
            h = self.addHost('h%d' % (j+1))
            self.addLink(h, s1)
```

### Example Script
The following script sets up the network using the `VLANStarTopo` topology and starts the Mininet CLI for manual testing.

```python
#!/usr/bin/env python

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from vlanhost import VLANStarTopo

def simulate_vlan_network():
    """Simulate a network with 2 VLANs, each having 2 hosts"""
    
    topo = VLANStarTopo(k=2, n=2, vlanBase=100)  # 2 VLANs, each with 2 hosts
    net = Mininet(topo=topo, waitConnected=True)
    
    net.start()
    
    print("Network setup complete. Entering CLI...")
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simulate_vlan_network()
```

## Usage
1. Install the necessary dependencies:
   ```sh
   sudo apt-get install vlan
   ```

2. Save the script as `simulate_vlan_network.py`.

3. Run the script using `sudo`:
   ```sh
   sudo python simulate_vlan_network.py
   ```

## Verification
After running the script, you will be presented with the Mininet CLI. Use the following commands to verify connectivity:

1. Hosts within the same VLAN should be able to communicate:
   ```sh
   mininet> h1-100 ping -c 1 h2-100  # Should succeed
   mininet> h1-101 ping -c 1 h2-101  # Should succeed
   ```

2. Hosts in different VLANs should not be able to communicate:
   ```sh
   mininet> h1-100 ping -c 1 h1-101  # Should fail
   mininet> h2-100 ping -c 1 h2-101  # Should fail
   ```

3. Hosts not in any VLAN should not be able to communicate with VLAN hosts:
   ```sh
   mininet> h1 ping -c 1 h1-100  # Should fail
   mininet> h2 ping -c 1 h2-100  # Should fail
   ```

This documentation provides a comprehensive guide to using the `vlanhost.py` script to simulate a VLAN network with Mininet.






Full code:

```python
#!/usr/bin/env python
"""
vlanhost.py: Host subclass that uses a VLAN tag for the default interface.

Dependencies:
    This class depends on the "vlan" package
    $ sudo apt-get install vlan

Usage (example uses VLAN ID=1000):
    From the command line:
        sudo mn --custom vlanhost.py --host vlan,vlan=1000

    From a script (see exampleUsage function below):
        from functools import partial
        from vlanhost import VLANHost

        ....

        host = partial( VLANHost, vlan=1000 )
        net = Mininet( host=host, ... )

    Directly running this script:
        sudo python vlanhost.py 1000

"""

from sys import exit  # pylint: disable=redefined-builtin

from mininet.node import Host
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.log import error


class VLANHost( Host ):
    "Host connected to VLAN interface"

    # pylint: disable=arguments-differ
    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = intf

        return r


hosts = { 'vlan': VLANHost }


def exampleAllHosts( vlan ):
    """Simple example of how VLANHost can be used in a script"""
    # This is where the magic happens...
    host = partial( VLANHost, vlan=vlan )
    # vlan (type: int): VLAN ID to be used by all hosts

    # Start a basic network using our VLANHost
    topo = SingleSwitchTopo( k=2 )
    net = Mininet( host=host, topo=topo, waitConnected=True )
    net.start()
    CLI( net )
    net.stop()

# pylint: disable=arguments-differ

class VLANStarTopo( Topo ):
    """Example topology that uses host in multiple VLANs

       The topology has a single switch. There are k VLANs with
       n hosts in each, all connected to the single switch. There
       are also n hosts that are not in any VLAN, also connected to
       the switch."""

    def build( self, k=2, n=2, vlanBase=100 ):
        s1 = self.addSwitch( 's1' )
        for i in range( k ):
            vlan = vlanBase + i
            for j in range(n):
                name = 'h%d-%d' % ( j+1, vlan )
                h = self.addHost( name, cls=VLANHost, vlan=vlan )
                self.addLink( h, s1 )
        for j in range( n ):
            h = self.addHost( 'h%d' % (j+1) )
            self.addLink( h, s1 )


def exampleCustomTags():
    """Simple example that exercises VLANStarTopo"""

    net = Mininet( topo=VLANStarTopo(), waitConnected=True )
    net.start()
    CLI( net )
    net.stop()


if __name__ == '__main__':
    import sys
    from functools import partial

    from mininet.net import Mininet
    from mininet.cli import CLI
    from mininet.topo import SingleSwitchTopo
    from mininet.log import setLogLevel

    setLogLevel( 'info' )

    if not quietRun( 'which vconfig' ):
        error( "Cannot find command 'vconfig'\nThe package",
               "'vlan' is required in Ubuntu or Debian,",
               "or 'vconfig' in Fedora\n" )
        exit()

    if len( sys.argv ) >= 2:
        exampleAllHosts( vlan=int( sys.argv[ 1 ] ) )
    else:
        exampleCustomTags()
```