"""
蓝牙打印机管理模块
支持 PC (pybluez) 和 Android (pyjnius) 双平台
适配喵学王等 ESC/POS 热敏打印机
"""

import threading
import time
import uuid as uuid_mod
from kivy.utils import platform
from kivy.logger import Logger
from kivy.clock import Clock, mainthread
from kivy.app import App


class ESCPosGenerator:
    """ESC/POS 指令生成器（纯 Python，不依赖外部库）"""

    ESC = b'\x1b'
    GS = b'\x1d'
    FS = b'\x1c'

    # 常用编码尝试顺序（中文优先 GBK/GB2312）
    ENCODING_FALLBACKS = ['gbk', 'gb2312', 'utf-8']

    @classmethod
    def _encode_text(cls, text):
        """尝试多种编码，返回可编码的字节"""
        for enc in cls.ENCODING_FALLBACKS:
            try:
                return text.encode(enc)
            except UnicodeEncodeError:
                continue
        return text.encode('utf-8', errors='replace')

    @classmethod
    def init_printer(cls):
        """初始化打印机"""
        return cls.ESC + b'@'

    @classmethod
    def align_left(cls):
        return cls.ESC + b'a\x00'

    @classmethod
    def align_center(cls):
        return cls.ESC + b'a\x01'

    @classmethod
    def align_right(cls):
        return cls.ESC + b'a\x02'

    @classmethod
    def bold_on(cls):
        return cls.ESC + b'E\x01'

    @classmethod
    def bold_off(cls):
        return cls.ESC + b'E\x00'

    @classmethod
    def font_double_width(cls):
        """倍宽字体"""
        return cls.ESC + b'!\x20'

    @classmethod
    def font_double_height(cls):
        """倍高字体"""
        return cls.ESC + b'!\x10'

    @classmethod
    def font_normal(cls):
        return cls.ESC + b'!\x00'

    @classmethod
    def font_large(cls):
        """倍高倍宽"""
        return cls.ESC + b'!\x30'

    @classmethod
    def feed_lines(cls, n=3):
        """走纸 n 行"""
        return cls.ESC + b'd' + bytes([n])

    @classmethod
    def cut_paper(cls, partial=False):
        """切纸：partial=True 部分切纸"""
        if partial:
            return cls.GS + b'V\x01'
        return cls.GS + b'V\x00'

    @classmethod
    def print_line(cls, text=''):
        """打印一行文本并换行"""
        return cls._encode_text(text) + b'\n'

    @classmethod
    def separator_line(cls, char='-', width=32):
        """分隔线（默认 32 字符宽度适配 58mm 纸）"""
        return cls._encode_text(char * width) + b'\n'

    @classmethod
    def generate_order_receipt(cls, order):
        """
        生成订单小票 ESC/POS 数据
        order 为 Order 对象或具有相同属性的 dict
        """
        # 兼容 dict 和对象
        def _get(attr, default=''):
            try:
                if isinstance(order, dict):
                    return order.get(attr, default)
                return getattr(order, attr, default)
            except Exception:
                return default

        def _get_float(attr, default=0.0):
            try:
                return float(_get(attr, default))
            except (TypeError, ValueError):
                return default

        def _get_int(val, default=0):
            try:
                return int(val)
            except (TypeError, ValueError):
                return default

        data = b''
        data += cls.init_printer()

        # 标题
        data += cls.align_center()
        data += cls.font_large()
        data += cls.bold_on()
        data += cls.print_line('购物商城')
        data += cls.bold_off()
        data += cls.font_normal()
        data += cls.print_line('订单小票')
        data += cls.separator_line()

        # 订单信息
        data += cls.align_left()
        order_id = str(_get('order_id', ''))[:20]
        data += cls.print_line(f"订单号: {order_id}")
        created_at = str(_get('created_at', ''))
        data += cls.print_line(f"下单时间: {created_at}")
        user_name = str(_get('user_name', ''))
        data += cls.print_line(f"收货人: {user_name}")
        data += cls.print_line("状态: 已完成")
        data += cls.separator_line()

        # 商品列表
        data += cls.bold_on()
        data += cls.print_line('商品名称          数量   小计')
        data += cls.bold_off()

        items = _get('items', [])
        if not isinstance(items, (list, tuple)):
            items = []
        for item in items:
            try:
                if isinstance(item, dict):
                    name = str(item.get('product_name', ''))
                    qty = _get_int(item.get('quantity', 0))
                    price = _get_float(item.get('price', 0))
                else:
                    name = str(getattr(item, 'product_name', ''))
                    qty = _get_int(getattr(item, 'quantity', 0))
                    price = _get_float(getattr(item, 'price', 0))
                sub = price * qty
                # 截断名称以适应 58mm 纸宽（按字符数）
                name_display = name[:12] if len(name) > 12 else name
                data += cls.print_line(f"{name_display:<12} {qty:>3}  ¥{sub:.1f}")
            except Exception:
                # 单条商品异常不中断整体打印
                continue

        data += cls.separator_line()

        # 金额汇总
        data += cls.align_right()
        subtotal = _get_float('subtotal', 0)
        discount = _get_float('discount', 0)
        total = _get_float('total', 0)
        data += cls.print_line(f"商品小计: ¥{subtotal:.1f}")
        data += cls.print_line(f"优惠金额: ¥{discount:.1f}")
        data += cls.font_double_width()
        data += cls.bold_on()
        data += cls.print_line(f"应付总额: ¥{total:.1f}")
        data += cls.bold_off()
        data += cls.font_normal()
        data += cls.align_left()
        data += cls.separator_line()

        # 页脚
        data += cls.align_center()
        data += cls.print_line('感谢您的惠顾！')
        data += cls.print_line('欢迎下次光临')
        data += cls.feed_lines(5)
        data += cls.cut_paper(partial=True)
        return data


