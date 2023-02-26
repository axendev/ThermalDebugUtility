import serial as ser
from time import sleep

BD_RATE = 115200
TEST_STEP = 0x100
USE_2COMPL_VS_OFFSET = True   # True: 2s complement data format False: offset binary
ANSWER_DELAY_SEC = 1

LE = '\r\n'
READ_CHUNK = 1000

AGC_BIT_POS = 16
AGC_COLOR_BIT_POS = 19
AGC_FILTER_BIT_POS = 20
TEST_MODE_BIT_POS = 21
CC_DEBUG_SHIFT_POS = 24

CALIB_CALIB_BIT_POS = 0
CALIB_CORRECT_BIT_POS = 1

CMD_READ_ADC = 'RA 8\r\n'
CMD_ADC_FRMT_OFFSET = 'WR 0x0009 0x01\r\n'
CMD_ADC_FRMT_COMPL = 'WR 0x0009 0x00\r\n'
CMD_ADC_DIS_TEST = 'WR 0x0006 0x00\r\n'
CMD_ADC_EN_TEST = 'WR 0x0006 0x02\r\n'
CMD_ADC_CHA_EN_TEST_CUSTOM = 'WR 0x000A 0x05\r\n'
CMD_ADC_TEST_CUSTOM_MSB = 'WR 0x000E '
CMD_ADC_TEST_CUSTOM_LSB = 'WR 0x000F '
CMD_ADC_FLIP_WIRE = 'WR 0x0004 0x01'
CMD_ADC_NOFLIP_WIRE = 'WR 0x0004 0x00'



