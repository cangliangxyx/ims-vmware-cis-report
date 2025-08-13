import os
from cryptography.fernet import Fernet

def load_key():
    key = os.getenv("SECRET_KEY")  # 从环境变量'SECRET_KEY'读取密钥
    if not key:
        raise ValueError("未设置环境变量 SECRET_KEY")
    return key.encode()  # Fernet 期待字节类型的密钥

# 加密信息
def encrypt_message(message):
    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message.decode()

# 解密信息
def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    try:
        decrypted_message = f.decrypt(encrypted_message.encode())
        return decrypted_message.decode()
    except Exception as e:
        return f"解密失败: {e}"

if __name__ == "__main__":

    encrypted_password = "123123"
    print("加密信息", encrypted_password)
    decrypt_password = decrypt_message("123123")
    print("解密信息", decrypt_password)