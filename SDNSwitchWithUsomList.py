from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ether_types

ipList = [] 
listFlowAdded = False

class SDNHub(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SDNHub, self).__init__(*args, **kwargs)
        # initialize mac address table.
        self.mac_to_port = {}
        listFlowAdded = False
        with open('ipAddressesList.txt') as fh:
            fstring = fh.readlines()

        a = 0
        for line in fstring:
            ip=line.strip()
            print("ipAddressNo:" + str(a))
            ipList.append(ip)
            a = a + 1
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        global listFlowAdded
        global ipList
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # get Datapath ID to identify OpenFlow switches.
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # analyse the received packets using the packet library.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)

        dst = eth_pkt.dst
        src = eth_pkt.src
        in_port = msg.match['in_port']

        # get the received port number from packet_in message.
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        # if the destination mac address is already learned,
        # decide which port to output the packet, otherwise FLOOD.
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        # construct action list.
        actions = [parser.OFPActionOutput(out_port)]

        if ipv4_pkt:
            srcExists = ipList.count(ipv4_pkt.src) > 0
            dstExists = ipList.count(ipv4_pkt.dst) > 0
            print("ipv4 trying")
            print("flow size:")
            print(len(ipList))
            if not listFlowAdded:
                if dpid == 65792 and (srcExists or dstExists):
                    a = 0
                    for element in ipList:
                        try:
                            a = a + 1
                            print("flow element trying to add:"+ str(a))
                            default_match_src = parser.OFPMatch(
                            eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_src=element
                            )
                            print("SRC packet should be dropped")
                            self.add_flow(datapath, 5, default_match_src, [])
                            default_match_dst = parser.OFPMatch(
                                eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_dst=element
                            )
                            print("DST packet should be dropped")
                            self.add_flow(datapath, 5, default_match_dst, [])
                        except:
                            print("problem happened")
                    listFlowAdded = True
                    print("flows added")
                    print("switch info:"+ str(dpid))
        # install a flow to avoid packet_in next time.
        elif out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 6, match, actions)

        # construct packet_out message and send it.
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
        datapath.send_msg(out)