class BluetoothBackendBase:
    """蓝牙后端基类"""

    def scan_devices(self, callback, timeout=12):
        """扫描设备，callback(device_list)"""
        raise NotImplementedError

    def connect(self, device_address, callback=None):
        """连接设备，callback(success, error_msg)"""
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def send(self, data):
        raise NotImplementedError

    def is_connected(self):
        raise NotImplementedError


class PybluezBackend(BluetoothBackendBase):
    """PC 端 pybluez 后端"""

    def __init__(self):
        self._socket = None
        self._address = None
        self._connected = False
        self._scanning = False

    def scan_devices(self, callback, timeout=12):
        def _scan():
            try:
                import bluetooth
                self._scanning = True
                Logger.info("BluetoothPrinter: 开始扫描设备...")
                nearby = bluetooth.discover_devices(duration=timeout, lookup_names=True, flush_cache=True)
                devices = []
                for addr, name in nearby:
                    devices.append({
                        'name': name or 'Unknown',
                        'address': addr,
                        'paired': False,  # pybluez discover 不区分配对状态
                    })
                Logger.info(f"BluetoothPrinter: 发现 {len(devices)} 个设备")
                Clock.schedule_once(lambda dt: callback(devices), 0)
            except Exception as e:
                Logger.error(f"BluetoothPrinter: 扫描失败 {e}")
                Clock.schedule_once(lambda dt: callback([]), 0)
            finally:
                self._scanning = False

        threading.Thread(target=_scan, daemon=True).start()

    def connect(self, device_address, callback=None):
        def _connect():
            try:
                import bluetooth
                self.disconnect()
                sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                # 尝试常见 channel（喵学王等热敏打印机通常使用 channel 1）
                for channel in [1, 3, 2, 4]:
                    try:
                        sock.connect((device_address, channel))
                        break
                    except bluetooth.BluetoothError:
                        continue
                else:
                    raise Exception("无法连接到打印机的 RFCOMM 服务")
                self._socket = sock
                self._address = device_address
                self._connected = True
                Logger.info(f"BluetoothPrinter: 已连接到 {device_address}")
                if callback:
                    Clock.schedule_once(lambda dt: callback(True, None), 0)
            except Exception as e:
                error_msg = str(e)
                Logger.error(f"BluetoothPrinter: 连接失败 {error_msg}")
                self._connected = False
                if callback:
                    Clock.schedule_once(lambda dt, msg=error_msg: callback(False, msg), 0)

        threading.Thread(target=_connect, daemon=True).start()

    def disconnect(self):
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        self._connected = False
        self._address = None

    def send(self, data):
        if not self._socket:
            raise RuntimeError("蓝牙未连接")
        try:
            self._socket.send(data)
        except Exception as e:
            self._connected = False
            raise RuntimeError(f"发送失败: {e}")

    def is_connected(self):
        return self._connected


