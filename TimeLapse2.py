# Created by Wayne Porter and Valerii Zalit

from ..Script import Script


class TimeLapse2(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Time Lapse 2",
            "key": "TimeLapse2",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "enable_trigger_command":
                {
                    "label": "Trigger command",
                    "description": "G-code command used to trigger camera.",
                    "type": "bool",
                    "default_value": false
                },
				"trigger_command":
                {
                    "label": "Trigger camera command",
                    "description": "G-code command used to trigger camera.",
                    "type": "str",
                    "default_value": "M240",
					"enabled": "enable_trigger_command"
                },
                "trigger_pause_length":
                {
                    "label": "Pause length",
                    "description": "How long to wait (in ms) after camera was triggered.",
                    "type": "int",
                    "default_value": 700,
                    "minimum_value": 0,
                    "unit": "ms",
					"enabled": "enable_trigger_command"
                },
                "park_print_head":
                {
                    "label": "Print head parking",
                    "description": "Make parking of the print head.",
                    "type": "bool",
                    "default_value": false
                },
                "head_park_x":
                {
                    "label": "Print head parking X",
                    "description": "What X location does the head move to for photo.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
					"minimum_value": 0,
                    "enabled": "park_print_head"
                },
                "head_park_y":
                {
                    "label": "Print head parking Y",
                    "description": "What Y location does the head move to for photo.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 190,
					"minimum_value": 0,
                    "enabled": "park_print_head"
                },
				"park_feed_rate":
                {
                    "label": "Parking feed rate",
                    "description": "How fast does the head move to the parking coordinates.",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 9000,
					"minimum_value": 0,
                    "enabled": "park_print_head"
                },
				"enable_head_rebounds":
                {
                    "label": "Print head rebound",
                    "description": "A rebound is needed in order to move out of the shutter button of the camera so as not to cause serial shooting.",
                    "type": "enum",
                    "options": {"enable_rebounds":"Don't rebounds","rebounds_left":"Rebound left","rebounds_right":"Rebound right"},
                    "default_value": "enable_rebounds",
                    "enabled": "park_print_head"
                },
				"pause_rebounds":
                {
                    "label": "Pause before rebound",
                    "description": "After this pause, the print head will rebound.",
                    "type": "int",
                    "default_value": 500,
                    "minimum_value": 0,
                    "unit": "ms",
                    "enabled": "enable_head_rebounds != 'enable_rebounds' and park_print_head == 1"
                },
				 "head_rebounds":
                {
                    "label": "Rebound length",
                    "description": "Usually 1-2 mm is enough for a rebound.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 2,
                    "minimum_value": 0,
					"enabled": "enable_head_rebounds != 'enable_rebounds' and park_print_head == 1"
                },
				"pause_park":
                {
                    "label": "Parking pause length",
                    "description": "How long to wait (in ms) after camera was triggered.",
                    "type": "int",
                    "default_value": 700,
                    "minimum_value": 0,
                    "unit": "ms",
					"enabled": "park_print_head"
                },
				"enable_retraction":
                {
                    "label": "Retraction",
                    "description": "Enable filament retraction.",
                    "type": "bool",
                    "default_value": false
                },
				"retraction_amount":
                {
                    "label": "Retraction length",
                    "description": "How much filament must be retracted.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 6,
					"minimum_value": 0,
					"enabled": "enable_retraction"
                },
				"retraction_speed":
                {
                    "label": "Retraction speed",
                    "description": "How fast to retract the filament.",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 25,
					"minimum_value": 0,
					"enabled": "enable_retraction"
                }
            }
        }"""

    def execute(self, data):
        enable_trigger_command = self.getSettingValueByKey("enable_trigger_command")
        park_print_head = self.getSettingValueByKey("park_print_head")
        enable_head_rebounds = self.getSettingValueByKey("enable_head_rebounds")
        enable_retraction = self.getSettingValueByKey("enable_retraction")

        trigger_command = self.getSettingValueByKey("trigger_command")
        trigger_pause_length = self.getSettingValueByKey("trigger_pause_length")
        x_park = self.getSettingValueByKey("head_park_x")
        y_park = self.getSettingValueByKey("head_park_y")
        park_feed_rate = self.getSettingValueByKey("park_feed_rate")
        pause_rebounds = self.getSettingValueByKey("pause_rebounds")
        head_rebounds = self.getSettingValueByKey("head_rebounds")
        pause_park = self.getSettingValueByKey("pause_park")
        retraction_amount = self.getSettingValueByKey("retraction_amount")
        retraction_speed = self.getSettingValueByKey("retraction_speed")

        gcode_to_append = ";TimeLapse Begin\n"
        last_x = 0
        last_y = 0

        if enable_retraction and park_print_head:
            gcode_to_append += self.putValue(G = 91) + ";Switch to relative positioning\n"
        if enable_retraction and park_print_head:
            gcode_to_append += self.putValue(G=1, F=retraction_speed * 60, E=-retraction_amount) + " ;Park print head\n"
        if enable_retraction and park_print_head:
            gcode_to_append += self.putValue(G = 90) + ";Switch to relative positioning\n"

        if park_print_head:
            gcode_to_append += self.putValue(G=1, F=park_feed_rate,X=x_park, Y=y_park) + " ;Park print head\n"
        if park_print_head:
            gcode_to_append += self.putValue(M=400) + " ;Wait for moves to finish\n"

        if park_print_head and enable_head_rebounds != "enable_rebounds":
            gcode_to_append += self.putValue(G=4, P=pause_rebounds) + " ;Wait for camera\n"
        if park_print_head and enable_head_rebounds != "enable_rebounds" and enable_head_rebounds == "rebounds_left":
            gcode_to_append += self.putValue(G=1, F=park_feed_rate / 10, X=x_park - head_rebounds, Y=y_park) + " ;Park print head\n"
        if park_print_head and enable_head_rebounds != "enable_rebounds" and enable_head_rebounds == "rebounds_right":
            gcode_to_append += self.putValue(G=1, F=park_feed_rate / 10, X=x_park + head_rebounds, Y=y_park) + " ;Park print head\n"
        if park_print_head and enable_head_rebounds != "enable_rebounds":
            gcode_to_append += self.putValue(M=400) + " ;Wait for moves to finish\n"

        if park_print_head and (enable_trigger_command==0):
            gcode_to_append += self.putValue(G=4, P=pause_park) + " ;Wait for camera\n"

        if enable_trigger_command and (park_print_head==0):
            gcode_to_append += self.putValue(M=400) + " ;Wait for moves to finish\n"
        if enable_trigger_command:
            gcode_to_append += trigger_command + " ;Snap Photo\n"
        if enable_trigger_command:
            gcode_to_append += self.putValue(G=4, P=trigger_pause_length) + " ;Wait for camera\n"


        for idx, layer in enumerate(data):
            for line in layer.split("\n"):
                if self.getValue(line, "G") in {0, 1}:  # Track X,Y location.
                    last_x = self.getValue(line, "X", last_x)
                    last_y = self.getValue(line, "Y", last_y)
            # Check that a layer is being printed
            lines = layer.split("\n")
            for line in lines:
                if ";LAYER:" in line:
                    layer += gcode_to_append

                    layer += "G0 X%s Y%s F%s\n " % (last_x, last_y, park_feed_rate,)

                    data[idx] = layer
                    break
        return data
