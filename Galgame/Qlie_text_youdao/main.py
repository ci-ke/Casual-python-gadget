# 用法：python main.py <双行文本文件路径> ，
# 之后将【网易有道翻译】调到翻译功能，最大化，弹出的python窗口放到屏幕右中部即可点击开始。
# 两个图片在不同的电脑上需要重新截取

import sys, time, tkinter
import os.path as op
import pyautogui
import pyperclip

# constant
TRANS_PIC = 'translate.png'
COPY_PIC = 'copy.png'
WAITING_TIME = 0.1

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
    pyperclip.copy(text)
    script_dir_path = op.split(op.realpath(__file__))[0]

    trans_button = pyautogui.locateOnScreen(
        op.join(script_dir_path, TRANS_PIC), confidence=0.8
    )
    if trans_button is None:
        WINDOW.label.config(text='can\'t find translate button in current window')
        raise LongRet

    pyautogui.click(0.25 * WIDTH, 0.5 * HEIGHT)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.typewrite(['backspace'])

    while True:
        copy_button = pyautogui.locateOnScreen(
            op.join(script_dir_path, COPY_PIC), confidence=0.8
        )
        if copy_button is None:
            break
        time.sleep(WAITING_TIME)

    pyautogui.hotkey('ctrl', 'v')

    while True:
        copy_button = pyautogui.locateOnScreen(
            op.join(script_dir_path, COPY_PIC), confidence=0.8
        )
        if copy_button is not None:
            break
        time.sleep(WAITING_TIME)

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
    filename = sys.argv[1]
    savefile = op.splitext(op.basename(filename))[0] + '_youdao.txt'

    writefile = open(savefile, 'w', encoding='utf8')

    with open(filename, encoding='utf8') as tmp:
        lines = len(tmp.readlines())

    for num, line in enumerate(open(filename, encoding='utf8')):
        WINDOW.label.config(text=f'working...{num}/{lines}')
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
            assert False, 'impossiable'

        cycle_index += 1


if __name__ == '__main__':
    WINDOW.root = tkinter.Tk()
    WINDOW.root.attributes('-topmost', True)  # 保持置顶
    WINDOW.root.geometry("300x100")
    tkinter.Button(WINDOW.root, text="Run", command=run).pack()
    WINDOW.label = tkinter.Label(WINDOW.root, text='Ready')
    WINDOW.label.pack()
    WINDOW.root.mainloop()
