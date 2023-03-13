import os, re, struct
from typing import List

# 使用说明
# Out：从 scenario_jp 转入 script_jp, selection_jp
# In：从 senario_jp, script_cn, selection_cn 转入 scenario_done
# Out_CNed：
#   从 scenario_cned 转入 script_cned, selection_cned
#   从 script_jp, selection_jp, script_cned, selection_cned 转入 script_merge, selection_merge

# 原始的scenario
original_scenario = 'scenario_jp'
processed_scenario = 'scenario_done'

extracted_script = 'script_jp'
translated_script = 'script_cn'

extracted_selection = 'selection_jp'
translated_selection = 'selection_cn'

# 如果要提取汉化过的scenario
original_scenario_cned = 'scenario_cned'

extracted_script_cned = 'script_cned'
extracted_selection_cned = 'selection_cned'

merged_script = 'script_merged'
merged_selection = 'selection_merged'

# 遍历文件夹，返回文件列表
def walk(adr: str) -> List[str]:
    mylist = []
    for root, _, files in os.walk(adr):
        for name in files:
            adrlist = os.path.join(root, name)
            mylist.append(adrlist)
    return mylist


class Text_out:
    # 将4字节byte转换成整数
    @staticmethod
    def byte2int(byte: bytes) -> int:
        long_tuple = struct.unpack('L', byte)
        long = long_tuple[0]
        return long

    # 将整数转换为4字节二进制byte
    @staticmethod
    def int2byte(num: int) -> bytes:
        return struct.pack('L', num)

    @staticmethod
    def FormatString(string: str, count: int) -> str:
        # 格式说明：
        # ★字符串行数★字符串
        '''
        res = "★%08d★\n%s\n"%(count, string+'\n')

        res = "☆%08d☆\n%s★%08d★\n%s\n"%(count, string+'\n', count, string+'\n')
        '''

        res = "○%08d○%s●%08d●%s\r\n" % (count, string, count, string)

        '''
        res = "●%08d●%s●\n%s\n"%(count, name, string)
        '''
        return res

    @staticmethod
    def StringFilter(string: str) -> str:
        left = b'\x6a\x22'.decode('utf16')
        right = b'\x6b\x22'.decode('utf16')
        if left in string:
            string = string.replace(left, '《')
        if right in string:
            string = string.replace(right, '》')
        return string

    @staticmethod
    def run(
        from_dir: str = original_scenario,
        to_dir: str = extracted_script,
        src_encoding: str = 'sjis',
    ) -> None:
        strlen = 0
        if not os.path.isdir(from_dir):
            print('No original scenario')
            return
        f_lst = walk(from_dir)  # 提取出文本，等待翻译的txt文件
        if not os.path.isdir(to_dir):
            os.mkdir(to_dir)
        for fn in f_lst:
            dstname = os.path.join(
                to_dir,
                os.path.splitext(os.path.split(fn)[1])[0] + '.txt',
            )
            print(dstname)

            dst = open(dstname, 'w+', encoding='utf8')
            src = open(fn, 'r', encoding=src_encoding, errors='ignore')
            lines = src.readlines()

            num = len(lines)
            stringline = ''
            j = 0
            for index, line in enumerate(lines):
                if (
                    line[0] != '^'
                    and line[0] != '\\'
                    and line[0] != '@'
                    and line[0] != '％'
                    and line != '\n'
                    and (src_encoding != 'gbk' or line[0] != '亾')  #### new
                ):
                    string = Text_out.FormatString(line, j)
                    dst.write(string)
                    j += 1
                    strlen += len(line) * 2

            src.close()
            dst.close()

        # fl = walk(to_dir)
        # for fn in fl:
        #    if os.path.getsize(fn) < 10:
        #        os.remove(fn) # 不该删，有的光提取出了选项

        print('\n文本总量' + str(strlen / 1024) + ' KB\n')


class Selection_out:
    @staticmethod
    def run(
        from_dir: str = original_scenario,
        to_dir: str = extracted_selection,
        src_encoding: str = 'sjis',
    ) -> None:
        if not os.path.isdir(from_dir):
            print('No original scenario')
            return
        f_lst = walk(from_dir)
        if not os.path.isdir(to_dir):
            os.mkdir(to_dir)
        for fn in f_lst:
            dstname = os.path.join(
                to_dir, os.path.splitext(os.path.split(fn)[1])[0] + '.txt'
            )
            print(dstname)
            dst = open(dstname, 'w', encoding='utf8')
            src = open(fn, 'r', encoding=src_encoding, errors='ignore')
            lines = src.readlines()

            num = len(lines)
            stringline = ''
            j = 0
            for index, line in enumerate(lines):
                if line[0:8] == '^select,':
                    # dst.write(line)
                    dst.write(Text_out.FormatString(line, j))
                    j += 1

            src.close()
            dst.close()

        fl = walk(to_dir)
        for fn in fl:
            if os.path.getsize(fn) <= 0:
                os.remove(fn)


