from PySide6.QtWidgets import QWidget, QHBoxLayout

from helpers.SensorManager import SensorManager

from typing import Optional

from widgets.ClockDesigns.AnalogClock import AnalogClock
from widgets.ClockDesigns.DigitalClockDesignA import DigitalClockDesignA
from widgets.SensorWidgets.WeatherStationWidget import WeatherStationWidget
from widgets.SensorWidgets.ArtificialHorizonWidget import ArtificialHorizonWidget

class ManualModeLayout(QWidget):
    def __init__(self,
                 sensor_manager: SensorManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self.sensor_manager = sensor_manager
        self.current_widget: QWidget | None = None
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.widget_index = 0
        self.clock_style_index = 0
        self.weather_station_style_index = 0
        self.accelerometer_style_index = 0

        self.setClock()

    def setDisplayedWidget(self, index: int):
        prev_index = self.widget_index
        self.widget_index = index

        if index == 0:
            self.setClock()
        elif index == 1:
            self.setWeatherStation()
        elif index == 2:
            self.setAccelerometer()
        else:
            self.widget_index = prev_index

    def changeWidgetStyle(self, widget_index: int, style_index: int):
        if widget_index == 0:
            self.setClock(style_index)
        elif widget_index == 1:
            self.setWeatherStation(style_index)
        elif widget_index == 2:
            self.setAccelerometer(style_index)

    def setClock(self, index: int = -1):
        prev_index = self.clock_style_index
        if index != -1:
            self.clock_style_index = index

        if self.clock_style_index == 0:
            self.setContent(AnalogClock())
        elif self.clock_style_index == 1:
            self.setContent(DigitalClockDesignA())
        else:
            self.clock_style_index = prev_index

    def setWeatherStation(self, index: int = -1):
        prev_index = self.weather_station_style_index
        if index != -1:
            self.weather_station_style_index = index

        if self.weather_station_style_index == 0:
            self.setContent(WeatherStationWidget(self.sensor_manager))
        else:
            self.weather_station_style_index = prev_index

    def setAccelerometer(self, index: int = -1):
        prev_index = self.accelerometer_style_index
        if index != -1:
            self.accelerometer_style_index = index

        if self.accelerometer_style_index == 0:
            self.setContent(ArtificialHorizonWidget(self.sensor_manager))
        else:
            self.accelerometer_style_index = prev_index

    def setContent(self, widget: QWidget):
        if self.current_widget is not None:
            self.root_layout.removeWidget(self.current_widget)
            self.current_widget.deleteLater()
            self.current_widget = None

        self.current_widget = widget
        self.root_layout.addWidget(widget)

