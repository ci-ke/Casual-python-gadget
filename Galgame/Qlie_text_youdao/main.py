# 用法：python main.py <双行文本文件夹路径> ，
# 之后将【网易有道翻译】调到翻译功能，最大化，弹出的python窗口放到屏幕右中部即可点击开始。
# 两个图片在不同的电脑上需要重新截取

import sys, time, tkinter, os
import os.path as op
import pyautogui
import pyperclip

# constant
TRANS_PIC = 'translate.png'
COPY_PIC = 'copy.png'
WAITING_TIME = 0.1
RETRY_TIME = 2

# variable
WIDTH, HEIGHT = pyautogui.size()


# window
class WINDOW:
    root: tkinter.Tk
    label: tkinter.Label


# jump out
class LongRet(Exception):
    pass


def youdao_translate(text: str) -> str:
    if text.isspace():
        return text

    if 'おまんこ' in text:
        return text

    pyperclip.copy(text)
    script_dir_path = op.split(op.realpath(__file__))[0]

    trans_button = pyautogui.locateOnScreen(
        op.join(script_dir_path, TRANS_PIC), confidence=0.8
    )
    if trans_button is None:
        WINDOW.label.config(text='can\'t find translate button in current window')
        raise LongRet

    def step(check: bool = True) -> None:
        pyautogui.click(0.25 * WIDTH, 0.5 * HEIGHT)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.typewrite(['backspace'])

        if check:
            sum_wait = 0
            while True:
                copy_button = pyautogui.locateOnScreen(
                    op.join(script_dir_path, COPY_PIC), confidence=0.8
                )
                if copy_button is None:
                    break
                time.sleep(WAITING_TIME)
                sum_wait += WAITING_TIME
                if sum_wait >= RETRY_TIME:
                    break
        else:
            time.sleep(WAITING_TIME)

        pyautogui.hotkey('ctrl', 'v')

    step()

    sum_wait = 0
    while True:
        copy_button = pyautogui.locateOnScreen(
            op.join(script_dir_path, COPY_PIC), confidence=0.8
        )
        if copy_button is not None:
            break
        time.sleep(WAITING_TIME)
        sum_wait += WAITING_TIME
        if sum_wait >= RETRY_TIME:
            step(False)
            sum_wait = 0

    pyautogui.click(pyautogui.center(copy_button))

    return pyperclip.paste()


def run() -> None:
    try:
        WINDOW.root.title('working...')
        WINDOW.label.config(text='working...')

        start_task()

        WINDOW.label.config(text='done')
        WINDOW.root.title('done')
    except LongRet:
        WINDOW.root.title('pause')
        return


def start_task() -> None:
    dirname = sys.argv[1]
    filelist = os.listdir(dirname)

    for filename in filelist:
        if 'youdao' in filename:
            continue
        savefile = op.splitext(op.basename(filename))[0] + '_youdao.txt'

        writefile = open(savefile, 'w', encoding='utf8')

        with open(op.join(dirname, filename), encoding='utf8') as tmp:
            lines = len(tmp.readlines())

        for num, line in enumerate(open(op.join(dirname, filename), encoding='utf8')):
            WINDOW.label.config(text=f'working on {filename}...{num}/{lines}')
            WINDOW.label.update()

            if line[0] == '○':
                cycle_index = 0

            if cycle_index == 0:
                writefile.write(line)
                if (line[10] == '【') or ('\\ret' in line):
                    translated = None
                else:
                    if line[10] == '「' and line[-2] == '」':
                        translated = '「' + youdao_translate(line[11:-2]) + '」'
                    else:
                        translated = youdao_translate(line[10:-1])
            elif cycle_index == 1:
                if not translated:
                    writefile.write(line)
                else:
                    writefile.write(line[:10] + translated + '\n')
            elif cycle_index in (2, 3):
                writefile.write('\n')
            else:
                writefile.write(line)

            cycle_index += 1


if __name__ == '__main__':
    WINDOW.root = tkinter.Tk()
    WINDOW.root.attributes('-topmost', True)  # 保持置顶
    WINDOW.root.geometry("300x100")
    tkinter.Button(WINDOW.root, text="Run", command=run).pack()
    WINDOW.label = tkinter.Label(WINDOW.root, text='Ready')
    WINDOW.label.pack()
    WINDOW.root.mainloop()
