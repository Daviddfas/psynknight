// 配置文件 - 请勿将此文件提交到版本控制系统
// Configuration file - Do not commit this file to version control

// DeepSeek API 配置
const CONFIG = {
    // DeepSeek API 密钥 - 请替换为您的实际密钥
    DEEPSEEK_API_KEY: 'your-deepseek-api-key-here',
    
    // API 基础URL
    DEEPSEEK_BASE_URL: 'https://api.deepseek.com',
    
    // 模型配置
    MODEL_CONFIG: {
        model: 'deepseek-chat',
        max_tokens: 1000,
        temperature: 0.7
    },
    
    // 其他配置
    APP_CONFIG: {
        debug: false,
        timeout: 30000 // 30秒超时
    }
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else {
    window.CONFIG = CONFIG;
}