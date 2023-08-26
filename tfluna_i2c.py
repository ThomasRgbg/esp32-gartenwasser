# V1 baseline
# V2 make I2C Addr configurable, convert to uasyncio
# V3 direct consider offsets and height
# V4 fix potential div by 0, add register dump
# V5 play with delays on read_avg_dist

import uasyncio
import time
 
class Luna:
    def __init__(self, i2c, i2c_addr=0x10):
        self.i2c = i2c
        self.addr = i2c_addr
        self.reset_sensor()
        self.offset = 0
        
    def setoffset(self, offset):
        self.offset = offset

    def sensor_present(self):
        if self.i2c.readfrom_mem(self.addr, 0x0a, 1) == b'\x08':
            return True
        else:
            return False

    def read_distance(self):
        val = self.i2c.readfrom_mem(self.addr, 0x00, 2)
        return(int.from_bytes(val, 'little'))

    async def read_avg_dist(self):
        dist = 0
        min_dist = 80000
        max_dist = 0
        j = 0
        self.high_power(True)
        await uasyncio.sleep_ms(500)
        for i in range(20):
            val = self.read_distance()
            if val == 0:
                val = self.read_distance()
            print("tfluna_i2c/read_avg_dist() - {0}".format(val))
            if val > 0:
                dist += val
                j += 1
                if min_dist > val:
                    min_dist = val
                if max_dist < val:
                    max_dist = val
            await uasyncio.sleep_ms(250)
        self.high_power(False)
        if j > 0:
            dist = dist / j
            return dist, min_dist, max_dist
        else:
            return False, False, False

    async def read_height(self):
        dist, min_dist, max_dist = await self.read_avg_dist()
        if dist == False:
            return False, False, False
        height = (dist * -1) - self.offset
        max_height = (min_dist * -1) - self.offset
        min_height = (max_dist * -1) - self.offset
        return height, min_height, max_height

    def read_amp(self):
        val = self.i2c.readfrom_mem(self.addr, 0x02, 2)
        return(int.from_bytes(val, 'little'))

    def read_error(self):
        val = self.i2c.readfrom_mem(self.addr, 0x08, 2)
        return(int.from_bytes(val, 'little'))

    def read_temp(self):
        val = self.i2c.readfrom_mem(self.addr, 0x04, 2)
        return(int.from_bytes(val, 'little'))

    def high_power(self, power):
        if power:
            self.i2c.writeto_mem(self.addr, 0x28, b'\x00')
        else:
            self.i2c.writeto_mem(self.addr, 0x28, b'\x01')

    def reset_sensor(self):
        self.i2c.writeto_mem(self.addr, 0x21, b'\x02')
        # await uasyncio.sleep_ms(2000)
        time.sleep(1)
        self.i2c.writeto_mem(self.addr, 0x26, b'\x02')
        self.i2c.writeto_mem(self.addr, 0x28, b'\x01')

    async def print_loop(self):
        while True:
            print("----")
            self.high_power(True)
            print(self.read_distance())
            print(self.read_amp())
            print(self.read_temp())
            self.high_power(False)
            await uasyncio.sleep_ms(5000)

    def dump_registers(self):
        for i in range(0x32):
            val = self.i2c.readfrom_mem(self.addr, i, 1)
            print('{0:02x} = {1}'.format(i, val))


