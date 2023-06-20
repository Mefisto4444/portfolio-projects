import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, TclError
from io import TextIOWrapper
from PIL import Image
from tkinter import Widget
from os import kill
from signal import SIGTERM
import subprocess
import threading
MODES = {
    'creator':{'file':'RAP_bot_creator.py', 'arguments':{'':'', '-v':'', '-a':'','-p':'', '-d':5, '-n':''}}
}

PYTHON_INTERPRETER = 'Path to your python interpreter'

current_mode = 'creator'

def safe_opener(io:TextIOWrapper, var:ctk.IntVar):
    if io is None:
        return ''
    io.close()
    var.set(io.name)


def safe_opener2(io:TextIOWrapper, var:ctk.IntVar):
    if io is None:
        return ''
    var.set(io)


def spinbox_behave(mode:str, delay_var:ctk.IntVar):
    if mode == 'increment':
        delay_var.set(delay_var.get()+1)
    if mode == 'decrement':
        delay_var.set(delay_var.get()-1)
    if delay_var.get() < 5:
        delay_var.set(60)
    elif delay_var.get() > 60:
        delay_var.set(5)

def increment_delay(event:tk.Event, delay_var):
    if event.delta > 0:
        spinbox_behave(mode='increment', delay_var=delay_var)
    if event.delta < 0:
        spinbox_behave(mode='decrement', delay_var=delay_var)

def extract_children(frame:ctk.CTkFrame):
    to_return = []
    for widget in frame.children.values():
        if type(widget) is ctk.CTkFrame:
            to_return + extract_children(widget)
        else:
            to_return.append(widget)
    return to_return

def get_visible_variables():
    visible_variables = []
    for widget in content_frame.grid_slaves():
        if type(widget) is ctk.CTkFrame:
            for nested_widget in extract_children(widget):
                nested_widget:Widget
                if type(nested_widget) is not ctk.CTkCanvas:
                    if type(nested_widget) in [ctk.CTkButton, ctk.CTkCheckBox, ctk.CTkRadioButton, ctk.CTkSwitch, ctk.CTkEntry]:
                        visible_variables.append(nested_widget.cget('textvariable'))
                    if type(nested_widget) in [ctk.CTkCheckBox, ctk.CTkComboBox, ctk.CTkOptionMenu, ctk.CTkRadioButton, ctk.CTkSegmentedButton, ctk.CTkSwitch]:
                        visible_variables.append(nested_widget.cget('variable'))
        else:
            if type(widget) in [ctk.CTkButton, ctk.CTkCheckBox, ctk.CTkRadioButton, ctk.CTkSwitch, ctk.CTkEntry]:
                visible_variables.append(widget.cget('textvariable'))
            if type(widget) in [ctk.CTkCheckBox, ctk.CTkComboBox, ctk.CTkOptionMenu, ctk.CTkRadioButton, ctk.CTkSegmentedButton, ctk.CTkSwitch]:
                visible_variables.append(widget.cget('variable'))
    visible_variables.reverse()
    return [var.get() for var in visible_variables if var is not None]

def get_content_widgtes():
    widgets = []
    for widget in content_frame.grid_slaves():
        if type(widget) is ctk.CTkFrame:
            for nested_widget in extract_children(widget):
                nested_widget:Widget
                try:
                    nested_widget.cget('state')
                    widgets.append(nested_widget)
                except TclError:
                    pass
        else:
            try:
                widget.cget('state')
                widgets.append(widget)
            except TclError:
                pass
    return widgets

def freeze_widgets(widgets, mode='freeze'):
    for widget in widgets:
        if mode == 'freeze':
            widget.configure(state='disabled')
        if mode == 'unfreeze':
            widget.configure(state='normal')

