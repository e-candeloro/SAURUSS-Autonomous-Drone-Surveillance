""" Little state machine for the alarm """

alarm_state = 0


def enable_alarm():
    global alarm_state
    alarm_state = 1


def disable_alarm():
    global alarm_state
    alarm_state = 0
