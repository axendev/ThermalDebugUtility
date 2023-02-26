import PySimpleGUI as sg
import os.path
import api
from time import sleep

# First the window layout in 2 columns

file_list_column = [
    [
        sg.Text("COM Port"),
        sg.In('COM2', size=(25, 1),  key="-PORT-"),
    ],

    [sg.Text('COM Delay (ms): '), sg.Slider(default_value=200, range=(0, 1000), resolution=200, key='-COM DELAY-', orientation='horizontal')],
    [sg.Button('Connect', enable_events=True, key='-CONNECT-')],
    [
        sg.Multiline(
            autoscroll=True, size=(40, 20), key="-LOG LIST-",

        )
    ],
]

# For now will only show the name of the file that was chosen
agc_regs_column = [
    [sg.Button('Reload', enable_events=True, key='-RELOAD-')],
    [sg.Text("last_pix:"), sg.Text('Do reload', key='-LAST PIX-')],

    [sg.Text("NSHARE (dec):     "),
    sg.In('0', size=(20,1), key='-NSHARE INPUT-'), sg.Button('Set', key='-NSHARE SET-', enable_events=True)],

    [sg.Text("CC_DEBUG (hex):"),
     sg.Column([[sg.In('0', size=(20,1), key='-CUSTOM INPUT-'), sg.Button('Set', key='-CUSTOM SET-', enable_events=True)]])],

    [sg.Text("TEST_VEC_IN (hex):"),
     sg.Column([[sg.In('0', size=(20,1), key='-TEST_VEC_IN INPUT-'), sg.Button('Set', key='-TEST_VEC_IN SET-', enable_events=True)]])],

    [sg.Sizer(h_pixels = 100, v_pixels = 20)],
    [sg.Checkbox('Test mode', enable_events=True, key='-TEST MODE-')],
    [sg.Checkbox('AGC', enable_events=True, key='-AGC EN-')],
    [sg.Checkbox('Color mode', enable_events=True, key='-COLOR-')],
    [sg.Checkbox('Median filter', enable_events=True, key='-FILTER-')],
    [sg.Checkbox('Calibration', enable_events=True, key='-CALIB-')],
    [sg.Checkbox('Correction', enable_events=True, key='-CORRECT-')],
    [sg.Text(size=(40, 1), key="-TOUT-")],

]

adc_regs_column = [
    [sg.Text("ADC Controls")],
    [sg.Button('Reload', enable_events=True, key='-ADC RELOAD-')],

    [sg.Checkbox('Disable Chopper', enable_events=True, key='-ADC CHOP-')],
    [sg.Checkbox('Disable Dither', enable_events=True, key='-ADC DITH-')],
    [sg.Checkbox('High IF Mode', enable_events=True, key='-ADC HIF-')],

[sg.Sizer(h_pixels = 100, v_pixels = 20)],
[sg.Text("Data format:")],
    [sg.Checkbox('OFB', enable_events=True, key='-ADC OFB-'), sg.Checkbox('2s', enable_events=True, key='-ADC 2S-')],

[sg.Sizer(h_pixels = 100, v_pixels = 20)],
[sg.Text("Pattern mode:")],
    [sg.Checkbox('Normal', enable_events=True, key='-ADC NORMAL-')],
[sg.Checkbox('All 0`s', enable_events=True, key='-ADC 0-')],
[sg.Checkbox('All 1`s', enable_events=True, key='-ADC 1-')],
[sg.Checkbox('Ramp', enable_events=True, key='-ADC RAMP-')],
[sg.Checkbox('Toggle', enable_events=True, key='-ADC TOG-')],
[sg.Checkbox('Noise', enable_events=True, key='-ADC NOISE-')],
[sg.Checkbox('Sine', enable_events=True, key='-ADC SIN-')],

]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(agc_regs_column),
        sg.VSeperator(),
        sg.Column(adc_regs_column),
    ]
]

window = sg.Window("AGC Utility", layout, finalize=True)

log_lines = []
def log(text):
    window["-LOG LIST-"].print(text)
    window["-LOG LIST-"].update()


device = api.BoardAPI(log)

