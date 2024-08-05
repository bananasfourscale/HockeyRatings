import tkinter as tk
from tkinter.ttk import Progressbar
from Weights import team_weights, goalie_weights, forward_weights, \
    defenseman_weights, update_team_weights, update_goalie_weights, \
    update_forward_weights, update_defenseman_weights

main_window = tk.Tk()


widget_links = {
    'main-frame' : '.main-frame1',
    'welcome-text' : '.main-frame1.welcome-textbox',
    'eye-test-text' : '.main-frame1.eye-test-textbox',
    'eye-test-entry' : '.main-frame1.eye-test-file-entry',
    'run-button' : '.main-frame1.run-button',
    'progress-frame' : '.progress-frame',
    'progress-bar' : '.progress-frame.progress-bar'
}


def get_main_window() -> tk.Tk:
    return main_window


def get_widget(widget_name : str=''):
    try:
        return main_window.nametowidget(widget_links[widget_name])
    except KeyError:
        return ''
    

def display_error_window(error_text : str='', error_code : int=0):
    error_window = tk.Tk()
    height=error_window.winfo_screenheight()/4
    width=error_window.winfo_screenwidth()/4
    error_window.geometry('{}x{}'.format(int(width), int(height)))
    error_frame = tk.Frame(master=error_window, name="error-frame1",
        background="red", width=error_window.winfo_screenwidth(),
        height=error_window.winfo_screenheight()
    )
    error_text = tk.Label(master=error_frame, name="error-textbox",
        text=error_text + ":" + str(error_code), background="red",
        foreground="black", 
    )
    error_text.pack()
    error_frame.pack(fill=tk.BOTH, expand=True)
    tk.mainloop()
    

def check_team_weights(weight_list : list=[]):
    if sum(weight_list) != 1.0:
        display_error_window("Weights do not sum to 1.0", -2)
    update_team_weights(weight_list)


def check_goalie_weights(weight_list : list=[]):
    if sum(weight_list) != 1.0:
        display_error_window("Weights do not sum to 1.0", -2)


def edit_team_weights_window():
    team_weight_window = tk.Tk()
    height=team_weight_window.winfo_screenheight()/4
    width=team_weight_window.winfo_screenwidth()/4
    team_weight_window.geometry('{}x{}'.format(int(width), int(height)))

    team_weights_frame = tk.Frame(master=team_weight_window, name="main-frame1",
        background="black", width=team_weight_window.winfo_screenwidth(),
        height=team_weight_window.winfo_screenheight()/2
    )

    # clutch weight pack
    clutch_weight_text = tk.Label(master=team_weights_frame,
        name="clutch-textbox", text="Clutch Rating", background="black",
        foreground="white", 
    )
    clutch_weight_text.pack()
    clutch_weight_entry = tk.Entry(master=team_weights_frame,
        name="clutch-entry"
    )
    clutch_weight_entry.insert(0, team_weights['clutch_weight'])
    clutch_weight_entry.pack()

    # defensive weight pack
    defensive_weight_text = tk.Label(master=team_weights_frame,
        name="defensive-textbox", text="Defensive Rating", background="black",
        foreground="white", 
    )
    defensive_weight_text.pack()
    defensive_weight_entry = tk.Entry(master=team_weights_frame,
        name="defensive-entry"
    )
    defensive_weight_entry.insert(0, team_weights['defensive_weight'])
    defensive_weight_entry.pack()

    # offensive weight pack
    offensive_weight_text = tk.Label(master=team_weights_frame,
        name="offensive-textbox", text="Offensive Rating", background="black",
        foreground="white", 
    )
    offensive_weight_text.pack()
    offensive_weight_entry = tk.Entry(master=team_weights_frame,
        name="offensive-entry"
    )
    offensive_weight_entry.insert(0, team_weights['offensive_weight'])
    offensive_weight_entry.pack()

    # recent form pack
    recent_form_weight_text = tk.Label(master=team_weights_frame,
        name="recent-form-textbox", text="Recent Form Rating", background="black",
        foreground="white", 
    )
    recent_form_weight_text.pack()
    recent_form_weight_entry = tk.Entry(master=team_weights_frame,
        name="recent-form-entry"
    )
    recent_form_weight_entry.insert(0, team_weights['recent_form_weight'])
    recent_form_weight_entry.pack()

    # sos weight pack
    sos_weight_text = tk.Label(master=team_weights_frame,
        name="sos-textbox", text="Strength of Schedule Rating",
        background="black", foreground="white"
    )
    sos_weight_text.pack()
    sos_weight_entry = tk.Entry(master=team_weights_frame,
        name="sos-entry"
    )
    sos_weight_entry.insert(0, team_weights['strength_of_schedule_weight'])
    sos_weight_entry.pack()

    # submit button
    submit_button = tk.Button(master=team_weights_frame, name="submit-button",
        text="Submit",
        command=lambda : check_team_weights(
            [
                float(clutch_weight_entry.get()),
                float(defensive_weight_entry.get()),
                float(offensive_weight_entry.get()),
                float(recent_form_weight_entry.get()),
                float(sos_weight_entry.get())
            ]
        ),
        background='orange', foreground='black'
    )
    submit_button.pack()

    team_weights_frame.pack(expand=True, fill=tk.BOTH)
    team_weight_window.update()


