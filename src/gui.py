"""
图形用户界面（GUI）
作用：提供图形化的用户交互界面，加载DSL脚本，处理用户输入，执行解释器
在全项目中的作用：这是CLI的图形化版本，提供更友好的用户体验
"""

import sys
import os
import threading
from pathlib import Path
from tkinter import (
    Tk, Frame, Text, Entry, Button, Label, Scrollbar, 
    filedialog, messagebox, ttk, StringVar, Toplevel, Canvas
)

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter
from src.llm_client import create_llm_client
from src.logger import setup_logger

# 初始化日志记录器
logger = setup_logger("DSL_Agent_GUI")


class ChatBubble(Canvas):
    """消息气泡组件 - 莫兰迪色系精致设计"""
    
    def __init__(self, parent, message, is_user=False, **kwargs):
        super().__init__(parent, **kwargs)
        self.message = message
        self.is_user = is_user
        self.configure(highlightthickness=0, bd=0, bg=parent.cget('bg'))
        self.create_bubble()
    
    def create_bubble(self):
        """创建消息气泡"""
        # 计算文本宽度和高度
        self.update_idletasks()
        width = self.winfo_reqwidth() if self.winfo_reqwidth() > 1 else 400
        
        # 创建文本标签来测量文本大小
        temp_label = Label(self, text=self.message, font=('Microsoft YaHei', 11),
                         wraplength=320, justify='left')
        temp_label.update_idletasks()
        text_width = temp_label.winfo_reqwidth()
        text_height = temp_label.winfo_reqheight()
        
        # 气泡尺寸（更精致的间距）
        bubble_width = min(max(text_width + 40, 90), 380)
        bubble_height = text_height + 28
        
        self.configure(width=bubble_width, height=bubble_height)
        
        # 莫兰迪色系
        if self.is_user:
            bubble_color = '#D4A5A5'  # 莫兰迪粉
            text_color = '#FFFFFF'
            shadow_color = '#C89B9B'
        else:
            bubble_color = '#F5F1E8'  # 莫兰迪米色
            text_color = '#6B6B6B'
            shadow_color = '#E8E4DB'
        
        # 绘制圆角矩形（气泡）- 更精致的圆角
        radius = 24
        x0, y0 = 0, 0
        x1, y1 = bubble_width, bubble_height
        
        # 创建圆角矩形
        self.create_oval(x0, y0, x0 + radius*2, y0 + radius*2, 
                        fill=bubble_color, outline=bubble_color)
        self.create_oval(x1 - radius*2, y0, x1, y0 + radius*2, 
                        fill=bubble_color, outline=bubble_color)
        self.create_oval(x0, y1 - radius*2, x0 + radius*2, y1, 
                        fill=bubble_color, outline=bubble_color)
        self.create_oval(x1 - radius*2, y1 - radius*2, x1, y1, 
                        fill=bubble_color, outline=bubble_color)
        
        self.create_rectangle(x0 + radius, y0, x1 - radius, y1, 
                             fill=bubble_color, outline=bubble_color)
        self.create_rectangle(x0, y0 + radius, x1, y1 - radius, 
                             fill=bubble_color, outline=bubble_color)
        
        # 添加精致阴影效果
        shadow_offset = 3
        for i in range(2, 0, -1):
            offset = shadow_offset - i
            alpha = 0.15 - i * 0.05
            shadow_oval = self.create_oval(x0 + offset, y0 + offset, 
                                          x0 + radius*2 + offset, y0 + radius*2 + offset,
                                          fill=shadow_color, outline=shadow_color, stipple='gray50')
            self.tag_lower(shadow_oval)
        
        # 将阴影移到后面
        for item in self.find_all():
            if self.itemcget(item, 'fill') == shadow_color:
                self.tag_lower(item)
        
        # 添加文本（更精致的字体和间距）
        self.create_text(bubble_width // 2, bubble_height // 2,
                        text=self.message, fill=text_color,
                        font=('Microsoft YaHei', 11), width=bubble_width - 32,
                        justify='left', anchor='center')


