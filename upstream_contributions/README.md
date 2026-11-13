# Upstream Wazuh Open-Source Contributions

This directory contains our open-source contributions to the Wazuh project made as part of the hackathon.

## Contribution: Fix pfSense Filterlog Decoder (Issue #41226)

**GitHub Issue**: [wazuh/wazuh#41226](https://github.com/wazuh/wazuh/issues/41226)

### Problem
The existing Wazuh pfSense filterlog decoder only matches IPv4 TCP traffic. It fails silently on:
- **IPv4 UDP traffic** — ports are not extracted
- **IPv6 TCP/UDP traffic** — lines are completely unmatched
- **ICMP traffic** — no port fields, causes regex failure

This means a large portion of real-world pfSense firewall logs produce no structured output in Wazuh, severely limiting network visibility for SOC analysts.

### Root Cause
The original decoder uses a single regex anchored to IPv4 (`4`) and TCP protocol (`6,tcp`). The regex does not account for:
1. Protocol field `17` (UDP) — different from `6` (TCP)
2. IPv6 header structure — different field ordering and address format
3. ICMP — no source/destination port fields

### Fix
We replaced the single broken decoder with a **decoder family** using parent-child inheritance:
- Parent decoder: matches any `filterlog:` line
- Child decoder for IPv4 TCP: captures src_ip, dst_ip, src_port, dst_port
- Child decoder for IPv4 UDP: same extraction, matches protocol `17,udp` **(the main fix)**
- Child decoder for IPv6 TCP/UDP: handles IPv6 address format
- Child decoder for ICMP: no port extraction, handles gracefully

### Files
- `issue_41226_pfsense_decoder/original_decoder.xml` — The original broken decoder
- `issue_41226_pfsense_decoder/updated_decoders.xml` — Our fixed decoder family
- `issue_41226_pfsense_decoder/test_samples/filterlog_samples.txt` — Real-world log samples
- `issue_41226_pfsense_decoder/test_runner.py` — Regression test suite
- `issue_41226_pfsense_decoder/PR_DESCRIPTION.md` — Ready-to-submit PR description

### How to Test
```bash
cd upstream_contributions/issue_41226_pfsense_decoder
python test_runner.py
# Expected: 2/6 pass with original, 6/6 pass with fixed decoder
```