def edit_goalie_weights_window():
    goalie_weight_window = tk.Tk()
    height=goalie_weight_window.winfo_screenheight()/4
    width=goalie_weight_window.winfo_screenwidth()/4
    goalie_weight_window.geometry('{}x{}'.format(int(width), int(height)))

    goalie_weights_frame = tk.Frame(master=goalie_weight_window,
        name="main-frame1", background="black",
        width=goalie_weight_window.winfo_screenwidth(),
        height=goalie_weight_window.winfo_screenheight()/2
    )

    # clutch weight pack
    utilization_weight_text = tk.Label(master=goalie_weights_frame,
        name="utilization-textbox", text="Utilization Rating",
        background="black", foreground="white", 
    )
    utilization_weight_text.pack()
    utilization_weight_entry = tk.Entry(master=goalie_weights_frame,
        name="utilization-entry"
    )
    utilization_weight_entry.insert(0, goalie_weights['utilization_weight'])
    utilization_weight_entry.pack()

    # discipline weight pack
    discipline_weight_text = tk.Label(master=goalie_weights_frame,
        name="discipline-textbox", text="Discipline Rating", background="black",
        foreground="white", 
    )
    discipline_weight_text.pack()
    discipline_weight_entry = tk.Entry(master=goalie_weights_frame,
        name="discipline-entry"
    )
    discipline_weight_entry.insert(0, goalie_weights['discipline_weight'])
    discipline_weight_entry.pack()

    # save_percentage weight pack
    save_percentage_weight_text = tk.Label(master=goalie_weights_frame,
        name="save_percentage-textbox", text="Save% Rating", background="black",
        foreground="white", 
    )
    save_percentage_weight_text.pack()
    save_percentage_weight_entry = tk.Entry(master=goalie_weights_frame,
        name="save-percentage-entry"
    )
    save_percentage_weight_entry.insert(0,
        goalie_weights['save_percentage_weight'])
    save_percentage_weight_entry.pack()

    # goals against pack
    goals_against_weight_text = tk.Label(master=goalie_weights_frame,
        name="goals-against-textbox", text="Goals Against Rating",
        background="black", foreground="white", 
    )
    goals_against_weight_text.pack()
    goals_against_weight_entry = tk.Entry(master=goalie_weights_frame,
        name="goals-against-entry"
    )
    goals_against_weight_entry.insert(0, goalie_weights['goals_against_weight'])
    goals_against_weight_entry.pack()

    # save_consitency weight pack
    save_consitency_weight_text = tk.Label(master=goalie_weights_frame,
        name="save_consitency-textbox", text="Save Consitency Rating",
        background="black", foreground="white"
    )
    save_consitency_weight_text.pack()
    save_consitency_weight_entry = tk.Entry(master=goalie_weights_frame,
        name="save_consitency-entry"
    )
    save_consitency_weight_entry.insert(0,
        goalie_weights['save_consitency_weight'])
    save_consitency_weight_entry.pack()

    # submit button
    submit_button = tk.Button(master=goalie_weights_frame, name="submit-button",
        text="Submit",
        command=lambda : check_goalie_weights(
            [
                float(utilization_weight_entry.get()),
                float(discipline_weight_entry.get()),
                float(save_percentage_weight_entry.get()),
                float(goals_against_weight_entry.get()),
                float(save_consitency_weight_entry.get())
            ]
        ),
        background='orange', foreground='black'
    )
    submit_button.pack()

    goalie_weights_frame.pack(expand=True, fill=tk.BOTH)
    goalie_weight_window.update()


