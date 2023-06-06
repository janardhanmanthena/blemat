#!/usr/bin/env python3
import uuid
import datetime
from bluepy import btle
from bluepy.btle import Scanner, Peripheral, Characteristic, ScanEntry, UUID
from statistics import mean


class BLELS:
    SCAN_TIMEOUT = 5
    scanner = None
    publicdevices = []

    def scan(self, duration=SCAN_TIMEOUT):
        try:
            devices_list_not_averaged = []
            for i in range(0, 2):
                print(i)
                # devices_list = []
                print("scan: starting scan for {}s".format(duration))
                self.scanner = Scanner()
                devices = self.scanner.scan(duration)
                # print(devices)
                foundDevices = 0
                for dev in devices:
                    devname = dev.getValueText(btle.ScanEntry.COMPLETE_LOCAL_NAME)
                    if devname is None:
                        devname = dev.getValueText(btle.ScanEntry.SHORT_LOCAL_NAME)

                    # print("scan: Device {} [{}] ({}), Connect={}, RSSI={} dB".format(dev.addr, devname, dev.addrType,
                    #                                                                  dev.connectable, dev.rssi))


                    device = dict()
                    # device['uuid'] = uuid
                    # device['major'] = major_id
                    # device['minor'] = minor_id

                    device['rssi'] = dev.rssi
                    device['addr'] = dev.addr
                    device['name'] = devname

                    # if len(devices_list_not_averaged) == 0: 
                    #     devices_list_not_averaged.append(
                    #         {   
                    #         "addr": device['addr'],
                    #         "name": device["name"],
                    #         "rssi": [device["rssi"]]
                    #     })

                    # print(devices_list_not_averaged)

                    if (lambda list, elem: any(x['addr'] == elem for x in list))(devices_list_not_averaged, device['addr']):
                        # print("tu sam")
                        # print(x)
                        for x in devices_list_not_averaged:
                            if x['addr'] == device["addr"]:
                                x['rssi'].append(device["rssi"])
                    else:
                        # print("ipak sam tu")
                        devices_list_not_averaged.append(
                            {   
                            "addr": device['addr'],
                            "name": device["name"],
                            "rssi": [device["rssi"]]
                        })
                    # devices_list.append(device)
                    
                    # {   
                    #     "addr": "",
                    #     "name": "",
                    #     "rssi": []
                    # }

                    # for (adtype, desc, value) in dev.getScanData():
                    #    print("  %s = %s" % (desc, value))

                    if dev.addrType == btle.ADDR_TYPE_PUBLIC:
                        foundDevices = foundDevices + 1
                        self.publicdevices.append(dev)

                # print("scan: Complete, found {} devices, {} public".format(len(devices), len(self.publicdevices)))
                # print('------------------')
            # print(devices_list_not_averaged)

            # devices_list = list((lambda lst: (mean(x['rssi']) for x['rssi'] in lst))(devices_list_not_averaged))
            # devices_list = list(map(lambda x: {'addr': x['addr'], 'name': x['name'], 'rssi': round(mean(x['rssi']))}, devices_list_not_averaged))
            # devices_list_not_averaged = list(filter(lambda x: len(x['rssi']) > 4, devices_list_not_averaged))
            # print(devices_list_not_averaged)
            devices_list = list(map(lambda x: {'addr': x['addr'],  'rssi': round(mean(x['rssi']))}, devices_list_not_averaged))
            # print(devices_list)
            return devices_list

        except Exception as e:
            print("scan: Error, ", e)

    def scan_light(self, duration=SCAN_TIMEOUT):
        try:
            devices_list = []
            self.scanner = Scanner()
            devices = self.scanner.scan(duration)
            for dev in devices:
                devname = dev.getValueText(btle.ScanEntry.COMPLETE_LOCAL_NAME)
                if devname is None:
                    devname = dev.getValueText(btle.ScanEntry.SHORT_LOCAL_NAME)

                try:
                    ibeacon_data = dev.getScanData()[-1][2][8:50]
                    uuid = ibeacon_data[0:32]
                    major_id = int(str(ibeacon_data[32:36]), 16)
                    minor_id = int(str(ibeacon_data[36:40]), 16)
                    device = dict()
                    device['uuid'] = uuid
                    device['major'] = major_id
                    device['minor'] = minor_id
                    device['rssi'] = dev.rssi
                    device['addr'] = dev.addr
                    devices_list.append(device)
                except:
                    continue
            return devices_list

        except Exception as e:
            print("scan: Error, ", e)

    def connectandread(self, addr):
        try:

            peri = Peripheral()
            peri.connect(addr)

            print("Listing services...")
            services = peri.getServices()
            for serv in services:
                print("   -- SERVICE: {} [{}]".format(serv.uuid, UUID(serv.uuid).getCommonName()))
                characteristics = serv.getCharacteristics()
                for chara in characteristics:
                    print("   --   --> CHAR: {}, Handle: {} (0x{:04x}) - {} - [{}]".format(chara.uuid,
                                                                                           chara.getHandle(),
                                                                                           chara.getHandle(),
                                                                                           chara.propertiesToString(),
                                                                                           UUID(
                                                                                               chara.uuid).getCommonName()))
            print("Listing descriptors...")
            descriptors = peri.getDescriptors()
            for desc in descriptors:
                print("   --  DESCRIPTORS: {}, [{}], Handle: {} (0x{:04x})".format(desc.uuid,
                                                                                   UUID(desc.uuid).getCommonName(),
                                                                                   desc.handle, desc.handle))

            print("Reading characteristics...")
            chars = peri.getCharacteristics()
            for c in chars:
                print("  -- READ: {} [{}] (0x{:04x}), {}, Value: {}".format(c.uuid, UUID(c.uuid).getCommonName(),
                                                                            c.getHandle(), c.descs,
                                                                            c.read() if c.supportsRead() else ""))


        except Exception as e:
            print("connectandread: Error,", e)


if __name__ == '__main__':
    devices = BLELS().scan(1)