def execute_with_threads(*args, **kwargs):
    def start(current_mode:str):
        global current_process
        current_params_vals = get_visible_variables()
        if current_mode == 'creator':
            current_params_vals = current_params_vals[-1:] + current_params_vals[:-1]
        current_vals =  list(MODES[current_mode]['arguments'].keys())
        params_top_prepare = {}
        for i in range(len(current_vals)):
            params_top_prepare[current_vals[i]] = str(current_params_vals[i])
        params = {key:value for key, value in params_top_prepare.items() if value != ''}
        final_params = []
        for key, value in params.items():
            if key == '' or key == value:
                final_params.append(value)
            else:
                final_params.append(key)
                final_params.append(value)
        current_process = subprocess.Popen([PYTHON_INTERPRETER, MODES[current_mode]['file']]+final_params, stdout=subprocess.PIPE)
        insert_output(process=current_process)
    threading.Thread(target=start, args=args).start()
    run_button.configure(state='disabled')
    stop_button.configure(state='normal')


def insert_output(process:subprocess.Popen):
    global proc_pid
    proc_pid = process.pid
    licznik = 0
    text_output.configure(state='disabled')
    for line in iter(process.stdout.readline, b''):
        text_output.configure(state='normal')
        text_output.insert(ctk.INSERT, line.decode('utf-8'))
        text_output.configure(state='disabled')
        licznik = licznik + 1
    process.stdout.close()
    process.wait()
    run_button.configure(state='normal')
    stop_button.configure(state='disabled')

def stop(pid, signal):
    kill(pid, signal)
    text_output.configure(state='normal')
    text_output.insert(ctk.INSERT, 'Process killed.\n')
    text_output.configure(state='disabled')

def create_accounts_widgets():
    global current_mode
    current_mode = 'creator'

    [widget.grid_forget() for widget in content_frame.winfo_children()]

    verify_label.grid(row=0, column=0)
    verify_check.grid(row=0, column=1)

    api_label.grid(row = 1, column=0)
    api_check.grid(row=1, column=1)

    proxy_label.grid(row=2, column=0)
    proxies_frame.grid(row=2, column=1)
    open_proxies.grid(row=0, column=2, padx=5)
    proxies_path.grid(row=0, column=1)

    delay_label.grid(row=3, column=0)
    delay_frame.columnconfigure((0,1,2), weight=1)
    delay_frame.rowconfigure(0, weight=1)
    delay_frame.grid(row=3, column=1)
    delay_entry.grid(row=0, column=1)
    delay_down.grid(row=0, column=0)
    delay_up.grid(row=0, column=2)

    nsfw_label.grid(row=4, column=0)
    nsfw_check.grid(row=4, column=1)

    output_file_label.grid(row=5, column=0)
    output_file_frame.grid(row=5, column=1)
    output_file_dialog.grid(row=0, column=0)
    output_file_button.grid(row=0, column=1, padx=5)





root = ctk.CTk(fg_color='#2C2B2B')
root.geometry('1200x700')
root.title('Reddit Automation Package')
root.resizable(False,False)
root.iconbitmap('./icons/logo.ico')

root.columnconfigure((0,1,2,3,4,5), weight=1)
root.rowconfigure(0, weight=1)

navigation_frame = ctk.CTkFrame(root)
navigation_frame.grid(row=0, column=0, columnspan=1 ,sticky='nsew')

content_frame = ctk.CTkFrame(master=root)
content_frame.grid(row=0, column=2,columnspan=3, sticky='nsew')
content_frame.grid_propagate(False)
content_frame.columnconfigure((0,1,2), weight=1)
content_frame.rowconfigure((0,1,2,3,4,5), weight=1)


output_label = ctk.CTkFrame(root, bg_color='#2C2B2B', fg_color='#2C2B2B')
output_label.grid(row=0, column=5,sticky='nsew')
output_label.columnconfigure((0,1), weight=1)
output_label.rowconfigure((0,1,2,3), weight=1)

verify_var = ctk.StringVar()
verify_label = ctk.CTkLabel(master=content_frame, text=f'Verify', compound='center')
verify_check = ctk.CTkCheckBox(master=content_frame, variable=verify_var, checkbox_height=20, checkbox_width=20, border_width=18, text='', border_color='#206ca4', onvalue='-v', offvalue='')

