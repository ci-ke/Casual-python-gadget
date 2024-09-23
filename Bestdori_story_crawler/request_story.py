# 所有活动 摘要：https://bestdori.com/api/events/all.stories.json
# 特定活动 摘要：https://bestdori.com/api/events/1.json
# 数据包列表：https://bestdori.com/api/explorer/cn/assets/scenario/eventstory/event1.json
# 数据包json：https://bestdori.com/assets/cn/scenario/eventstory/event1_rip/Scenarioevent01-01.asset

# 乐队 摘要：https://bestdori.com/api/misc/bandstories.5.json
# 数据包列表：https://bestdori.com/api/explorer/cn/assets/scenario/band/001.json
# 数据包json：https://bestdori.com/assets/cn/scenario/band/001_rip/Scenarioband1-001.asset

# 主线 摘要：https://bestdori.com/api/misc/mainstories.5.json
# 数据包列表：https://bestdori.com/api/explorer/cn/assets/scenario/main.json
# 数据包json：https://bestdori.com/assets/cn/scenario/main_rip/Scenariomain001.asset

import os
from typing import Any, Dict, Optional, Sequence
import requests  # type: ignore

EVENT_SAVE_DIR = r'D:\Workspace\test\event_story'
BAND_SAVE_DIR = r'D:\Workspace\test\band_story'
MAIN_SAVE_DIR = r'D:\Workspace\test\main_story'


BAND_ID_NAME = {
    1: 'Poppin\'Party',
    2: 'Afterglow',
    3: 'Hello, Happy World!',
    4: 'Pastel＊Palettes',
    5: 'Roselia',
    18: 'RAISE A SUILEN',
    21: 'Morfonica',
    45: 'MyGO!!!!!',
}

PROXY = None
# PROXY = {'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'}


def read_story_in_json(json_data: Dict[str, Dict[str, Any]]) -> str:
    ret = ''

    talks = json_data['Base']['talkData']
    scenes = json_data['Base']['specialEffectData']

    scripts = json_data['Base']['snippets']
    for script in scripts:
        if script['actionType'] == 6:
            scene = scenes[script['referenceIndex']]
            if scene['effectType'] == 8:
                ret += '【' + scene['stringVal'] + '】\n'
        elif script['actionType'] == 1:
            talk = talks[script['referenceIndex']]
            ret += (
                talk['windowDisplayName'] + '：' + talk['body'].replace('\n', '') + '\n'
            )

    return ret[:-1]


def get_event_story_cn(event_id: int) -> None:
    res = requests.get(
        f'https://bestdori.com/api/events/{event_id}.json', proxies=PROXY
    )
    res.raise_for_status()
    res_json: Dict[str, Any] = res.json()

    event_name = res_json['eventName'][3]
    if event_name is None:
        print(f'event {event_id} has no CN.')
        return

    event_save_dir = os.path.join(EVENT_SAVE_DIR, f'{event_id} {event_name}')
    os.makedirs(event_save_dir, exist_ok=True)

    for story in res_json['stories']:
        name = f"{story['scenarioId']} {story['caption'][3]} {story['title'][3]}"
        synopsis = story['synopsis'][3]
        id = story['scenarioId']

        if not 'bandStoryId' in story:
            res2 = requests.get(
                f'https://bestdori.com/assets/cn/scenario/eventstory/event{event_id}_rip/Scenario{id}.asset',
                proxies=PROXY,
            )
            res2.raise_for_status()
            res_json2: Dict[str, Dict[str, Any]] = res2.json()

            text = read_story_in_json(res_json2)
        else:
            text = '见乐队故事'

        filename = name.replace('*', '＊')  # SAKURA*BLOOMING！

        with open(
            os.path.join(event_save_dir, filename) + '.txt', 'w', encoding='utf8'
        ) as f:
            f.write(name + '\n\n')
            f.write(synopsis + '\n\n')
            f.write(text + '\n')

        print(f'get event {event_id} {event_name} {name} done.')


def get_band_story_cn(
    want_band_id: Optional[int] = None, want_chapter_number: Optional[int] = None
) -> None:
    if want_band_id is not None:
        assert want_band_id in BAND_ID_NAME

    res = requests.get(
        'https://bestdori.com/api/misc/bandstories.5.json', proxies=PROXY
    )
    res.raise_for_status()
    res_json: Dict[str, Dict[str, Any]] = res.json()

    for band_story in res_json.values():
        band_id = band_story['bandId']
        try:
            chapterNumber = band_story['chapterNumber']
        except KeyError:
            continue

        if want_band_id is not None:
            if want_band_id != band_id:
                continue
        if want_chapter_number is not None:
            if want_chapter_number != chapterNumber:
                continue

        band_name = BAND_ID_NAME[band_id]

        if band_story['mainTitle'][3] == None:
            print(
                f'band story {band_name} {band_story["mainTitle"][0]} {band_story["subTitle"][0]} has no CN.'
            )
            continue

        band_save_dir = os.path.join(
            BAND_SAVE_DIR,
            band_name,
            f'{band_story["mainTitle"][3]} {band_story["subTitle"][3]}',
        )
        os.makedirs(band_save_dir, exist_ok=True)

        for story in band_story['stories'].values():
            name = f"{story['scenarioId']} {story['caption'][3]} {story['title'][3]}"
            synopsis = story['synopsis'][3]
            id = story['scenarioId']

            res2 = requests.get(
                f'https://bestdori.com/assets/cn/scenario/band/{band_id:03}_rip/Scenario{id}.asset',
                proxies=PROXY,
            )
            res2.raise_for_status()
            res_json2: Dict[str, Dict[str, Any]] = res2.json()

            text = read_story_in_json(res_json2)

            with open(
                os.path.join(band_save_dir, name) + '.txt', 'w', encoding='utf8'
            ) as f:
                f.write(name + '\n\n')
                f.write(synopsis + '\n\n')
                f.write(text + '\n')

            print(
                f'get band story {band_name} {band_story["mainTitle"][3]} {name} done.'
            )


def get_main_story_cn(id_range: Optional[Sequence[int]] = None) -> None:
    res = requests.get(
        'https://bestdori.com/api/misc/mainstories.5.json', proxies=PROXY
    )
    res.raise_for_status()
    res_json: Dict[str, Dict[str, Any]] = res.json()

    os.makedirs(MAIN_SAVE_DIR, exist_ok=True)

    for strId, main_story in res_json.items():
        if id_range is not None and int(strId) not in id_range:
            continue

        if main_story['title'][3] == None:
            print(
                f'main story {main_story["caption"][0]} {main_story["title"][0]} has no CN.'
            )
            continue

        name = f"{main_story['scenarioId']} {main_story['caption'][3]} {main_story['title'][3]}"
        synopsis = main_story['synopsis'][3]
        id = main_story['scenarioId']

        res2 = requests.get(
            f'https://bestdori.com/assets/cn/scenario/main_rip/Scenario{id}.asset',
            proxies=PROXY,
        )
        res2.raise_for_status()
        res_json2: Dict[str, Dict[str, Any]] = res2.json()

        text = read_story_in_json(res_json2)

        with open(
            os.path.join(MAIN_SAVE_DIR, name) + '.txt', 'w', encoding='utf8'
        ) as f:
            f.write(name + '\n\n')
            f.write(synopsis + '\n\n')
            f.write(text + '\n')

        print(f'get main story {name} done.')


if __name__ == '__main__':
    get_main_story_cn()
    get_band_story_cn()
    for i in range(1, 253):
        get_event_story_cn(i)
