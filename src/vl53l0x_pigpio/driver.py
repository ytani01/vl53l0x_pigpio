"""
Python driver for the VL53L0X distance sensor.
"""

import time
import pigpio
import numpy as np

# Registers
SYSRANGE_START                              = 0x00
SYSTEM_THRESH_HIGH                          = 0x0C
SYSTEM_THRESH_LOW                           = 0x0E
SYSTEM_SEQUENCE_CONFIG                      = 0x01
SYSTEM_RANGE_CONFIG                         = 0x09
SYSTEM_INTERMEASUREMENT_PERIOD              = 0x04
SYSTEM_INTERRUPT_CONFIG_GPIO                = 0x0A
GPIO_HV_MUX_ACTIVE_HIGH                     = 0x84
SYSTEM_INTERRUPT_CLEAR                      = 0x0B
RESULT_INTERRUPT_STATUS                     = 0x13
RESULT_RANGE_STATUS                         = 0x14
RESULT_CORE_AMBIENT_WINDOW_EVENTS_RTN       = 0xBC
RESULT_CORE_RANGING_TOTAL_EVENTS_RTN        = 0xC0
RESULT_CORE_AMBIENT_WINDOW_EVENTS_REF       = 0xD0
RESULT_CORE_RANGING_TOTAL_EVENTS_REF        = 0xD4
RESULT_PEAK_SIGNAL_RATE_REF                 = 0xB6
ALGO_PART_TO_PART_RANGE_OFFSET_MM           = 0x28
I2C_SLAVE_DEVICE_ADDRESS                    = 0x8A
MSRC_CONFIG_CONTROL                         = 0x60
PRE_RANGE_CONFIG_MIN_SNR                    = 0x27
PRE_RANGE_CONFIG_VALID_PHASE_LOW            = 0x56
PRE_RANGE_CONFIG_VALID_PHASE_HIGH           = 0x57
PRE_RANGE_MIN_COUNT_RATE_RTN_LIMIT          = 0x64
FINAL_RANGE_CONFIG_MIN_SNR                  = 0x67
FINAL_RANGE_CONFIG_VALID_PHASE_LOW          = 0x47
FINAL_RANGE_CONFIG_VALID_PHASE_HIGH         = 0x48
FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT = 0x44
PRE_RANGE_CONFIG_SIGMA_THRESH_HI            = 0x61
PRE_RANGE_CONFIG_SIGMA_THRESH_LO            = 0x62
PRE_RANGE_CONFIG_VCSEL_PERIOD               = 0x50
PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI          = 0x51
PRE_RANGE_CONFIG_TIMEOUT_MACROP_LO          = 0x52
SYSTEM_HISTOGRAM_BIN                        = 0x81
HISTOGRAM_CONFIG_INITIAL_PHASE_SELECT       = 0x33
HISTOGRAM_CONFIG_READOUT_CTRL               = 0x55
FINAL_RANGE_CONFIG_VCSEL_PERIOD             = 0x70
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI        = 0x71
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_LO        = 0x72
CROSSTALK_COMPENSATION_PEAK_RATE_MCPS       = 0x20
MSRC_CONFIG_TIMEOUT_MACROP                  = 0x46
SOFT_RESET_GO2_SOFT_RESET_N                 = 0xBF
IDENTIFICATION_MODEL_ID                     = 0xC0
IDENTIFICATION_REVISION_ID                  = 0xC2
OSC_CALIBRATE_VAL                           = 0xF8
GLOBAL_CONFIG_VCSEL_WIDTH                   = 0x32
GLOBAL_CONFIG_SPAD_ENABLES_REF_0            = 0xB0
GLOBAL_CONFIG_SPAD_ENABLES_REF_1            = 0xB1
GLOBAL_CONFIG_SPAD_ENABLES_REF_2            = 0xB2
GLOBAL_CONFIG_SPAD_ENABLES_REF_3            = 0xB3
GLOBAL_CONFIG_SPAD_ENABLES_REF_4            = 0xB4
GLOBAL_CONFIG_SPAD_ENABLES_REF_5            = 0xB5
GLOBAL_CONFIG_REF_EN_START_SELECT           = 0xB6
DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD         = 0x4E
DYNAMIC_SPAD_REF_EN_START_OFFSET            = 0x4F
POWER_MANAGEMENT_GO1_POWER_FORCE            = 0x80
VHV_CONFIG_PAD_SCL_SDA__EXTSUP_HV           = 0x89
ALGO_PHASECAL_LIM                           = 0x30
ALGO_PHASECAL_CONFIG_TIMEOUT                = 0x30

