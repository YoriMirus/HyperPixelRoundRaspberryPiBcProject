from PySide6.QtWidgets import QWidget, QHBoxLayout

from helpers.SensorManager import SensorManager

from widgets.ClockDesigns.AnalogClock import AnalogClock
from widgets.ClockDesigns.DigitalClockDesignA import DigitalClockDesignA
from widgets.SensorWidgets.WeatherStationWidget import WeatherStationWidget
from widgets.SensorWidgets.ArtificialHorizonWidget import ArtificialHorizonWidget

class ManualModeLayout(QWidget):
    def __init__(self, sensor_manager: SensorManager, parent: QWidget | None=None):
        super().__init__(parent=parent)
        self.sensor_manager = sensor_manager
        self.current_widget: QWidget | None = None
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0,0,0,0)
        self.root_layout.setSpacing(0)
        self.widget_index = 0
        self.clock_style_index = 0
        self.weather_station_style_index = 0
        self.accelerometer_style_index = 0

        self.setClock()

    def setDisplayedWidget(self, index: int):
        prev_index = self.widget_index
        self.widget_index = index
        match index:
            case 0:
                self.setClock()
            case 1:
                self.setWeatherStation()
            case 2:
                self.setAccelerometer()
            case _:
                self.widget_index = prev_index

    def changeWidgetStyle(self, widget_index: int, style_index: int):
        match widget_index:
            case 0:
                self.setClock(style_index)
            case 1:
                self.setWeatherStation(style_index)
            case 2:
                self.setAccelerometer(style_index)

    def setClock(self, index: int = -1):
        prev_index = self.clock_style_index
        if index != -1:
            self.clock_style_index = index

        match self.clock_style_index:
            case 0:
                self.setContent(AnalogClock())
            case 1:
                self.setContent(DigitalClockDesignA())
            case _:
                self.clock_style_index = prev_index

    def setWeatherStation(self, index: int = -1):
        prev_index = self.weather_station_style_index
        if index != -1:
            self.weather_station_style_index = index
        match self.weather_station_style_index:
            case 0:
                self.setContent(WeatherStationWidget(self.sensor_manager))
            case _:
                self.weather_station_style_index = prev_index

    def setAccelerometer(self, index: int = -1):
        prev_index = self.accelerometer_style_index
        if index != -1:
            self.accelerometer_style_index = index
        match self.accelerometer_style_index:
            case 0:
                self.setContent(ArtificialHorizonWidget(self.sensor_manager))
            case _:
                self.accelerometer_style_index = prev_index


    def setContent(self, widget: QWidget):
        # Remove old widget
        if self.current_widget is not None:
            self.root_layout.removeWidget(self.current_widget)
            self.current_widget.deleteLater()
            self.current_widget = None

        # Add new widget
        self.current_widget = widget
        self.root_layout.addWidget(widget)
