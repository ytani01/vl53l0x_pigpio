"Python driver for the VL53L0X distance sensor."

import time
import pigpio
import numpy as np

from vl53l0x_pigpio.constants import (
    SYSRANGE_START,
    SYSTEM_SEQUENCE_CONFIG,
    SYSTEM_INTERRUPT_CONFIG_GPIO,
    GPIO_HV_MUX_ACTIVE_HIGH,
    SYSTEM_INTERRUPT_CLEAR,
    RESULT_INTERRUPT_STATUS,
    RESULT_RANGE_STATUS,
    MSRC_CONFIG_CONTROL,
    FINAL_RANGE_CFG_MIN_COUNT_RATE_RTN_LIMIT,
    GLOBAL_CFG_SPAD_ENABLES_REF_0,
    GLOBAL_CFG_REF_EN_START_SELECT,
    DYN_SPAD_NUM_REQUESTED_REF_SPAD,
    DYN_SPAD_REF_EN_START_OFFSET,
    VALUE_00,
    VALUE_01,
    VALUE_02,
    VALUE_03,
    VALUE_04,
    VALUE_05,
    VALUE_06,
    VALUE_07,
    VALUE_08,
    VALUE_09,
    VALUE_0A,
    VALUE_10,
    VALUE_12,
    VALUE_14,
    VALUE_1A,
    VALUE_20,
    VALUE_21,
    VALUE_25,
    VALUE_26,
    VALUE_28,
    VALUE_30,
    VALUE_32,
    VALUE_34,
    VALUE_40,
    VALUE_44,
    VALUE_6B,
    VALUE_83,
    VALUE_96,
    VALUE_A0,
    VALUE_B4,
    VALUE_E8,
    VALUE_FE,
    VALUE_FF,
    VALUE_F8,
    REG_00,
    REG_01,
    REG_0D,
    REG_0E,
    REG_09,
    REG_10,
    REG_11,
    REG_20,
    REG_22,
    REG_23,
    REG_24,
    REG_25,
    REG_27,
    REG_30,
    REG_31,
    REG_32,
    REG_34,
    REG_35,
    REG_40,
    REG_42,
    REG_43,
    REG_44,
    REG_45,
    REG_46,
    REG_47,
    REG_48,
    REG_49,
    REG_4A,
    REG_4B,
    REG_4C,
    REG_4D,
    REG_4E,
    REG_50,
    REG_51,
    REG_52,
    REG_54,
    REG_56,
    REG_57,
    REG_60,
    REG_61,
    REG_62,
    REG_64,
    REG_65,
    REG_66,
    REG_67,
    REG_70,
    REG_71,
    REG_72,
    REG_75,
    REG_76,
    REG_77,
    REG_78,
    REG_7A,
    REG_7B,
    REG_80,
    REG_81,
    REG_8E,
    REG_91,
    REG_92,
    REG_94,
    REG_FF,
    I2C_STANDARD_MODE,
    SPAD_NUM_REQUESTED_REF,
    GPIO_INTERRUPT_CONFIG,
    CALIBRATION_VALUE_40,
    TIMEOUT_LIMIT,
)


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

    def _set_i2c_registers_initial_values(self):
        """
        I2Cレジスタの初期値を設定します。
        """
        self.write_byte(I2C_STANDARD_MODE, VALUE_00)
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)
        self.stop_variable = self.read_byte(REG_91)
        self.write_byte(REG_00, VALUE_01)
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

    def _configure_signal_rate_limit(self):
        """
        信号レート制限を設定します。
        """
        # disable SIGNAL_RATE_MSRC (bit 1) and SIGNAL_RATE_PRE_RANGE (bit 4) limit checks
        self.write_byte(
            MSRC_CONFIG_CONTROL,
            (self.read_byte(MSRC_CONFIG_CONTROL) | VALUE_12),
        )

        # set final range signal rate limit to 0.25 MCPS (million counts per second)
        self.write_word(
            FINAL_RANGE_CFG_MIN_COUNT_RATE_RTN_LIMIT, VALUE_32
        )  # 0.25 * 128 = 32

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_FF)

    def _setup_spad_info(self):
        """
        SPAD情報を設定します。
        """
        spad_count, spad_is_aperture = self._get_spad_info()

        # The SPAD map (RefGoodSpadMap) is read by VL53L0X_get_info_from_device() in the API, but the same data seems to
        # be written to GLOBAL_CONFIG_SPAD_ENABLES_REF_0 through GLOBAL_CONFIG_SPAD_ENABLES_REF_5, so read it from there
        ref_spad_map = self.read_block(GLOBAL_CFG_SPAD_ENABLES_REF_0, 6)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(DYN_SPAD_REF_EN_START_OFFSET, VALUE_00)
        self.write_byte(
            DYN_SPAD_NUM_REQUESTED_REF_SPAD, SPAD_NUM_REQUESTED_REF
        )
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(GLOBAL_CFG_REF_EN_START_SELECT, VALUE_B4)

        first_spad_to_enable = 12 if spad_is_aperture else 0
        spads_enabled = 0

        for i in range(48):
            if i < first_spad_to_enable or spads_enabled == spad_count:
                # This bit is lower than the first one to enable, or (spad_count) bits have already been enabled, so zero this bit
                ref_spad_map[i // 8] &= ~(1 << (i % 8))
            elif (ref_spad_map[i // 8] >> (i % 8)) & 0x1:
                spads_enabled += 1

        self.write_block(GLOBAL_CFG_SPAD_ENABLES_REF_0, ref_spad_map)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_09, VALUE_00)
        self.write_byte(REG_10, VALUE_00)
        self.write_byte(REG_11, VALUE_00)

        self.write_byte(REG_24, VALUE_01)
        self.write_byte(REG_25, VALUE_FF)
        self.write_byte(REG_75, VALUE_00)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_4E, SPAD_NUM_REQUESTED_REF)
        self.write_byte(REG_48, VALUE_00)
        self.write_byte(REG_30, VALUE_20)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_30, VALUE_09)
        self.write_byte(REG_54, VALUE_00)
        self.write_byte(REG_31, VALUE_04)
        self.write_byte(REG_32, VALUE_03)
        self.write_byte(REG_40, VALUE_83)
        self.write_byte(REG_46, VALUE_25)
        self.write_byte(REG_60, VALUE_00)
        self.write_byte(REG_27, VALUE_00)
        self.write_byte(REG_50, VALUE_06)
        self.write_byte(REG_51, VALUE_00)
        self.write_byte(REG_52, VALUE_96)
        self.write_byte(REG_56, VALUE_08)
        self.write_byte(REG_57, VALUE_30)
        self.write_byte(REG_61, VALUE_00)
        self.write_byte(REG_62, VALUE_00)
        self.write_byte(REG_64, VALUE_00)
        self.write_byte(REG_65, VALUE_00)
        self.write_byte(REG_66, VALUE_A0)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_22, VALUE_32)
        self.write_byte(REG_47, VALUE_14)
        self.write_byte(REG_49, VALUE_FF)
        self.write_byte(REG_4A, VALUE_00)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_7A, VALUE_0A)
        self.write_byte(REG_7B, VALUE_00)
        self.write_byte(REG_78, VALUE_21)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_23, VALUE_34)
        self.write_byte(REG_42, VALUE_00)
        self.write_byte(REG_44, VALUE_FF)
        self.write_byte(REG_45, VALUE_26)
        self.write_byte(REG_46, VALUE_05)
        self.write_byte(REG_40, VALUE_40)
        self.write_byte(REG_0E, VALUE_06)
        self.write_byte(REG_20, VALUE_1A)
        self.write_byte(REG_43, VALUE_40)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_34, VALUE_03)
        self.write_byte(REG_35, VALUE_44)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_31, VALUE_04)
        self.write_byte(REG_4B, VALUE_09)
        self.write_byte(REG_4C, VALUE_05)
        self.write_byte(REG_4D, VALUE_04)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_44, VALUE_00)
        self.write_byte(REG_45, VALUE_20)
        self.write_byte(REG_47, VALUE_08)
        self.write_byte(REG_48, VALUE_28)
        self.write_byte(REG_67, VALUE_00)
        self.write_byte(REG_70, VALUE_04)
        self.write_byte(REG_71, VALUE_01)
        self.write_byte(REG_72, VALUE_FE)
        self.write_byte(REG_76, VALUE_00)
        self.write_byte(REG_77, VALUE_00)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_0D, VALUE_01)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_01, VALUE_F8)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_8E, VALUE_01)
        self.write_byte(REG_00, VALUE_01)
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

    def _configure_interrupt_gpio(self):
        """
        割り込みGPIOを設定します。
        """
        self.write_byte(SYSTEM_INTERRUPT_CONFIG_GPIO, GPIO_INTERRUPT_CONFIG)
        self.write_byte(
            GPIO_HV_MUX_ACTIVE_HIGH,
            (self.read_byte(GPIO_HV_MUX_ACTIVE_HIGH) & ~VALUE_10),
        )  # active low
        self.write_byte(SYSTEM_INTERRUPT_CLEAR, VALUE_01)

    def _set_timing_budget_and_calibrations(self):
        """
        タイミングバジェットを設定し、キャリブレーションを実行します。
        """
        self.measurement_timing_budget_us = (
            self.get_measurement_timing_budget()
        )
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)

        # restore the previous Sequence Config
        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_E8)
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_01)
        self.perform_single_ref_calibration(CALIBRATION_VALUE_40)

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_02)
        self.perform_single_ref_calibration(VALUE_00)

        # "restore the previous Sequence Config"
        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_E8)

    def initialize(self):
        """
        Initialize the sensor.
        """
        self._set_i2c_registers_initial_values()
        self._configure_signal_rate_limit()
        self._setup_spad_info()
        self._configure_interrupt_gpio()
        self._set_timing_budget_and_calibrations()

    def _get_spad_info(self):
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)

        self.write_byte(REG_FF, VALUE_06)
        self.write_byte(VALUE_83, (self.read_byte(VALUE_83) | VALUE_04))
        self.write_byte(REG_FF, VALUE_07)
        self.write_byte(REG_81, VALUE_01)

        self.write_byte(REG_80, VALUE_01)

        self.write_byte(REG_94, VALUE_6B)
        self.write_byte(VALUE_83, VALUE_00)
        start = time.time()
        while self.read_byte(VALUE_83) == VALUE_00:
            if time.time() - start > TIMEOUT_LIMIT:
                raise Exception("Timeout")
        self.write_byte(VALUE_83, VALUE_01)
        tmp = self.read_byte(REG_92)

        count = tmp & 0x7F
        is_aperture = ((tmp >> 7) & VALUE_01) == 1

        self.write_byte(REG_81, VALUE_00)
        self.write_byte(REG_FF, VALUE_06)
        self.write_byte(VALUE_83, (self.read_byte(VALUE_83) & ~VALUE_04))
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_01)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

        return count, is_aperture

    def get_measurement_timing_budget(self) -> int:
        """
        現在の測定タイミングバジェットをマイクロ秒単位で取得します。
        (実際のレジスタ実装はより複雑です。これはプレースホルダーです。)
        """
        # 実際のVL53L0Xドライバでは、複数のレジスタを読み取り、
        # 有効なタイミングバジェットを計算する必要があります。
        # ここではプレースホルダーとして固定値を返します。
        return 500000  # 500ms (例)

    def set_measurement_timing_budget(self, budget_us: int):
        """
        測定タイミングバジェットをマイクロ秒単位で設定します。
        (実際のレジスタ実装はより複雑です。これはプレースホルダーです。)
        """
        # 実際のVL53L0Xドライバでは、目的のタイミングバジェットに合わせて
        # センサーを構成するために、一連のレジスタ書き込みが必要になります。
        # (例: プリレンジ、ファイナルレンジ、様々なタイミングパラメータ)
        # 現時点では、このメソッドは何もしません。
        pass

    def perform_single_ref_calibration(self, vhv_init_byte):
        self.write_byte(SYSRANGE_START, VALUE_01 | vhv_init_byte)
        start = time.time()
        while (self.read_byte(RESULT_INTERRUPT_STATUS) & 0x07) == VALUE_00:
            if time.time() - start > TIMEOUT_LIMIT:
                raise Exception("Timeout")
        self.write_byte(SYSTEM_INTERRUPT_CLEAR, VALUE_01)
        self.write_byte(SYSRANGE_START, VALUE_00)

    def get_range(self):
        """
        Perform a single ranging measurement and return the result in mm.
        """
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)
        self.write_byte(REG_91, self.stop_variable)
        self.write_byte(REG_00, VALUE_01)
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

        self.write_byte(SYSRANGE_START, VALUE_01)

        start = time.time()
        while self.read_byte(SYSRANGE_START) & VALUE_01:
            if time.time() - start > TIMEOUT_LIMIT:
                raise Exception("Timeout")

        start = time.time()
        while (self.read_byte(RESULT_INTERRUPT_STATUS) & 0x07) == VALUE_00:
            if time.time() - start > TIMEOUT_LIMIT:
                raise Exception("Timeout")

        # assumptions: Linearity Corrective Gain is 1000 (default)
        # fractional ranging is not enabled
        range_mm = self.read_word(
            RESULT_RANGE_STATUS + VALUE_0A
        )  # 10 is 0x0A

        self.write_byte(SYSTEM_INTERRUPT_CLEAR, VALUE_01)

        return range_mm

    def get_ranges(self, num_samples: int) -> np.ndarray:
        """
        Performs continuous ranging measurements for a specified number of samples
        and returns the results in a numpy array.
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
        _, data = self.pi.i2c_read_i2c_block_data(
            self.handle, register, count
        )
        return data

    def write_block(self, register, data):
        """
        Write a block of data to a register.
        """
        self.pi.i2c_write_i2c_block_data(self.handle, register, data)