def update_AGC_UI():
    last_pix = device.get_last_pix()

    control = device.get_control_params()
    test_mode = control['Test mode']
    agc_state = control['AGC']
    color = control['Color']
    filter_en = control['Filter']
    nshare = control['NSHARE']
    cc_debug = control['CC_DEBUG']

    calib_params = device.get_calib_params()
    calib = calib_params['Calibration']
    correct = calib_params['Correction']
    calib_reg = device.get_calib_reg(False)

    window['-LAST PIX-'].update(str(last_pix))

    window['-TEST MODE-'].update(test_mode)
    window['-AGC EN-'].update(agc_state)
    window['-COLOR-'].update(color)
    window['-FILTER-'].update(filter_en)
    window['-NSHARE INPUT-'].update(nshare)
    window['-CUSTOM INPUT-'].update(f'{cc_debug:X}')
    window['-TEST_VEC_IN INPUT-'].update(f'{calib_reg:X}')

    window['-CALIB-'].update(calib)
    window['-CORRECT-'].update(correct)


def update_ADC_UI():
    chop = device.adc_get_chopper_disable()
    dith = device.adc_get_dither_disable()
    hif = device.adc_get_hif()

    pattern = device.adc_get_pattern()

    format = device.adc_get_dataformat()

    window['-ADC HIF-'].update(hif)
    window['-ADC CHOP-'].update(chop)
    window['-ADC DITH-'].update(dith)

    window['-ADC NORMAL-'].update(False)
    window['-ADC 0-'].update(False)
    window['-ADC 1-'].update(False)
    window['-ADC RAMP-'].update(False)
    window['-ADC TOG-'].update(False)
    window['-ADC NOISE-'].update(False)
    window['-ADC SIN-'].update(False)

    if pattern == 'normal':
        window['-ADC NORMAL-'].update(True)
    elif pattern == 'zeros':
        window['-ADC 0-'].update(True)
    elif pattern == 'ones':
        window['-ADC 1-'].update(True)
    elif pattern == 'toggle':
        window['-ADC TOG-'].update(True)
    elif pattern == 'ramp':
        window['-ADC RAMP-'].update(True)
    elif pattern == 'random':
        window['-ADC NOISE-'].update(True)
    elif pattern == 'sine':
        window['-ADC SIN-'].update(True)

    window['-ADC OFB-'].update(False)
    window['-ADC 2S-'].update(False)
    if format == 'offset':
        window['-ADC OFB-'].update(True)
    elif format == 'compl':
        window['-ADC 2S-'].update(True)



