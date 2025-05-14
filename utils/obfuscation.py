import base64
import zlib
import marshal
import random
import string

class Obfuscator:
    @staticmethod
    def obfuscate_python(code):
        """Obfuscate Python code using multiple techniques"""
        # Compile to bytecode
        bytecode = compile(code, '<string>', 'exec')
        
        # Marshal and compress
        marshaled = marshal.dumps(bytecode)
        compressed = zlib.compress(marshaled)
        
        # Base64 encode
        encoded = base64.b64encode(compressed)
        
        # Generate random variable names
        var1 = ''.join(random.choices(string.ascii_lowercase, k=8))
        var2 = ''.join(random.choices(string.ascii_lowercase, k=8))
        var3 = ''.join(random.choices(string.ascii_lowercase, k=8))
        
        # Create obfuscated loader
        obfuscated = f"""
import base64,zlib,marshal
{var1}='{encoded.decode()}'
{var2}=base64.b64decode({var1})
{var3}=zlib.decompress({var2})
exec(marshal.loads({var3}))
"""
        return obfuscated

    @staticmethod
    def string_encrypt(text):
        """Simple string encryption"""
        return ''.join([chr(ord(c) + 1) for c in text])

    @staticmethod
    def string_decrypt(text):
        """Simple string decryption"""
        return ''.join([chr(ord(c) - 1) for c in text])