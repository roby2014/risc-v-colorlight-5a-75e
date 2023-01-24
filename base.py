#!/usr/bin/env python3

import argparse
import os

from migen import *
from migen.genlib.io import CRG

from litex_boards.platforms import colorlight_5a_75e
from litex.build.lattice.trellis import trellis_args, trellis_argdict
from litex.soc.integration.soc_core import *
from litex.soc.integration.builder import *


# BaseSoC -----------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, version, revision):
        sys_clk_freq = int(25e6)
        platform = colorlight_5a_75e.Platform(revision)

        # SoC with CPU
        SoCCore.__init__(self, platform,
            cpu_type                 = "vexriscv",
            clk_freq                 = sys_clk_freq,
            ident                    = f"LiteX RISC-V CPU Test SoC {version}", ident_version=True,
            integrated_rom_size      = 0x8000,
            integrated_main_ram_size = 0x4000)

        # Clock Reset Generation
        self.submodules.crg = CRG(platform.request("clk25"))


# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX RISC-V SoC on Colorlight 5A-75E")
    builder_args(parser)
    soc_core_args(parser)
    trellis_args(parser)
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load",  action="store_true", help="Load bitstream")
    parser.add_argument("--cable", default="ft232RL",    help="JTAG probe model")
    parser.add_argument("--revision", default="6.0",  help="Colorlight board model revision")
    args = parser.parse_args()

    soc = BaseSoC("5A-75E", revision=args.revision)

    builder = Builder(soc, **builder_argdict(args))
    builder.build(**trellis_argdict(args), run=args.build)

    bitstream_file = os.path.join(builder.gateware_dir, f'{soc.build_name}.bit')
    if args.load:
        if args.cable == "ft232RL":
            extra_args = "--pins=RXD:RTS:TXD:CTS"
        elif args.cable == "usb-blaster":
            quartus_path = os.environ['QUARTUSPATH']
            extra_args = f'--probe-firmware {quartus_path}/linux64/blaster_6810.hex'
        else:
            extra_args = ""
        print("Uploading bitstream file: {}".format(bitstream_file))
        print("JTAG cable: {}".format(args.cable))
        print("Extra openFPGALoader arguments: {}".format(extra_args))
        os.system("openFPGALoader --cable {0} {1} {2}""".format(args.cable, extra_args, bitstream_file))


if __name__ == "__main__":
    main()
