# DSP_SaveGameManager
This is an SaveGameManger for DSP Nebula Multiplayer.

To use this script its neccasary to install the following DSP Plugin.
- ScheduledSave

Please create a new folder in the Documents\DSPGAME directory or change the paths yourself.
See config.ini, possible parameters

DSPGAME_PROCESS = DSPGAME.exe 
 - Set the DSPGAME Process Name, if it changes in the future

FOLDER_WATCHDOG = False 
 - If True: The programm watches for changes in DSP_SAVEGAME_FOLDER and react to the events 

DSP_SAVEGAME_FOLDER = "C:\Users\apwxv\Documents\Dyson Sphere Program\Save"
 - Set the Original Savegamefolder

BACKUP_SAVE_PATH = "C:\Users\apwxv\Documents\Dyson Sphere Program\save_backup"
 - Set the Backup Savegamefolder

COPY_FROM_SAVE_TO_ORIGINAL = True
 - if True: copies the Data from DSP_SAVEGAME_FOLDER back to "Save" folder

COUNTER_TO_LOGOFF = 6  # int
 - set the ammount of Saves before the system shut off
