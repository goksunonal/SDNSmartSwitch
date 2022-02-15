from mininet.topo import Topo

class Project( Topo ):
    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )
        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2', ip='172.217.169.174')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        h5 = self.addHost('h5')
        h6 = self.addHost('h6')
        h7 = self.addHost('h7')
        h8 = self.addHost('h8')
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        s3 = self.addSwitch('s3', dpid='00:00:00:00:00:01:01:00')
        
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s7 = self.addSwitch('s7')

        # Add links
        self.addLink(s1,s2)
        self.addLink(s1,s5)
        self.addLink(s2,s3)
        self.addLink(s2,s4)

        self.addLink(h1,s3)
        self.addLink(h2,s3)
        
        self.addLink(h3,s4)
        self.addLink(h4,s4)

        self.addLink(s5,s6)
        self.addLink(s5,s7)
        self.addLink(s6,h5)
        self.addLink(s6,h6)
        self.addLink(s7,h7)
        self.addLink(s7,h8)

topos = { 'project': ( lambda: Project() )} 
