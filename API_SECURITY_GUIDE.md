# API 密钥安全配置指南

## 🔐 重要安全提醒

**您之前分享的API密钥已经暴露，请立即采取以下措施：**

1. **立即撤销暴露的密钥**：`sk-8eaa9ad64b5d4c58a0ea1be29e8081d1`
2. **生成新的API密钥**
3. **按照本指南安全配置**

## 📁 配置文件说明

### 1. config.js
- 用于前端JavaScript项目的配置
- **注意**：不要在前端直接暴露API密钥
- 建议仅用于开发环境或通过后端代理

### 2. .env.example
- 环境变量配置模板
- 复制为 `.env` 文件并填入真实值
- 适用于Node.js后端项目

## 🛡️ 安全最佳实践

### 前端项目安全配置

```javascript
// 推荐：通过后端API代理
const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: userMessage
    })
});
```

### 后端项目安全配置

```javascript
// 使用环境变量
require('dotenv').config();

const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;

// API调用示例
const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [{
            role: 'user',
            content: userMessage
        }]
    })
});
```

## 📋 配置步骤

### 步骤1：创建 .env 文件
```bash
cp .env.example .env
```

### 步骤2：填入真实配置
编辑 `.env` 文件：
```
DEEPSEEK_API_KEY=sk-your-new-api-key-here
```

### 步骤3：添加到 .gitignore
```
# 环境变量文件
.env
config.js
```

## ⚠️ 安全检查清单

- [ ] 已撤销暴露的API密钥
- [ ] 已生成新的API密钥
- [ ] 配置文件已添加到 .gitignore
- [ ] 不在前端代码中直接使用API密钥
- [ ] 使用环境变量存储敏感信息
- [ ] 设置适当的API密钥权限和限制

## 🔧 集成到现有项目

### 修改 index（心理陪伴）.html

如果需要在前端调用AI API，建议创建后端接口：

```html
<script>
// 不要直接在前端使用API密钥
// 通过后端API调用
async function callAI(message) {
    try {
        const response = await fetch('/api/deepseek-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('AI调用失败:', error);
        return '抱歉，AI服务暂时不可用。';
    }
}
</script>
```

## 📞 技术支持

如果在配置过程中遇到问题，请检查：
1. API密钥格式是否正确
2. 网络连接是否正常
3. API配额是否充足
4. 请求格式是否符合DeepSeek API文档