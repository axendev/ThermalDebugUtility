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
    [sg.Text("info_Br:"), sg.Text('Do reload', key='-INFO BR-')],
    [sg.Text("info_Cr:"), sg.Text('Do reload', key='-INFO CR-')],
    [sg.Text("info_umin:"), sg.Text('Do reload', key='-INFO UMIN-')],
    [sg.Text("info_umax:"), sg.Text('Do reload', key='-INFO UMAX-')],
    [sg.Text("last_pix:"), sg.Text('Do reload', key='-LAST PIX-')],
    [sg.Text("\nNSHARE:"),
     sg.Column([[sg.Slider(enable_events=True, key='-NSHARE SLIDER-', orientation='horizontal', range=(0, 0xFFFF), resolution=0xF)],
                [sg.In('0', size=(20,1), key='-NSHARE INPUT-'), sg.Button('Set', key='-NSHARE SET-', enable_events=True)]])],
    [sg.Sizer(0, 20)],
    [sg.Text("CUSTOM:"),
     sg.Column([[sg.In('0', size=(20,1), key='-CUSTOM INPUT-'), sg.Button('Set', key='-CUSTOM SET-', enable_events=True)]])],
    [sg.Sizer(h_pixels = 100, v_pixels = 20)],
    [sg.Checkbox('Test mode', enable_events=True, key='-TEST MODE-')],
    [sg.Checkbox('AGC', enable_events=True, key='-AGC EN-')],
    [sg.Checkbox('Manual', enable_events=True, key='-AGC MANUAL U-')],
    [sg.Checkbox('Median filter', enable_events=True, key='-FILTER-')],
    [sg.Text("\nUMIN:"), sg.Slider(enable_events=True, key='-UMIN SLIDER-', orientation='horizontal', range=(0, 0xFFFF), resolution=16)],
    [sg.Text("\nUMAX:"), sg.Slider(enable_events=True, key='-UMAX SLIDER-', orientation='horizontal', range=(0, 0xFFFF), resolution=16)],
    [sg.Text(size=(40, 1), key="-TOUT-")],

]

adc_regs_column = [
    [sg.Text("ADC Controls")],
    [sg.Button('Reload', enable_events=True, key='-ADC RELOAD-')],

    [sg.Checkbox('Disable Chopper', enable_events=True, key='-ADC CHOP-')],
    [sg.Checkbox('Disable Dither', enable_events=True, key='-ADC DITH-')],
    [sg.Checkbox('High IF Mode', enable_events=True, key='-ADC HIF-')],

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
window['-UMIN SLIDER-'].bind('<ButtonRelease-1>', ' Release')
window['-UMAX SLIDER-'].bind('<ButtonRelease-1>', ' Release')
window['-NSHARE SLIDER-'].bind('<ButtonRelease-1>', ' Release')

log_lines = []
def log(text):
    window["-LOG LIST-"].print(text)


device = api.BoardAPI(log)

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

        else:
            print('Do disconnect')
            device.disconnect()
            window['-CONNECT-'].update('Connect')

    elif event == "-RELOAD-":
        print('Do reload')
        last_pix = device.get_last_pix()
        umax, umin = device.get_info_agc_lvls()
        umax_c, umin_c = device.get_contr_agc_lvls()
        br, cr = device.get_brcr()

        control = device.get_control_params()
        test_mode = control['Test mode']
        agc_state = control['AGC']
        agc_manual_u_state = control['AGC Manual']
        filter_en = control['Filter']
        nshare = control['NSHARE']

        window['-INFO BR-'].update(str(br))
        window['-INFO CR-'].update(str(cr))
        window['-LAST PIX-'].update(str(last_pix))
        window['-INFO UMIN-'].update(str(umin))
        window['-INFO UMAX-'].update(str(umax))

        window['-TEST MODE-'].update(test_mode)
        window['-AGC EN-'].update(agc_state)
        window['-AGC MANUAL U-'].update(agc_manual_u_state)
        window['-FILTER-'].update(filter_en)

        window['-NSHARE SLIDER-'].update(nshare)
        window['-NSHARE INPUT-'].update(nshare)
        window['-UMIN SLIDER-'].update(umin_c)
        window['-UMAX SLIDER-'].update(umax_c)

    elif event == "-ADC RELOAD-":
        print('Do reload')
        chop = device.adc_get_chopper_disable()
        dith = device.adc_get_dither_disable()
        hif = device.adc_get_hif()

        window['-ADC HIF-'].update(hif)
        window['-ADC CHOP-'].update(chop)
        window['-ADC DITH-'].update(dith)

    elif event == '-TEST MODE-':
        device.set_test_mode(bool(values['-TEST MODE-']))
        print('ADC HIF')

    elif event == '-ADC HIF-':
        device.adc_set_hif(bool(values['-ADC HIF-']))
        print('ADC HIF')

    elif event == '-ADC CHOP-':
        device.adc_set_chopper_disable(bool(values['-ADC CHOP-']))
        print('ADC CHOP')

    elif event == '-ADC DITH-':
        device.adc_set_dither_disable(bool(values['-ADC DITH-']))
        print('ADC DITH')


    elif event == '-AGC EN-':
        device.set_agc_state(bool(values['-AGC EN-']))
        print('AGC EN')

    elif event == '-AGC MANUAL U-':
        device.set_agc_manual_u_state(bool(values['-AGC MANUAL U-']))
        print('AGC MANUAL U')

    elif event == '-FILTER-':
        device.set_filter_state(bool(values['-FILTER-']))
        print('FILTER')

    elif event == '-UMIN SLIDER- Release' or event == '-UMAX SLIDER- Release':
        print('UMIN UMAX SLIDER')
        umin = int(values['-UMIN SLIDER-'])
        umax = int(values['-UMAX SLIDER-'])
        device.set_contr_agc_lvls(umin, umax)

    elif event == '-NSHARE SLIDER- Release':
        print('NSHARE SLIDER')
        nshare = int(values['-NSHARE SLIDER-'])
        window['-NSHARE INPUT-'].update(nshare)
        device.set_nshare(nshare)

    elif event == '-NSHARE SET-':
        nshare = int(values['-NSHARE INPUT-'])

        if nshare > 0xFFFF:
            log(f'NSHARE value too much: {nshare}')
        else:
            print('NSHARE SET: ' + str(nshare))
            window['-NSHARE SLIDER-'].update(nshare)
            device.set_nshare(nshare)

    elif event == '-CUSTOM SET-':
        value = -1

        try:
            value = int(values['-CUSTOM INPUT-'], 16)
        except Exception as e:
            print('Custom field is not a hex')

        if value > 0xFFFF:
            log(f'CUSTOM value too much: {value}')
        elif value == -1:
            print('Value mistake')
            window['-CUSTOM INPUT-'].update('0')
        else:
            print('CUSTOM SET: ' + str(value))
            device.set_custom_AGC_reg(10, value)


    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
               and f.lower().endswith((".png", ".gif"))
        ]
        window["-FILE LIST-"].update(fnames)

    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(filename=filename)
        except:
            pass

window.close()