class Text_in:
    # 将txt转换成文本列表
    @staticmethod
    def makestr(lines: List[str]) -> List[str]:
        string_list = []
        for index, line in enumerate(lines):
            s = re.match('●[0-9A-Fa-f]+●', line)
            if s:
                string_list.append(line[10:])
            elif line == '\n' or re.match('○[0-9A-Fa-f]+○', line):
                pass
            else:
                print('\n', index + 1, repr(line), '\n')
        return string_list

    @staticmethod
    def StringFilter(string: str) -> str:
        lst = re.findall('\[.+?\]', string)
        if not lst:
            return string

        for part in lst:
            temp = part.replace('，', ',')
            string = string.replace(part, temp)
        string = string.replace('♪', '〈ハ〉')
        return string

    @staticmethod
    def StringFilter2(string: str) -> str:
        if '，' in string:
            string = string.replace('，', ',')
        return string

    @staticmethod
    def run(
        senario_from_dir: str = original_scenario,
        script_from_dir: str = translated_script,
        selection_from_dir: str = translated_selection,
        to_dir: str = processed_scenario,
    ) -> None:
        if not os.path.isdir(translated_script):
            print('No translated script')
            return
        f_lst = walk(senario_from_dir)  # 输入文件夹
        for fn in f_lst:
            original_fn = fn

            if not os.path.isdir(to_dir):
                os.mkdir(to_dir)

            dstname = os.path.join(to_dir, os.path.split(fn)[1])
            print(dstname)
            dst = open(dstname, 'w+', encoding='gbk', errors='ignore')

            rawname = os.path.join(
                script_from_dir, os.path.splitext(os.path.split(fn)[1])[0] + '.txt'
            )
            raw = open(rawname, 'r', encoding='utf8')
            cn_lines = raw.readlines()
            cn_strlist = Text_in.makestr(cn_lines)

            src = open(original_fn, 'r', encoding='sjis', errors='ignore')
            jp_lines = src.readlines()

            selection_name = os.path.join(
                selection_from_dir, os.path.splitext(os.path.split(fn)[1])[0] + '.txt'
            )
            if os.path.exists(selection_name):
                print(selection_name)
                selection = open(selection_name, 'r', encoding='utf8')
                selection_lines = selection.readlines()
                selection_lines = Text_in.makestr(selection_lines)

            dstlines = []
            i = 0
            j = 0
            for index, line in enumerate(jp_lines):
                if line[0:8] == '^select,':
                    # dstlines.append(line)
                    dstlines.append(Text_in.StringFilter2(selection_lines[i]))
                    i += 1
                    continue

                if (
                    line[0] != '^'
                    and line[0] != '\\'
                    and line[0] != '@'
                    and line[0] != '％'
                    and line != '\n'
                ):
                    dstlines.append(Text_in.StringFilter(cn_strlist[j]))
                    j += 1
                else:
                    dstlines.append(line.encode('sjis').decode('gbk'))

            for l in dstlines:
                dst.write(l)

            raw.close()
            src.close()
            dst.close()

        print("finished")


class CNed_out:
    @staticmethod
    def merge(
        jp_text_dir: str = extracted_script,
        cned_text_dir: str = extracted_script_cned,
        jp_selection_dir: str = extracted_selection,
        cned_selection_dir: str = extracted_selection_cned,
        merge_text_dir: str = merged_script,
        merge_selection_dir: str = merged_selection,
    ) -> None:
        jp_files_text = walk(jp_text_dir)
        cned_files_text = [
            os.path.join(cned_text_dir, s.split('\\')[1]) for s in jp_files_text
        ]
        jp_files_selection = walk(jp_selection_dir)
        cned_files_selection = [
            os.path.join(cned_selection_dir, s.split('\\')[1])
            for s in jp_files_selection
        ]

        for dst_dir, task in [
            (merge_text_dir, zip(jp_files_text, cned_files_text)),
            (merge_selection_dir, zip(jp_files_selection, cned_files_selection)),
        ]:
            if not os.path.isdir(dst_dir):
                os.mkdir(dst_dir)
            for jf, cf in task:
                dst_name = os.path.join(dst_dir, jf.split('\\')[1])
                print(dst_name)
                jp_lines = open(jf, 'r', encoding='utf8').readlines()
                cn_lines = open(cf, 'r', encoding='utf8').readlines()
                dst_lines = []

                i = 0
                while i < len(jp_lines):
                    dst_lines.append(jp_lines[i])
                    dst_lines.append(cn_lines[i + 1])
                    dst_lines.append('\n\n')
                    i += 4

                open(dst_name, 'w', encoding='utf8').writelines(dst_lines)

    @staticmethod
    def run() -> None:
        if not os.path.isdir(original_scenario_cned) or not os.path.isdir(
            extracted_script
        ):
            print('No CNed scenario or extracted script')
            return
        Text_out.run(original_scenario_cned, extracted_script_cned, 'gbk')
        Selection_out.run(original_scenario_cned, extracted_selection_cned, 'gbk')
        CNed_out.merge(
            extracted_script,
            extracted_script_cned,
            extracted_selection,
            extracted_selection_cned,
            merged_script,
            merged_selection,
        )


if __name__ == '__main__':
    mode = int(input('Input a number (Run mode): 1 (Out), 2 (In), 3 (Out_CNed): '))
    assert mode in range(1, 4)
    if mode == 1:
        Selection_out.run()
        Text_out.run()
    elif mode == 2:
        Text_in.run()
    elif mode == 3:
        CNed_out.run()
