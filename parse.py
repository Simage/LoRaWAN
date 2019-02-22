import sys
import LoRaWAN
import logging
import argparse
import json

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--all", action="store_true", help="report all traffic"
)
parser.add_argument(
    "--log-level", type=str,default='INFO', help="report all traffic"
)
parser.add_argument(
    "--keys", type=argparse.FileType("r"), default=None, help="file contianing keys"
)
args = parser.parse_args()
keys=json.load(args.keys)
logging.getLogger('').setLevel(getattr(logging,args.log_level.upper()))

for i,l in enumerate(sys.stdin):
    fields = l.split(",")
    time, status, packet = fields[0], fields[20], fields[-1]
    if status[-3:-1] != "OK":
        continue

    packet=packet[1:-2].replace("-", "")
    try:
        packet = bytes.fromhex(packet)
    except:
        logging.warn(f"Error decoding record {i} ({packet})")
        continue
        
    lorawan = LoRaWAN.new(None,None)
    lorawan.read(packet)

    devaddr=lorawan.get_devaddr()[::-1].hex().upper()
    if devaddr in keys:
        logging.debug(f"Found Keys for Devaddr: {devaddr!r}")
        logging.debug("%s\t%s\t%s\t%s",f"{i:4d}",time,devaddr,packet.hex().upper())
        lorawan.appkey=bytes.fromhex(keys[devaddr]["appskey"])
        lorawan.nwkey=bytes.fromhex(keys[devaddr]["nwkey"])
        logging.debug("Version      %s",lorawan.get_mhdr().get_mversion())
        logging.debug("Type         %s",lorawan.get_mhdr().get_mtype())
        logging.debug("Received MIC %s",lorawan.get_mic().hex().upper())
        logging.debug("Computed MIC %s",bytes(lorawan.compute_mic()).hex().upper())
        logging.debug("Valid MIC    %s",lorawan.valid_mic())
        payload=bytes(lorawan.get_payload())
        logging.debug("Payload      %s",payload.hex().upper())
        reading=int.from_bytes(payload[2:4],byteorder='big',signed=True)
        logging.info("%s\t%s\t%s\t%s\t%s",f"{i:4d}",time,devaddr,payload.hex().upper(),f"{reading} mV")
    elif args.all:
        logging.info("%s\t%s\t%s\t%s",f"{i:4d}",time,devaddr,packet.hex().upper())
