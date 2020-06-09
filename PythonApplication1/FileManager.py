import inspect
import os
import sys
import json
import pickle
import secrets

def CheckFolderAccessableFromExecutingScript(folder):
    f = folder
    path = GetExecutingScriptDir()
    path = path +'\\'+ f +'\\'
    return os.path.isdir(path)

def OpenFile(path):
        return open(path, 'rU').read().splitlines()

def OpenJson(path):
    file = OpenFile(path)
    json_list =[]
    for record in file:
        json_list.append(json.loads(record))

    return json_list

def SaveJson(data, path, name):
    if name == None:
        hash = secrets.token_hex(nbytes=4)
        fname = 'new_json_file'+hash
    else:
        fname = name

    completeName = os.path.join(path, fname+'.json')   

    with open(completeName, 'w+') as outfile:
        json.dump(data, outfile)

def SavePickle(model, path, name):
    if name == None:
        hash = secrets.token_hex(nbytes=4)
        fname = 'new_model_file'+hash
    else:
        fname = name

    completeName = os.path.join(path, fname+'.pickle')   

    with open(completeName, 'wb') as outfile:
        pickle.dump(model, outfile)
        outfile.close()

def LoadPickle(path, name):
    completeName = os.path.join(path, name+'.pickle')

    with open(completeName, 'rb') as outfile:
        model = pickle.load(outfile)
        outfile.close()
    return model


def GetExecutingScriptDir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(GetExecutingScriptDir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)




if __name__ == '__main__':
    pass