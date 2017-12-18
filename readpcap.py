##
## Author: Zeyu Chen
##         Ruijia Wang
##
from __future__ import division
import math
import dpkt
import binascii
import os

# part B function
def get_congestion_win(flow_src, flow_cwnd):
    for i in range(0, len(flow_src)):
        src = flow_src[i]
        print "Initial window size:", flow_cwnd.get(src)[0], "||first five window size", flow_cwnd.get(src)[2:7]


def get_transmission_num(flow_src, triple_Dup_num_EachFlow, rto_num_EachFlow):
    timeoutNum = 0
    triple_Dup_num = 0
    for i in range(0, len(flow_src)):
        src = flow_src[i]
        timeoutNum += rto_num_EachFlow[src]
        triple_Dup_num += triple_Dup_num_EachFlow[src]
        # print "Flow", i + 1, "transmission number of triple duplicate ack: ", triple_Dup_num_EachFlow[src]
        # print "Flow", i + 1, "transmission number of time out: ", rto_num_EachFlow[src]
    return timeoutNum


# part A function
def get_flow_num(tcp_c):
    return tcp_c


def get_transaction_info(transaction_string):
    for i in transaction_string:
        print transaction_string[i]


def get_throughput(flow_src, flow_size, flow_end_time, flow_start_time):
    totalByte = 0
    for i in range(0, len(flow_src)):
        src = flow_src[i]
        totalByte += flow_size.get(src)
        # print "Flow " + str(i + 1) + " Bytes send:", flow_size.get(src), "||Duration:", flow_end_time.get(src) - flow_start_time.get(src)\
        #     , "||Throughput(Byte/s):", flow_size.get(src) / (flow_end_time.get(src) - flow_start_time.get(src))
    print "Bytes send: ", totalByte, "|Duration: ", (flow_end_time - flow_start_time), "|Throughput(Mbps):", totalByte * 8/ (100000*(flow_end_time - flow_start_time))
    return totalByte * 8/ (100000*(flow_end_time - flow_start_time))


def get_loss_rate(flow_src, flowLossRate, pkt_s, pkt_r, retran_c):
    totalRetran = 0
    totalPackSend = 0
    for i in range(0, len(flow_src)):
        src = flow_src[i]
        # flowLossRate[src] = (pkt_s.get(src) - pkt_r.get(src)) / pkt_s.get(src)
        totalRetran += retran_c.get(src)
        totalPackSend += pkt_s.get(src)
        # flowLossRate[src] = (retran_c.get(src)) / pkt_s.get(src)
        # print "Flow " + str(i + 1) + ": Num of Retransmission: ",retran_c.get(src), "||Num of Packets send:", pkt_s.get(src), "||Loss Rate:", flowLossRate.get(src)
    print "Num of Retransmission:", totalRetran, "|Num of Packets send: ", totalPackSend, "|Loss Rate", totalRetran / totalPackSend
    return totalRetran,totalPackSend


def get_avgRtt(flow_src, flow_rtt, flow_transaction_c, mss, flowLossRate):
    for i in range(0, len(flow_src)):
        src = flow_src[i]
        tRtt = flow_rtt.get(src) / flow_transaction_c.get(src)
        tMss = mss.get(src)
        tP = flowLossRate.get(src)
        theory_throughput = None
        if (tP == 0):
            theory_throughput = (math.sqrt(1.5) * tMss) / tRtt
        else:
            theory_throughput = (math.sqrt(1.5) * tMss) / (math.sqrt(tP) * tRtt)
        print "RTT is", tRtt, "||Theoretical Throughput is", theory_throughput



