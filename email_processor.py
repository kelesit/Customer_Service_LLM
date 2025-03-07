import requests
import json
from typing import List
import asyncio
import aiohttp
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from data_structure.email import Email
from utils.chat import generate_chat_completion
from utils.tools import parse_html_email

from database.database import get_db
from database.crud import EmailCRUD

# ======== 邮件数据获取部份函数 ========

# ======= 通过API获取邮件数据 =======

# ==== 串行获取邮件数据 ====
def get_single_email_data_with_api(email_id: str):
    url = "https://api.baycheer.com/Email/getEmailDetail"
    param = {
        "app_id": "392020",
        "app_token": "BT095WCP2ZE5KF1WDGV8YD420U6VVMIY",
        "email_id": email_id
    }
    response = requests.post(url, data=param)
    if response.status_code == 200:
        data = response.json().get("data")
        return data[0] if data else {}
    else:
        print(Exception(f"请求邮件详情服务失败:{response.status_code}"))
        return {}


def get_email_data_with_api(email_id_list:List[str]):
    if len(email_id_list) >= 1000:
        result = []
        for i in range(0, len(email_id_list), 1000):
            batch_result = get_email_data_with_api(email_id_list[i:i+1000])
            result.extend(batch_result)
        return result
    else:
        email_id = ",".join(email_id_list)
        url = "https://api.baycheer.com/Email/getEmailDetail"
        param = {
            "app_id": "392020",
            "app_token": "BT095WCP2ZE5KF1WDGV8YD420U6VVMIY",
            "email_id": email_id
        }
        response = requests.post(url, data=param)
        if response.status_code == 200:
            data = response.json().get("data")
            return data
        else:
            print(Exception(f"请求邮件详情服务失败:{response.status_code}"))
            return []


# ==== 异步获取邮件数据 ====
async def get_single_email_data_async(email_id: str, session: aiohttp.ClientSession):
    """异步获取单个邮件数据"""
    try:
        url = "https://api.baycheer.com/Email/getEmailDetail"
        param = {
            "app_id": "392020",
            "app_token": "BT095WCP2ZE5KF1WDGV8YD420U6VVMIY",
            "email_id": email_id
        }
        async with session.post(url=url, data=param) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data")
    except Exception as e:
        print(f"获取邮件 {email_id} 失败: {e}")
        return None

# ==== 异步获取大批量邮件数据 ====
async def get_batch_email_data_async(email_id_batch: List[str]):
    """异步处理单批次(<=1000)邮件ID
    Args:
        email_id_batch: 不超过1000个邮件ID的列表
    Returns:
        List: 邮件数据列表
    """
    assert len(email_id_batch)<=1000, "批量获取邮件数据不能超过1000"
    
    max_retries = 3
    retry_count = 0

    url = "https://api.baycheer.com/Email/getEmailDetail"
    param = {
        "app_id": "392020",
        "app_token": "BT095WCP2ZE5KF1WDGV8YD420U6VVMIY",
        "email_id": ",".join(email_id_batch)
    }

    for retry_count in range(max_retries):
        try:
            timeout = aiohttp.ClientTimeout(total=30*(retry_count+1))

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=url, 
                    data=param, 
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=timeout,
                ) as response:
                # 检查响应状态
                    if response.status != 200:
                        print(f"HTTP错误: {response.status}, 第{retry_count+1}次重试")
                        await asyncio.sleep(2 ** retry_count)
                        continue

                    try:
                        data = await response.json()
                        return data.get("data", [])
                    except json.JSONDecodeError:
                        print("JSON解析错误, 第{retry_count+1}次重试")
                        await asyncio.sleep(2 ** retry_count)
                        continue
                
        except Exception as e:
            print(f"请求错误: {str(e)}")
            if retry_count < max_retries - 1:
                await asyncio.sleep(2 ** retry_count)
                continue

    print(f"批次邮件数据获取失败: {email_id_batch}")
    return []

async def get_email_data_large_batch(email_id_list: List[str]):
    """处理大批量邮件ID，自动分批异步处理
    Args:
        email_id_list: 邮件ID列表，数量不限
    Returns:
        List: 所有邮件数据的合并列表
    """
    batch_size = 1000
    batches = [email_id_list[i:i+batch_size] for i in range(0, len(email_id_list), batch_size)]
    total_batches = len(batches)
    semaphore = asyncio.Semaphore(3)

    async def process_batch(batch, batch_index):
        async with semaphore:
            try:
                batch_result = await get_batch_email_data_async(batch)
                print(f"批次{batch_index + 1}/{total_batches}处理完成")
                print(f"获取到{len(batch_result)}条邮件数据")
                return batch_result
            except Exception as e:
                print(f"批次{batch_index + 1}/{total_batches}处理失败: {str(e)}")
                return []
    
    tasks = [process_batch(batch, i) for i, batch in enumerate(batches)]

    results = []
    completed_batches=0

    with tqdm(total=len(tasks), desc="正在获取邮件数据") as pbar:
        for coro in asyncio.as_completed(tasks):
            try:
                batch_result = await coro
                if batch_result:
                    results.extend(batch_result)
                completed_batches += 1
                pbar.update(1)
            except Exception as e:
                print(f"Task failed: {str(e)}")
                completed_batches += 1
                pbar.update(1)
    if results:
        print(f"成功获取{len(results)}条邮件数据")
        success_rate = len(results) / len(email_id_list) * 100
        print(f"成功率: {success_rate:.2f}%")

    return results


# ======= 通过数据库获取邮件数据 =======
def get_single_email_data_from_db(email_id: str):
    try:
        db = next(get_db())
        try:
            email = EmailCRUD.get_email(db, email_id)
            if email:
                return email.to_dict()
            else:
                pass
                # print(f"邮件ID {email_id} 不存在")
            return {}
        finally:
            db.close()
    except Exception as e:
        print(f"获取邮件数据失败: {e}")
        return {}