def edit_forward_weights_window():
    pass


def edit_defensemen_weights_window():
    pass


def construct_main_menu(run_command):

    # Add the main frame with staring info
    main_menu_frame = tk.Frame(master=main_window, name="main-frame1",
        background="black", width=main_window.winfo_screenwidth(),
        height=main_window.winfo_screenheight()/2
    )

    # Label with the opening text
    welcome_text = tk.Label(master=main_menu_frame, name="welcome-textbox",
        text="Welcome To Hockey Ratings", background="black",
        foreground="white", 
    )
    welcome_text.pack()

    # Add some text boxes for file inputs
    eye_test_text = tk.Label(master=main_menu_frame, name="eye-test-textbox",
        text="Enter the full path of the Eye Test File", background="black",
        foreground="white", 
    )
    eye_test_text.pack()
    eye_test_file_entry = tk.Entry(master=main_menu_frame,
        name="eye-test-file-entry")
    eye_test_file_entry.insert(0, "player_eye_test.csv")
    eye_test_file_entry.pack()

    # Run button
    run_button = tk.Button(master=main_menu_frame, name="run-button",
        text="Run Main Stats Engine", command=run_command, background='green',
        foreground='white'
    )
    run_button.pack()

    # Finalize the frame by packing it into the window
    main_menu_frame.pack(fill=tk.BOTH, expand=True)
    main_menu_frame.update()

    # Frame for buttons to call up Weight Edits
    weight_button_frame = tk.Frame(master=main_window,
        name='weight-button-frame', background="black",
        width=main_window.winfo_screenwidth(),
        height=main_window.winfo_screenheight()/2
    )
    weight_button_frame.pack()
    team_weight_button = tk.Button(master=weight_button_frame,
        name="team-weight-button", text="Edit Team Weights",
        command=edit_team_weights_window, background='blue', foreground='white'
    )
    team_weight_button.pack()
    goalie_weight_button = tk.Button(master=weight_button_frame,
        name="goalie-weight-button", text="Edit Goalie Weights",
        command=edit_goalie_weights_window, background='blue',
        foreground='white'
    )
    goalie_weight_button.pack()
    forward_weight_button = tk.Button(master=weight_button_frame,
        name="forward-weight-button", text="Edit Forward Weights",
        command=edit_forward_weights_window, background='blue',
        foreground='white'
    )
    forward_weight_button.pack()
    defensemen_weight_button = tk.Button(master=weight_button_frame,
        name="defensemen-weight-button", text="Edit Defensemen Weights",
        command=edit_defensemen_weights_window, background='blue',
        foreground='white'
    )
    defensemen_weight_button.pack()
    weight_button_frame.pack(fill=tk.BOTH, expand=True)
    weight_button_frame.update()


def add_progress_frame():
    progress_frame = tk.Frame(master=main_window, name="progress-frame",
        background="black", width=main_window.winfo_screenwidth(),
        height=main_window.winfo_screenheight()/2
    )
    game_data_progress_bar = Progressbar(master=progress_frame,
        name="progress-bar", orient='horizontal', value=0,
        mode='determinate', length=main_window.winfo_width()*.80)
    game_data_progress_bar.pack()
    progress_frame.pack(fill=tk.BOTH, expand=True)
    progress_frame.update()


def close_progress_frame(): 
    main_window.nametowidget(widget_links['progress-bar']).pack_forget()
    main_window.nametowidget(widget_links['progress-bar']).destroy()


def update_progress_bar(value):
    progress_bar = main_window.nametowidget(widget_links['progress-bar'])
    progress_bar['value'] = value
    progress_bar.update()


if __name__ == "__main__":

    main_window = tk.Tk()
    height=main_window.winfo_screenheight()/2
    width=main_window.winfo_screenwidth()/2
    main_window.geometry('{}x{}'.format(int(width), int(height)))
    construct_main_menu(main_window)
    print(main_window.winfo_children())
    tk.mainloop()