api_label = ctk.CTkLabel(content_frame, text='Give accounts access to Reddit API')
api_var = ctk.StringVar()
api_check = ctk.CTkCheckBox(content_frame, variable=api_var, checkbox_height=20, checkbox_width=20, border_width=18, border_color='#206ca4', text='', onvalue='-a', offvalue='')

proxy_label = ctk.CTkLabel(master=content_frame, text = 'Proxies')
proxies_frame = ctk.CTkFrame(master=content_frame, bg_color='#2C2B2B', fg_color='#2C2B2B')
open_proxies_image = ctk.CTkImage(Image.open('./icons/folder.png'))
open_proxies = ctk.CTkButton(master=proxies_frame, command=lambda:safe_opener(filedialog.askopenfile(initialdir='C:\\', defaultextension=['.txt']), var=proxies_var), width=1, image=open_proxies_image, text='')#.......Musi być zamykane!!
proxies_var = ctk.StringVar()
proxies_path = ctk.CTkEntry(master=proxies_frame, textvariable=proxies_var)

delay_label = ctk.CTkLabel(master=content_frame, text='Delay between reach creation\nin minutes')
delay_frame = ctk.CTkFrame(content_frame, bg_color='#2C2B2B', fg_color='#2C2B2B')
delay_frame.columnconfigure((0,1,2), weight=1)
delay_frame.rowconfigure(0, weight=1)
delay_var = ctk.IntVar(value=5)
delay_entry = ctk.CTkEntry(master=delay_frame, textvariable=delay_var)
delay_entry.bind('<MouseWheel>', lambda event:increment_delay(event, delay_var))
delay_down = ctk.CTkButton(master=delay_frame, width=20, height=28, command=lambda:spinbox_behave('decrement', delay_var=delay_var), text='V')
delay_up = ctk.CTkButton(master=delay_frame, width=20, height=28, command=lambda:spinbox_behave('increment', delay_var=delay_var), text='Ʌ')

nsfw_label = ctk.CTkLabel(content_frame, text='Set account as NSFW')
nsfw_var = ctk.StringVar()
nsfw_check = ctk.CTkCheckBox(content_frame, variable=nsfw_var, checkbox_height=20, checkbox_width=20, border_width=18, border_color='#206ca4', text='', onvalue='-n', offvalue='')

output_file_label = ctk.CTkLabel(content_frame, text='Output file location')
output_file_frame = ctk.CTkFrame(content_frame, bg_color='#2C2B2B', fg_color='#2C2B2B')
output_file_frame.columnconfigure((0,1), weight=1)
output_file_frame.rowconfigure(0, weight=1)
output_file_var = ctk.StringVar()
output_file_dialog = ctk.CTkEntry(output_file_frame, textvariable=output_file_var)
output_file_button = ctk.CTkButton(master=output_file_frame, command=lambda:safe_opener2(filedialog.askdirectory(initialdir='C:\\'), var=output_file_var), width=1, image=open_proxies_image, text='')#.......Musi być zamykane!!

create_accounts_widgets()


account_creator_button = ctk.CTkButton(navigation_frame, text='Account creator', command=create_accounts_widgets)
account_creator_button.pack(fill='x', pady = 15)

def forget():
    [widget.grid_forget() for widget in content_frame.winfo_children()]


output_var = ctk.StringVar(value='aaaa\n\n\n\n\n\n\aaaaaaa')
text_output = ctk.CTkTextbox(master=output_label, width=20)
text_output.grid(row=0, column=0, columnspan=4, sticky='ew')
stop_button = ctk.CTkButton(master=output_label, text='STOP', command=lambda:stop(proc_pid, SIGTERM), state='disabled')
stop_button.grid(row=1, column=0)
run_button = ctk.CTkButton(master=output_label, text='START', command= lambda: execute_with_threads(current_mode))
run_button.grid(row=1, column=1)

root.mainloop()