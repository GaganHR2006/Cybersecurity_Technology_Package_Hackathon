#!/usr/bin/env python3
"""
Regression Test Suite for Wazuh pfSense Filterlog Decoder Fix
Issue: https://github.com/wazuh/wazuh/issues/41226

Tests both the original (broken) and fixed decoder regex patterns against
real-world pfSense filterlog samples.

Usage:
    python test_runner.py

Exit codes:
    0 = all fixed decoder tests pass
    1 = one or more fixed decoder tests failed
"""
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# ORIGINAL (BUGGY) DECODER PATTERN
# Only matches IPv4 TCP. Fails on UDP, IPv6, and ICMP.
# ---------------------------------------------------------------------------
ORIGINAL_PATTERN = re.compile(
    r"filterlog:\s+[\d,]+,[\d,]*,[\d,]*,\S+,\S+,\w+,\w+,\w+,"
    r"4,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,DF,"
    r"6,tcp,\d+,"
    r"(\d+\.\d+\.\d+\.\d+),(\d+\.\d+\.\d+\.\d+),"
    r"(\d+),(\d+)"
)

# ---------------------------------------------------------------------------
# FIXED DECODER PATTERNS (one per child decoder)
# ---------------------------------------------------------------------------
FIXED_IPV4_TCP = re.compile(
    r"filterlog:.*?,4,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,"
    r"6,tcp,\d+,"
    r"(\d+\.\d+\.\d+\.\d+),(\d+\.\d+\.\d+\.\d+),"
    r"(\d+),(\d+)"
)

FIXED_IPV4_UDP = re.compile(
    r"filterlog:.*?,4,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,"
    r"17,udp,\d+,"
    r"(\d+\.\d+\.\d+\.\d+),(\d+\.\d+\.\d+\.\d+),"
    r"(\d+),(\d+)"
)

FIXED_IPV6 = re.compile(
    r"filterlog:.*?,6,[^,]*,[^,]*,[^,]*,[^,]*,"
    r"(tcp|udp),\d+,"
    r"([0-9a-fA-F:]+),([0-9a-fA-F:]+),"
    r"(\d+),(\d+)"
)

FIXED_ICMP = re.compile(
    r"filterlog:.*?1,icmp,\d+,"
    r"(\d+\.\d+\.\d+\.\d+),(\d+\.\d+\.\d+\.\d+),"
    r"(\d+),(\d+)"
)


def try_fixed_patterns(line: str):
    """Try all fixed decoder patterns, return first match."""
    for pattern in [FIXED_IPV4_TCP, FIXED_IPV4_UDP, FIXED_IPV6, FIXED_ICMP]:
        m = pattern.search(line)
        if m:
            return m
    return None


# ---------------------------------------------------------------------------
# TEST CASES
# Each: (description, log_line, should_pass_original, should_pass_fixed)
# ---------------------------------------------------------------------------
TEST_CASES = [
    (
        "IPv4 TCP block",
        "Nov 13 12:00:01 pfsense filterlog: 5,,,1000000103,em0,match,block,in,4,0x0,,64,12345,0,DF,6,tcp,60,203.0.113.45,192.168.10.50,54321,22,0",
        True,   # original should match
        True,   # fixed should match
    ),
    (
        "IPv4 UDP pass (PRIMARY BUG - Issue #41226)",
        "Nov 13 12:00:02 pfsense filterlog: 5,,,1000000104,em0,match,pass,in,4,0x0,,64,12346,0,DF,17,udp,40,203.0.113.45,192.168.10.50,54322,53,0",
        False,  # original FAILS (bug)
        True,   # fixed should match
    ),
    (
        "IPv6 TCP block",
        "Nov 13 12:00:03 pfsense filterlog: 5,,,1000000105,em1,match,block,in,6,0x60,,128,12347,tcp,40,2001:db8::cafe:1,2001:db8::192:168:10:50,44444,443,0",
        False,  # original FAILS (IPv6 not supported)
        True,   # fixed should match
    ),
    (
        "IPv6 UDP pass",
        "Nov 13 12:00:04 pfsense filterlog: 5,,,1000000106,em1,match,pass,in,6,0x60,,64,12348,udp,32,2001:db8::1,2001:db8::2,54323,53,0",
        False,  # original FAILS (IPv6 not supported)
        True,   # fixed should match
    ),
    (
        "ICMPv4 block (no ports)",
        "Nov 13 12:00:05 pfsense filterlog: 5,,,1000000107,em0,match,block,in,4,0x0,,64,12349,0,DF,1,icmp,28,203.0.113.45,192.168.10.50,8,0",
        False,  # original FAILS (ICMP not supported)
        True,   # fixed should match
    ),
    (
        "IPv4 TCP large outbound (exfil indicator)",
        "Nov 13 12:04:30 pfsense filterlog: 5,,,1000000108,em0,match,pass,out,4,0x0,,64,55000,0,DF,6,tcp,471859200,192.168.10.50,203.0.113.45,34567,443,0",
        True,   # original should match
        True,   # fixed should match
    ),
]

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

PASS = f"{GREEN}PASS{RESET}"
FAIL = f"{RED}FAIL{RESET}"
EXPECTED_FAIL = f"{YELLOW}EXPECTED FAIL{RESET}"


def run_tests():
    print(f"\n{BOLD}{CYAN}Wazuh pfSense Decoder Regression Test Suite{RESET}")
    print(f"{CYAN}Issue: https://github.com/wazuh/wazuh/issues/41226{RESET}")
    print("=" * 80)

    original_pass = 0
    fixed_pass = 0
    fixed_fail = 0
    total = len(TEST_CASES)

    # Header
    print(f"\n{'Test':<50} {'Original':^16} {'Fixed':^12}")
    print("-" * 80)

    for desc, line, exp_orig, exp_fixed in TEST_CASES:
        orig_match = ORIGINAL_PATTERN.search(line)
        fixed_match = try_fixed_patterns(line)

        orig_result = bool(orig_match)
        fixed_result = bool(fixed_match)

        # Evaluate original
        if orig_result == exp_orig:
            orig_display = PASS if orig_result else EXPECTED_FAIL
            if orig_result:
                original_pass += 1
        else:
            orig_display = FAIL

        # Evaluate fixed
        if fixed_result == exp_fixed and exp_fixed:
            fixed_display = PASS
            fixed_pass += 1
        elif not exp_fixed and not fixed_result:
            fixed_display = EXPECTED_FAIL
        else:
            fixed_display = FAIL
            fixed_fail += 1

        print(f"{desc[:48]:<50} {orig_display:^25} {fixed_display:^20}")

        if fixed_match:
            groups = fixed_match.groups()
            print(f"  {'':>50} Fields extracted: {groups}")

    print("\n" + "=" * 80)
    print(f"\n{BOLD}SUMMARY:{RESET}")
    print(f"  Original decoder: {original_pass}/{total} tests matched (expected — only IPv4 TCP supported)")
    print(f"  Fixed decoder:    {fixed_pass}/{total} tests passed")

    if fixed_fail == 0:
        print(f"\n{GREEN}{BOLD}✓ ALL {total}/{total} FIXED DECODER TESTS PASSED{RESET}")
        print(f"{GREEN}The fix correctly handles IPv4 TCP, IPv4 UDP, IPv6, and ICMP filterlog lines.{RESET}")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ {fixed_fail} FIXED DECODER TEST(S) FAILED{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