while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    elif event == "-CONNECT-":
        if not device.is_connected():
            print('Do connect')
            if device.connect(values['-PORT-'], float(values['-COM DELAY-'])/1000):
                window['-CONNECT-'].update('Disconnect')
                window['-PORT-'].update()

                print('Connected normally. Reloading all UI elements (wait a moment...)')
                log('Connected normally. Reloading all UI elements (wait a moment...)')

                update_ADC_UI()
                update_AGC_UI()

        else:
            print('Do disconnect')
            device.disconnect()
            window['-CONNECT-'].update('Connect')

    elif event == "-RELOAD-":
        print('Do AGC reload')
        update_AGC_UI()



    elif event == '-TEST MODE-':
        device.set_test_mode(bool(values['-TEST MODE-']))
        print('TEST MODE')

    elif event == '-COLOR-':
        device.set_color_state(bool(values['-COLOR-']))
        print('COLOR')


    elif event == '-AGC EN-':
        device.set_agc_state(bool(values['-AGC EN-']))
        print('AGC EN')

    elif event == '-FILTER-':
        device.set_filter_state(bool(values['-FILTER-']))
        print('FILTER')

    elif event == '-CALIB-':
        print('CALIB')

        device.set_calib_state(bool(values['-CALIB-']))

        calib_reg = device.get_calib_reg(False)
        window['-TEST_VEC_IN INPUT-'].update(f'{calib_reg:X}')

    elif event == '-CORRECT-':
        print('CORRECT')
        device.set_correct_state(bool(values['-CORRECT-']))

        calib_reg = device.get_calib_reg(False)
        window['-TEST_VEC_IN INPUT-'].update(f'{calib_reg:X}')

    elif event == '-NSHARE SET-':
        value = -1

        try:
            value = int(values['-NSHARE INPUT-'])
        except Exception as e:
            print('NSHARE field is not a decimal')
            log(f'Error: NSHARE field is not a decimal')

        if value > 0xFFFF:
            log(f'NSHARE value too much: {value}')
        elif value != -1:
            print('NSHARE SET: ' + str(value))
            device.set_nshare(value)

    elif event == '-CUSTOM SET-':
        value = -1

        try:
            value = int(values['-CUSTOM INPUT-'], 16)
        except Exception as e:
            print('Custom field is not a hex')
            log(f'Error: CC_DEBUG field is not a hex')

        if value > 0xFF:
            log(f'CC_DEBUG value too much: {value}')
        elif value != -1:
            print('CC_DEBUG SET: ' + str(value))
            device.set_cc_debug(value)

    elif event == '-TEST_VEC_IN SET-':
        value = -1

        try:
            value = int(values['-TEST_VEC_IN INPUT-'], 16)
        except Exception as e:
            print('TEST_VEC_IN field is not a hex')
            log(f'Error: TEST_VEC_IN field is not a hex')

        if value > 0xFF:
            log(f'TEST_VEC_IN value too much: {value}')
        elif value != -1:
            print('TEST_VEC_IN SET: ' + str(value))
            device.set_calib_reg(value)

            calib_params = device.get_calib_params(False)
            calib = calib_params['Calibration']
            correct = calib_params['Correction']
            window['-CALIB-'].update(calib)
            window['-CORRECT-'].update(correct)

    elif event == '-ADC HIF-':
        device.adc_set_hif(bool(values['-ADC HIF-']))
        print('ADC HIF')

    elif event == '-ADC CHOP-':
        device.adc_set_chopper_disable(bool(values['-ADC CHOP-']))
        print('ADC CHOP')

    elif event == '-ADC DITH-':
        device.adc_set_dither_disable(bool(values['-ADC DITH-']))
        print('ADC DITH')

    elif event == '-ADC OFB-':
        window['-ADC 2S-'].update(False)
        device.adc_set_dataformat('offset')
        print('ADC Offset binary')

    elif event == '-ADC 2S-':
        window['-ADC OFB-'].update(False)
        device.adc_set_dataformat('compl')
        print('ADC 2s complement')

    elif event == '-ADC NORMAL-':
        window['-ADC 0-'].update(False)
        window['-ADC 1-'].update(False)
        window['-ADC RAMP-'].update(False)
        window['-ADC TOG-'].update(False)
        window['-ADC NOISE-'].update(False)
        window['-ADC SIN-'].update(False)

        device.adc_set_pattern('normal')
        device.adc_enable_pattern(False)
        print('ADC pattern NO')

    elif event == '-ADC 0-':
        window['-ADC NORMAL-'].update(False)
        window['-ADC 1-'].update(False)
        window['-ADC RAMP-'].update(False)
        window['-ADC TOG-'].update(False)
        window['-ADC NOISE-'].update(False)
        window['-ADC SIN-'].update(False)

        device.adc_enable_pattern(True)
        device.adc_set_pattern('zeros')
        print('ADC pattern 0')

    elif event == '-ADC 1-':
        window['-ADC NORMAL-'].update(False)
        window['-ADC 0-'].update(False)
        window['-ADC RAMP-'].update(False)
        window['-ADC TOG-'].update(False)
        window['-ADC NOISE-'].update(False)
        window['-ADC SIN-'].update(False)
        device.adc_enable_pattern(True)
        device.adc_set_pattern('ones')
        print('ADC pattern 1')

    elif event == '-ADC RAMP-':
        window['-ADC NORMAL-'].update(False)
        window['-ADC 0-'].update(False)
        window['-ADC 1-'].update(False)
        window['-ADC TOG-'].update(False)
        window['-ADC NOISE-'].update(False)
        window['-ADC SIN-'].update(False)
        device.adc_enable_pattern(True)
        device.adc_set_pattern('ramp')
        print('ADC pattern RAMP')

    elif event == '-ADC TOG-':
        window['-ADC NORMAL-'].update(False)
        window['-ADC 0-'].update(False)
        window['-ADC 1-'].update(False)
        window['-ADC RAMP-'].update(False)
        window['-ADC NOISE-'].update(False)
        window['-ADC SIN-'].update(False)
        device.adc_enable_pattern(True)
        device.adc_set_pattern('toggle')
        print('ADC pattern TOG')

    elif event == '-ADC NOISE-':
        window['-ADC NORMAL-'].update(False)
        window['-ADC 0-'].update(False)
        window['-ADC 1-'].update(False)
        window['-ADC RAMP-'].update(False)
        window['-ADC TOG-'].update(False)
        window['-ADC SIN-'].update(False)
        device.adc_enable_pattern(True)
        device.adc_set_pattern('random')
        print('ADC pattern NOISE')

    elif event == '-ADC SIN-':
        window['-ADC NORMAL-'].update(False)
        window['-ADC 0-'].update(False)
        window['-ADC 1-'].update(False)
        window['-ADC RAMP-'].update(False)
        window['-ADC TOG-'].update(False)
        window['-ADC NOISE-'].update(False)
        device.adc_enable_pattern(True)
        device.adc_set_pattern('sine')
        print('ADC pattern SIN')

    elif event == "-ADC RELOAD-":
        print('Do ADC reload')
        update_ADC_UI()

window.close()