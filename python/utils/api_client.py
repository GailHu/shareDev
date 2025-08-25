import requests
import logging
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置一个专用的logger，而不是使用全局的basicConfig
# 这样可以更好地与其他模块的日志系统集成
logger = logging.getLogger("ApiClient")
logger.setLevel(logging.DEBUG)  # 默认设置为DEBUG，可以捕获所有信息
# 如果不想看到这么多日志，可以在使用时调整handler的级别
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class APIError(Exception):
    """自定义API异常"""
    def __init__(self, status_code, message="API Error"):
        self.status_code = status_code
        self.message = f"{message} (Status Code: {status_code})"
        super().__init__(self.message)

class ApiClient:
    """
    一个通用的API接口调用工具类，具备可配置的重试和详细的日志记录。
    """
    def __init__(self, base_url, headers=None, timeout=30,
                 retry_total=3, retry_backoff_factor=0.5,
                 retry_status_forcelist=None):
        """
        初始化ApiClient
        :param base_url: API的基础URL
        :param headers: 全局请求头, 例如 {'Authorization': 'Bearer YOUR_TOKEN'}
        :param timeout: 请求超时时间
        :param retry_total: 重试总次数
        :param retry_backoff_factor: 重试退避因子，用于计算等待时间
        :param retry_status_forcelist: 需要强制重试的HTTP状态码列表
        """
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.timeout = timeout

        # 配置重试机制
        if retry_status_forcelist is None:
            retry_status_forcelist = [500, 502, 503, 504]
        
        retries = Retry(
            total=retry_total,
            backoff_factor=retry_backoff_factor,
            status_forcelist=retry_status_forcelist,
            # 对所有请求方法都启用重试
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _log_request(self, method, url, kwargs):
        """记录请求发出的详细信息"""
        logger.info(f"Requesting: {method.upper()} {url}")
        # 隐藏敏感信息，如Authorization头
        safe_headers = {k: v for k, v in kwargs.get('headers', {}).items() if k.lower() != 'authorization'}
        logger.debug(f"--> Headers: {safe_headers}")

        if 'json' in kwargs and kwargs['json']:
            logger.debug(f"--> JSON Body: {json.dumps(kwargs['json'], indent=2, ensure_ascii=False)}")
        if 'data' in kwargs and kwargs['data']:
            logger.debug(f"--> Form Data: {kwargs['data']}")

    def _log_response(self, response):
        """记录收到的响应详细信息"""
        logger.info(f"Response: {response.status_code} {response.reason} from {response.url}")
        logger.debug(f"<-- Headers: {response.headers}")
        try:
            # 尝试以JSON格式记录响应体，并截断过长的内容
            response_body = response.text
            if response_body:
                log_body = json.dumps(response.json(), indent=2, ensure_ascii=False)
                if len(log_body) > 1000:
                    log_body = log_body[:1000] + "\n... (truncated)"
                logger.debug(f"<-- Response Body:\n{log_body}")
        except json.JSONDecodeError:
            # 如果不是JSON，直接记录文本，同样截断
            log_body = response.text
            if len(log_body) > 1000:
                log_body = log_body[:1000] + "... (truncated)"
            logger.debug(f"<-- Response Body (text):\n{log_body}")

    def _request(self, method, path, **kwargs):
        """核心请求方法"""
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        request_headers = self.session.headers.copy()
        if 'headers' in kwargs:
            request_headers.update(kwargs['headers'])
        kwargs['headers'] = request_headers
        kwargs.setdefault('timeout', self.timeout)

        self._log_request(method, url, kwargs)

        try:
            response = self.session.request(method, url, **kwargs)
            self._log_response(response)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {method.upper()} {url}: {e}")
            status_code = getattr(e.response, 'status_code', 500)
            raise APIError(status_code=status_code, message=str(e)) from e
        
        return response

    def get(self, path, **kwargs):
        return self._request('GET', path, **kwargs)

    def post(self, path, **kwargs):
        return self._request('POST', path, **kwargs)

    def put(self, path, **kwargs):
        return self._request('PUT', path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request('DELETE', path, **kwargs)

    def patch(self, path, **kwargs):
        return self._request('PATCH', path, **kwargs)

