/*
 * Author: Zeyu Chen
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/csma-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/ipv4-global-routing-helper.h"
#include "ns3/ipv4-nix-vector-helper.h"
#include <string>
#include <sstream>
#include <iostream>

using namespace ns3;

/* Topology
 *
 *	                                                                                       
 *	                                                                                      Data Center 
 *	                                                                                          |
 *	                                                             __________1.5 MB/s___________|___________
 *	                                                            |                                         |
 *	                                                            |                                         |
 *	                                                           Agg0                                      Agg1    
 * Layer 1                                       ______1MB/s____|_________________                        |____________
 *	                                            |               |                 |                       |
 *	                                            |               |                 |                       |
 * Layer 2    ________1MB/s___________________Agg 0      _____Agg 1_____         Agg 2______________       ``````   
 *	         |   |   |   |   |   |   |   |   |          |   |                        |   |         |
 *	         |   |   |   |   |   |   |   |   |          |   |           |            |   |         |          
 * Layer 3  c0  c1  c2  c3  c3  c4  c5  c6  c7               `````                        ````      
 *
 *
 * In our topology, Layer 1 has 2 nodes, Layer 2 has 2*3 nodes, Layer 3 has 2*3*8 = 48 leaves
 * The connection we used is ethernet, thus csma is used instead of simple p2p. 
 *
 *
 *
 * Three protocols are used to verify the algorithm: NewReno, ICTCP, Improved-ICTCP
 */


NS_LOG_COMPONENT_DEFINE ("DataCenter");

// Test Funciton
void DisplayIp (const char* Node_Name, Ptr<Node> node) {
	Ptr<Ipv4> ipv4 = node->GetObject<Ipv4>();
	Ipv4InterfaceAddress iaddr = ipv4->GetAddress (1,0);
	Ipv4Address addri = iaddr.GetLocal ();
	std::cout << Node_Name << ": " << addri << std::endl;
}

const char* AddressHelper (std::string pre_add, std::string suf_add, int i) {
	std::stringstream s;
	s << pre_add << i << suf_add;
	const std::string tmp = s.str(); 
	const char* cstr = tmp.c_str();
	// std::cout << cstr << std::endl;
	return cstr; 
}

