#!/usr/bin/env python3
"""
pfSense Filterlog and Suricata EVE JSON sample generator.
Generates realistic log samples for testing the upstream decoder fix.
"""
import json
import os

PFSENSE_SAMPLES = [
    # IPv4 TCP block (should parse with both old and new decoder)
    "Nov 13 12:00:01 pfsense filterlog: 5,,,1000000103,em0,match,block,in,4,0x0,,64,12345,0,DF,6,tcp,60,203.0.113.45,192.168.10.50,54321,22,0",
    # IPv4 UDP pass (BROKEN in original decoder - no port extraction)
    "Nov 13 12:00:02 pfsense filterlog: 5,,,1000000104,em0,match,pass,in,4,0x0,,64,12346,0,DF,17,udp,40,203.0.113.45,192.168.10.50,54322,53,0",
    # IPv6 TCP block (BROKEN in original decoder - completely missed)
    "Nov 13 12:00:03 pfsense filterlog: 5,,,1000000105,em1,match,block,in,6,0x60,,128,12347,tcp,40,2001:db8::cafe:1,2001:db8::192:168:10:50,44444,443,0",
    # IPv6 UDP pass (BROKEN in original decoder)
    "Nov 13 12:00:04 pfsense filterlog: 5,,,1000000106,em1,match,pass,in,6,0x60,,64,12348,udp,32,2001:db8::1,2001:db8::2,54323,53,0",
    # ICMP (no ports - edge case)
    "Nov 13 12:00:05 pfsense filterlog: 5,,,1000000107,em0,match,block,in,4,0x0,,64,12349,0,DF,1,icmp,28,203.0.113.45,192.168.10.50,8,0",
    # Large outbound (exfil indicator) IPv4 TCP
    "Nov 13 12:04:30 pfsense filterlog: 5,,,1000000108,em0,match,pass,out,4,0x0,,64,55000,0,DF,6,tcp,471859200,192.168.10.50,203.0.113.45,34567,443,0",
]

SURICATA_EVE_SAMPLES = [
    {
        "timestamp": "2026-11-13T12:00:00.000000+0000",
        "flow_id": 100000001,
        "event_type": "alert",
        "src_ip": "203.0.113.45",
        "src_port": 54321,
        "dest_ip": "192.168.10.50",
        "dest_port": 22,
        "proto": "TCP",
        "alert": {
            "action": "allowed",
            "gid": 1,
            "signature_id": 2001219,
            "rev": 20,
            "signature": "ET SCAN Potential SSH Scan",
            "category": "Attempted Information Leak",
            "severity": 2
        }
    },
    {
        "timestamp": "2026-11-13T12:04:30.000000+0000",
        "flow_id": 100000002,
        "event_type": "alert",
        "src_ip": "192.168.10.50",
        "src_port": 34567,
        "dest_ip": "203.0.113.45",
        "dest_port": 443,
        "proto": "TCP",
        "alert": {
            "action": "allowed",
            "gid": 1,
            "signature_id": 2013028,
            "rev": 6,
            "signature": "ET POLICY PE EXE or DLL Windows file download HTTP",
            "category": "Potential Corporate Privacy Violation",
            "severity": 1
        },
        "fileinfo": {
            "size": 471859200,
            "filename": "customers_export.zip"
        }
    },
    {
        "timestamp": "2026-11-13T11:55:00.000000+0000",
        "flow_id": 100000003,
        "event_type": "alert",
        "src_ip": "203.0.113.45",
        "src_port": 0,
        "dest_ip": "192.168.10.50",
        "dest_port": 0,
        "proto": "TCP",
        "alert": {
            "action": "blocked",
            "gid": 1,
            "signature_id": 2400000,
            "rev": 1,
            "signature": "ET CINS Active Threat Intelligence Poor Reputation IP group 1",
            "category": "Misc Attack",
            "severity": 2
        }
    }
]


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_dir = os.path.join(base_dir, "..", "test_fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)

    pfsense_path = os.path.join(fixtures_dir, "pfsense_samples.log")
    suricata_path = os.path.join(fixtures_dir, "suricata_eve_samples.json")

    with open(pfsense_path, "w") as f:
        for line in PFSENSE_SAMPLES:
            f.write(line + "\n")
    print(f"Written {len(PFSENSE_SAMPLES)} pfSense filterlog samples to {pfsense_path}")

    with open(suricata_path, "w") as f:
        json.dump(SURICATA_EVE_SAMPLES, f, indent=2)
    print(f"Written {len(SURICATA_EVE_SAMPLES)} Suricata EVE JSON samples to {suricata_path}")

    print("\nSample pfSense lines:")
    for line in PFSENSE_SAMPLES:
        print(f"  {line[:90]}...")


if __name__ == "__main__":
    main()
