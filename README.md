# DSP_SaveGameManager
This is an SaveGameManger for DSP Nebula Multiplayer.

To use this script its neccasary to install the following Plugin.
- ScheduledSave

Please create a new folder in the DSP root directory or change the paths yourself.

RAW_DISK_SAVE_PATH=rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\Save'
SSD_SAVE_PATH=rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\save_backup'


In the main-function u can set some features:
COPY_TO_RAMDISK = True # boolean
 - if True:
      copies the Data from SSD_SAVE_PATH back to "Save" folder
LOGOFF = False # boolean
  - if True:
    Shutdown the entire System after the ammount of "ScheduledSaves"

COUNTER_TO_LOGOFF = 6  # int
  - set the ammount of Saves before the system shut off
  
  
 
