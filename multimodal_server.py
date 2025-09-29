# multimodal_server.py
# 修复Werkzeug版本冲突问题
import sys
import os

# 添加当前目录到Python路径，确保使用本地安装的包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 手动导入url_quote
try:
    from werkzeug.urls import url_quote
except ImportError:
    # 如果导入失败，提供一个简单的url_quote实现
    import urllib.parse
    def url_quote(string, charset='utf-8', errors='strict', safe='/:'):
        return urllib.parse.quote(string, safe=safe)
    
    # 将函数添加到werkzeug.urls模块
    import werkzeug.urls
    werkzeug.urls.url_quote = url_quote

import base64
import requests
import io
# 添加静态文件服务支持
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pydub import AudioSegment

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)  # 允许跨域请求

# ---------- 百度 API 配置 ----------
# ASR (语音识别) API 配置
ASR_API_KEY = "JP4P10HaLRDaukXw8XYxLk3Y"
ASR_SECRET_KEY = "PndlFRH1EAiTChn35rEjXbFza3yJaNaw"

# OCR (图像识别) API 配置
OCR_API_KEY = "d4mOamuM2mjiBNwbBiJC5TtR"
OCR_SECRET_KEY = "Chby7J7PGsRBNxVGXzga9z0pRbZO7bKh"

# 设备标识符
CUID = "psychology_assistant_device"

# ---------- 百度 API Token 缓存 ----------
asr_token_cache = {"access_token": None, "expires_at": 0}
ocr_token_cache = {"access_token": None, "expires_at": 0}

# ---------- 获取 Access Token ----------
def get_asr_token():
    """获取百度语音识别 Access Token"""
    import time
    current_time = int(time.time())
    
    # 如果缓存的token仍然有效，直接返回
    if asr_token_cache["access_token"] and asr_token_cache["expires_at"] > current_time:
        return asr_token_cache["access_token"]
    
    # 否则重新获取token
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": ASR_API_KEY,
        "client_secret": ASR_SECRET_KEY
    }
    
    response = requests.get(url, params=params)
    if response.ok:
        result = response.json()
        asr_token_cache["access_token"] = result["access_token"]
        # 设置过期时间（提前5分钟过期）
        asr_token_cache["expires_at"] = current_time + result["expires_in"] - 300
        return result["access_token"]
    else:
        raise Exception(f"获取ASR Token失败: {response.text}")

def get_ocr_token():
    """获取百度OCR Access Token"""
    import time
    current_time = int(time.time())
    
    # 如果缓存的token仍然有效，直接返回
    if ocr_token_cache["access_token"] and ocr_token_cache["expires_at"] > current_time:
        return ocr_token_cache["access_token"]
    
    # 否则重新获取token
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": OCR_API_KEY,
        "client_secret": OCR_SECRET_KEY
    }
    
    response = requests.get(url, params=params)
    if response.ok:
        result = response.json()
        ocr_token_cache["access_token"] = result["access_token"]
        # 设置过期时间（提前5分钟过期）
        ocr_token_cache["expires_at"] = current_time + result["expires_in"] - 300
        return result["access_token"]
    else:
        raise Exception(f"获取OCR Token失败: {response.text}")

