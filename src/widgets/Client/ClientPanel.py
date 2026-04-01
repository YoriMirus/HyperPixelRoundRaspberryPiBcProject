from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSizePolicy, QSlider
from PySide6.QtCore import Qt, Signal, QTimer

from networking.CommandTypes import *
from networking.GetStatusDTO import *

class ClientPanel(QWidget):
    on_command_send_request = Signal(object)
    def __init__(self, parent=None):
        super(ClientPanel, self).__init__(parent)

        self.BMP180_status_label = QLabel()
        self.MMA5452Q_status_label = QLabel()
        self.SHT3x_status_label = QLabel()
        self.SHT3x_temp_label = QLabel("0 °C")
        self.SHT3x_humidity_label = QLabel("0 %")

        self.MMA5452Q_x_label = QLabel("0")
        self.MMA5452Q_y_label = QLabel("0")
        self.MMA5452Q_z_label = QLabel("0")

        self.MMA5452Q_roll_label = QLabel("0°")
        self.MMA5452Q_pitch_label = QLabel("0°")

        self.bmp180_temp_label = QLabel("0 °C")
        self.bmp180_pressure_label = QLabel("0 Pa")
        self.bmp180_altitude_label = QLabel("0 m")

        self.red_hex = "#c30101"
        self.green_hex = "#00b34d"

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10,10,10,10)

        main_layout.addLayout(self.create_shutdown_buttons_layout())

        render_style_lbl = QLabel("Styl vykreslování")
        render_style_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(render_style_lbl)

        main_layout.addLayout(self.create_rendering_style_layout())
        main_layout.addLayout(self.create_widget_styles_layout())

        lbl, slider = self.create_brightness_slider()
        self.brightness_slider = slider
        main_layout.addWidget(lbl)
        main_layout.addWidget(slider)

        render_style_lbl = QLabel("Stav senzorů")
        render_style_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(render_style_lbl)

        main_layout.addLayout(self.create_sensor_status_layout())
        main_layout.addWidget(self.create_filler_widget())

        # Zkusme vynutit aktualizaci jasu
        # Pravděpodobně to ale nic neudělá jelikož nevíme, zda je aktuálně připojeno zařízení nebo ne
        self.current_brightness = self.brightness_slider.value()
        self.brightness_timer = QTimer(self)
        self.brightness_timer.timeout.connect(self.on_timer_tick)
        self.brightness_timer.start(50)

    def on_timer_tick(self):
        val = self.brightness_slider.value()
        if val != self.current_brightness:
            self.send_change_brightness_command()


    def create_shutdown_buttons_layout(self):
        # Tlačítka pro vypnutí programu
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        shutdown_btn = QPushButton("Vypnout raspberry pi")
        shutdown_btn.clicked.connect(self.send_shutdown_command)
        debug_btn = QPushButton("Ukončit program")
        debug_btn.clicked.connect(self.send_shutdown_debug_command)
        layout.addWidget(shutdown_btn)
        layout.addWidget(debug_btn)

        return layout

    def create_rendering_style_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(10)

        default_btn = QPushButton("Výchozí režim")
        default_btn.clicked.connect(self.send_default_window_command)
        manual_btn = QPushButton("Manuální režim")
        manual_btn.clicked.connect(self.send_manual_window_command)
        layout.addWidget(default_btn)
        layout.addWidget(manual_btn)

        return layout

    def create_widget_styles_layout(self):
        # Nastavení stylů stránek
        page_style_grid = QGridLayout()

        page_style_grid.addWidget(QLabel("Hodiny"), 0, 0)
        page_style_grid.addWidget(QLabel("Meteostanice"), 1, 0)
        page_style_grid.addWidget(QLabel("Akcelerometr"), 2, 0)

        btn = QPushButton("Klasické")
        btn.clicked.connect(self.send_set_clock_style_analog_command)
        page_style_grid.addWidget(btn, 0, 1)

        btn = QPushButton("Digitální")
        btn.clicked.connect(self.send_set_clock_style_digital_a_command)
        page_style_grid.addWidget(btn, 0, 2)

        page_style_grid.addWidget(QPushButton("Digitální 2"), 0, 3)

        btn = QPushButton("Digitální")
        btn.clicked.connect(self.send_set_weather_station_digital_command)
        page_style_grid.addWidget(btn, 1, 1)

        btn = QPushButton("Umělý horizont")
        btn.clicked.connect(self.send_set_accelerometer_artificial_horizon_command)
        page_style_grid.addWidget(btn, 2, 1)

        return page_style_grid

    def create_brightness_slider(self):
        lbl = QLabel("Jas")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(50)

        return lbl, slider


    def create_sensor_status_layout(self):
        layout = QGridLayout()

        # SHT3x

        sht3_label = QLabel("SHT3x")
        sht3_status_label = QLabel("Odpojen")
        sht3_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sht3_status_label.setStyleSheet(f"color: {self.red_hex}")
        self.SHT3x_status_label = sht3_status_label

        sht3_meas_label = QLabel("Naměřené hodnoty")

        self.SHT3x_temp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.SHT3x_humidity_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        sht3_sub_layout = QHBoxLayout()
        sht3_sub_layout.addWidget(self.SHT3x_temp_label)
        sht3_sub_layout.addWidget(self.SHT3x_humidity_label)

        # MMA5452Q

        mma5452q_label = QLabel("MMA5452")
        mma5452_status_label = QLabel("Odpojen")
        mma5452_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mma5452_status_label.setStyleSheet(f"color: {self.red_hex}")
        self.MMA5452Q_status_label = mma5452_status_label

        mma5452q_meas_label = QLabel("Naměřené hodnoty (x,y,z)")

        self.MMA5452Q_x_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.MMA5452Q_y_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.MMA5452Q_z_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        mma5452q_accel_sub_layout = QHBoxLayout()
        mma5452q_accel_sub_layout.addWidget(self.MMA5452Q_x_label)
        mma5452q_accel_sub_layout.addWidget(self.MMA5452Q_y_label)
        mma5452q_accel_sub_layout.addWidget(self.MMA5452Q_z_label)

        self.MMA5452Q_roll_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.MMA5452Q_pitch_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        mma5452q_gyro_sub_layout = QHBoxLayout()
        mma5452q_gyro_sub_layout.addWidget(self.MMA5452Q_roll_label)
        mma5452q_gyro_sub_layout.addWidget(self.MMA5452Q_pitch_label)

        # BMP180

        bmp_label =QLabel("BMP180")
        bmp_status_label = QLabel("Odpojen")
        bmp_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bmp_status_label.setStyleSheet(f"color: {self.red_hex}")
        self.BMP180_status_label = bmp_status_label

        bmp_meas_label = QLabel("Naměřené hodnoty (°C, Pa, m)")

        self.bmp180_temp_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.bmp180_pressure_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bmp180_altitude_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        bmp_sub_layout = QHBoxLayout()
        bmp_sub_layout.addWidget(self.bmp180_temp_label)
        bmp_sub_layout.addWidget(self.bmp180_pressure_label)
        bmp_sub_layout.addWidget(self.bmp180_altitude_label)

        layout.addWidget(sht3_label, 0, 0)
        layout.addWidget(sht3_status_label, 0, 1)
        layout.addWidget(sht3_meas_label, 1, 0)
        layout.addLayout(sht3_sub_layout, 1, 1)

        layout.addWidget(mma5452q_label, 2, 0)
        layout.addWidget(mma5452_status_label, 2, 1)
        layout.addWidget(mma5452q_meas_label, 3, 0)
        layout.addLayout(mma5452q_accel_sub_layout, 3, 1)
        layout.addLayout(mma5452q_gyro_sub_layout, 4, 1)

        layout.addWidget(bmp_label, 5, 0)
        layout.addWidget(bmp_status_label, 5, 1)
        layout.addWidget(bmp_meas_label, 6, 0)
        layout.addLayout(bmp_sub_layout, 6, 1)

        return layout

    def create_filler_widget(self):
        filler_label = QLabel("")
        filler_label.setStyleSheet("background-color: transparent")
        filler_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return filler_label

    def update_status(self, DTO: GetStatusDTO):
        if not DTO.is_raspberry_pi and False:
            return

        mma_connected = DTO.MMA5452Q.connected
        if mma_connected:
            self.MMA5452Q_status_label.setText("Připojen")
            self.MMA5452Q_status_label.setStyleSheet(f"color: {self.green_hex}")

            self.MMA5452Q_x_label.setText(str(DTO.MMA5452Q.values_accel.x))
            self.MMA5452Q_y_label.setText(str(DTO.MMA5452Q.values_accel.y))
            self.MMA5452Q_z_label.setText(str(DTO.MMA5452Q.values_accel.z))

            self.MMA5452Q_roll_label.setText(str(DTO.MMA5452Q.values_gyro.roll))
            self.MMA5452Q_pitch_label.setText(str(DTO.MMA5452Q.values_gyro.pitch))
        else:
            self.MMA5452Q_status_label.setText("Odpojen")
            self.MMA5452Q_status_label.setStyleSheet(f"color: {self.red_hex}")

        sht_connected = DTO.SHT3x.connected
        if sht_connected:
            self.SHT3x_status_label.setText("Připojen")
            self.SHT3x_status_label.setStyleSheet(f"color: {self.green_hex}")

            self.SHT3x_temp_label.setText(str(DTO.SHT3x.values.temperature))
            self.SHT3x_humidity_label.setText(str(DTO.SHT3x.values.humidity))
        else:
            self.SHT3x_status_label.setText("Odpojen")
            self.SHT3x_status_label.setStyleSheet(f"color: {self.red_hex}")


    # KOMUNIKACE PŘES TCP
    # Zde se nacházejí všechny instrukce, které je tento klient schopný poslat

    def send_shutdown_command(self):
        self.on_command_send_request.emit(SHUTDOWN_DTO)

    def send_shutdown_debug_command(self):
        self.on_command_send_request.emit(SHUTDOWN_DEBUG_DTO)

    def send_default_window_command(self):
        self.on_command_send_request.emit(GET_STATUS_DTO)
        self.on_command_send_request.emit(ENTER_DEFAULT_WINDOW_DTO)

    def send_manual_window_command(self):
        self.on_command_send_request.emit(ENTER_MANUAL_WINDOW_DTO)

    def send_set_clock_style_analog_command(self):
        self.on_command_send_request.emit(DISPLAY_CLOCK_DTO)
        self.on_command_send_request.emit(CHANGE_CLOCK_STYLE_ANALOG_DTO)

    def send_set_clock_style_digital_a_command(self):
        self.on_command_send_request.emit(DISPLAY_CLOCK_DTO)
        self.on_command_send_request.emit(CHANGE_CLOCK_STYLE_DIGITAL_A_DTO)

    def send_set_weather_station_digital_command(self):
        self.on_command_send_request.emit(DISPLAY_WEATHER_STATION_DTO)

    def send_set_accelerometer_artificial_horizon_command(self):
        self.on_command_send_request.emit(DISPLAY_ARTIFICIAL_HORIZON_DTO)

    def send_change_brightness_command(self):
        self.on_command_send_request.emit(create_change_brightness_dto(self.brightness_slider.value()))
        self.current_brightness = self.brightness_slider.value()


