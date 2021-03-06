#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTE: run this script with sudo

import os
import mmap
import subprocess

import numpy as np


class BitField():

    def __init__(self, value, size, fields=[], description="BitField"):
        self.value = int(value)
        self.size = size
        self.fields = fields
        self.description = description
        self.max_field_name_len = 0
        for field in fields:
            if self.max_field_name_len < len(field[0]):
                self.max_field_name_len = len(field[0])

    def get_mask(self, start_bit, end_bit):
        return (((1 << (end_bit + 1)) - 1) ^ (((1 << (start_bit)) - 1)))

    def __getattr__(self, name):
        for field in self.fields:
            if field[0] == name:
                val = (self.value & self.get_mask(*field[1])) >> field[1][0]
                return val
        raise AttributeError

    def __str__(self):
        s = "{}: ".format(self.description)
        if self.size == 1:
            s += "0x{:02X}".format(self.value)
        elif self.size == 2:
            s += "0x{:04X}".format(self.value)
        elif self.size == 4:
            s += "0x{:08X}".format(self.value)
        elif self.size == 8:
            s += "{:016X}".format(self.value)
        elif self.size == 16:
            s += "{:032X}".format(self.value)
        else:
            s += "{:064X}".format(self.value)
        for field in self.fields:
            s += "\n{}".format(" " * (len(self.description) + 2))
            s_ = "{{:{}s}} = 0x{{:X}}".format(self.max_field_name_len)
            s += s_.format(
                field[0],
                (self.value & self.get_mask(*field[1])) >> field[1][0])
        return s


