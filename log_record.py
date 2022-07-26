import datetime


def logs(text, pr=True, log=True):
    '''log and print texts'''
    # pr - print logs, log - write logs in files
    if log:
        with open("logs.txt", "a") as f:
            f.write(f'{datetime.datetime.now().strftime("%H:%M:%S:%f %d/%m/%Y")} | {text}\n')
    if pr:
        print(text)
    return
