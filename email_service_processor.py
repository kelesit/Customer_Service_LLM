from typing import List
import requests
import json
from tqdm import tqdm
from datetime import datetime
from database.database import get_db
from database.crud import EmailServiceCRUD

from data_structure.email_service import Email_Service


# ======== 服务单数据获取 ========
# ======= 通过API获取服务单数据 =======

def get_single_email_service_data(service_id: str):
    """通过服务单号从api获取服务单数据"""
    url = "https://api.baycheer.com/Email/getEmailServiceDetail"
    param = {
        "app_id": "392020",
        "app_token": "BT095WCP2ZE5KF1WDGV8YD420U6VVMIY",
        "email_service_id": service_id
    }
    response = requests.post(url, data=param)
    if response.status_code == 200:
        # 提取返回内容
        data = response.json().get("data")
        return data[0]
    else:
        raise Exception(f"请求邮件服务失败，状态码：{response.status_code}")


def get_email_service_data(service_id:List[str]):
    """
    通过服务单号从api获取服务单数据
    """
    if isinstance(service_id, str):
        return get_single_email_service_data(service_id)
    
    if len(service_id) >= 1000:
        result = []
        for i in tqdm(range(0, len(service_id), 1000), desc="正在获取服务单数据"):
            chunk = service_id[i:i+1000]
            chunk_ids = ",".join(chunk)
            url = "https://api.baycheer.com/Email/getEmailServiceDetail"
            param = {
                "app_id": "392020",
                "app_token": "BT095WCP2ZE5KF1WDGV8YD420U6VVMIY",
                "email_service_id": chunk_ids
            }
            response = requests.post(url, data=param)
            if response.status_code == 200:
                chunk_data = response.json().get("data")
                result.extend(chunk_data if chunk_data else [])
        return result

    else:
        service_id = ",".join(service_id)
        url = "https://api.baycheer.com/Email/getEmailServiceDetail"
        param = {
            "app_id": "392020",
            "app_token": "BT095WCP2ZE5KF1WDGV8YD420U6VVMIY",
            "email_service_id": service_id
        }
        response = requests.post(url, data=param)
        if response.status_code == 200:
            # 提取返回内容
            data = response.json().get("data")
            return data
        else:
            raise Exception(f"请求邮件服务失败，状态码：{response.status_code}")


# ======== 通过数据库获取服务单数据 ========
def get_single_email_service_data_from_db(service_id: str):
    try:
        db = next(get_db())
        try:
            service = EmailServiceCRUD.get_service(db, service_id)
            if service:
                return service.to_dict()
            else:
                print(f"服务单号{service_id}不存在")
                return {}
        finally:
            db.close()
    except Exception as e:
        print(f"获取服务单数据失败：{e}")
        return {}

def get_batch_email_service_data_from_db(service_id:List[str]):
    results = []

    try:
        db = next(get_db())
        try:
            for i in tqdm(range(0, len(service_id), 1000), desc="正在从数据库中获取服务单数据"):
                batch = service_id[i:i+1000]
                services = EmailServiceCRUD.get_services_by_ids(db, batch)
                results.extend([s.to_dict() if s else {} for s in services])
        finally:
            db.close()
    except Exception as e:
        print(f"获取服务单数据失败：{e}")
        results.extend([{}] * (len(service_id) - len(results)))

    return results
                


def get_email_service_data_from_db(service_id:List[str]):
    """
    从数据库获取服务单数据
    Args:
        service_id: 服务单号列表
    Returns:Union[List[dict], dict]
    """
    if isinstance(service_id, str):
        return get_single_email_service_data_from_db(service_id)
    return get_batch_email_service_data_from_db(service_id)



def get_email_service(service_id:List[str]):
    """
    通过服务单号获取邮件对象
    """
    pass

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


if __name__ == '__main__':
    """
    测试服务单数据获取
    """
    service_id_list = ['360517083', '360517081']
    # email_services = get_email_service_data(service_id_list)
    email_services = get_email_service_data_from_db(service_id_list)
    with open('email_service_data.json', 'w', encoding='utf-8') as f:
        json.dump(email_services, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)



