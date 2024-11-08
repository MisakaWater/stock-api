from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Encryptor:
    """数据加密处理类"""

    def __init__(self, key: bytes):
        if not key:
            raise ValueError("需要提供加密密钥")
        self.key = key
        # 密钥长度不足, 使用填充补齐
        if len(self.key) < 32:
            padder = padding.PKCS7(128).padder()
            self.key = padder.update(self.key) + padder.finalize()

        self.algorithm = algorithms.AES(self.key)
        self.backend = default_backend()

    def encrypt(self, data: str, encode: str = "utf-8") -> str:
        """AES加密方法（使用CTR模式，无需填充）"""
        try:
            iv = os.urandom(16)
            cipher = Cipher(self.algorithm, modes.CTR(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            encrypted_data = (
                encryptor.update(data.encode(encode)) + encryptor.finalize()
            )
            return iv.hex() + encrypted_data.hex()
        except Exception as e:
            logger.error(f"加密失败: {str(e)}")
            raise

    def decrypt(self, data: str, encode: str = "utf-8") -> str:
        """AES解密方法（使用CTR模式，无需填充）"""
        try:
            iv = bytes.fromhex(data[:32])
            encrypted_data = bytes.fromhex(data[32:])
            cipher = Cipher(self.algorithm, modes.CTR(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            return decrypted_data.decode(encode)
        except Exception as e:
            logger.error(f"解密失败: {str(e)}")
            raise
