# 基于`ChatGPT`的医生模拟器 _Doctor Simulator_

## 〇、最近消息
- 2023/5/1 更新： 完全重写代码，代码量精简了三分之一，更加整齐规范可拓展


## 一、缘起
> 里语曰：「家有敝帚，享之千金」，斯不自见之患也。

此小小软件，即在下自珍之敝帚；因知其必有不自见之处，故公开于GitHub之上，以小此患。

## 二、使用
```
# clone本仓库到本地
cd doctor-simulator
python -m venv .venv

# 激活环境
source .venv/bin/activate # Linux/MacOS
.venv\Scripts\activate.bat # Windows CMD
.venv\Scripts\Activate.ps1 # Windows PowerShell

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 如果使用官方API的话，只需要在系统环境变量配置
# OPENAI_API_KEY=sk-......
# 如果使用第三方API的话，还需要设置第三方的API端点
# 类似：https://api.xxxgtp.com/v1
# OPENAI_API_BASE=
# 如果对环境变量设置不熟悉的话，可以在根目录的 .env 文件中设置
# 首先把 .env.example 复制一份，并改名为 .env
# 使用官方API，就取消注释 OPENAI_API_KEY= 这行，并填写
# 使用第三方API，就再取消注释 OPENAI_API_BASE= 这行，
# 并填写第三方的API端点

# 启动程序
python main.py

```

## 三、说明
1. 软件完全使用`Flet`开发，进行二次开发可以进入其官网学习：https://flet.dev 。

2. 软件最初是从借鉴[官方Demo](https://flet.dev/docs/tutorials/python-realtime-chat)开始的，最然后来对整个软件进行了从同步到异步的改写，然而刀剑不利，斧凿不工，代码中仍有馀迹。

3. 软件布局:总共有四个主要区域,由于开始设计时没有想好，navigation rail 和 app bar （组件名称）都是后来添加，代码布局可能会部分错乱，在下已尽力写好注释。
![软件截图](/assets/img/1.png)




## 四、致谢

- 白云
- ChatGPT
- Codeium


## License
[MIT](/LICENSE)
