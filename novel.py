from salmon import Service, Bot
from salmon.typing import CQEvent, T_State
from salmon.service import add_header
from salmon.modules.novel.novel_data import get_single_continuation


sv = Service('小说续写', bundle='娱乐', help_='''
[续写] 续写智障小说
'''.strip())


continuation = sv.on_prefix('续写', only_group=False)

@continuation.handle()
async def novel_continue_rec(bot: Bot, event: CQEvent, state: T_State):
    text = event.get_plaintext().strip()
    if text:
        state['text'] = text
    message = await add_header(bot, event, msg='请发送小说内容')
    state['prompt'] = message


@continuation.got('text', prompt='{prompt}')
async def novel_continue(bot: Bot, event: CQEvent, state: T_State):
    text = state['text']
    await continuation.send('请稍等片刻~', call_header=True)
    res = await get_single_continuation(text)
    if res:
        await continuation.finish(res, call_header=True)