class VL53L0X:
    """
    VL53L0X driver.
    """

    def __init__(self, pi: pigpio.pi, i2c_bus=1, i2c_address=0x29):
        """
        Initialize the VL53L0X sensor.
        """
        self.pi = pi
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.handle = self.pi.i2c_open(self.i2c_bus, self.i2c_address)
        self.initialize()

    def initialize(self):
        """
        Initialize the sensor.
        """
        # set I2C standard mode
        self.write_byte(0x88, 0x00)

        self.write_byte(0x80, 0x01)
        self.write_byte(0xFF, 0x01)
        self.write_byte(0x00, 0x00)
        self.stop_variable = self.read_byte(0x91)
        self.write_byte(0x00, 0x01)
        self.write_byte(0xFF, 0x00)
        self.write_byte(0x80, 0x00)

        # disable SIGNAL_RATE_MSRC (bit 1) and SIGNAL_RATE_PRE_RANGE (bit 4) limit checks
        self.write_byte(MSRC_CONFIG_CONTROL, self.read_byte(MSRC_CONFIG_CONTROL) | 0x12)

        # set final range signal rate limit to 0.25 MCPS (million counts per second)
        self.write_word(FINAL_RANGE_CONFIG_MIN_COUNT_RATE_RTN_LIMIT, 32) # 0.25 * 128 = 32

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, 0xFF)

        spad_count, spad_is_aperture = self._get_spad_info()

        # The SPAD map (RefGoodSpadMap) is read by VL53L0X_get_info_from_device() in the API, but the same data seems to
        # be written to GLOBAL_CONFIG_SPAD_ENABLES_REF_0 through GLOBAL_CONFIG_SPAD_ENABLES_REF_5, so read it from there
        ref_spad_map = self.read_block(GLOBAL_CONFIG_SPAD_ENABLES_REF_0, 6)

        self.write_byte(0xFF, 0x01)
        self.write_byte(DYNAMIC_SPAD_REF_EN_START_OFFSET, 0x00)
        self.write_byte(DYNAMIC_SPAD_NUM_REQUESTED_REF_SPAD, 0x2C)
        self.write_byte(0xFF, 0x00)
        self.write_byte(GLOBAL_CONFIG_REF_EN_START_SELECT, 0xB4)

        first_spad_to_enable = 12 if spad_is_aperture else 0
        spads_enabled = 0

        for i in range(48):
            if i < first_spad_to_enable or spads_enabled == spad_count:
                # This bit is lower than the first one to enable, or (spad_count) bits have already been enabled, so zero this bit
                ref_spad_map[i // 8] &= ~(1 << (i % 8))
            elif (ref_spad_map[i // 8] >> (i % 8)) & 0x1:
                spads_enabled += 1

        self.write_block(GLOBAL_CONFIG_SPAD_ENABLES_REF_0, ref_spad_map)

        self.write_byte(0xFF, 0x01)
        self.write_byte(0x00, 0x00)

        self.write_byte(0xFF, 0x00)
        self.write_byte(0x09, 0x00)
        self.write_byte(0x10, 0x00)
        self.write_byte(0x11, 0x00)

        self.write_byte(0x24, 0x01)
        self.write_byte(0x25, 0xFF)
        self.write_byte(0x75, 0x00)

        self.write_byte(0xFF, 0x01)
        self.write_byte(0x4E, 0x2C)
        self.write_byte(0x48, 0x00)
        self.write_byte(0x30, 0x20)

        self.write_byte(0xFF, 0x00)
        self.write_byte(0x30, 0x09)
        self.write_byte(0x54, 0x00)
        self.write_byte(0x31, 0x04)
        self.write_byte(0x32, 0x03)
        self.write_byte(0x40, 0x83)
        self.write_byte(0x46, 0x25)
        self.write_byte(0x60, 0x00)
        self.write_byte(0x27, 0x00)
        self.write_byte(0x50, 0x06)
        self.write_byte(0x51, 0x00)
        self.write_byte(0x52, 0x96)
        self.write_byte(0x56, 0x08)
        self.write_byte(0x57, 0x30)
        self.write_byte(0x61, 0x00)
        self.write_byte(0x62, 0x00)
        self.write_byte(0x64, 0x00)
        self.write_byte(0x65, 0x00)
        self.write_byte(0x66, 0xA0)

        self.write_byte(0xFF, 0x01)
        self.write_byte(0x22, 0x32)
        self.write_byte(0x47, 0x14)
        self.write_byte(0x49, 0xFF)
        self.write_byte(0x4A, 0x00)

        self.write_byte(0xFF, 0x00)
        self.write_byte(0x7A, 0x0A)
        self.write_byte(0x7B, 0x00)
        self.write_byte(0x78, 0x21)

        self.write_byte(0xFF, 0x01)
        self.write_byte(0x23, 0x34)
        self.write_byte(0x42, 0x00)
        self.write_byte(0x44, 0xFF)
        self.write_byte(0x45, 0x26)
        self.write_byte(0x46, 0x05)
        self.write_byte(0x40, 0x40)
        self.write_byte(0x0E, 0x06)
        self.write_byte(0x20, 0x1A)
        self.write_byte(0x43, 0x40)

        self.write_byte(0xFF, 0x00)
        self.write_byte(0x34, 0x03)
        self.write_byte(0x35, 0x44)

        self.write_byte(0xFF, 0x01)
        self.write_byte(0x31, 0x04)
        self.write_byte(0x4B, 0x09)
        self.write_byte(0x4C, 0x05)
        self.write_byte(0x4D, 0x04)

        self.write_byte(0xFF, 0x00)
        self.write_byte(0x44, 0x00)
        self.write_byte(0x45, 0x20)
        self.write_byte(0x47, 0x08)
        self.write_byte(0x48, 0x28)
        self.write_byte(0x67, 0x00)
        self.write_byte(0x70, 0x04)
        self.write_byte(0x71, 0x01)
        self.write_byte(0x72, 0xFE)
        self.write_byte(0x76, 0x00)
        self.write_byte(0x77, 0x00)

        self.write_byte(0xFF, 0x01)
        self.write_byte(0x0D, 0x01)

        self.write_byte(0xFF, 0x00)
        self.write_byte(0x80, 0x01)
        self.write_byte(0x01, 0xF8)

        self.write_byte(0xFF, 0x01)
        self.write_byte(0x8E, 0x01)
        self.write_byte(0x00, 0x01)
        self.write_byte(0xFF, 0x00)
        self.write_byte(0x80, 0x00)

        self.write_byte(SYSTEM_INTERRUPT_CONFIG_GPIO, 0x04)
        self.write_byte(GPIO_HV_MUX_ACTIVE_HIGH, self.read_byte(GPIO_HV_MUX_ACTIVE_HIGH) & ~0x10) # active low
        self.write_byte(SYSTEM_INTERRUPT_CLEAR, 0x01)

        self.measurement_timing_budget_us = self.get_measurement_timing_budget()
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, 0xE8)
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, 0x01)
        self.perform_single_ref_calibration(0x40)

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, 0x02)
        self.perform_single_ref_calibration(0x00)

        # "restore the previous Sequence Config"
        self.write_byte(SYSTEM_SEQUENCE_CONFIG, 0xE8)

    def _get_spad_info(self):
        self.write_byte(0x80, 0x01)
        self.write_byte(0xFF, 0x01)
        self.write_byte(0x00, 0x00)

        self.write_byte(0xFF, 0x06)
        self.write_byte(0x83, self.read_byte(0x83) | 0x04)
        self.write_byte(0xFF, 0x07)
        self.write_byte(0x81, 0x01)

        self.write_byte(0x80, 0x01)

        self.write_byte(0x94, 0x6b)
        self.write_byte(0x83, 0x00)
        start = time.time()
        while self.read_byte(0x83) == 0x00:
            if time.time() - start > 1:
                raise Exception("Timeout")
        self.write_byte(0x83, 0x01)
        tmp = self.read_byte(0x92)

        count = tmp & 0x7f
        is_aperture = ((tmp >> 7) & 0x01) == 1

        self.write_byte(0x81, 0x00)
        self.write_byte(0xFF, 0x06)
        self.write_byte(0x83, self.read_byte(0x83) & ~0x04)
        self.write_byte(0xFF, 0x01)
        self.write_byte(0x00, 0x01)

        self.write_byte(0xFF, 0x00)
        self.write_byte(0x80, 0x00)

        return count, is_aperture

    def get_measurement_timing_budget(self):
        #... (implementation to be added)
        return 500000 # placeholder

    def set_measurement_timing_budget(self, budget_us):
        #... (implementation to be added)
        pass

    def perform_single_ref_calibration(self, vhv_init_byte):
        self.write_byte(SYSRANGE_START, 0x01 | vhv_init_byte)
        start = time.time()
        while (self.read_byte(RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            if time.time() - start > 1:
                raise Exception("Timeout")
        self.write_byte(SYSTEM_INTERRUPT_CLEAR, 0x01)
        self.write_byte(SYSRANGE_START, 0x00)

    def get_range(self):
        """
        Perform a single ranging measurement and return the result in mm.
        """
        self.write_byte(0x80, 0x01)
        self.write_byte(0xFF, 0x01)
        self.write_byte(0x00, 0x00)
        self.write_byte(0x91, self.stop_variable)
        self.write_byte(0x00, 0x01)
        self.write_byte(0xFF, 0x00)
        self.write_byte(0x80, 0x00)

        self.write_byte(SYSRANGE_START, 0x01)

        start = time.time()
        while (self.read_byte(SYSRANGE_START) & 0x01):
            if time.time() - start > 1:
                raise Exception("Timeout")

        start = time.time()
        while (self.read_byte(RESULT_INTERRUPT_STATUS) & 0x07) == 0:
            if time.time() - start > 1:
                raise Exception("Timeout")

        # assumptions: Linearity Corrective Gain is 1000 (default)
        # fractional ranging is not enabled
        range_mm = self.read_word(RESULT_RANGE_STATUS + 10)

        self.write_byte(SYSTEM_INTERRUPT_CLEAR, 0x01)

        return range_mm

    def get_ranges(self, num_samples: int) -> np.ndarray:
        """
        指定された回数だけ連続で距離を測定し、結果を numpy 配列で返す。
        """
        samples = np.empty(num_samples, dtype=np.uint16)
        for i in range(num_samples):
            samples[i] = self.get_range()
        return samples

    def close(self):
        """
        Close the I2C connection.
        """
        self.pi.i2c_close(self.handle)

    def read_byte(self, register):
        """
        Read a byte from a register.
        """
        return self.pi.i2c_read_byte_data(self.handle, register)

    def write_byte(self, register, value):
        """
        Write a byte to a register.
        """
        self.pi.i2c_write_byte_data(self.handle, register, value)

    def read_word(self, register):
        """
        Read a word from a register.
        """
        val = self.pi.i2c_read_word_data(self.handle, register)
        # pigpio reads as little-endian, VL53L0X is big-endian
        return ((val & 0xFF) << 8) | (val >> 8)


    def write_word(self, register, value):
        """
        Write a word to a register.
        """
        # pigpio writes as little-endian, VL53L0X is big-endian
        value = ((value & 0xFF) << 8) | (value >> 8)
        self.pi.i2c_write_word_data(self.handle, register, value)

    def read_block(self, register, count):
        """
        Read a block of data from a register.
        """
        _, data = self.pi.i2c_read_i2c_block_data(self.handle, register, count)
        return data

    def write_block(self, register, data):
        """
        Write a block of data to a register.
        """
        self.pi.i2c_write_i2c_block_data(self.handle, register, data)
