

#HARDWARE = "SIM"
#HARDWARE = "PICO_SIM"
HARDWARE = "PICO"

#run directly on actual pi pico glowclock
if HARDWARE == "PICO":
    from HAL_pico import sdaPin, sclPin, i2c, ds, stepPin, dirPin, homeSensorPin
    from HAL_pico import okButtonPin, backButtonPin, upButtonPin, downButtonPin, leftButtonPin, rightButtonPin
    from HAL_pico import pixels, uv_pixels, uv_pixels2, num_pixels, num_uv_pixels#, drawBufferForwards, drawBufferBackwards

#intermediate transition mode, runs code on pi pico, but minimizing actual hardware use
if HARDWARE == "PICO_SIM":
    from HAL_pico import sdaPin, sclPin, i2c, stepPin, dirPin, homeSensorPin
    from HAL_pico import okButtonPin, backButtonPin, upButtonPin, downButtonPin, leftButtonPin, rightButtonPin
    from HAL_pico import pixels, uv_pixels, uv_pixels2, num_pixels, num_uv_pixels
    from HAL_sim import ds #, drawBufferForwards, drawBufferBackwards

#todo implement pure sim, runs locally on computer
if HARDWARE == "SIM":
    from HAL_sim import sdaPin, sclPin, i2c, ds, stepPin, dirPin, homeSensorPin
    from HAL_sim import okButtonPin, backButtonPin, upButtonPin, downButtonPin, leftButtonPin, rightButtonPin
    from HAL_sim import pixels, uv_pixels, uv_pixels2, num_pixels, num_uv_pixels #, drawBufferForwards, drawBufferBackwards