## Get Data
def getData(file_name, output_name):
    f = open(file_name, 'rb')
    pcap = dpkt.pcap.Reader(f)

    
    sourIp = None
    destIp = None
    send_set = {}                # Set saving source ip

    # Counter
    total_c = 0
    tcp_c = 0                     # Count all flows
    send_c = 0                    # Count all send
    rece_c = 0                    # Count all receive
    retran_c = {}                 # Count retransmission for each source ip
    pkt_s = {}                    # Count packets for each source ip
    pkt_r = {}                    # Count packets for each dest ip

    
    transaction2str = {}
    transaction2ind = {}
    
    is_retran = []                # Retransmission Flag

    # Flow
    ## 
    flow_src = []                 # List for all flow sources 
    
    ##
    flow_size = {}                # Flow size
    flow_start_time = {}          # Start time of the flow
    flow_end_time = {}            # End time of the flow
    flow_win_scale = {}           # Window scale of each flow
    flow_rtt = {}                 # Total Round Trip Time
    flow_transaction_c = {}

    ##
    mss = {}                      # Maximum Segment Size

    ## 
    ack_pkt_num = {}              # ACK Number
    ack_pkt_num_checked = {}      # ACK
    flow_cwnd = {}                # Congestion window of the flow

    ##
    flow_time_out = {}            # Retransmission Time Out
    triple_Dup_num_EachFlow = {}  # the number that retrans by triple dup
    rto_num_EachFlow = {}         # the number that retrans by rto
    
    # Global Time
    start_time = 0
    end_time = 0
    
    f1 = open(output_name, "a")
    for ts, buf in pcap:  

        total_c += 1
        if (len(buf) == 64):
            continue
        if (start_time == 0):     # Record time
            start_time = ts
        end_time = ts

        # Length of the packet
        totalLen = int(binascii.hexlify(buf)[32:36], 16)
        # Ip
        srcIp = binascii.hexlify(buf)[52:60]
        dstIp = binascii.hexlify(buf)[60:68]
        ipHeaderLen = 20

        # New connection
        if (destIp == None):
            destIp = dstIp

        # TCP header
        headerStart = buf[34:]
        seq = binascii.hexlify(headerStart)[8:16]
        ackNum = binascii.hexlify(headerStart)[16:24]

        ran = bin(int(binascii.hexlify(headerStart)[24:28], 16))[2:]
        win = int(binascii.hexlify(headerStart)[28:32], 16)
        tcpHeaderLen = int(ran[0:6], 2)
        flags = ran[10:16]
        urg = flags[0]
        ack = flags[1]
        psh = flags[2]
        rst = flags[3]
        syn = flags[4]
        fin = flags[5]
        tcpSegLen = totalLen - ipHeaderLen - tcpHeaderLen

        # src -> dest
        if (destIp == dstIp):
            send_c += 1
            tuple = (int(seq, 16) + tcpSegLen, ackNum)
            if (not send_set.__contains__(srcIp)):
                tcp_c += 1
                flow_src.append(srcIp)
                send_set[srcIp] = {tuple: (ts, seq, tcpSegLen, win, total_c)}
                flow_rtt[srcIp] = 0
                flow_transaction_c[srcIp] = 0
                transaction2str[srcIp] = ""
                transaction2ind[srcIp] = 1
                flow_size[srcIp] = len(buf)
                flow_start_time[srcIp] = ts
                pkt_s[srcIp] = 1
                pkt_r[srcIp] = 0
                flow_win_scale[srcIp] = int(binascii.hexlify(buf[-1]), 16)
                ack_pkt_num[srcIp] = []
                ack_pkt_num_checked[srcIp] = []
                triple_Dup_num_EachFlow[srcIp] = 0
                rto_num_EachFlow[srcIp] = 0
                retran_c[srcIp] = 0
            else:  # contain srcIp
                flow_size[srcIp] = flow_size.get(srcIp) + len(buf)
                pkt_s[srcIp] = pkt_s.get(srcIp) + 1
                eachFlow = send_set.get(srcIp)
                if (eachFlow.__contains__(tuple)):  # cover
                    retran_c[srcIp] = retran_c.get(srcIp) + 1
                    loss_pac = eachFlow.get(tuple)
                    rto = flow_time_out.get(srcIp)
                    if (ts - loss_pac[0] < rto):
                        triple_Dup_num_EachFlow[srcIp] = triple_Dup_num_EachFlow.get(srcIp) + 1
                    elif (ts - loss_pac[0] >= rto):
                        rto_num_EachFlow[srcIp] = rto_num_EachFlow.get(srcIp) + 1
                    eachFlow[tuple] = (ts, seq, tcpSegLen, win, total_c)
                    is_retran.append(tuple)
                else:  # new thing
                    eachFlow[tuple] = (ts, seq, tcpSegLen, win, total_c)
        # dest -> src
        else:
            rece_c += 1
            flow = send_set.get(dstIp)
            sending_Tuple = None
            pkt_r[dstIp] = pkt_r.get(dstIp) + 1
            # 3-way handshake case
            if (int(syn, 2) == 1) and (int(ack, 2) == 1):

                mss[dstIp] = int(binascii.hexlify(headerStart)[44:48], 16)
                if (mss[dstIp]) > 2190:
                    flow_cwnd[dstIp] = [2 * mss[dstIp]]
                elif (mss[dstIp] > 1095) and (mss[dstIp] <= 2190):
                    flow_cwnd[dstIp] = [3 * mss[dstIp]]
                elif (mss[dstIp] <= 1095):
                    flow_cwnd[dstIp] = [4 * mss[dstIp]]
                for i in flow:
                    if (i[0] == int(ackNum, 16) - 1):
                        sending_Tuple = flow.get(i)
                        flow_rtt[dstIp] = flow_rtt.get(dstIp) + (ts - sending_Tuple[0])
                        flow_time_out[dstIp] = 2 * (ts - sending_Tuple[0])
                        flow_transaction_c[dstIp] = flow_transaction_c.get(dstIp) + 1
                        del flow[i]
                        break
            # close cases
            elif (int(fin, 2) == 1) and (int(ack, 2) == 1):
                flow_end_time[dstIp] = ts
                for i in flow:
                    if (i[0] == int(ackNum, 16) - 1):
                        sending_Tuple = flow.get(i)
                        flow_rtt[dstIp] = flow_rtt.get(dstIp) + (ts - sending_Tuple[0])
                        flow_transaction_c[dstIp] = flow_transaction_c.get(dstIp) + 1
                        del flow[i]
                        break
            else:
                tuple = (int(ackNum, 16), seq)  # key = (int(seq, 16) + tcpSegLen, ackNum) value = (ts, seq, tcpSegLen, win, total_c)
                #print tuple
                sending_Tuple = flow.get(tuple)
                # duplicated case
                if (sending_Tuple == None):
                    continue
                if (not is_retran.__contains__(tuple)):
                    flow_rtt[dstIp] = flow_rtt.get(dstIp) + (ts - sending_Tuple[0])
                    flow_transaction_c[dstIp] = flow_transaction_c.get(dstIp) + 1

                # Record all duplicate cases
                if (transaction2ind.get(dstIp) <= 2):
                    curString = transaction2str.get(dstIp) + str(flow.get(tuple)[4]) + " " + str(transaction2ind.get(dstIp)) \
                                + ": Sending part of flow: Sequence num: " + str(flow.get(tuple)[1]) \
                                + "  ||Ack num: " + str(seq) + " ||Receive Window Size: " + str(flow.get(tuple)[3] * pow(2, flow_win_scale.get(dstIp))) + "\n" \
                                + str(total_c) + " " + str(transaction2ind.get(dstIp)) + ": Response part of flow: Sequence num: " \
                                + str(seq) + "  ||Ack num: " + str(ackNum) + " ||Receive Window Size: " + str(win * pow(2, flow_win_scale.get(dstIp))) + "\n"
                    #print curString
                    transaction2ind[dstIp] = transaction2ind.get(dstIp) + 1
                    transaction2str[dstIp] = curString

                # cwnd size has problem for the dup cases
                ack_pkt_num.get(dstIp).append(total_c)

                cwnd_now = flow_cwnd.get(dstIp)[-1]
                eMss = mss.get(dstIp)

                for i in ack_pkt_num.get(dstIp):
                    if (i > sending_Tuple[4] + 1) and (i < total_c):  # and (i not in ack_pkt_num_checked.get(dport)):
                        cwnd_now += eMss
                        ack_pkt_num_checked.get(dstIp).append(i)

                for i in ack_pkt_num_checked.get(dstIp):
                    ack_pkt_num_checked.get(dstIp).remove(i)

                del ack_pkt_num_checked.get(dstIp)[:]
                flow_cwnd.get(dstIp).append(cwnd_now)
                del flow[tuple]


    flowLossRate = {}
    print "How many server send together:"
    num = get_flow_num(tcp_c)
    print num

    print end_time
    print start_time
    print "Total throughput:"
    throughput = get_throughput(flow_src, flow_size, end_time, start_time)

    print "\nRetransmission Rate:"
    totalRetran, totalPackSend = get_loss_rate(flow_src, flowLossRate, pkt_s, pkt_r, retran_c)
    #goodput = (1 - totalRetran/totalPackSend) * throughput
    goodput = (1 - (send_c - rece_c) /send_c) *throughput
    
    print "\nGoodput: ", "\n", goodput

    print "\nRatio TCP timeout: "
    timeoutNum = get_transmission_num(flow_src, triple_Dup_num_EachFlow, rto_num_EachFlow)
    print "\n", timeoutNum/totalPackSend

    print "Loss rate: ", (send_c - rece_c)*100 / send_c,"%"

    # Output to txt
    f1.write(str(totalRetran * 100/ totalPackSend) + "%")
    f1.write("    " + str(goodput))
    f1.write("    " + str((send_c - rece_c)*100 / send_c) + "%")
    f1.write("    " + str(throughput) + "\n")
    f1.close()
    f.close()

## Main
def main():
    path1 = "results_ICTCP/"
    path2 = "results_Tcpveno/"
    path3 = "results_Improved/"
    output1 = 'ICTCP.txt'
    output2 = 'Tcpveno.txt'
    output3 = 'Improved.txt'
    #files = os.listdir(path)
    for i in range(1,49):
        file_path = 'N1-received-packets{}-9-0.pcap'.format(str(i))
        getData((str(path1) + str(file_path)), output1)
        getData((str(path2) + str(file_path)), output2)
        getData((str(path3) + str(file_path)), output3)
        print(i)
    #getData('./results/N1-received-packets5-0-1.pcap')
## Run 
if __name__ == '__main__':
    main()
