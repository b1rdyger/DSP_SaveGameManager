from psutil import process_iter,NoSuchProcess,AccessDenied
import os, glob

def ProcessChecker(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (NoSuchProcess, AccessDenied):
            pass
    return False

def GetLastSaves(folder):
    files = list(filter(os.path.isfile, glob.glob(folder + "\\*")))
    files.sort(key=lambda x: os.path.getmtime(x))
    return files[-3:]

if __name__ == "__main__":
    print('global_functions.py loaded')