def get_batch_email_data_from_db(email_id_list: List[str]):
    """
    从数据库获取邮件数据
    Args:
        email_id_list: 邮件ID列表
    """
    results = []
    try:
        db = next(get_db())
        try:
            for i in tqdm(range(0, len(email_id_list), 1000), desc="正在从数据库中获取邮件数据"):
                batch = email_id_list[i:i+1000]
                email = EmailCRUD.get_emails_by_ids(db, batch)
                results.extend([e.to_dict() if e else {} for e in email])
        finally:
            db.close()
    except Exception as e:
        print(f"获取邮件数据失败: {e}")
        results.extend([{}] * (len(email_id_list) - len(results)))

    return results

def get_email_data_from_db(email_id_list: List[str]):
    """
    从数据库中获取邮件数据
    Args:
        email_id_list: 邮件ID列表
    Returns: Union[List[dict], dict]
    """
    if isinstance(email_id_list, str):
        return get_single_email_data_from_db(email_id_list)
    return get_batch_email_data_from_db(email_id_list)


async def get_email_data(email_id_list: List[str]) -> List[dict]:
    """获取邮件数据的主入口函数
    Args:
        email_id_list: 邮件ID列表
    Returns:
        List[dict]: 邮件数据列表
    """
    # 1. 从数据库获取已存在的邮件数据
    email_data_in_db = get_email_data_from_db(email_id_list)
    
    
    # 2. 获取数据库中不存在的邮件ID
    email_id_not_in_db =  [
        email_id for email_id, email_data 
        in zip(email_id_list, email_data_in_db) 
        if not email_data
    ]
    # 去掉email_data_in_db中的空字典
    email_data_in_db = [email_data for email_data in email_data_in_db if email_data]
    
    email_data_in_db = []
    email_id_not_in_db = email_id_list

    # 3. 通过API获取剩余邮件数据
    if email_id_not_in_db:
        email_data_not_in_db = await get_email_data_large_batch(email_id_not_in_db)
    else:
        email_data_not_in_db = []
    
    # 4. 合并数据库和API的结果
    return email_data_in_db + email_data_not_in_db




# ======= 邮件处理部份函数 =======

def create_email_prompt(email: Email):
    """生成邮件解析的prompt"""
    prompt = f"发件人:{email.from_name}\n"
    prompt += f"收件人:{email.to_name}\n"
    prompt += f"主题:{email.subject}\n"
    prompt += f"内容:{email.current_content}\n"
    return prompt


async def process_single_email(email: Email, model: str):
    """处理单个邮件"""
    try:
        prompt = create_email_prompt(email=email)
        llm_response = await generate_chat_completion(prompt, "email", model)
        response_data = json.loads(llm_response)
        email.order_id = response_data.get("order_id", "")
        email.original_language = response_data.get("original_language", "")
        email.zh_translation = response_data.get("zh_translation", "")
        email.content_preview = response_data.get("content_preview", "")
        return email.model_dump()
    
    except Exception as e:
        print(f"处理邮件 {email.email_id} 失败: {e}")
        return None


async def process_emails_async(email_id_list: List[str], model: str):
    """异步处理邮件列表"""
    try:
        # 1. 获取邮件数据
        emails_data = await get_email_data(email_id_list)
        if not emails_data:
            print("获取邮件数据失败")
            return []
        
        # 2. 创建邮件对象列表
        emails = []
        for email_data in emails_data:
            try:
                email = Email(**email_data)
                if email.current_content == "":
                    # 从html中提取正文内容
                    email.current_content = parse_html_email(email.content)
                emails.append(email)
            except Exception as e:
                print(f"创建邮件对象失败: {e}")
                continue

        if not emails:
            print("没有创建成功的邮件对象")
            return []

        # 3. 异步处理每封邮件
        tasks = [process_single_email(email, model) for email in emails]
        results = await tqdm_asyncio.gather(*tasks, desc="llm解析邮件中")

        # 4. 存入数据库中
        for email in emails:
            email.save_to_db()

        # 5. 返回处理成功的邮件
        processed_emails = []
        for result in results:
            if result is not None:
                processed_emails.append(result)
        return processed_emails

    
    except Exception as e:
        print(f"处理邮件列表失败: {e}")
        return None


def process_emails(email_id_list: List[str]):
    """
    Args:
        email_id: [str] 邮件id列表
    Returns:
        emails_data:
        [
            {
                "email_id": "308352387",
                ...
                "order_id": "xxx",
                "long_order_id": "xxx",
                "original_language": "xxx",
                "zh_translation": "xxx",
                "en_translation": "xxx",
                "content_preview": "xxx",
            },
            ...
        ]
    1. 获取邮件数据（异步）
    2. 创建邮件对象
    3. 通过llm解析邮件，获得订单号、原始语种、中文翻译、英文翻译、内容预览等信息 
    4. 将结果写入邮件对象
    5. 写入数据库
    6. 构建json格式返回
    """
    return asyncio.run(process_emails_async(email_id_list, "qwen-max"))




if __name__ == '__main__':
    """
    llm解析邮件内容
    """
    email_id_list = ['308375163']
    emails = []
    for email_id in email_id_list:
        email = get_email_data(email_id)
        emails.append(email)
    # emails = get_email_data_list(email_id_list)

    with open('email_data.json', 'w', encoding='utf-8') as f:
       json.dump(emails, f, ensureascii=False, inent=4)
    
    # results = process_emails(email_id_list)
    # with open('processed_emails.json', 'w', encoding='utf-8') as f:
    #     json.dump(results, f, ensure_ascii=False, indent=4)
    