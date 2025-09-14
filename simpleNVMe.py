#!/usr/bin/env python3
import argparse
import sys
import mmap
import os
import struct

# NVMe 2.1 Controller Registers
NVME_REGS = {
    0x00: ("CAP", [
        (0, 15, "MQES", "RO"),
        (16, 16, "CQR", "RO"),
        (17, 18, "AMS", "RO"),
        (19, 19, "RESERVED", "RO"),
        (20, 23, "TO", "RO"),
        (24, 27, "DSTRD", "RO"),
        (28, 31, "NSSRS", "RO"),
        (32, 35, "CSS", "RO"),
        (36, 36, "BPS", "RO"),
        (37, 37, "CRWMS", "RO"),
        (38, 38, "CRIMS", "RO"),
        (39, 39, "RESERVED", "RO"),
        (40, 43, "PMRS", "RO"),
        (44, 45, "CMBS", "RO"),
        (48, 51, "MPSMIN", "RO"),
        (52, 55, "MPSMAX", "RO"),
        (56, 63, "RESERVED", "RO")
    ]),
    0x08: ("VS", [
        (0, 15, "TER", "RO"),
        (16, 23, "MNR", "RO"),
        (24, 31, "MJR", "RO")
    ]),
    0x0C: ("INTMS", [
        (0, 31, "MSI-X Mask Set", "RW")
    ]),
    0x10: ("INTMC", [
        (0, 31, "MSI-X Mask Clear", "RW")
    ]),
    0x14: ("CC", [
        (0, 0, "EN", "RW"),
        (4, 7, "CSS", "RW"),
        (11, 14, "MPS", "RW"),
        (16, 19, "AMS", "RW"),
        (20, 21, "SHN", "RW"),
        (23, 23, "IOSQES", "RW"),
        (27, 27, "IOCQES", "RW")
    ]),
    0x1C: ("CSTS", [
        (0, 0, "RDY", "RO"),
        (1, 1, "CFS", "RO"),
        (2, 2, "SHST", "RO"),
        (3, 3, "NSSRO", "RO"),
        (4, 4, "PP", "RO"),
        (31, 31, "RESERVED", "RO")
    ]),
    0x20: ("NSSR", [
        (0, 31, "Subsystem Reset", "WO")
    ]),
    0x24: ("AQA", [
        (0, 11, "ASQS", "RW"),
        (16, 27, "ACQS", "RW")
    ]),
    0x28: ("ASQ", []),
    0x30: ("ACQ", []),
    0x38: ("CMBLOC", [
        (0, 11, "BAR", "RO"),
        (12, 13, "CQS", "RO"),
        (14, 15, "CDPLMS", "RO"),
        (16, 17, "CDPCILS", "RO"),
        (18, 19, "CMSE", "RO"),
        (20, 31, "RESERVED", "RO")
    ]),
    0x3C: ("CMBSZ", [
        (0, 7, "SZU", "RO"),
        (8, 31, "SZ", "RO")
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

def dump_registers_from_fd(fd):
    PAGE_SIZE = mmap.PAGESIZE
    mem = mmap.mmap(fd, 0x1000, mmap.MAP_SHARED, mmap.PROT_READ, offset=0)

    for off, (name, fields) in NVME_REGS.items():
        size = 8 if name in ["CAP", "ASQ", "ACQ"] else 4
        val = read_reg(mem, off, size)
        print(f"[0x{off:02X}] [{name}] : 0x{val:0{16 if size==8 else 8}X}")
        for (lo, hi, fname, acc) in fields:
            mask = (1 << (hi - lo + 1)) - 1
            fval = (val >> lo) & mask
            print(f"         -- [{lo}:{hi}] [{acc}] {fname} : 0x{fval:X}")

    mem.close()

def is_nvme_device(bdf):
    class_path = f"/sys/bus/pci/devices/{bdf}/class"
    try:
        with open(class_path, "r") as f:
            val = int(f.read().strip(), 16)
        base_class = (val >> 16) & 0xFF
        sub_class = (val >> 8) & 0xFF
        # NVMe = Class 0x01 (Mass Storage), Subclass 0x08 (NVM)
        return base_class == 0x01 and sub_class == 0x08
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Simple NVMe 2.1 register dumper")
    parser.add_argument("-s", "--show", type=str,
                        help="PCI BDF (e.g. 0000:04:00.0)")
    args = parser.parse_args()

    if args.show:
        if not is_nvme_device(args.show):
            print(f"Error: {args.show} is not an NVMe device.")
            sys.exit(1)
        path = f"/sys/bus/pci/devices/{args.show}/resource0"
        if not os.path.exists(path):
            print(f"Error: PCI device {args.show} not found.")
            sys.exit(1)
        fd = os.open(path, os.O_RDONLY)
        dump_registers_from_fd(fd)
        os.close(fd)
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
