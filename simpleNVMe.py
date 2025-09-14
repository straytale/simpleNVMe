#!/usr/bin/env python3
import argparse
import sys
import mmap
import os
import struct

# NVMe 2.1 Controller Registers
NVME_REGS = {
    0x00: ("CAP", [   # Controller Capabilities (64-bit)
        (0, 15, "MQES", "RO"),    # Max Queue Entries Supported
        (16, 16, "CQR", "RO"),    # Contiguous Queues Required
        (17, 18, "AMS", "RO"),    # Arbitration Mechanism Supported
        (19, 19, "RESERVED", "RO"),
        (20, 23, "TO", "RO"),     # Timeout
        (24, 27, "DSTRD", "RO"),  # Doorbell Stride
        (28, 31, "NSSRS", "RO"),  # NVM Subsystem Reset Supported
        (32, 35, "CSS", "RO"),    # Command Sets Supported
        (36, 36, "BPS", "RO"),    # Boot Partition Support
        (37, 37, "CRWMS", "RO"),  # Controller Ready With Media Support
        (38, 38, "CRIMS", "RO"),  # Controller Ready Independent of Media Support
        (39, 39, "RESERVED", "RO"),
        (40, 43, "PMRS", "RO"),   # Persistent Memory Region Supported
        (44, 45, "CMBS", "RO"),   # Controller Memory Buffer Supported
        (48, 51, "MPSMIN", "RO"), # Memory Page Size Minimum
        (52, 55, "MPSMAX", "RO"), # Memory Page Size Maximum
        (56, 63, "RESERVED", "RO")
    ]),
    0x08: ("VS", [   # Version (32-bit)
        (0, 15, "TER", "RO"),     # Tertiary Version
        (16, 23, "MNR", "RO"),    # Minor Version
        (24, 31, "MJR", "RO")     # Major Version
    ]),
    0x0C: ("INTMS", [
        (0, 31, "MSI-X Mask Set", "RW")
    ]),
    0x10: ("INTMC", [
        (0, 31, "MSI-X Mask Clear", "RW")
    ]),
    0x14: ("CC", [   # Controller Configuration
        (0, 0, "EN", "RW"),       # Enable
        (4, 7, "CSS", "RW"),      # I/O Command Set Selected
        (11, 14, "MPS", "RW"),    # Memory Page Size
        (16, 19, "AMS", "RW"),    # Arbitration Mechanism Selected
        (20, 21, "SHN", "RW"),    # Shutdown Notification
        (23, 23, "IOSQES", "RW"), # Submission Queue Entry Size
        (27, 27, "IOCQES", "RW")  # Completion Queue Entry Size
    ]),
    0x1C: ("CSTS", [ # Controller Status
        (0, 0, "RDY", "RO"),      # Ready
        (1, 1, "CFS", "RO"),      # Controller Fatal Status
        (2, 2, "SHST", "RO"),     # Shutdown Status
        (3, 3, "NSSRO", "RO"),    # NVM Subsystem Reset Occurred
        (4, 4, "PP", "RO"),       # Processing Paused
        (31, 31, "RESERVED", "RO")
    ]),
    0x20: ("NSSR", [
        (0, 31, "Subsystem Reset", "WO")
    ]),
    0x24: ("AQA", [
        (0, 11, "ASQS", "RW"),    # Admin SQ Size
        (16, 27, "ACQS", "RW")    # Admin CQ Size
    ]),
    0x28: ("ASQ", []),  # Admin Submission Queue Base Address (64-bit)
    0x30: ("ACQ", []),  # Admin Completion Queue Base Address (64-bit)
    0x38: ("CMBLOC", [
        (0, 11, "BAR", "RO"),
        (12, 13, "CQS", "RO"),
        (14, 15, "CDPLMS", "RO"),
        (16, 17, "CDPCILS", "RO"),
        (18, 19, "CMSE", "RO"),
        (20, 31, "RESERVED", "RO")
    ]),
    0x3C: ("CMBSZ", [
        (0, 7, "SZU", "RO"),      # Size Units
        (8, 31, "SZ", "RO")       # Size
    ])
}

def read_reg(mem, offset, size=8):
    mem.seek(offset)
    data = mem.read(size)
    if size == 4:
        return struct.unpack("<I", data)[0]
    elif size == 8:
        return struct.unpack("<Q", data)[0]
    else:
        raise ValueError("Unsupported size")

def dump_registers(bar_addr):
    fd = os.open("/dev/mem", os.O_RDONLY | os.O_SYNC)

    # page-align
    PAGE_SIZE = mmap.PAGESIZE
    aligned_offset = bar_addr & ~(PAGE_SIZE - 1)
    page_diff = bar_addr - aligned_offset

    mem = mmap.mmap(fd, 0x1000 + page_diff, mmap.MAP_SHARED,
                    mmap.PROT_READ, offset=aligned_offset)

    for off, (name, fields) in NVME_REGS.items():
        size = 8 if name in ["CAP", "ASQ", "ACQ"] else 4
        val = read_reg(mem, page_diff + off, size)
        print(f"[0x{off:02X}] [{name}] : 0x{val:0{16 if size==8 else 8}X}")
        for (lo, hi, fname, acc) in fields:
            mask = (1 << (hi - lo + 1)) - 1
            fval = (val >> lo) & mask
            print(f"         -- [{lo}:{hi}] [{acc}] {fname} : 0x{fval:X}")

    mem.close()
    os.close(fd)

def main():
    parser = argparse.ArgumentParser(description="Simple NVMe 2.1 register dumper")
    parser.add_argument("-s", "--show", type=lambda x: int(x, 16),
                        help="BAR physical address (hex)")
    args = parser.parse_args()

    if args.show is None:
        parser.print_help()
        sys.exit(0)

    dump_registers(args.show)

if __name__ == "__main__":
    main()