int main (int argc, char *argv[]) {
	// Packet Size
	int pktSize = 10000000;
	// Protocol
	std::string protocol = "TcpVeno";

	// Time
	double startTime = 0.0;
	double endTime = 80.0;

	// Layer
	int l1_cli = 2; // number of aggragation
	int l2_cli = 3; // number toR
	int l3_cli = 8;	//number of nodes on each toR
	int activate = 2; // number of activate clients

	// Sum of each layer 
	int L1 = l1_cli;
	int L2 = l1_cli * l2_cli;
	int L3 = l1_cli * l2_cli * l3_cli;

	
	CommandLine cmd;
	cmd.AddValue("Activate_clients","number of Parallel Clients",activate);
	cmd.AddValue("Protocol","TCP Protocol",protocol);
	//cmd.AddValue("PacketSize","PacketSize per client",pktSize);
	cmd.AddValue("Start","TCP Protocol",startTime);
	cmd.AddValue("End","TCP Protocol",endTime);
	cmd.Parse(argc,argv);
	
	if (protocol == "TcpVeno")
		Config::SetDefault ("ns3::TcpL4Protocol::SocketType", StringValue ("ns3::TcpVeno"));
	else if (protocol == "TcpIctcp")
		Config::SetDefault ("ns3::TcpL4Protocol::SocketType", StringValue ("ns3::TcpIctcp"));
	else if (protocol == "TcpIctcpImproved")
		Config::SetDefault ("ns3::TcpL4Protocol::SocketType", StringValue ("ns3::TcpIctcpImproved"));
	else {
		std::cout << "Wrong Protocol!" << std::endl;
		return 0;
	}

	// Layer 0 Data Center
	NodeContainer Data_center;
	Data_center.Create(1);

	// Layer 1 
	NodeContainer L1_Node[100];
	for(int i = 0; i < L1; i++) {
		//std::cout << i << std::endl;
		L1_Node[i].Add(Data_center.Get(0));
		L1_Node[i].Create(1);
	}
	
	//Construct the network between each aggregation and toR
	//The number of toR is set by l2_cli
	NodeContainer L2_Node[100];
	for(int i = 0; i < L2; i++) {
		L2_Node[i].Add(L1_Node[i/(L2/L1)].Get(1));
		L2_Node[i].Create(1);
		//std::cout << "L2:" << i << std::endl;
		//std::cout << "L1:" << i/(L2/L1) << std::endl;
	}

	//Construct L3_Node layer
	NodeContainer L3_Node[100];
	for(int i = 0; i < L3; i++) {	
		L3_Node[i].Add(L2_Node[i/(L3/L2)].Get(1));
		L3_Node[i].Create(1);
		//std::cout << "L3:" << i << std::endl;
		//std::cout << "L2:" << i/(L3/L2) << std::endl;
	}
	std::cout << "Nodes Built..." << std::endl;
	// Connect Setting
	CsmaHelper csma;
	csma.SetChannelAttribute ("DataRate", StringValue ("1.5Mbps"));
	csma.SetChannelAttribute ("Delay", TimeValue (NanoSeconds (500)));

	std::cout << "Connection Built..." << std::endl;

	// Connection
	// Layer 1
	NetDeviceContainer L1_Device[200];
	for(int i = 0; i < L1; i++)
		L1_Device[i] = csma.Install(L1_Node[i]); // Node 0 is upper layer, Node 1 is current layer

	csma.SetChannelAttribute ("DataRate", StringValue ("1Mbps"));
	csma.SetChannelAttribute ("Delay", TimeValue (NanoSeconds (500)));
	// Layer 2
	NetDeviceContainer  L2_Device[200];
	for(int i = 0; i < L2; i++) 
		L2_Device[i] = csma.Install(L2_Node[i]);

	// Layer 3
	NetDeviceContainer L3_Device[200];

	for(int i = 0; i < L3; i++) 
		L3_Device[i] = csma.Install (L3_Node[i]);

	std::cout << "Devices Built..." << std::endl;

	// Install protocol stack
	InternetStackHelper stack;
	stack.InstallAll ();

	std::cout << "Stack Built..." << std::endl;
	
	// Assign Address
	Ipv4InterfaceContainer L1_ip[100];
	Ipv4InterfaceContainer L2_ip[500];
	Ipv4InterfaceContainer L3_ip[1000];

	Ipv4AddressHelper address;
	
	// Layer 1
	std::string pre_add = "10.0.";
	std::string suf_add = ".0";
	for(int i = 0; i < L1; i++) {
		address.SetBase(AddressHelper (pre_add, suf_add, i), "255.255.255.0");
		L1_ip[i] = address.Assign(L1_Device[i]);
	}

	// Layer 2
	pre_add = "10.1.";
	suf_add = ".0";
	for(int i = 0; i < L2; i++) {
		address.SetBase(AddressHelper (pre_add, suf_add, i), "255.255.255.0");
		L2_ip[i] = address.Assign(L2_Device[i]);
	}

	// Layer 3
	pre_add = "192.168.";
	suf_add = ".0";
	for(int i = 0; i < L3; i++) {
		address.SetBase(AddressHelper (pre_add, suf_add, i), "255.255.255.0");
		L3_ip[i] = address.Assign(L3_Device[i]);
	}
	Ipv4GlobalRoutingHelper::PopulateRoutingTables ();
	std::cout << "Address Assigned..." << std::endl;


	// Receiver
	std::cout << "Sink built at the center..." << std::endl;
	PacketSinkHelper sink ("ns3::TcpSocketFactory", InetSocketAddress(Ipv4Address::GetAny (),8080));
	ApplicationContainer sinkApp = sink.Install (L3_Node[0].Get(1));
	sinkApp.Start (Seconds(startTime));
	sinkApp.Stop (Seconds(endTime));

	// Clients 
	ApplicationContainer clientApps;
	int num = activate;
	BulkSendHelper source ("ns3::TcpSocketFactory", Address ());
	///source.SetAttribute ("OnTime", StringValue("ns3::ConstantRandomVariable[Constant=50]"));
	//source.SetAttribute ("OffTime", StringValue("ns3::ConstantRandomVariable[Constant=0]"));
	//source.SetAttribute ("DataRate", DataRateValue (DataRate (u_dataRate)));
	source.SetAttribute ("MaxBytes", UintegerValue (pktSize)); 
	AddressValue remoteAddress (InetSocketAddress (L3_ip[0].GetAddress(1), 8080));
	source.SetAttribute("Remote", remoteAddress);;
	for(int i = 1; i < L3 && num > 0; i++) {	
		clientApps.Add (source.Install (L3_Node[i].Get(1)));
		num--;
	}

	clientApps.Start (Seconds (startTime));
	clientApps.Stop (Seconds (endTime));
	std::cout << "Clients built..." << std::endl;

	std::string temp = "N1-received-packets";
	temp += std::to_string(activate);
  	csma.EnablePcap(temp, L3_Device[0].Get(1),true);
  	//csma.EnablePcap(temp, L2_Device[0].Get(0),true);

  	std::cout << "Pcap Setting..." << std::endl;

  	std::cout << "Start Simulating..." << std::endl;

	Simulator::Stop (Seconds(endTime));
	Simulator::Run ();
	Simulator::Destroy ();
#if 0 // Test
	DisplayIp ("Center:", L1_Node[0].Get(0));

	DisplayIp ("L1_1", L1_Node[0].Get(1));
	DisplayIp ("L1_2", L1_Node[1].Get(1));

	DisplayIp ("L2_1", L2_Node[0].Get(1));
	DisplayIp ("L2_2", L2_Node[1].Get(1));
	DisplayIp ("L2_3", L2_Node[2].Get(1));
	DisplayIp ("L2_4", L2_Node[3].Get(1));
	DisplayIp ("L2_5", L2_Node[4].Get(1));
	DisplayIp ("L2_6", L2_Node[5].Get(1));

	DisplayIp ("L3_1", L3_Node[0].Get(1));
	DisplayIp ("L3_2", L3_Node[1].Get(1));
	DisplayIp ("L3_3", L3_Node[2].Get(1));
	DisplayIp ("L3_4", L3_Node[3].Get(1));
	DisplayIp ("L3_5", L3_Node[4].Get(1));
	DisplayIp ("L3_47", L3_Node[47].Get(1));

#endif
	return 0;
} 
