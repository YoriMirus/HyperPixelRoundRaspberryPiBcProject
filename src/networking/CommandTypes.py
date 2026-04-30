from typing import Tuple

from networking.CommandDTO import CommandDTO

SHUTDOWN_DTO = CommandDTO(name="shutdown")
SHUTDOWN_DEBUG_DTO = CommandDTO(name="shutdown_debug")
ENTER_DEFAULT_WINDOW_DTO = CommandDTO(name="enter_default_window")
ENTER_MANUAL_WINDOW_DTO = CommandDTO(name="enter_manual_window")
GET_STATUS_DTO = CommandDTO(name="get_status")
CALIBRATE_GYRO_LEVEL_DTO = CommandDTO(name="calibrate_gyro_level")
CALIBRATE_GYRO_ARTIFICIAL_HORIZON_DTO = CommandDTO(name="calibrate_gyro_artificial_horizon")


def create_status_dto(status_str: str) -> CommandDTO:
    return CommandDTO(name="get_status_response", args=(status_str,))

def create_change_brightness_dto(value: int):
    percent = max(0, min(100, value))
    return CommandDTO(name="change_brightness", args=(str(percent),))

def create_set_virtual_gyro_value_dto(roll: float, pitch: float):
    return CommandDTO(name="set_virtual_gyro_value", args=(str(roll), str(pitch)))

def create_set_virtual_barometer_altitude_dto(altitude_ft: int):
    return CommandDTO(name="set_virtual_barometer_altitude", args=(str(altitude_ft),))

def create_change_displayed_widget_dto(index: int):
    return CommandDTO("change_display", args=(str(index),))

def create_change_display_widget_style_dto(widget_index: int, style_index: int):
    return CommandDTO("change_display_style", args=(str(widget_index), str(style_index),))