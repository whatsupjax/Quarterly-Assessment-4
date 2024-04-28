import tkinter as tk
import sqlite3 as sql
from tkinter import messagebox

class AthleticsRoster:
    def __init__(self):
        self.conn = sql.connect('example.db')
        self.curr = self.conn.cursor()
        
        self.winWelcome = tk.Tk()
        
        self.labWelcome = tk.Label(self.winWelcome, text="Welcome!")
        self.labWelcome.grid()
        
        self.btnStartApp = tk.Button(self.winWelcome, text='Continue to App', command=self.fctnSignLogIn)
        self.btnStartApp.grid()
        
        self.winWelcome.mainloop()
        
    def fctnSignLogIn(self):
        self.winWelcome.destroy()

        self.winSignLogIn = tk.Tk()

        self.labInstructorUsername = tk.Label(self.winSignLogIn, text="Username:")
        self.labInstructorUsername.grid(column=0, row=0)

        self.labInstructorPassword = tk.Label(self.winSignLogIn, text="Password:")
        self.labInstructorPassword.grid(column=0, row=1)

        self.etryInstructorUsername = tk.Entry(self.winSignLogIn)
        self.etryInstructorUsername.grid(column=1, row=0)

        self.etryInstructorPassword = tk.Entry(self.winSignLogIn, show="*")
        self.etryInstructorPassword.grid(column=1, row=1)

        self.btnSubmit = tk.Button(self.winSignLogIn, text='Submit', command=self.checkCredentials)
        self.btnSubmit.grid(columnspan=2)

        self.winSignLogIn.mainloop()

    def checkCredentials(self):
        username = self.etryInstructorUsername.get()
        password = self.etryInstructorPassword.get()

        self.curr.execute("SELECT * FROM instructors WHERE username=? AND password=?", (username, password))
        user = self.curr.fetchone()

        if user:
            self.fctnSelectAthleticTeam()
        else:
            messagebox.showerror("Error", "Invalid username or password")


    def fctnSelectAthleticTeam(self):
        self.winSignLogIn.destroy()

        self.winSelectAthleticTeam = tk.Tk()

        teams = ['TrackAndField', 'Football', 'Golf']

        self.lstbxAthleticTeams = tk.Listbox(self.winSelectAthleticTeam, selectmode=tk.SINGLE)
        for team in teams:
            self.lstbxAthleticTeams.insert(tk.END, team)
        self.lstbxAthleticTeams.pack()

        self.btnConfirmSelection = tk.Button(self.winSelectAthleticTeam, text='Confirm', command=self.confirmSelection)
        self.btnConfirmSelection.pack()

        self.winSelectAthleticTeam.mainloop()

    def confirmSelection(self):
        self.selectedTeam = self.lstbxAthleticTeams.get(self.lstbxAthleticTeams.curselection())
        self.fctnTeamRoster(self.selectedTeam)

    def fctnTeamRoster(self, selectedTeam):
        self.winSelectAthleticTeam.destroy()

        self.winTeamRoster = tk.Tk()
        self.winTeamRoster.title(selectedTeam + " Roster")

        self.btnAthleteStats = tk.Button(self.winTeamRoster, text="View the athlete's information and statistics", command=self.showAthleteStats)
        self.btnAthleteStats.pack()

        self.txtQueryAnswer = tk.Text(self.winTeamRoster)
        self.txtQueryAnswer.pack()

        self.winTeamRoster.mainloop()

    def showAthleteStats(self):
        selected_team = self.selectedTeam
        self.curr.execute("SELECT atlt_fullname, atlt_PR FROM Teams WHERE team=?", (selected_team,))
        athlete_stats = self.curr.fetchall()
    
        if athlete_stats:
            self.txtQueryAnswer.delete('1.0', tk.END)
            for athlete in athlete_stats:
                atlt_fullname, atlt_PR = athlete
                self.txtQueryAnswer.insert(tk.END, f"{atlt_fullname}: {atlt_PR}\n")
        else:
            self.txtQueryAnswer.delete('1.0', tk.END)
            self.txtQueryAnswer.insert(tk.END, "No athletes found for this team.")

        self.btnAthleteStats = tk.Button(self.winTeamRoster, text="View the athlete's information and statistics", command=self.showAthleteStats)
        self.btnAthleteStats.pack()


app = AthleticsRoster()
