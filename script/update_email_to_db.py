import sys
import os
from typing import List
from tqdm import tqdm
import logging
import asyncio
from time import sleep

current_script_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(current_script_path))
sys.path.append(project_root)

from data_structure.email import Email
from database.crud import EmailCRUD
from database.database import get_db
from email_processor import get_email_data


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_email_data_to_db(emails_data:List[dict]):
    
    """
    将邮件数据更新到数据库
    """
    success_count = 0
    failed_count = 0
    batch_size = 500
    max_retries = 3

    with tqdm(total=len(emails_data)) as pbar:
        for i in range(0, len(emails_data), batch_size):
            batch = emails_data[i:i+batch_size]
            retry_count = 0

            while retry_count < max_retries:
                db = None
                try:
                    db = next(get_db())
                    emails = [Email(**email_data) for email_data in batch]
                    for email in emails:
                        try:
                            email.save_to_db(db)
                            success_count += 1
                            pbar.set_description(f"处理: {email.email_id}")
        
                        except Exception as e:
                            failed_count += 1
                            logger.error(f"保存邮件失败 {email.email_id}: {str(e)}")
                            continue
                    db.commit()
                    break
                except Exception as e:
                    if db:
                        db.rollback()
                    logger.error(f"批量保存邮件失败: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        sleep(2 ** retry_count)
                    else:
                        failed_count += len(batch)
                finally:
                    if db:
                        db.close()
                    pbar.update(len(batch))

    logger.info(f"处理完成 - 成功: {success_count}, 失败: {failed_count}")
    return success_count, failed_count


async def async_main():
    email_id_file = "email_ids.txt"
    with open(email_id_file, 'r') as f:
        email_id_list = [line.strip() for line in f.readlines()]

    emails = await get_email_data(email_id_list)
    save_email_data_to_db(emails)


if __name__ == '__main__':
    asyncio.run(async_main())