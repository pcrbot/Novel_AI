from salmon import Service, Bot
from salmon.typing import CQEvent, GroupMessageEvent, PrivateMessageEvent, T_State
from salmon.modules.novel.novel_data import get_single_continuation


sv = Service('小说续写', bundle='娱乐', help_='''
[续写] 续写智障小说
'''.strip())


continuation = sv.on_fullmatch('续写', only_group=False)


@continuation.handle()
async def novel_continue_rec(bot: Bot, event: CQEvent, state: T_State):
    user_info = await bot.get_stranger_info(user_id=event.user_id)
    nickname = user_info.get('nickname', '未知用户')
    text = event.get_plaintext().strip()
    if text:
        state['text'] = text
    if isinstance(event, GroupMessageEvent):
        message = f'>{nickname}\n请发送小说内容'
    elif isinstance(event, PrivateMessageEvent):
        message = '请发送小说内容'
    state['prompt'] = message


@continuation.got('text', prompt='{prompt}')
async def novel_continue(bot: Bot, event: CQEvent, state: T_State):
    user_info = await bot.get_stranger_info(user_id=event.user_id)
    nickname = user_info.get('nickname', '未知用户')
    text = state['text']
    await bot.send(event, '请稍等片刻~')
    res = await get_single_continuation(text)
    if res:
        if isinstance(event, GroupMessageEvent):
            await continuation.finish(f'>{nickname}\n' + res)
        elif isinstance(event, PrivateMessageEvent):
            await continuation.finish(res)
