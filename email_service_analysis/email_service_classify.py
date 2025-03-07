from typing import List
import sys
import os
import asyncio
import pandas as pd
from tqdm import tqdm
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_structure.email_service import Email_Service
from email_service_processor import get_email_service_data_from_db
from email_processor import get_email_data_from_db, get_email_data_with_api
from utils.chat import generate_chat_completion
from utils.tools import parse_html_email


"""
当前存在问题！！！！
邮件正文解析不完善！！！
"""



def fetch_email_services(service_id_list: List[str]) -> List[Email_Service]:
    """
    通过邮件服务单号在数据库中查询所有对应的服务单
    :param service_id_list: 服务单号列表
    :return: 服务单列表
    """
    email_services_data = get_email_service_data_from_db(service_id_list)
    return [Email_Service(**email_service_data) for email_service_data in email_services_data]
    

class ServiceClassifier:
    def __init__(self):
        self.total_cost = 0
        
    async def classify_service(self, service: Email_Service) -> Email_Service:
        """
        对服务单进行分类
        :param service: 服务单
        :return: 分类后的服务单
        """
        email_id = service.email_list[0]['email_id']
        email_data = get_email_data_from_db(email_id)
        if not email_data:
            email_data = get_email_data_with_api(email_id)
        if not email_data:
            service.p_type = "email_data_error"
            return service
        if email_data["current_content"] == "":
            email_data["current_content"] = parse_html_email(email_data["content"])
        
        predict_json, input_token, output_token = await generate_chat_completion(
            email_data["content"], 
            "service_classify", 
            "qwen-max"
        )
        predict = json.loads(predict_json)
        service.p_type = predict["service_type"]
        
        # 计算成本
        cost = (0.0024 * input_token + 0.0096 * output_token) / 1000
        self.total_cost += cost
        
        return service

    async def classify_services(self, services: List[Email_Service]):
        """
        对服务单进行分类
        :param services: 服务单列表
        :return: 分类后的服务单列表
        """
        semaphore = asyncio.Semaphore(10)
        pbar = tqdm(total=len(services), desc="Classifying services")
        
        async def classify_with_semaphore(service):
            async with semaphore:
                result = await self.classify_service(service)
                pbar.update(1)
                return result
            
        tasks = [classify_with_semaphore(service) for service in services]
        results = await asyncio.gather(*tasks)
        pbar.close()
        
        print(f"Total cost: ${self.total_cost:.4f}")
        return results
    


def compile_results(services: List[Email_Service], data: pd.DataFrame) -> dict:
    """
    对分类后的服务单进行统计
    :param services: 服务单列表
    :param data: 历史数据
    :return: 统计结果
    """
    results = {}
    data_dict = data.set_index("service_id").to_dict(orient="index")
    for service in services:
        service_id = int(service.email_service_id)
        if service_id in data_dict:
            service_data = data_dict[service_id]
            results[service_id] = {
                "service_id": service_id,
                "auto_type": str(service_data.get('auto_type', 'unknown')),
                "modified_type": str(service_data.get('modified_type', 'unknown')),
                "predict_type": service.p_type,
            }
        else:
            results[service_id] = {
                "service_id": service_id,
                "auto_type": "unknown",
                "modified_type": "unknown",
                "predict_type": service.p_type,
            }
    return results


def evaluate_results(results: dict) -> dict:
    """
    对结果进行评估
    :param results: 统计结果
    :return: 评估结果
    """
    auto_correct = 0
    predict_correct = 0

    # 结果清洗
    # 去掉summary
    results.pop("summary")
    raw_len = len(results)
    # 去掉"predict_type": "email_data_error"的服务单
    results = {service_id: result for service_id, result in results.items() if result['predict_type'] != "email_data_error"}
    print(f"Raw services: {raw_len}, Cleaned services: {len(results)}")

    total_services = len(results)
    for service_id, result in results.items():
        if result['auto_type'] == result['modified_type']:
            auto_correct += 1
        if result['predict_type'] == result['modified_type']:
            predict_correct += 1
    auto_accuracy = auto_correct / total_services
    predict_accuracy = predict_correct / total_services
    print(f"Auto correct: {auto_accuracy:.2%}")
    print(f"Predict correct: {predict_accuracy:.2%}")


async def main():
    service_file = r"D:\work\email_anay\服务单日志_处理后.xlsx"
    data = pd.read_excel(service_file)

    # service_id_file = r"D:\work\email_anay\email_service_analysis\test_service_id_beta.txt"
    service_id_file = r"D:\work\email_anay\email_service_analysis\test_service_id.txt"
    with open(service_id_file, "r") as f:
        service_id_list = [line.strip() for line in f.readlines()]

    email_services = fetch_email_services(service_id_list)
    
    # 使用类来管理服务分类和成本计算
    classifier = ServiceClassifier()
    classified_services = await classifier.classify_services(email_services)
    
    results = compile_results(classified_services, data)
    
    # 在结果中添加总成本信息
    results["summary"] = {
        "total_cost": classifier.total_cost,
        "total_services": len(classified_services)
    }

    with open(r"D:\work\email_anay\email_service_analysis\test_results.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(results, indent=4, ensure_ascii=False))

    
    evaluate_results(results)

    
if __name__ == '__main__':
    asyncio.run(main())