class AndroidBackend(BluetoothBackendBase):
    """Android 端后端，支持经典蓝牙 SPP 和 BLE GATT"""

    # 标准 SPP UUID
    SPP_UUID = uuid_mod.UUID("00001101-0000-1000-8000-00805F9B34FB")

    # 常见 BLE UART Service UUID
    BLE_UART_SERVICES = [
        "0000ffe0-0000-1000-8000-00805f9b34fb",
        "6e400001-b5a3-f393-e0a9-e50e24dcca9e",
    ]

    def __init__(self):
        # 经典蓝牙
        self._socket = None
        self._output_stream = None
        # BLE
        self._gatt = None
        self._write_char = None
        self._gatt_callback = None
        self._write_event = threading.Event()
        self._write_success = True
        # 通用
        self._device = None
        self._connected = False
        self._scanning = False
        self._is_ble = False
        self._bluetooth_adapter = None
        self._ensure_adapter()

    def _ensure_adapter(self):
        try:
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            self._bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()
        except Exception as e:
            Logger.error(f"BluetoothPrinter: 获取 BluetoothAdapter 失败: {e}")
            self._bluetooth_adapter = None

    def _check_enabled(self):
        if self._bluetooth_adapter is None:
            return False
        return self._bluetooth_adapter.isEnabled()

    def scan_devices(self, callback, timeout=12):
        def _scan():
            try:
                self._scanning = True
                if not self._check_enabled():
                    Logger.warning("BluetoothPrinter: 蓝牙未启用")
                    Clock.schedule_once(lambda dt: callback([]), 0)
                    return

                from jnius import autoclass
                BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')

                try:
                    bonded = self._bluetooth_adapter.getBondedDevices()
                except Exception as e:
                    Logger.error(f"BluetoothPrinter: getBondedDevices 调用失败: {e}")
                    Clock.schedule_once(lambda dt: callback([]), 0)
                    return

                devices = []
                if bonded:
                    try:
                        count = 0
                        for device in bonded:
                            count += 1
                            try:
                                name = device.getName()
                                addr = device.getAddress()
                                dev_type = device.getType()
                                type_str = {1: "CLASSIC", 2: "LE", 3: "DUAL"}.get(dev_type, "UNKNOWN")
                                devices.append({
                                    'name': name or 'Unknown',
                                    'address': addr or '',
                                    'paired': True,
                                    'type': type_str,
                                })
                            except Exception as dev_e:
                                Logger.warning(f"BluetoothPrinter: 读取单个设备信息失败: {dev_e}")
                        Logger.info(f"BluetoothPrinter: getBondedDevices 迭代了 {count} 个设备，成功读取 {len(devices)} 个")
                    except Exception as e:
                        Logger.error(f"BluetoothPrinter: 遍历 bonded devices 失败: {e}")
                else:
                    Logger.info("BluetoothPrinter: getBondedDevices 返回空")

                Logger.info(f"BluetoothPrinter: 最终返回 {len(devices)} 个设备")
                Clock.schedule_once(lambda dt: callback(devices), 0)
            except Exception as e:
                Logger.error(f"BluetoothPrinter: Android 扫描失败 {e}")
                Clock.schedule_once(lambda dt: callback([]), 0)
            finally:
                self._scanning = False

        threading.Thread(target=_scan, daemon=True).start()

    def connect(self, device_address, callback=None):
        def _connect():
            sock = None
            error_msg = ""
            try:
                self.disconnect()
                if not self._check_enabled():
                    raise Exception("蓝牙未启用")

                from jnius import autoclass
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
                adapter = BluetoothAdapter.getDefaultAdapter()
                device = adapter.getRemoteDevice(device_address)

                if adapter.isDiscovering():
                    adapter.cancelDiscovery()

                dev_type = device.getType()
                Logger.info(f"BluetoothPrinter: 设备类型={dev_type} (1=CLASSIC,2=LE,3=DUAL)")

                if dev_type == BluetoothDevice.DEVICE_TYPE_LE:
                    # 纯 BLE 设备
                    Logger.info("BluetoothPrinter: 检测到 BLE 设备，尝试连接")
                    self._is_ble = True
                    self._connect_ble(device)
                    if self._connected:
                        Logger.info(f"BluetoothPrinter: BLE 已连接到 {device_address}")
                        if callback:
                            Clock.schedule_once(lambda dt: callback(True, None), 0)
                    else:
                        raise Exception("该 BLE 打印机无法连接（L2CAP 失败且当前环境不支持 GATT）")
                    return

                # 经典蓝牙尝试（适用于 CLASSIC 和 DUAL）
                self._is_ble = False
                UUID = autoclass('java.util.UUID')
                spp_uuid = UUID.fromString(str(self.SPP_UUID))

                # --- 策略1: insecure SPP UUID（部分打印机必须用 insecure） ---
                if not sock:
                    try:
                        Logger.info("BluetoothPrinter: 尝试 insecure SPP UUID")
                        sock = device.createInsecureRfcommSocketToServiceRecord(spp_uuid)
                        sock.connect()
                        Logger.info("BluetoothPrinter: insecure SPP UUID 连接成功")
                    except Exception as e:
                        Logger.warning(f"BluetoothPrinter: insecure SPP UUID 失败: {e}")
                        try:
                            sock.close()
                        except Exception:
                            pass
                        sock = None

                # --- 策略2: 标准 secure SPP UUID ---
                if not sock:
                    try:
                        Logger.info("BluetoothPrinter: 尝试标准 SPP UUID")
                        sock = device.createRfcommSocketToServiceRecord(spp_uuid)
                        sock.connect()
                        Logger.info("BluetoothPrinter: 标准 SPP UUID 连接成功")
                    except Exception as e:
                        Logger.warning(f"BluetoothPrinter: 标准 SPP UUID 失败: {e}")
                        try:
                            sock.close()
                        except Exception:
                            pass
                        sock = None

                # --- 策略3: insecure RFCOMM channel ---
                if not sock:
                    for channel in [1, 2]:
                        try:
                            Logger.info(f"BluetoothPrinter: 尝试 insecure channel {channel}")
                            sock = device.createInsecureRfcommSocket(channel)
                            sock.connect()
                            Logger.info(f"BluetoothPrinter: insecure channel {channel} 连接成功")
                            break
                        except Exception as e:
                            Logger.warning(f"BluetoothPrinter: insecure channel {channel} 失败: {e}")
                            try:
                                sock.close()
                            except Exception:
                                pass
                            sock = None

                # --- 策略4: secure RFCOMM channel ---
                if not sock:
                    for channel in [1, 2]:
                        try:
                            Logger.info(f"BluetoothPrinter: 尝试 createRfcommSocket({channel})")
                            sock = device.createRfcommSocket(channel)
                            sock.connect()
                            Logger.info(f"BluetoothPrinter: channel {channel} 连接成功")
                            break
                        except Exception as e:
                            Logger.warning(f"BluetoothPrinter: channel {channel} 失败: {e}")
                            try:
                                sock.close()
                            except Exception:
                                pass
                            sock = None

                if sock:
                    self._socket = sock
                    self._device = device
                    self._output_stream = sock.getOutputStream()
                    self._connected = True
                    Logger.info(f"BluetoothPrinter: 经典蓝牙已连接到 {device_address}")
                    if callback:
                        Clock.schedule_once(lambda dt: callback(True, None), 0)
                    return

                # 经典蓝牙全部失败
                classic_error = "所有经典蓝牙连接方式均失败"

                # DUAL 设备回退到 BLE
                if dev_type == BluetoothDevice.DEVICE_TYPE_DUAL:
                    Logger.info("BluetoothPrinter: DUAL 设备经典蓝牙失败，回退到 BLE")
                    self._is_ble = True
                    self._connect_ble(device)
                    if self._connected:
                        Logger.info(f"BluetoothPrinter: BLE 回退成功 {device_address}")
                        if callback:
                            Clock.schedule_once(lambda dt: callback(True, None), 0)
                        return
                    else:
                        classic_error += "；BLE 也无法连接"

                raise Exception(classic_error + "，请确认打印机已开启并在范围内")

            except Exception as e:
                error_msg = str(e)
                Logger.error(f"BluetoothPrinter: Android 连接失败 {error_msg}")
                self._connected = False
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass
                if callback:
                    Clock.schedule_once(lambda dt, msg=error_msg: callback(False, msg), 0)

        threading.Thread(target=_connect, daemon=True).start()

    def _connect_ble(self, device):
        """BLE 连接：只尝试 L2CAP socket。GATT 需要 BluetoothGattCallback，
        在当前 pyjnius 环境下会触发 native crash，因此不再尝试。"""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity

            # L2CAP socket（Android 10+，无需 GATT callback）
            try:
                Logger.info("BluetoothPrinter: 尝试 L2CAP socket 连接")
                for psm in [0x80, 0x81, 0x82, 0x83]:
                    sock = None
                    try:
                        Logger.info(f"BluetoothPrinter: 尝试 insecure L2CAP PSM={psm}")
                        sock = device.createInsecureL2capSocket(psm)
                        sock.connect()
                        self._socket = sock
                        self._output_stream = sock.getOutputStream()
                        self._connected = True
                        self._is_ble = True
                        Logger.info(f"BluetoothPrinter: L2CAP PSM={psm} 连接成功")
                        return
                    except Exception as l2cap_e:
                        Logger.warning(f"BluetoothPrinter: L2CAP PSM={psm} 失败: {l2cap_e}")
                        if sock:
                            try:
                                sock.close()
                            except Exception:
                                pass
            except AttributeError:
                Logger.warning("BluetoothPrinter: 设备不支持 createInsecureL2capSocket（API < 29）")

            Logger.error("BluetoothPrinter: L2CAP 均失败，且 GATT 在当前 pyjnius 环境下不稳定，放弃 BLE 连接")
            self._connected = False
        except Exception as e:
            Logger.error(f"BluetoothPrinter: BLE 连接异常: {e}")
            import traceback
            Logger.error(traceback.format_exc())
            self._connected = False

    def disconnect(self):
        # BLE 清理
        if self._gatt:
            try:
                self._gatt.disconnect()
                self._gatt.close()
            except Exception:
                pass
            self._gatt = None
        self._write_char = None
        # 经典蓝牙清理
        if self._output_stream:
            try:
                self._output_stream.close()
            except Exception:
                pass
            self._output_stream = None
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        self._device = None
        self._connected = False
        self._is_ble = False

    def send(self, data):
        if not self.is_connected():
            raise RuntimeError("蓝牙未连接")
        try:
            # L2CAP 和经典蓝牙都使用 _socket/_output_stream
            if self._gatt:
                self._send_ble(data)
            else:
                self._send_classic(data)
        except Exception as e:
            self._connected = False
            raise RuntimeError(f"发送失败: {e}")

    def _send_classic(self, data):
        if not self._output_stream:
            raise RuntimeError("经典蓝牙未连接")
        chunk_size = 1024
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            self._output_stream.write(list(bytearray(chunk)))
            self._output_stream.flush()

    def _send_ble(self, data):
        if not self._gatt or not self._write_char:
            raise RuntimeError("BLE 未连接")
        from jnius import autoclass
        BluetoothGattCharacteristic = autoclass('android.bluetooth.BluetoothGattCharacteristic')

        chunk_size = 20  # BLE 默认 MTU 减去 ATT header
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]

            # 设置写入类型
            props = self._write_char.getProperties()
            if props & BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE:
                self._write_char.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE)
            else:
                self._write_char.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT)

            self._write_char.setValue(list(bytearray(chunk)))
            ok = self._gatt.writeCharacteristic(self._write_char)
            if not ok:
                raise RuntimeError(f"BLE writeCharacteristic 返回 false (chunk {i // chunk_size})")

            # 空的 callback 没有写入完成通知，用固定延迟给蓝牙堆栈处理时间
            time.sleep(0.15)

    def is_connected(self):
        return self._connected


