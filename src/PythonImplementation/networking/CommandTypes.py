from typing import Tuple

from networking.CommandDTO import CommandDTO

SHUTDOWN_DTO = CommandDTO(name="shutdown")
SHUTDOWN_DEBUG_DTO = CommandDTO(name="shutdown_debug")
ENTER_DEFAULT_WINDOW_DTO = CommandDTO(name="enter_default_window")
ENTER_MANUAL_WINDOW_DTO = CommandDTO(name="enter_manual_window")
CHANGE_CLOCK_STYLE_ANALOG_DTO = CommandDTO(name="change_clock_style", args=tuple("0"))
CHANGE_CLOCK_STYLE_DIGITAL_A_DTO = CommandDTO(name="change_clock_style", args=tuple("1"))
DISPLAY_CLOCK_DTO = CommandDTO(name="change_display", args=tuple("0"))
DISPLAY_WEATHER_STATION_DTO = CommandDTO(name="change_display", args=tuple("1"))
DISPLAY_ARTIFICIAL_HORIZON_DTO = CommandDTO(name="change_display", args=tuple("2"))