class BoardAPI:
    connected = False
    port = None
    recv_delay = 0
    log_func = None
    control_reg = 0
    calib_reg = 0


    def __init__(self, log_func=None):
        self.log_func = log_func
        print('API inited')

    def connect(self, port, delay=0):
        self.port = ser.Serial(port, BD_RATE, timeout=0.1)
        self.recv_delay = delay
        if self.port is not None:
            self.connected = True
            self.log_func('API: Connected')
        else:
            self.log_func('API: Not Connected')
            self.connected = False

        return self.connected

    def disconnect(self):
        if self.port is not None:
            self.port.close()
            self.log_func('API: Disconnected')

        self.connected = False
        return self.connected

    def is_connected(self):
        return self.connected

    def get_last_pix(self):
        self.port.write('RA 8\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = recv.decode().split('value ')[-1].strip()
        return val

    def set_test_mode(self, state):
        if state:
            self.control_reg |= 1 << TEST_MODE_BIT_POS
        else:
            self.control_reg &= ~(1 << TEST_MODE_BIT_POS)

        self.__set_control_reg()

    def set_agc_state(self, state):
        if state:
            self.control_reg |= 1 << AGC_BIT_POS
        else:
            self.control_reg &= ~(1 << AGC_BIT_POS)

        self.__set_control_reg()

    def set_filter_state(self, state):
        if state:
            self.control_reg |= (1 << AGC_FILTER_BIT_POS)
        else:
            self.control_reg &= ~(1 << AGC_FILTER_BIT_POS)

        self.__set_control_reg()

    def set_color_state(self, state):
        if state:
            self.control_reg |= (1 << AGC_COLOR_BIT_POS)
        else:
            self.control_reg &= ~(1 << AGC_COLOR_BIT_POS)

        self.__set_control_reg()

    def set_nshare(self, value):
        self.control_reg &= 0xFFFF0000
        self.control_reg |= (value & 0xFFFF)

        self.__set_control_reg()

    def set_cc_debug(self, value):
        self.control_reg &= 0x00FFFFFF
        self.control_reg |= ((value << CC_DEBUG_SHIFT_POS) & 0xFF000000)

        self.__set_control_reg()

    def get_agc_state(self):
        self.__get_control_reg()
        return (self.control_reg >> AGC_BIT_POS) & 1


    def get_control_params(self):
        self.__get_control_reg()

        params = {'AGC': (self.control_reg >> AGC_BIT_POS) & 1,
                  'Color': (self.control_reg >> AGC_COLOR_BIT_POS) & 1,
                  'Filter': (self.control_reg >> AGC_FILTER_BIT_POS) & 1,
                  'NSHARE': (self.control_reg & 0xFFFF),
                  'Test mode': (self.control_reg >> TEST_MODE_BIT_POS) & 1,
                  'CC_DEBUG': ((self.control_reg >> CC_DEBUG_SHIFT_POS ) & 0xFF)}

        return params

    def set_calib_state(self, state):
        if state:
            self.calib_reg|= (1 << CALIB_CALIB_BIT_POS)
        else:
            self.calib_reg &= ~(1 << CALIB_CALIB_BIT_POS)

        self.__set_calib_reg()

    def set_correct_state(self, state):
        if state:
            self.calib_reg|= (1 << CALIB_CORRECT_BIT_POS)
        else:
            self.calib_reg &= ~(1 << CALIB_CORRECT_BIT_POS)

        self.__set_calib_reg()

    def get_calib_params(self, do_reload=True):
        if do_reload:
            self.__get_calib_reg()

        params = {'Calibration': (self.control_reg >> CALIB_CALIB_BIT_POS) & 1,
                  'Correction': (self.control_reg >> CALIB_CORRECT_BIT_POS) & 1}

        return params

    def set_calib_reg(self, value):
        self.calib_reg = value
        self.__set_calib_reg()

    def get_calib_reg(self, do_reload=True):
        if do_reload:
            self.__get_calib_reg()

        return self.calib_reg

    def set_custom_AGC_reg(self, reg, value):
        self.port.write(f'WA {reg} {hex(value)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

    def __get_control_reg(self):
        self.port.write('RA 0\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = recv.decode().split('value ')[-1].strip()
        self.control_reg = int(val, 16)


    def __set_control_reg(self):
        self.port.write(f'WA 0 {hex(self.control_reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))


    def __get_calib_reg(self):
        self.port.write('RA 10\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = recv.decode().split('value ')[-1].strip()
        self.calib_reg = int(val, 16)


    def __set_calib_reg(self):
        self.port.write(f'WA 10 {hex(self.calib_reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))


    def adc_get_dither_disable(self):
        self.log_func('adc_get_dither_disable')
        self.port.write('RR 0x0001\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = int(recv.decode().split('value ')[-1].strip(), 16)
        dith = (val >> 4) & 1
        return dith

    def adc_get_chopper_disable(self):
        self.log_func('adc_get_chopper_disable')
        self.port.write('RR 0x0422\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = int(recv.decode().split('value ')[-1].strip(), 16)
        chop = (val >> 1) & 1
        return chop

    def adc_get_hif(self):
        self.log_func('adc_get_hif')
        self.port.write('RR 0x041D\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = int(recv.decode().split('value ')[-1].strip(), 16)
        dith = (val >> 1) & 1
        return dith

    def adc_set_dither_disable(self, state):
        self.log_func('adc_set_dither_disable')

        reg = 0
        if state:
            reg |= ((1 << 2) | (1 << 3) | (1 << 4) | (1 << 5))
        self.port.write(f'WR 0x0001 {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        reg = 0
        if state:
            reg |= ((1 << 3) | (1 << 5))
        self.port.write(f'WR 0x0434 {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        reg = 0
        if state:
            reg |= ((1 << 3) | (1 << 5))
        self.port.write(f'WR 0x0534 {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))


    def adc_set_chopper_disable(self, state):
        self.log_func('adc_set_chopper_disable')
        reg = 0
        if state:
            reg |= (1 << 1)
        self.port.write(f'WR 0x0422 {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

    def adc_set_hif(self, state):
        self.log_func('adc_set_hif')

        reg = 0
        if state:
            reg |= (1 << 1)
        self.port.write(f'WR 0x041D {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        reg = 0
        if state:
            reg |= (1 << 1)
        self.port.write(f'WR 0x051D {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        reg = 0
        if state:
            reg |= ((1 << 7) | (1 << 6))
        self.port.write(f'WR 0x0608 {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

    def adc_enable_pattern(self, state):
        self.log_func('adc_enable_pattern')
        reg = 0
        if state:
            reg |= (1 << 1)

        self.port.write(f'WR 0x06 {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

    def adc_set_pattern(self, pattern):
        self.log_func('adc_set_pattern: ' + pattern)
        reg = 0
        if pattern == 'normal':
            reg = 0
        elif pattern == 'zeros':
            reg = 1
        elif pattern == 'ones':
            reg = 2
        elif pattern == 'toggle':
            reg = 3
        elif pattern == 'ramp':
            reg = 4
        elif pattern == 'random':
            reg = 8
        elif pattern == 'sine':
            reg = 9


        self.port.write(f'WR 0x0A {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

    def adc_get_pattern(self):
        self.log_func('adc_get_hif')
        self.port.write('RR 0x0A\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = int(recv.decode().split('value ')[-1].strip(), 16)

        pattern = 'normal'

        if val == 0:
            pattern = 'normal'
        elif val == 1:
            pattern = 'zeros'
        elif val == 2:
            pattern = 'ones'
        elif val == 3:
            pattern = 'toggle'
        elif val == 4:
            pattern = 'ramp'
        elif val == 8:
            pattern = 'random'
        elif val == 9:
            pattern = 'sine'

        return pattern

    def adc_set_dataformat(self, format):
        self.log_func('adc_set_dataformat: ' + format)
        reg = 0
        if format == 'offset':
            reg = 1
        elif format == 'compl':
            reg = 0

        self.port.write(f'WR 0x09 {hex(reg)}\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))


    def adc_get_dataformat(self):
        self.log_func('adc_get_hif')
        self.port.write('RR 0x09\r\n'.encode())
        sleep(self.recv_delay)
        recv = self.port.read(READ_CHUNK)
        self.log_func('Received: ' + recv.decode())
        print('Recv: ' + str(recv))

        val = int(recv.decode().split('value ')[-1].strip(), 16)

        format = 'compl'

        if (val & 0x01) == 0:
            format = 'compl'
        elif (val & 0x01) == 1:
            format = 'offset'

        return format

    def write_pattern(self, data):
        msb = hex(data >> 6)
        lsb = hex((data << 2) & 0xFF)

        p.write(CMD_ADC_DIS_TEST.encode())
        recv = p.read(READ_CHUNK)

        p.write((CMD_ADC_TEST_CUSTOM_MSB + msb + LE).encode())
        recv = p.read(READ_CHUNK)
        # print('Received: ' + str(recv))
        p.write((CMD_ADC_TEST_CUSTOM_LSB + lsb + LE).encode())
        recv = p.read(READ_CHUNK)
        # print('Received: ' + str(recv.strip()))

        p.write(CMD_ADC_EN_TEST.encode())
        recv = p.read(READ_CHUNK)



