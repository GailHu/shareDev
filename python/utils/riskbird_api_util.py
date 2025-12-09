#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RiskBird API交互模块

此模块用于与RiskBird API进行交互，包括发起POST请求、解析响应、
并使用获取到的参数发起GET请求，最后解析HTML结果获取所需信息。
"""
from typing import Dict, List, Optional

import requests
import json
import argparse
import os
import time
import re
import logging
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HtmlFieldExtractor:
    """HTML字段提取器"""

    # 字段配置
    FIELD_CONFIG = {
        "统一社会信用代码": r"统一社会信用代码.*?<!--\[-->(.*?)<!--\]-->",
        "企业名称": r"企业名称.*?<!--\[-->(.*?)<!--\]-->",
        "法定代表人": r"法定代表人.*?<!--\[-->(.*?)<!--\]-->",
        "企业类型": r"企业类型.*?<!--\[-->(.*?)<!--\]-->",
        "注册地址": r"注册地址.*?<!--\[-->(.*?)<!--\]-->",
        "通信地址": r"通信地址.*?<!--\[-->(.*?)<!--\]-->",
        "所属地区": r"所属地区.*?<!--\[-->(.*?)<!--\]-->",
        "所属行业": r"所属行业.*?<!--\[-->(.*?)<!--\]-->",
        "公司规模": r"公司规模.*?<!--\[-->(.*?)<!--\]-->",
    }

    @staticmethod
    def clean_html_tags(text):
        """清除HTML标签"""
        if not text:
            return text
        # 移除所有HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除HTML注释
        text = re.sub(r'<!--\[-->', '', text)
        text = re.sub(r'<!--\]-->', '', text)
        return text.strip()


    @staticmethod
    def extract_field(html_content: str, field_name: str, pattern: str = None) -> str:
        """提取单个字段"""
        if pattern is None:
            pattern = HtmlFieldExtractor.FIELD_CONFIG.get(field_name)

        if pattern is None:
            logger.warning(f"未定义字段{field_name}的提取模式")
            return None

        try:
            match = re.search(pattern, html_content, re.DOTALL)
            return match.group(1).strip() if match else None
        except Exception as e:
            logger.error(f"提取{field_name}时出错: {e}")
            return None

    @staticmethod
    def extract_all(html_content: str, field_names: list = None) -> dict:
        """提取多个字段"""
        if field_names is None:
            field_names = list(HtmlFieldExtractor.FIELD_CONFIG.keys())

        result = {}
        for field_name in field_names:
            result[field_name] = HtmlFieldExtractor.extract_field(html_content, field_name)
            if result[field_name] is None:
                logger.warning(f"未找到{field_name}信息")
            # 清理HTML标签
            result[field_name] = HtmlFieldExtractor.clean_html_tags(result[field_name])

        return result


class PhoneExtractor:
    """专业电话号码提取器"""

    # 详细的电话号码模式
    PATTERNS = {
        "mobile_cn": {
            "pattern": r"1[3-9]\d{9}",
            "description": "中国手机号",
            "validate": lambda x: len(x) == 11
        },
        "landline": {
            "pattern": r"0\d{2,3}-?\d{7,8}",
            "description": "座机（带区号）",
            "validate": lambda x: 10 <= len(x) <= 12
        },
        "landline_parentheses": {
            "pattern": r"\(\d{2,3}\)\d{7,8}",
            "description": "座机（括号格式）",
            "validate": lambda x: 10 <= len(x) <= 14
        },
        "international": {
            "pattern": r"(?:\+86|86|-)?1[3-9]\d{9}",
            "description": "国际格式手机号",
            "validate": lambda x: True
        }
    }

    @staticmethod
    def extract(html_content: str, pattern_type: str = None) -> Dict[str, List[str]]:
        """
        提取电话号码

        Args:
            html_content: HTML内容
            pattern_type: 指定模式类型，None表示全部

        Returns:
            提取结果字典
        """
        result = {}

        if pattern_type:
            patterns = {pattern_type: PhoneExtractor.PATTERNS[pattern_type]}
        else:
            patterns = PhoneExtractor.PATTERNS

        for key, config in patterns.items():
            matches = re.findall(config["pattern"], html_content)
            # 验证和去重
            valid_phones = [phone for phone in set(matches) if config["validate"](phone)]
            result[key] = valid_phones

        return result

    @staticmethod
    def format_phone(phone: str, phone_type: str = "mobile") -> Optional[str]:
        """格式化电话号码"""
        phone = re.sub(r"\D", "", phone)  # 保留数字

        if phone_type == "mobile" and len(phone) == 11:
            return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        elif phone_type == "landline" and len(phone) >= 10:
            return f"{phone[:3]}-{phone[3:]}"

        return phone


# 使用示例
# result = PhoneExtractor.extract(html_content)
# formatted = PhoneExtractor.format_phone("13812345678", "mobile")


class RiskBirdAPI:
    """RiskBird API交互类"""
    def __init__(self, cookie, user_agent=None, enable_html_cache=True, html_cache_dir="temp-html"):
        """
        初始化RiskBirdAPI实例

        参数:
            cookie: 用于请求的Cookie字符串
            user_agent: 请求的User-Agent，默认为None
            enable_html_cache: 是否启用HTML缓存，默认为True
            html_cache_dir: HTML缓存目录，默认为"temp-html"
        """
        self.base_url = "https://riskbird.com"
        self.cookie = cookie
        self.user_agent = user_agent or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        self.headers = {
            "app-device": "WEB",
            "Cookie": self.cookie,
            "User-Agent": self.user_agent,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "riskbird.com",
            "Connection": "keep-alive"
        }
        self.enable_html_cache = enable_html_cache
        self.html_cache_dir = html_cache_dir

        # 确保缓存目录存在
        if self.enable_html_cache and not os.path.exists(self.html_cache_dir):
            os.makedirs(self.html_cache_dir, exist_ok=True)
            logger.info(f"创建HTML缓存目录: {self.html_cache_dir}")

    def post_search(self, search_key, page_no=1, range_=1):
        """
        发起POST搜索请求

        参数:
            search_key: 搜索关键词
            page_no: 页码，默认为1
            range_: 每页结果数量，默认为10

        返回:
            dict: 包含搜索结果的字典
        """
        url = urljoin(self.base_url, "/riskbird-api/newSearch")
        payload = {
            "queryType": "1",
            "searchKey": search_key,
            "pageNo": page_no,
            "range": range_,
            "selectConditionData": "{\"status\":\"\",\"sort_field\":\"\"}"
        }

        try:
            logger.info(f"发起POST搜索请求，关键词: {search_key}")
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 20000:
                logger.info("POST请求成功")
                return result
            else:
                logger.error(f"POST请求失败: {result.get('msg')}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"POST请求发生异常: {str(e)}")
            return None

    def get_company_info(self, ent_name, ent_id):
        """
        发起GET请求获取公司信息

        参数:
            ent_name: 企业名称
            ent_id: 企业ID

        返回:
            dict: 包含公司信息的字典
        """
        # 构建URL，替换entName和entid参数
        url_pattern = "/ent/{}.html?entid={}&fuzzyId=12178040&position=1"
        url = urljoin(self.base_url, url_pattern.format(ent_name, ent_id))

        try:
            logger.info(f"发起GET请求获取公司信息，企业名称: {ent_name}")
            logger.info(f"GET请求地址: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            # 缓存HTML内容
            html_content = response.text
            if self.enable_html_cache:
                self._cache_html(ent_name, ent_id, html_content)

            # 解析HTML结果
            return self._parse_company_html(html_content)
        except requests.exceptions.RequestException as e:
            logger.error(f"GET请求发生异常: {str(e)}")
            return None

    def _cache_html(self, ent_name, ent_id, html_content):
        """
        缓存HTML内容到文件

        参数:
            ent_name: 企业名称
            ent_id: 企业ID
            html_content: HTML内容
        """
        try:
            # 生成唯一的文件名
            timestamp = int(time.time())
            safe_ent_name = ent_name.replace(' ', '_').replace('/', '_')
            filename = f"{safe_ent_name}_{ent_id}_{timestamp}.html"
            file_path = os.path.join(self.html_cache_dir, filename)

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"HTML内容已缓存到: {file_path}")
        except Exception as e:
            logger.error(f"缓存HTML内容时发生异常: {str(e)}")

    def _parse_company_html(self, html_content):
        """
        解析公司信息HTML页面

        参数:
            html_content: HTML内容

        返回:
            dict: 包含解析结果的字典
        """
        try:
            logger.info("开始解析HTML内容")
            # 使用方法
            result = HtmlFieldExtractor.extract_all(html_content)
            phones = PhoneExtractor.extract(html_content)
            logger.info(f"result：{result}")
            logger.info(f"phones：{phones}")
            # 或指定字段
            # result = HtmlFieldExtractor.extract_all(html_content, ["所属地区", "所属行业"])
            logger.info("HTML解析完成")
            return result
        except Exception as e:
            logger.error(f"HTML解析发生异常: {str(e)}")
            return None


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='RiskBird API交互工具')
    parser.add_argument('--cookie', required=True, help='请求的Cookie字符串')
    parser.add_argument('--search-key', required=True, help='搜索关键词')
    parser.add_argument('--no-cache', action='store_true', help='禁用HTML缓存')
    parser.add_argument('--cache-dir', default='temp-html', help='HTML缓存目录')
    args = parser.parse_args()

    # 创建API实例
    api = RiskBirdAPI(
        args.cookie,
        enable_html_cache=not args.no_cache,
        html_cache_dir=args.cache_dir
    )

    # 发起POST搜索
    search_result = api.post_search(args.search_key)
    if not search_result:
        logger.info("搜索失败")
        return

    # 获取data.list.entName和entid
    data = search_result.get("data", {})
    company_list = data.get("list", [])
    if not company_list:
        logger.info("未找到公司信息")
        return

    # 以第一个公司为例
    first_company = company_list[0]
    ent_name = first_company.get("entName")
    ent_id = first_company.get("entid")

    if not ent_name or not ent_id:
        logger.info("未找到必要的公司参数")
        return

    logger.info(f"找到公司: {ent_name} (ID: {ent_id})")

    # 发起GET请求获取公司详情
    company_info = api.get_company_info(ent_name, ent_id)
    if not company_info:
        logger.info("获取公司详情失败")
        return

    # 打印结果
    logger.info("公司信息:")
    logger.info(f"所属地区: {company_info.get('所属地区')}")
    logger.info(f"所属行业: {company_info.get('所属行业')}")


if __name__ == "__main__":
    main()