class MMIO():

    def __init__(self, base_addr, length=0x1000, devmem='/dev/mem'):
        self.length = length
        fd = os.open(devmem, os.O_RDWR | os.O_SYNC)
        mem = mmap.mmap(fd,
                        length,
                        mmap.MAP_SHARED,
                        mmap.PROT_READ | mmap.PROT_WRITE,
                        offset=base_addr)
        self.byte = np.frombuffer(mem, np.uint8, length)
        self.word = np.frombuffer(mem, np.uint32, length // 4)
        self.qword = np.frombuffer(mem, np.uint64, length // 8)
        os.close(fd)

    def read(self, offset, size):
        assert size in [1, 4, 8, 16, 32]
        assert 0 <= offset + size <= self.length, f"{offset + size} > {self.length}"

        if size == 1:
            return self.byte[offset]
        if size == 4:
            assert offset % 4 == 0
            return self.word[offset // 4]
        if size == 8:
            assert offset % 8 == 0
            return self.qword[offset // 8]
        if size == 16:
            assert offset % 16 == 0
            a = int(self.read(offset, 8))
            b = int(self.read(offset + 8, 8))
            # FIXME: support big endian
            return (b << 64) | a
        if size == 32:
            assert offset % 32 == 0
            a = int(self.read(offset, 16))
            b = int(self.read(offset + 16, 16))
            return (b << 128) | a

        raise NotImplementedError


# (offset, size, description, fields)
REGS = {
    "DTBA": (0x00, 8, "Device Table Base Address Register", [
        ("Size", (0, 8)),
        ("DevTabBase", (12, 51)),
    ]),
    "CBBA": (0x08, 8, "Command Buffer Base Address Register", [
        ("ComBase", (12, 51)),
        ("ComLen", (56, 59)),
    ]),
    "ELBA": (0x10, 8, "Event Log Base Address Register", [
        ("EventBase", (12, 51)),
        ("EventLen", (56, 59)),
    ]),
    "CTL": (0x18, 8, "Control Register", [
        ("IommuEn", (0, 0)),
        ("HtTunEn", (1, 1)),
        ("EventLogEn", (2, 2)),
        ("EventIntEn", (3, 3)),
        ("ComWaitIntEn", (4, 4)),
        ("InvTimeOut", (5, 7)),
        ("PassPW", (8, 8)),
        ("ResPassPW", (9, 9)),
        ("Coherent", (10, 10)),
        ("Isoc", (11, 11)),
        ("CmdBufEn", (12, 12)),
        ("PPRLogEn", (13, 13)),
        ("PrrIntEn", (14, 14)),
        ("PPREn", (15, 15)),
        ("GTEn", (16, 16)),
        ("GAEn", (17, 17)),
        ("CRW", (18, 21)),
        ("SmiFEn", (22, 22)),
        ("SlfWBdis", (23, 23)),
        ("SmiFLogEn", (24, 24)),
        ("GAMEn", (25, 27)),
        ("GALogEn", (28, 28)),
        ("GAIntEn", (29, 29)),
        ("DualPprLogEn", (31, 30)),
        ("DualEventLogEn", (32, 33)),
        ("DevTblSegEn", (34, 36)),
        ("PrivAbrtEn", (37, 38)),
        ("PprAutoRspEn", (39, 39)),
        ("MarcEn", (40, 40)),
        ("BlkStopMrkEn", (41, 41)),
        ("PprAutoRspAon", (42, 42)),
        ("EPHEn", (45, 45)),
        ("HADUpdate", (46, 47)),
        ("GDUpdateDis", (48, 48)),
        ("XTEn", (50, 50)),
        ("IntCapXTEn", (51, 51)),
        ("vCmdEn", (52, 52)),
        ("vIommuEn", (53, 53)),
        ("GAUpdateDis", (54, 54)),
        ("IRTCacheDis", (59, 59)),
        ("SNPAVICEn", (61, 63)),
    ]),
    "EXBR": (0x20, 8, "Exclusion Base Register", [
        ("ExEn", (0, 0)),
        ("Allow", (1, 1)),
        ("Exclusion Base Address", (12, 51)),
    ]),
    "EXRLR": (0x20, 8, "Exclusion Range Limit Register", [
        ("Exclusion Limit", (12, 51)),
    ]),
    "EFR": (0x30, 8, "Extended Future Register", [
        ("PreFSup", (0, 0)),
        ("PPRSup", (1, 1)),
        ("XTSup", (2, 2)),
        ("NXSup", (3, 3)),
        ("GTSup", (4, 4)),
        ("IASup", (6, 6)),
        ("GASup", (7, 7)),
        ("HESup", (8, 8)),
        ("PCSup", (9, 9)),
        ("HATS", (10, 11)),
        ("GATS", (12, 13)),
        ("GLXSup", (14, 15)),
        ("SmiFSup", (16, 17)),
        ("SmiFRC", (18, 20)),
        ("GAMSup", (21, 23)),
        ("DualPprLogSup", (24, 25)),
        ("DualEventLogSup", (28, 29)),
        ("SATSup", (31, 31)),
        ("PASmax", (32, 36)),
        ("USSup", (37, 37)),
        ("DevTblSegSup", (39, 39)),
        ("PprOvrflwEarlySup", (40, 40)),
        ("PPRAutoRspSup", (41, 41)),
        ("MarcSup", (42, 43)),
        ("BlkStopMrkSup", (44, 44)),
        ("PerfOptSup", (45, 45)),
        ("MsiCapMmioSup", (46, 46)),
        ("GIoSup", (48, 48)),
        ("HASup", (49, 49)),
        ("EPHSup", (50, 50)),
        ("AttrFWSup", (51, 51)),
        ("HDSup", (52, 52)),
        ("InvIotlbTypeSup", (54, 54)),
        ("vIommuSup", (55, 55)),
        ("GAUpdateDisSups", (61, 61)),
        ("ForcePhyDestSup", (62, 62)),
        ("SNPSup", (63, 63)),
    ]),
}

# Device Table Entry
DTEFields = [
    ("V", (0, 0)),
    ("TV", (1, 1)),
    ("HAD", (7, 8)),
    ("Mode", (9, 11)),
    ("HostPageTableRootPointer", (12, 51)),
    ("PPR", (52, 52)),
    ("GPPR", (53, 53)),
    ("GIoV", (54, 54)),
    ("GV", (55, 55)),
    ("GLX", (56, 57)),
    ("GCR3TableRootPointer[14:12]", (58, 60)),
    ("IR", (61, 61)),
    ("IW", (62, 62)),
    ("DomainID", (64, 79)),
    ("GCR3TableRootPointer[30:15]", (80, 95)),
    ("I", (96, 96)),
    ("SE", (97, 97)),
    ("SA", (98, 98)),
    ("IoCtl", (99, 100)),
    ("Cache", (101, 101)),
    ("SD", (102, 102)),
    ("EX", (103, 103)),
    ("SysMgt", (104, 105)),
    ("SATS", (106, 106)),
    ("GCR3TableRootPointer[51:31]", (107, 127)),
    ("IV", (128, 128)),
    ("IntTabLen", (129, 132)),
    ("IG", (133, 133)),
    ("InterruptTableRootPointer", (134, 179)),
    ("InitPass", (184, 184)),
    ("EIntPass", (185, 185)),
    ("NMIPass", (186, 186)),
    ("HPTMode", (187, 187)),
    ("IntCtl", (188, 189)),
    ("Lint0Pass", (190, 190)),
    ("Lint1Pass", (191, 191)),
    ("vImuEn", (207, 207)),
    ("GDeviceID", (208, 239)),
    ("AttrV", (246, 246)),
    ("Mode0FC", (247, 247)),
    ("SnoopAttribute", (248, 255)),
]


def get_iommu_pci_bdf():
    bdfs = []
    p = subprocess.run(["lspci"], capture_output=True, encoding="utf-8")
    for line in p.stdout.split("\n"):
        if line.find("IOMMU") != -1:
            bdf = line.split(" ")[0]
            bdfs.append(bdf)
    return bdfs


def get_iommu_base_addr(bdf):
    p = subprocess.run(["lspci", "-s", f"{bdf}", "-xxx"],
                       capture_output=True,
                       encoding="utf-8")
    for line in p.stdout.split("\n"):
        if line.startswith("40: "):
            bytes_ = line.split(" ")[1:]
            addr = int(bytes_[7], 16) << 8 | int(bytes_[6], 16)
            addr <<= 16
            break
    return addr


def get_iommu_bdf_addr():
    r = []
    bdfs = get_iommu_pci_bdf()
    for bdf in bdfs:
        addr = get_iommu_base_addr(bdf)
        r.append((bdf, addr))
    return r


def get_dtba():
    dtba = None
    table_size = None
    info = get_iommu_bdf_addr()
    for bdf, addr in info:
        mem = MMIO(addr)
        field = get_field(mem, "DTBA")
        dtba_ = field.DevTabBase << 12
        table_size_ = (field.Size + 1) * 4096
        if dtba is None:
            dtba = dtba_
            table_size = table_size_
        if dtba != dtba_:
            print("WARN: multiple Device Table Base Addresses are found")
    return dtba, table_size


def get_field(mem, name):
    offset, size, description, fields = REGS[name]
    value = mem.read(offset, size)
    field = BitField(value, size, fields, description)
    return field


class Runner:

    def __init__(self):
        pass

    def dump_device_table(self, bdf=None):
        dtba, size = get_dtba()
        print(f"Device Table Base: {dtba:#08x}, {size/1024}KB")
        mem = MMIO(dtba, size)

        offset = 0
        field_size = 32
        for entry in range(size // field_size):
            bus = (entry >> 8) & 0xFF
            dev = (entry >> 3) & 0x1F
            func = entry & 0x7
            bdf_ = f"{bus:02x}:{dev:02x}.{func:x}"
            value = mem.read(offset, field_size)
            field = BitField(value, field_size, DTEFields,
                             "Device Table Entry")
            if bdf is not None:
                if bdf == bdf_:
                    print(f"{bdf} {field}")
            elif field.V == 1:
                print(f"{bdf} {field}")
            offset += field_size

    def check_viommu(self):
        info = get_iommu_bdf_addr()
        for bdf, addr in info:
            print(f"{bdf} {addr:#x}")
            mem = MMIO(addr)

            ctl = get_field(mem, "CTL")
            efr = get_field(mem, "EFR")

            print(f"IommuEn: {ctl.IommuEn}")
            print(f"vIommuEn: {ctl.vIommuEn}")
            print(f"GTEn: {ctl.GTEn}")
            print(f"SNPSup: {efr.SNPSup}")
            print(f"GTSup: {efr.GTSup}")
            print(f"vIommuSup: {efr.vIommuSup}")

    def regdump(self):
        info = get_iommu_bdf_addr()
        for bdf, addr in info:
            print(f"{bdf} {addr:#x}")

            mem = MMIO(addr)
            for offset, size, description, fields in REGS.values():
                value = mem.read(offset, size)
                print(BitField(value, size, fields, description))


if __name__ == "__main__":
    import fire
    fire.Fire(Runner)
