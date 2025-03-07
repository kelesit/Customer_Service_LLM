import sys
import os
from typing import List
from tqdm import tqdm
import logging
from time import sleep

current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(project_root)

from data_structure.email_service import Email_Service
from database.crud import EmailServiceCRUD
from database.database import get_db
from email_service_processor import get_email_service_data


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_email_service_data_to_db(email_services_data: List[dict]):
    """
    将邮件服务数据更新到数据库
    """
    success_count = 0
    failed_count = 0
    batch_size = 100
    max_retries = 3
    
    # 使用tqdm显示进度
    with tqdm(total=len(email_services_data)) as pbar:
        for i in range(0, len(email_services_data), batch_size):
            batch  = email_services_data[i:i+batch_size]
            retry_count = 0

            while retry_count < max_retries:
                db = None
                try:
                    db = next(get_db())
                    services = [Email_Service(**service_data) for service_data in batch]
                    for service in services:
                        try:
                            service.save_to_db(db)
                            success_count += 1
                            pbar.set_description(f"处理: {service.email_service_id}")
                        except Exception as e:
                            failed_count += 1
                            logger.error(f"保存服务单失败 {service.email_service_id}: {str(e)}")
                            continue

                    db.commit()
                    break
                except Exception as e:
                    if db:
                        db.rollback()
                    logger.error(f"批量保存服务单失败: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        sleep(2 ** retry_count)
                    else:
                        failed_count += len(batch)
                finally:
                    if db:
                        db.close()
                    pbar.update(len(batch))

        
    # 输出处理结果
    logger.info(f"处理完成 - 成功: {success_count}, 失败: {failed_count}")
    return success_count, failed_count



def main():
    sevice_id_file = "D:\work\email_anay\data\所有21-28服务单ID.txt"
    with open(sevice_id_file, "r") as f:
        service_id_list = [line.strip() for line in f.readlines()]

    email_services = get_email_service_data(service_id_list)
    save_email_service_data_to_db(email_services)


if __name__ == "__main__":
    
    main()