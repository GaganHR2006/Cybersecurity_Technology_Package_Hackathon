## fix(decoders): Fix pfSense filterlog decoder to support UDP, IPv6, and ICMP protocols

**Closes #41226**

---

### Problem

The existing pfSense `filterlog` decoder in Wazuh (`/var/ossec/ruleset/decoders/0225-pfsense_decoders.xml`) only matches **IPv4 TCP** traffic. All other traffic types are silently dropped during decoding:

| Traffic Type | Original Decoder | Impact |
|---|---|---|
| IPv4 TCP | ✅ Matches | None |
| IPv4 UDP | ❌ No match | DNS, NTP, DHCP traffic invisible to Wazuh |
| IPv6 TCP | ❌ No match | All IPv6 connections lost |
| IPv6 UDP | ❌ No match | All IPv6 UDP traffic lost |
| ICMP | ❌ No match | Ping sweeps, traceroutes not decoded |

In a typical enterprise network, **40–60% of firewall events are UDP** (DNS queries, NTP sync, DHCP, VoIP). These were all producing undecoded, unactionable raw log entries in Wazuh.

### Root Cause

The original decoder uses a single monolithic regex anchored to IPv4 and TCP:
```xml
<regex>...,4,[^,]*,...,6,tcp,...(\d+\.\d+\.\d+\.\d+),...(\d+),(\d+)</regex>
```

The `6,tcp` hardcoding means protocol `17` (UDP) never matches. The `,4,` anchor means IPv6 header format (which uses a different field layout and colon-separated addresses) is never attempted.

### Changes Made

Replaced the single decoder with a **parent-child decoder family**:

1. **`pfsense-filterlog`** (parent) — Matches any `filterlog:` line, extracts interface/action/direction
2. **`pfsense-filterlog-ipv4-tcp`** (child) — IPv4 TCP, extracts src_ip, dst_ip, src_port, dst_port
3. **`pfsense-filterlog-ipv4-udp`** (child) — **[PRIMARY FIX]** IPv4 UDP, same field extraction
4. **`pfsense-filterlog-ipv6`** (child) — IPv6 TCP+UDP, handles colon-separated IPv6 addresses
5. **`pfsense-filterlog-icmp`** (child) — ICMPv4, extracts type/code instead of ports

### Testing

A standalone regression test suite is included:

```bash
# Clone and run tests
cd upstream_contributions/issue_41226_pfsense_decoder
python test_runner.py
```

**Expected output:**
```
Wazuh pfSense Decoder Regression Test Suite
Issue: https://github.com/wazuh/wazuh/issues/41226
================================================================================

Test                                               Original         Fixed
--------------------------------------------------------------------------------
IPv4 TCP block                                       PASS            PASS
IPv4 UDP pass (PRIMARY BUG - Issue #41226)      EXPECTED FAIL        PASS
IPv6 TCP block                                  EXPECTED FAIL        PASS
IPv6 UDP pass                                   EXPECTED FAIL        PASS
ICMPv4 block (no ports)                         EXPECTED FAIL        PASS
IPv4 TCP large outbound (exfil indicator)            PASS            PASS

================================================================================
SUMMARY:
  Original decoder: 2/6 tests matched (expected — only IPv4 TCP supported)
  Fixed decoder:    6/6 tests passed

✓ ALL 6/6 FIXED DECODER TESTS PASSED
```

### Contributor Checklist

- [x] Tested against real pfSense filterlog samples (see `test_samples/filterlog_samples.txt`)
- [x] Regression test suite passes (`python test_runner.py` → exit code 0)
- [x] No existing IPv4 TCP decoding is broken (Test 1 and Test 6 still pass)
- [x] Parent-child decoder pattern follows Wazuh decoder conventions
- [x] Added coverage for all 4 missing protocol/IP version combinations
- [x] ICMP handled gracefully (type/code fields instead of port fields)
- [x] No changes to existing rules required (decoder output field names unchanged for TCP)
