import logging
from typing import Union, Optional
from dataclasses import dataclass, field
from fastapi import FastAPI, HTTPException
import requests
import os
from app.encryptor import Encryptor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """应用配置类"""
    API_URL: str = "http://hq.sinajs.cn/list="
    HEADERS: dict = field(default_factory=lambda: {
        "Referer": "https://finance.sina.com.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    ENCRYPT_KEY: Optional[bytes] = os.getenv("encrypt_key", "").encode() if os.getenv("encrypt_key") else None


class StockAPI:
    """股票数据API处理类"""
    def __init__(self, config: Config):
        self.config = config
        self.encryptor = Encryptor(config.ENCRYPT_KEY)

    async def get_stock_data(self, stock_code: str) -> dict:
        """获取并加密股票数据"""
        try:
            response = requests.get(
                f"{self.config.API_URL}{stock_code}", 
                headers=self.config.HEADERS
            )
            response.raise_for_status()
            encrypted_data = self.encryptor.encrypt(response.text, "gbk")
            return {"data": encrypted_data}
        except requests.RequestException as e:
            logger.error(f"Failed to fetch stock data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch stock data")

# 应用初始化
app = FastAPI(title="Stock Data API")
config = Config()
stock_api = StockAPI(config)

@app.get("/{stock_code}")
async def get_stock(stock_code: str) -> Union[dict, str]:
    """获取加密的股票数据"""
    a = await stock_api.get_stock_data(stock_code)
    logger.info(f"Stock data for {stock_code} fetched successfully")
    logger.info(f"Encrypted data: {a}")
    return a