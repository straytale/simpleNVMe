#!/usr/bin/env python3
import argparse
import sys
import mmap
import os
import struct

# NVMe Controller Register Offsets (per NVMe spec)
NVME_REGS = {
    0x00: ("CAP", [
        (0, 15, "MQES", "RO"),   # Max Queue Entries Supported
        (16, 16, "CQR", "RO"),   # Contiguous Queues Required
        (17, 17, "AMS", "RO"),   # Arbitration Mechanism Supported
        (20, 23, "TO", "RO"),    # Timeout
        (24, 27, "DSTRD", "RO"), # Doorbell Stride
        (32, 32, "CSS", "RO"),   # Command Sets Supported
        (37, 37, "BPS", "RO"),   # Boot Partition Support
        (48, 63, "MPSMIN", "RO") # Memory Page Size Minimum
    ]),
    0x14: ("VS", []),      # Version
    0x1c: ("INTMS", []),   # Interrupt Mask Set
    0x20: ("INTMC", []),   # Interrupt Mask Clear
    0x24: ("CC", []),      # Controller Configuration
    0x30: ("CSTS", []),    # Controller Status
    0x34: ("NSSR", []),    # NVM Subsystem Reset
    0x38: ("AQA", []),     # Admin Queue Attributes
    0x40: ("ASQ", []),     # Admin Submission Queue Base Address
    0x48: ("ACQ", []),     # Admin Completion Queue Base Address
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
    # Open /dev/mem and map BAR region
    fd = os.open("/dev/mem", os.O_RDONLY | os.O_SYNC)
    mem = mmap.mmap(fd, 0x1000, mmap.MAP_SHARED,
                    mmap.PROT_READ, offset=bar_addr)

    for off, (name, fields) in NVME_REGS.items():
        val = read_reg(mem, off, 8 if name == "CAP" else 4)
        print(f"[0x{off:02X}] [{name}] : 0x{val:0{16 if name=='CAP' else 8}X}")
        for (lo, hi, fname, acc) in fields:
            mask = (1 << (hi - lo + 1)) - 1
            fval = (val >> lo) & mask
            print(f"         -- [{lo}:{hi}] [{acc}] {fname} : 0x{fval:X}")

    mem.close()
    os.close(fd)

def main():
    parser = argparse.ArgumentParser(description="Simple NVMe register dumper")
    parser.add_argument("-s", "--show", type=lambda x: int(x, 16),
                        help="BAR physical address (hex)")
    args = parser.parse_args()

    if args.show is None:
        parser.print_help()
        sys.exit(0)

    dump_registers(args.show)

if __name__ == "__main__":
    main()