class ChatGUI:
    """聊天界面主类"""
    
    def __init__(self, root):
        logger.info("=" * 60)
        logger.info("GUI界面启动")
        logger.info("=" * 60)
        
        self.root = root
        self.root.title("DSL智能客服系统")
        self.root.geometry("850x950")
        self.root.resizable(True, True)
        # 莫兰迪色系背景 - 灰蓝色调
        self.root.configure(bg='#E8E8E8')
        
        # 系统状态
        self.interpreter = None
        self.program = None
        self.llm_client = None
        self.current_script_path = None
        self.waiting_for_input = False
        self.input_variable = None
        self.input_dialog = None
        
        # 创建界面
        logger.debug("创建GUI组件")
        self.create_widgets()
        
        # 检查API密钥
        self.check_api_key()
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部标题栏 - 莫兰迪米白色
        header = Frame(self.root, bg='#F5F1E8', height=75, relief='flat')
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        # 左侧：状态信息
        status_frame = Frame(header, bg='#F5F1E8')
        status_frame.pack(side='left', padx=25, pady=18)
        
        Label(status_frame, text="●", bg='#F5F1E8', fg='#A8B5A0',
             font=('Microsoft YaHei', 10)).pack(side='left', padx=3)
        Label(status_frame, text="在线", bg='#F5F1E8', fg='#8B8B8B',
             font=('Microsoft YaHei', 10)).pack(side='left', padx=3)
        Label(status_frame, text="智能客服", bg='#F5F1E8', fg='#6B6B6B',
             font=('Microsoft YaHei', 13, 'bold')).pack(side='left', padx=8)
        
        # 右侧：操作按钮
        action_frame = Frame(header, bg='#F5F1E8')
        action_frame.pack(side='right', padx=25, pady=18)
        
        # 加载脚本按钮 - 莫兰迪灰蓝色
        btn_load = Button(action_frame, text="📁 加载脚本", command=self.load_script,
                         bg='#A8B5A0', fg='white', font=('Microsoft YaHei', 10, 'bold'),
                         relief='flat', padx=16, pady=8, cursor='hand2',
                         activebackground='#95A390', activeforeground='white',
                         bd=0, highlightthickness=0)
        btn_load.pack(side='left', padx=6)
        
        # 当前脚本显示
        self.script_label = Label(action_frame, text="未加载", bg='#F5F1E8', 
                                 fg='#9B9B9B', font=('Microsoft YaHei', 9))
        self.script_label.pack(side='left', padx=12)
        
        # 主聊天区域（带滚动条）- 莫兰迪灰蓝背景
        chat_container = Frame(self.root, bg='#E8E8E8')
        chat_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # 创建Canvas用于滚动
        self.chat_canvas = Canvas(chat_container, bg='#E8E8E8', 
                                  highlightthickness=0, relief='flat')
        scrollbar = Scrollbar(chat_container, orient='vertical', 
                             command=self.chat_canvas.yview,
                             bg='#D4D4D4', troughcolor='#E8E8E8',
                             width=12, borderwidth=0, highlightthickness=0)
        self.scrollable_frame = Frame(self.chat_canvas, bg='#E8E8E8')
        
        # 创建窗口并保存窗口ID
        self.canvas_window = self.chat_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # 绑定scrollable_frame大小变化
        def on_frame_configure(event):
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # 绑定canvas大小变化，确保scrollable_frame宽度跟随canvas
        def on_canvas_configure(event):
            canvas_width = event.width
            self.chat_canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.chat_canvas.bind('<Configure>', on_canvas_configure)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.chat_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            self.chat_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.chat_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 底部输入区域 - 莫兰迪米白色
        input_container = Frame(self.root, bg='#F5F1E8', height=90)
        input_container.pack(fill='x', padx=0, pady=0)
        input_container.pack_propagate(False)
        
        input_frame = Frame(input_container, bg='#F5F1E8')
        input_frame.pack(fill='both', expand=True, padx=25, pady=18)
        
        # 输入框 - 莫兰迪灰白色
        self.input_entry = Entry(input_frame, font=('Microsoft YaHei', 11),
                                relief='flat', bd=0, bg='#FFFFFF',
                                highlightthickness=2, highlightcolor='#A8B5A0',
                                highlightbackground='#D4D4D4', insertbackground='#A8B5A0',
                                fg='#6B6B6B')
        self.input_entry.pack(side='left', fill='x', expand=True, padx=(0, 12), ipady=12, ipadx=18)
        self.input_entry.bind('<Return>', lambda e: self.send_message())
        self.input_entry.bind('<KeyPress>', self.on_input_key)
        
        # 发送按钮（圆形，带飞机图标）- 莫兰迪粉
        btn_send = Button(input_frame, text="✈", command=self.send_message,
                         bg='#D4A5A5', fg='white', font=('Arial', 18),
                         relief='flat', width=3, height=1, cursor='hand2',
                         activebackground='#C89B9B', activeforeground='white',
                         bd=0, highlightthickness=0)
        btn_send.pack(side='right')
        
        # 清空按钮 - 莫兰迪灰色
        btn_clear = Button(input_frame, text="🗑", command=self.clear_chat,
                          bg='#C4C4C4', fg='white', font=('Arial', 14),
                          relief='flat', width=2, height=1, cursor='hand2',
                          activebackground='#B4B4B4', bd=0, highlightthickness=0)
        btn_clear.pack(side='right', padx=8)
        
        # 初始欢迎消息
        self.add_bot_message("欢迎使用DSL智能客服系统！\n请先点击「加载脚本」按钮加载DSL脚本文件。")
    
    def on_input_key(self, event):
        """输入框按键事件"""
        # 自动调整输入框高度（如果需要多行输入）
        pass
    
    def check_api_key(self):
        """检查API密钥配置"""
        if not os.getenv("ZHIPUAI_API_KEY"):
            self.add_bot_message(
                "⚠️ 警告：未检测到智谱AI API密钥\n"
                "请配置 ZHIPUAI_API_KEY 环境变量\n"
                "配置方法：创建 .env 文件，添加 ZHIPUAI_API_KEY=your_key\n"
                "获取API密钥：访问 https://open.bigmodel.cn/"
            )
    
    def load_script(self):
        """加载DSL脚本文件"""
        logger.info("用户点击加载脚本按钮")
        file_path = filedialog.askopenfilename(
            title="选择DSL脚本文件",
            filetypes=[("DSL文件", "*.dsl"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            logger.debug("用户取消文件选择")
            return
        
        logger.info(f"用户选择脚本文件: {file_path}")
        self.current_script_path = file_path
        self.script_label.config(text=f"已加载: {Path(file_path).name}")
        
        # 在新线程中加载脚本，避免界面卡顿
        threading.Thread(target=self._load_script_thread, args=(file_path,), daemon=True).start()
    
    def _load_script_thread(self, file_path):
        """在后台线程中加载脚本"""
        try:
            logger.info(f"开始加载脚本: {file_path}")
            self.add_bot_message("正在加载脚本...")
            
            # 加载脚本内容
            with open(file_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
            logger.info(f"脚本文件加载成功，大小: {len(script_content)} 字符")
            
            # 词法分析
            self.add_bot_message("正在进行词法分析...")
            logger.debug("开始词法分析")
            lexer = Lexer(script_content)
            tokens = lexer.tokenize()
            logger.info(f"词法分析完成，Token数量: {len(tokens)}")
            
            # 语法分析
            self.add_bot_message("正在进行语法分析...")
            logger.debug("开始语法分析")
            lexer = Lexer(script_content)
            parser = Parser(lexer)
            program = parser.parse()
            logger.info(f"语法分析完成，意图数量: {len(program.intents)}")
            
            # 创建LLM客户端
            self.add_bot_message("正在初始化LLM客户端...")
            logger.debug("初始化LLM客户端")
            llm_client = create_llm_client("zhipuai")
            logger.info("LLM客户端初始化成功")
            
            # 创建解释器
            logger.debug("创建解释器")
            interpreter = Interpreter(llm_client)
            interpreter.interpret(program)
            
            # 设置用户输入回调
            interpreter.set_user_input_callback(self.get_user_input_callback)
            
            # 设置输出回调（用于显示ask、response、options等输出）
            interpreter.set_output_callback(self.on_interpreter_output)
            
            # 更新状态
            self.program = program
            self.interpreter = interpreter
            self.llm_client = llm_client
            
            # 更新UI（必须在主线程）
            self.root.after(0, lambda: self._on_script_loaded(len(tokens), len(program.intents)))
            logger.info("脚本加载完成")
            
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            self.root.after(0, lambda: self.add_bot_message(f"❌ 错误: 文件不存在: {file_path}"))
        except SyntaxError as e:
            logger.error(f"语法错误: {e}", exc_info=True)
            self.root.after(0, lambda: self.add_bot_message(f"❌ 语法错误: {e}"))
        except (ValueError, ImportError, RuntimeError) as e:
            logger.error(f"初始化失败: {e}", exc_info=True)
            self.root.after(0, lambda: self.add_bot_message(f"❌ 初始化失败: {e}"))
        except Exception as e:
            logger.error(f"发生错误: {e}", exc_info=True)
            self.root.after(0, lambda: self.add_bot_message(f"❌ 发生错误: {e}"))
    
    def _on_script_loaded(self, token_count, intent_count):
        """脚本加载完成后的回调"""
        self.add_bot_message(
            f"✅ 脚本加载成功！\n"
            f"Token数量: {token_count}\n"
            f"意图数量: {intent_count}\n"
            f"系统就绪，可以开始对话了！"
        )
    
    def get_user_input_callback(self, variable: str) -> str:
        """用户输入回调函数（用于wait_for）"""
        import queue
        
        # 使用队列在线程间传递结果
        result_queue = queue.Queue()
        
        def show_input_dialog():
            """在主线程中显示输入对话框"""
            dialog = Toplevel(self.root)
            dialog.title("输入")
            dialog.geometry("450x200")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            dialog.configure(bg='#FFFFFF')
            
            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"450x200+{x}+{y}")
            
            # 标题
            title_label = Label(dialog, text=f"请输入 {variable}:", 
                               font=('Microsoft YaHei', 12, 'bold'),
                               bg='#FFFFFF', fg='#2c3e50')
            title_label.pack(pady=20)
            
            # 输入框 - 莫兰迪风格
            entry = Entry(dialog, font=('Microsoft YaHei', 11), width=40,
                         relief='flat', bd=0, bg='#FFFFFF',
                         highlightthickness=2, highlightcolor='#A8B5A0',
                         highlightbackground='#D4D4D4', fg='#6B6B6B',
                         insertbackground='#A8B5A0')
            entry.pack(pady=12, padx=25, ipady=10, ipadx=15)
            entry.focus()
            
            def on_ok():
                result_queue.put(entry.get())
                dialog.destroy()
            
            def on_cancel():
                result_queue.put("")
                dialog.destroy()
            
            # 按钮容器
            btn_frame = Frame(dialog, bg='#FFFFFF')
            btn_frame.pack(pady=18)
            
            Button(btn_frame, text="确定", command=on_ok, 
                  bg='#A8B5A0', fg='white', width=10, relief='flat',
                  font=('Microsoft YaHei', 10, 'bold'), padx=18, pady=9,
                  cursor='hand2', activebackground='#95A390',
                  bd=0, highlightthickness=0).pack(side='left', padx=12)
            Button(btn_frame, text="取消", command=on_cancel, 
                  bg='#C4C4C4', fg='white', width=10, relief='flat',
                  font=('Microsoft YaHei', 10), padx=18, pady=9,
                  cursor='hand2', activebackground='#B4B4B4',
                  bd=0, highlightthickness=0).pack(side='left', padx=12)
            
            entry.bind('<Return>', lambda e: on_ok())
            
            def on_closing():
                result_queue.put("")
                dialog.destroy()
            
            dialog.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 在主线程中显示对话框
        self.root.after(0, show_input_dialog)
        
        # 等待用户输入
        try:
            result = result_queue.get(timeout=300)
            return result if result else ""
        except queue.Empty:
            return ""
    
    def on_interpreter_output(self, message: str):
        """解释器输出回调（用于显示ask、response、options等）"""
        # 移除"[机器人]"前缀（如果存在）
        if message.startswith("[机器人] "):
            message = message[9:]
        
        # 在主线程中显示消息
        self.root.after(0, lambda: self.add_bot_message(message))
    
    def send_message(self):
        """发送用户消息"""
        user_input = self.input_entry.get().strip()
        
        if not user_input:
            return
        
        if user_input.lower() in ['quit', 'exit', '退出']:
            logger.info("用户退出系统")
            self.add_bot_message("再见！")
            return
        
        # 检查是否已加载脚本
        if not self.interpreter:
            logger.warning("用户发送消息但未加载脚本")
            self.add_bot_message("❌ 请先加载DSL脚本文件！")
            return
        
        logger.info(f"用户发送消息: {user_input}")
        # 显示用户消息
        self.add_user_message(user_input)
        self.input_entry.delete(0, 'end')
        
        # 在新线程中处理意图识别和执行
        threading.Thread(target=self._process_message, args=(user_input,), daemon=True).start()
    
    def _process_message(self, user_input: str):
        """在后台线程中处理消息"""
        try:
            logger.debug("开始处理用户消息")
            # 意图识别
            matched_intent = self.interpreter.match_intent(user_input)
            
            if not matched_intent:
                logger.warning(f"未能识别用户意图: {user_input}")
                self.root.after(0, lambda: self.add_bot_message(
                    "抱歉，我没有理解您的意图。请尝试其他表达方式。"
                ))
                return
            
            logger.info(f"识别到意图: {matched_intent.name}")
            # 执行意图（response会通过output_callback显示）
            self.interpreter.execute_intent(matched_intent)
            logger.debug("消息处理完成")
            
        except Exception as e:
            logger.error(f"处理消息时发生错误: {e}", exc_info=True)
            self.root.after(0, lambda: self.add_bot_message(f"❌ 发生错误: {e}"))
            import traceback
            traceback.print_exc()
    
    def add_user_message(self, message: str):
        """添加用户消息（右侧莫兰迪粉气泡）"""
        bubble_frame = Frame(self.scrollable_frame, bg='#E8E8E8')
        bubble_frame.pack(fill='x', padx=(20, 8), pady=10)  # 右边距留8px，保持一点间距
        
        # 右侧对齐，保留一点右边距
        container = Frame(bubble_frame, bg='#E8E8E8')
        container.pack(side='right', anchor='e', padx=(0, 0))
        
        bubble = ChatBubble(container, message, is_user=True)
        bubble.pack(anchor='e', padx=(0, 0))  # 确保气泡本身也右对齐
        
        # 滚动到底部
        self.root.after(10, self.scroll_to_bottom)
    
    def add_bot_message(self, message: str):
        """添加机器人消息（左侧莫兰迪米色气泡）"""
        bubble_frame = Frame(self.scrollable_frame, bg='#E8E8E8')
        bubble_frame.pack(fill='x', padx=20, pady=10)
        
        # 左侧对齐
        container = Frame(bubble_frame, bg='#E8E8E8')
        container.pack(side='left', anchor='w')
        
        bubble = ChatBubble(container, message, is_user=False)
        bubble.pack()
        
        # 滚动到底部
        self.root.after(10, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        self.chat_canvas.update_idletasks()
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)
    
    def clear_chat(self):
        """清空聊天记录"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.add_bot_message("聊天记录已清空")


def main():
    """主函数"""
    root = Tk()
    app = ChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
