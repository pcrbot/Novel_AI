import asyncio
import random
import time
import salmon
from salmon import aiohttpx


HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Content-Type": "application/json;charset=utf-8",
}

async def get_nid(text: str) -> str:
    """获得文章id"""
    url = 'http://if.caiyunai.com/v1/dream/602c8c0826a17bcd889faca7/novel_save'
    data = {"content": text, "title": "", "ostype": ""}
    response = await aiohttpx.post(url, json=data, headers=HEADER)
    if response.status_code == 200:
        return response.json()['data']['nid']
    else:
        raise Exception(f'HTTP {response.status_code}')


async def submit_to_ai(text: str, novel_id: str, model_id: str = '601f92f60c9aaf5f28a6f908'):
    """将文本提交到指定模型的AI，得到xid"""
    url = 'http://if.caiyunai.com/v1/dream/602c8c0826a17bcd889faca7/novel_ai'
    data = {
        "nid": novel_id,
        "content": text,
        "uid": "602c8c0826a17bcd889faca7",
        "mid": model_id,
        "title": "",
        "ostype": ""
    }
    response = await aiohttpx.post(url, json=data, headers=HEADER)
    rsp_json = response.json()
    xid = rsp_json['data']['xid']
    return xid


async def poll_for_result(nid: str, xid: str):
    """不断查询，直到服务器返回生成结果"""
    url = 'http://if.caiyunai.com/v1/dream/602c8c0826a17bcd889faca7/novel_dream_loop'
    data = {
        "nid": nid,
        "xid": xid,
        "ostype": ""
    }
    max_retry_times = 10
    for _ in range(max_retry_times):
        response = await aiohttpx.post(url, json=data, headers=HEADER)
        rsp_json = response.json()
        if rsp_json['data']['count'] != 0:  # 说明还没有生成好，继续重试
            await asyncio.sleep(1.5)
            continue
        results = rsp_json['data']['rows']
        results = [res['content'] for res in results]
        return results
    raise TimeoutError('服务器响应超时')


async def get_single_continuation(text: str):
    try:
        result = ''
        for i in range(3): # 连续续写三次
            if i == 1:
                result = text
            nid = await get_nid(result)
            xid = await submit_to_ai(result, nid)
            salmon.logger.info(f'正在等待服务器返回第{i+1}段续写结果')
            continuation = await poll_for_result(nid, xid)
            result += random.choice(continuation)
            time.sleep(0.5)
        salmon.logger.info('续写完成')
        return result + '......'
    except Exception as e:
        salmon.logger.error(f'发生错误{e}')
        salmon.logger.exception(e)
        return f'发生错误：{e}\n请联系维护.'