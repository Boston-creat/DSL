# 百度文心一言 API Key 和 Secret Key 获取指南

## 重要提示

百度文心一言需要**两个密钥**：
- **API Key** (Access Key ID)
- **Secret Key** (Secret Access Key)

这两个密钥是**配对使用**的，缺一不可。

## 详细获取步骤

### 步骤1：登录百度智能云

1. 访问 https://cloud.baidu.com/
2. 使用百度账号登录（如果没有账号，先注册）

### 步骤2：开通千帆大模型平台

1. 登录后，在控制台搜索"千帆大模型平台"
2. 点击进入服务页面
3. 如果未开通，点击"立即开通"
4. 根据提示完成开通流程

### 步骤3：创建API密钥

1. 进入"千帆大模型平台"控制台
2. 在左侧菜单找到"API密钥管理"（或"应用接入" -> "API密钥"）
3. 点击"创建密钥"或"新建密钥"按钮
4. 填写密钥名称（可选，用于标识）
5. 点击"确定"或"创建"

### 步骤4：保存密钥

创建成功后，系统会显示：
- **API Key** (Access Key ID) - 类似：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Secret Key** (Secret Access Key) - 类似：`yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy`

**⚠️ 重要提示**：
- Secret Key **只显示一次**
- 关闭页面后无法再次查看
- 如果忘记 Secret Key，需要**删除旧密钥并重新创建**

### 步骤5：配置到项目

在项目根目录创建 `.env` 文件：

```env
QIANFAN_API_KEY=你的API_Key
QIANFAN_SECRET_KEY=你的Secret_Key
```

## 常见问题

### Q1: 我只看到了API Key，没有看到Secret Key？

**A**: Secret Key 在创建密钥时**只显示一次**。如果已经关闭了创建页面：
- 检查是否有保存记录
- 如果没有，需要删除旧密钥并重新创建

### Q2: 如何查看已创建的密钥？

**A**: 在"API密钥管理"页面可以查看：
- API Key 会一直显示
- Secret Key **不会显示**（出于安全考虑）
- 如果忘记 Secret Key，只能重新创建

### Q3: 可以只使用API Key吗？

**A**: 不可以。百度文心一言的API需要两个密钥配对使用，这是安全认证机制。

### Q4: 如何重新获取Secret Key？

**A**: 
1. 删除旧的密钥（在API密钥管理页面）
2. 重新创建新密钥
3. 这次务必保存好两个密钥

### Q5: 密钥在哪里使用？

**A**: 配置在项目的 `.env` 文件中：
```env
QIANFAN_API_KEY=你的API_Key
QIANFAN_SECRET_KEY=你的Secret_Key
```

## 安全建议

1. ✅ 不要将密钥提交到Git仓库（`.env` 已在 `.gitignore` 中）
2. ✅ 不要将密钥分享给他人
3. ✅ 定期更换密钥
4. ✅ 如果密钥泄露，立即删除并重新创建

## 验证配置

配置完成后，运行：

```bash
python src/cli.py scripts/order_query.dsl --llm-client qianfan
```

如果配置正确，程序会使用百度文心一言进行意图识别。

如果配置错误，程序会自动降级到简单匹配模式，并显示错误信息。

