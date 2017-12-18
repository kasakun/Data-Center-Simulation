/*
  Author: Zeyu Chen 
  Based on TCP VENO
*/

#ifndef TCPICTCPImproved_H
#define TCPICTCPImproved_H

#include "ns3/tcp-congestion-ops.h"

namespace ns3 {
  class TcpIctcpImproved : public TcpNewReno
  {
    public:

    static TypeId GetTypeId (void);

    TcpIctcpImproved (void);

    TcpIctcpImproved (const TcpIctcpImproved& sock);
    virtual ~TcpIctcpImproved (void);

    virtual std::string GetName () const;

    virtual void PktsAcked (Ptr<TcpSocketState> tcb, uint32_t segmentsAcked, const Time& rtt);

    virtual void CongestionStateSet (Ptr<TcpSocketState> tcb, const TcpSocketState::TcpCongState_t newState);

    virtual void IncreaseWindow (Ptr<TcpSocketState> tcb, uint32_t segmentsAcked);

    virtual uint32_t GetSsThresh (Ptr<const TcpSocketState> tcb, uint32_t bytesInFlight);

    virtual void RxCongestionAvoidance (Ptr<TcpSocketState> tcb, uint32_t segmentsAcked);
    virtual uint32_t RxSlowStart (Ptr<TcpSocketState> tcb, uint32_t segmentsAcked);
    
    virtual Ptr<TcpCongestionOps> Fork ();

  protected:
  private:
    void EnableIctcp (Ptr<TcpSocketState> tcb);
    void DisableIctcp ();

    // My code, Compute the throughput difference
    double ComputeThroughputDiff (Ptr<const TcpSocketState> tcb); 
  private:
    // My code
    double m_measure_thru;             //!<Measured throughput
    uint32_t m_count;                  //!<RTT counter, at least three times diff > threshhold, go to case 2.
    //
    Time m_baseRtt;                    //!< Minimum of all RTT measurements seen during connection
    Time m_minRtt;                     //!< Minimum of RTTs measured within last RTT
    uint32_t m_cntRtt;                 //!< Number of RTT measurements during last RTT
    bool m_doingVenoNow;               //!< If true, do Veno for this RTT
    uint32_t m_diff;                   //!< Difference between expected and actual throughput
    bool m_inc;                        //!< If true, cwnd needs to be incremented
    uint32_t m_ackCnt;                 //!< Number of received ACK
    uint32_t m_beta;                   //!< Threshold for congestion detection
  };

} // namespace ns3

#endif // TCPICTCPImproved_H