class BluetoothPrinterManager:
    """
    蓝牙打印机管理器（全局单例，建议挂载在 App 实例上）
    """

    def __init__(self):
        self._backend = None
        self._init_backend()
        self.connected_device = None  # {'name': ..., 'address': ...}
        self.connection_state = "disconnected"  # disconnected, scanning, connecting, connected, error
        self.last_error = ""
        self._on_state_changed = None

    def _init_backend(self):
        if platform == 'android':
            try:
                self._backend = AndroidBackend()
                Logger.info("BluetoothPrinter: 使用 AndroidBackend")
            except Exception as e:
                Logger.error(f"BluetoothPrinter: AndroidBackend 初始化失败: {e}")
                self._backend = None
        else:
            try:
                self._backend = PybluezBackend()
                Logger.info("BluetoothPrinter: 使用 PybluezBackend")
            except Exception as e:
                Logger.error(f"BluetoothPrinter: PybluezBackend 初始化失败: {e}")
                self._backend = None

    def set_state_callback(self, callback):
        """设置状态变更回调 callback(state, device_info, error_msg)"""
        self._on_state_changed = callback

    def _set_state(self, state, device=None, error=""):
        self.connection_state = state
        if device is not None:
            self.connected_device = device
        if error:
            self.last_error = error
        Logger.info(f"BluetoothPrinter: 状态 -> {state}, 设备={device}, 错误={error}")
        if self._on_state_changed:
            try:
                self._on_state_changed(state, self.connected_device, error)
            except Exception as e:
                Logger.error(f"BluetoothPrinter: state callback error {e}")

    def is_available(self):
        return self._backend is not None

    def is_connected(self):
        if self._backend:
            return self._backend.is_connected()
        return False

    def get_connected_device_name(self):
        if self.connected_device:
            return self.connected_device.get('name', '')
        return ""

    def scan_devices(self, on_devices_found=None):
        """
        扫描蓝牙设备
        on_devices_found(devices_list) -> devices_list = [{'name':..., 'address':..., 'paired':...}, ...]
        """
        if not self._backend:
            self._set_state("error", error="蓝牙后端未初始化")
            if on_devices_found:
                on_devices_found([])
            return

        self._set_state("scanning")

        def _callback(devices):
            self._set_state("disconnected" if not self.is_connected() else "connected")
            if on_devices_found:
                on_devices_found(devices)

        self._backend.scan_devices(callback=_callback, timeout=12)

    def connect(self, device_info, on_result=None):
        """
        连接指定设备
        device_info: {'name':..., 'address':...}
        on_result(success: bool, error_msg: str)
        """
        if not self._backend:
            self._set_state("error", error="蓝牙后端未初始化")
            if on_result:
                on_result(False, "蓝牙后端未初始化")
            return

        self._set_state("connecting", device=device_info)

        def _callback(success, error_msg):
            if success:
                self._set_state("connected", device=device_info)
            else:
                self._set_state("error", device=device_info, error=error_msg or "连接失败")
            if on_result:
                on_result(success, error_msg or "")

        self._backend.connect(device_info['address'], callback=_callback)

    def disconnect(self):
        if self._backend:
            self._backend.disconnect()
        self.connected_device = None
        self._set_state("disconnected")

    def print_order(self, order):
        """
        打印订单
        order: Order 对象 或 dict
        返回: (success: bool, error_msg: str)
        """
        if not self.is_connected():
            return False, "蓝牙打印机未连接"
        try:
            data = ESCPosGenerator.generate_order_receipt(order)
            self._backend.send(data)
            return True, ""
        except Exception as e:
            Logger.error(f"BluetoothPrinter: 打印失败 {e}")
            return False, str(e)


def get_printer_manager():
    """获取 App 上的蓝牙打印机管理器"""
    try:
        app = App.get_running_app()
        if hasattr(app, 'bluetooth_printer_manager'):
            return app.bluetooth_printer_manager
    except Exception:
        pass
    return None