# ---------- 音频处理 ----------
def convert_to_wav_16k_mono(file_bytes, src_format=None):
    """将音频转换为16kHz单声道WAV格式"""
    try:
        # 检查ffmpeg是否可用
        import shutil
        import glob
        
        # 首先检查当前目录下是否有ffmpeg可执行文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg_path = None
        
        # 在Linux环境下检查当前目录下的ffmpeg_files目录
        if os.name == 'posix':  # Linux/Unix系统
            ffmpeg_dir = os.path.join(current_dir, 'ffmpeg_files')
            if os.path.exists(ffmpeg_dir):
                # 尝试查找可能的ffmpeg可执行文件路径
                possible_paths = [
                    os.path.join(ffmpeg_dir, 'ffmpeg'),
                    os.path.join(ffmpeg_dir, 'ffmp', 'ffmpeg')
                ]
                
                # 添加通配符路径
                possible_paths.extend(glob.glob(os.path.join(ffmpeg_dir, '*', 'ffmpeg')))
                possible_paths.extend(glob.glob(os.path.join(ffmpeg_dir, '*', '*', 'ffmpeg')))
                possible_paths.extend(glob.glob(os.path.join(ffmpeg_dir, '*', '*', '*', 'ffmpeg')))
                
                for path in possible_paths:
                    if os.path.isfile(path):
                        # 如果文件存在但没有执行权限，尝试添加执行权限
                        if not os.access(path, os.X_OK):
                            try:
                                os.chmod(path, os.stat(path).st_mode | 0o111)  # 添加执行权限
                            except Exception as e:
                                print(f"无法为 {path} 添加执行权限: {e}")
                                continue
                        
                        if os.access(path, os.X_OK):
                            local_ffmpeg_path = path
                            print(f"使用本地Linux ffmpeg: {local_ffmpeg_path}")
                            # 将本地ffmpeg路径添加到环境变量
                            os.environ['PATH'] = f"{os.path.dirname(local_ffmpeg_path)}:{os.environ.get('PATH', '')}"
                            break
        
        # 在Windows环境下检查当前目录下的ffmpeg.exe
        elif os.name == 'nt':  # Windows系统
            win_ffmpeg_path = os.path.join(current_dir, 'ffmpeg.exe')
            if os.path.exists(win_ffmpeg_path):
                local_ffmpeg_path = win_ffmpeg_path
                print(f"使用本地Windows ffmpeg: {local_ffmpeg_path}")
                # 将本地ffmpeg路径添加到环境变量
                os.environ['PATH'] = f"{current_dir};{os.environ.get('PATH', '')}"
        
        # 如果找到本地ffmpeg，使用它
        if local_ffmpeg_path:
            ffmpeg_path = local_ffmpeg_path
        else:
            # 否则尝试在系统PATH中查找
            ffmpeg_path = shutil.which("ffmpeg")
            
        if not ffmpeg_path:
            print("警告: 未找到ffmpeg可执行文件，将尝试使用pydub内置方法处理音频")
        
        # 从字节流创建音频对象
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format=src_format)
        # 转换为16kHz单声道
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        # 导出为WAV格式
        out_io = io.BytesIO()
        audio.export(out_io, format="wav")
        return out_io.getvalue()
    except FileNotFoundError as e:
        raise Exception(f"音频转换失败: 找不到ffmpeg。请确保ffmpeg已正确安装或上传到服务器。详细错误: {str(e)}")
    except Exception as e:
        raise Exception(f"音频转换失败: {str(e)}。请确保ffmpeg已正确安装或上传到服务器。")

# ---------- API 路由 ----------
@app.route("/asr", methods=["POST"])
def asr_endpoint():
    """语音识别API端点"""
    if "file" not in request.files:
        return jsonify({"error": "未上传音频文件"}), 400
    
    file = request.files["file"]
    filename = file.filename or "audio"
    file_bytes = file.read()
    
    # 尝试从文件名判断格式
    src_format = None
    if "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
        if ext in ("mp3", "wav", "m4a", "amr", "flac", "ogg"):
            src_format = ext
    
    try:
        # 转换音频格式
        wav_bytes = convert_to_wav_16k_mono(file_bytes, src_format=src_format)
        
        # 获取Access Token
        access_token = get_asr_token()
        
        # 调用百度ASR API
        url = "https://vop.baidu.com/server_api"
        headers = {"Content-Type": "application/json"}
        data = {
            "format": "wav",
            "rate": 16000,
            "channel": 1,
            "token": access_token,
            "cuid": CUID,
            "len": len(wav_bytes),
            "speech": base64.b64encode(wav_bytes).decode("utf-8")
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        return jsonify({"baidu_result": result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    """图像识别API端点"""
    if "file" not in request.files:
        return jsonify({"error": "未上传图片文件"}), 400
    
    file = request.files["file"]
    file_bytes = file.read()
    
    try:
        # 获取Access Token
        access_token = get_ocr_token()
        
        # 调用百度OCR API
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {"image": base64.b64encode(file_bytes).decode("utf-8")}
        
        response = requests.post(url, data=params, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if "words_result" in result:
            # 返回完整的百度OCR结果，以便前端处理
            return jsonify({"baidu_result": result})
        else:
            return jsonify({"error": result.get("error_msg", "识别失败")}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 添加静态文件路由
@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)
    
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)