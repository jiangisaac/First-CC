import tkinter as tk
import math
import re


class ScientificCalculator:
    """桌面科学计算器"""

    def __init__(self, root):
        self.root = root
        self.root.title("科学计算器")
        self.root.geometry("420x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        self._center_window(self.root)

        # 状态
        self.expression = ""
        self.display_text = tk.StringVar(value="0")
        self.result_text = tk.StringVar(value="")
        self.memory = 0.0
        self.has_memory = False
        self.angle_mode = "DEG"
        self.need_new_input = True
        self.error = False
        self.mode_btn = None  # 底部模式按钮引用

        self.setup_ui()
        self.setup_keyboard()
        self._refresh_mode_button()

    # ----------------------------------------------------------------
    #  UI
    # ----------------------------------------------------------------
    @staticmethod
    def _center_window(win=None, w=420, h=620):
        """将窗口居中显示"""
        if win is None:
            return
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 3
        win.geometry(f"{w}x{h}+{x}+{y}")

    def setup_ui(self):
        # 显示区域
        display_frame = tk.Frame(self.root, bg="#ffffff",
                                 highlightbackground="#d0d0d0", highlightthickness=1)
        display_frame.pack(fill=tk.X, padx=10, pady=(10, 2))

        self.expr_label = tk.Label(display_frame, textvariable=self.display_text,
                                   font=("Consolas", 14), anchor=tk.E, fg="#888888",
                                   bg="#ffffff", padx=12, height=1)
        self.expr_label.pack(fill=tk.X, pady=(6, 0))

        self.result_display = tk.Label(display_frame, textvariable=self.result_text,
                                       font=("Consolas", 28, "bold"), anchor=tk.E,
                                       fg="#1a1a1a", bg="#ffffff", padx=12, height=1)
        self.result_display.pack(fill=tk.X, pady=(0, 6))

        # 状态指示
        status_frame = tk.Frame(self.root, bg="#f0f0f0")
        status_frame.pack(fill=tk.X, padx=15, pady=(0, 4))
        self.mode_indicator = tk.Label(status_frame, text="DEG", font=("Consolas", 10, "bold"),
                                       fg="#4a90d9", bg="#f0f0f0")
        self.mode_indicator.pack(side=tk.LEFT)
        self.mem_indicator = tk.Label(status_frame, text="", font=("Consolas", 10, "bold"),
                                      fg="#e67e22", bg="#f0f0f0")
        self.mem_indicator.pack(side=tk.RIGHT)

        # 按钮框架
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(expand=True, fill=tk.BOTH, padx=8, pady=(0, 10))

        # 按钮定义: 9 行, 5 列 (末行有 colspan)
        # 每项: (显示文本, 背景色, 前景色, 回调, [colspan])
        rows_data = [
            # row 0 — 内存
            [("MC", "#eef2f7", "#34495e", self.mem_clear),
             ("MR", "#eef2f7", "#34495e", self.mem_recall),
             ("M+", "#eef2f7", "#34495e", self.mem_add),
             ("M-", "#eef2f7", "#34495e", self.mem_sub),
             ("⌫",  "#e8e8e8", "#1a1a1a", self.backspace)],

            # row 1 — 括号 / 清除
            [("(", "#f0f0f0", "#555555", lambda: self.insert_text("(")),
             (")", "#f0f0f0", "#555555", lambda: self.insert_text(")")),
             ("C", "#e74c3c", "#ffffff", self.clear_all),
             ("%", "#e8e8e8", "#1a1a1a", self.percentage),
             ("±", "#e8e8e8", "#1a1a1a", self.toggle_sign)],

            # row 2 — 科学运算 1
            [("x²", "#f5f5f5", "#2c3e50", lambda: self.apply_unary("square")),
             ("√",  "#f5f5f5", "#2c3e50", lambda: self.apply_unary("sqrt")),
             ("x³", "#f5f5f5", "#2c3e50", lambda: self.apply_unary("cube")),
             ("xʸ", "#f5f5f5", "#2c3e50", lambda: self.insert_text("^")),
             ("÷",  "#e8e8e8", "#1a1a1a", lambda: self.insert_text("/"))],

            # row 3 — 三角 / 对数
            [("sin", "#f5f5f5", "#2c3e50", lambda: self.apply_trig("sin")),
             ("cos", "#f5f5f5", "#2c3e50", lambda: self.apply_trig("cos")),
             ("tan", "#f5f5f5", "#2c3e50", lambda: self.apply_trig("tan")),
             ("log", "#f5f5f5", "#2c3e50", lambda: self.apply_log("log")),
             ("×",   "#e8e8e8", "#1a1a1a", lambda: self.insert_text("*"))],

            # row 4 — 科学运算 2
            [("ln", "#f5f5f5", "#2c3e50", lambda: self.apply_log("ln")),
             ("π",  "#f5f5f5", "#2c3e50", lambda: self.insert_text("π")),
             ("e",  "#f5f5f5", "#2c3e50", lambda: self.insert_text("e")),
             ("x!", "#f5f5f5", "#2c3e50", lambda: self.apply_unary("factorial")),
             ("-",  "#e8e8e8", "#1a1a1a", lambda: self.insert_text("-"))],

            # row 5 — 数字 7-9
            [("7",   "#ffffff", "#1a1a1a", lambda: self.insert_text("7")),
             ("8",   "#ffffff", "#1a1a1a", lambda: self.insert_text("8")),
             ("9",   "#ffffff", "#1a1a1a", lambda: self.insert_text("9")),
             ("1/x", "#f5f5f5", "#2c3e50", lambda: self.apply_unary("inverse")),
             ("+",   "#e8e8e8", "#1a1a1a", lambda: self.insert_text("+"))],

            # row 6 — 数字 4-6 · 角度 · 小数点
            [("4",   "#ffffff", "#1a1a1a", lambda: self.insert_text("4")),
             ("5",   "#ffffff", "#1a1a1a", lambda: self.insert_text("5")),
             ("6",   "#ffffff", "#1a1a1a", lambda: self.insert_text("6")),
             ("DEG", "#f5f5f5", "#e67e22", self.toggle_angle),
             (".",   "#ffffff", "#1a1a1a", lambda: self.insert_text("."))],

            # row 7 — 数字 1-3 · 指数
            [("1",   "#ffffff", "#1a1a1a", lambda: self.insert_text("1")),
             ("2",   "#ffffff", "#1a1a1a", lambda: self.insert_text("2")),
             ("3",   "#ffffff", "#1a1a1a", lambda: self.insert_text("3")),
             ("10ˣ", "#f5f5f5", "#2c3e50", lambda: self.apply_unary("10x")),
             ("Exp", "#f5f5f5", "#2c3e50", lambda: self.insert_text("e^"))],

            # row 8 — 0 (colspan 2) · 模式切换 · = (colspan 2)
            [("0",   "#ffffff", "#1a1a1a", lambda: self.insert_text("0"), 2),
             ("(mode)",   "#f5f5f5", "#e67e22", self.toggle_angle),
             ("=",   "#4a90d9", "#ffffff", self.evaluate, 2)],
        ]

        for r_idx, row in enumerate(rows_data):
            btn_frame.grid_rowconfigure(r_idx, weight=1)
            c_idx = 0
            for item in row:
                text, bg, fg, cmd = item[0], item[1], item[2], item[3]
                colspan = item[4] if len(item) > 4 else 1

                btn = tk.Button(btn_frame, text=text, font=("Segoe UI", 10),
                                relief=tk.FLAT, bg=bg, fg=fg,
                                activebackground=bg, activeforeground=fg,
                                command=cmd, borderwidth=0,
                                highlightthickness=0, cursor="hand2")
                btn.grid(row=r_idx, column=c_idx, columnspan=colspan,
                         sticky=tk.W + tk.E + tk.N + tk.S, padx=2, pady=2)

                # 记录底部模式按钮引用
                if r_idx == 8 and c_idx == 2:
                    self.mode_btn = btn

                # 悬停效果
                if bg == "#ffffff":
                    btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#e8f0fe"))
                    btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#ffffff"))
                elif bg == "#4a90d9":
                    btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#3a7bc8"))
                    btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="#4a90d9"))

                c_idx += colspan

        for c in range(5):
            btn_frame.grid_columnconfigure(c, weight=1, uniform="btn")

        # 更新底栏角度按钮文本
        self._refresh_mode_button()

    # ----------------------------------------------------------------
    #  键盘
    # ----------------------------------------------------------------
    def setup_keyboard(self):
        mapping = {
            "0": "0", "1": "1", "2": "2", "3": "3", "4": "4",
            "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
            "plus": "+", "minus": "-", "asterisk": "*", "slash": "/",
            "parenleft": "(", "parenright": ")", "period": ".",
            "Return": "=", "Escape": "C",
        }
        for key, val in mapping.items():
            self.root.bind(f"<Key-{key}>", lambda e, v=val: self._key_handler(v))
        self.root.bind("<BackSpace>", lambda e: self.backspace())
        self.root.bind("<Delete>", lambda e: self.clear_all())
        self.root.bind("<Control-c>", lambda e: self._copy_result())

    def _key_handler(self, val):
        if val == "=":
            self.evaluate()
        elif val == "C":
            self.clear_all()
        else:
            self.insert_text(val)

    def _copy_result(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_text.get() or self.display_text.get())

    # ----------------------------------------------------------------
    #  输入
    # ----------------------------------------------------------------
    def insert_text(self, text):
        if self.error:
            self.clear_all()

        if self.need_new_input:
            if text in "+-*/^)":  # 运算符延续当前结果
                self.need_new_input = False
            else:  # 数字/常数/小数点 — 开始新计算
                self.expression = ""
                self.display_text.set("")
                self.need_new_input = False

        if text == ".":
            parts = re.split(r"[+\-*/^]", self.expression)
            if "." in (parts[-1] if parts else ""):
                return

        self.expression += text
        self._refresh_display()
        self.result_text.set("")

    def _refresh_display(self):
        d = self.expression.replace("*", "×").replace("/", "÷").replace("^", "^")
        self.display_text.set(d or "0")

    def clear_all(self):
        self.expression = ""
        self.display_text.set("0")
        self.result_text.set("")
        self.need_new_input = True
        self.error = False

    def backspace(self):
        if self.error:
            self.clear_all()
            return
        if self.expression:
            self.expression = self.expression[:-1]
            if not self.expression:
                self.display_text.set("0")
                self.result_text.set("")
                self.need_new_input = True
            else:
                self._refresh_display()

    def toggle_sign(self):
        if self.error:
            self.clear_all()
        if not self.expression:
            self.expression = "-"
            self._refresh_display()
            return
        if self.expression.startswith("-"):
            self.expression = self.expression[1:]
        else:
            self.expression = "-" + self.expression
        self._refresh_display()

    def percentage(self):
        try:
            val = self._safe_eval(self.expression)
            r = val / 100
            self.expression = self._fmt(r)
            self._refresh_display()
            self.result_text.set(self._fmt(r))
        except Exception:
            pass

    def toggle_angle(self):
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        self.mode_indicator.config(text=self.angle_mode)
        self._refresh_mode_button()

    def _refresh_mode_button(self):
        if self.mode_btn:
            self.mode_btn.config(text=self.angle_mode)

    # ----------------------------------------------------------------
    #  科学函数
    # ----------------------------------------------------------------
    def apply_unary(self, func):
        if self.error:
            self.clear_all()
        try:
            val = self._safe_eval(self.expression) if self.expression else 0.0
            result = None
            if func == "square":
                result = val * val
            elif func == "cube":
                result = val * val * val
            elif func == "sqrt":
                if val < 0:
                    raise ValueError("负数不能开平方")
                result = math.sqrt(val)
            elif func == "inverse":
                if val == 0:
                    raise ValueError("除数不能为零")
                result = 1.0 / val
            elif func == "factorial":
                if val < 0 or val != int(val):
                    raise ValueError("阶乘需要非负整数")
                result = math.factorial(int(val))
            elif func == "10x":
                result = 10.0 ** val
            elif func == "ln":
                if val <= 0:
                    raise ValueError("ln 需要正数")
                result = math.log(val)

            if result is not None:
                self.expression = self._fmt(result)
                self._refresh_display()
                self.result_text.set(self._fmt(result))
                self.need_new_input = False

        except Exception as e:
            self._show_error(str(e))

    def apply_trig(self, func):
        if self.error:
            self.clear_all()
        try:
            val = self._safe_eval(self.expression) if self.expression else 0.0
            rad = math.radians(val) if self.angle_mode == "DEG" else val

            result = None
            if func == "sin":
                result = math.sin(rad)
            elif func == "cos":
                result = math.cos(rad)
            elif func == "tan":
                if abs(math.cos(rad)) < 1e-15:
                    raise ValueError("tan 在 90° 倍数处无定义")
                result = math.tan(rad)

            self.expression = self._fmt(result)
            self._refresh_display()
            self.result_text.set(self._fmt(result))
            self.need_new_input = False

        except Exception as e:
            self._show_error(str(e))

    def apply_log(self, base):
        if self.error:
            self.clear_all()
        try:
            val = self._safe_eval(self.expression) if self.expression else 1.0
            if val <= 0:
                raise ValueError("log 需要正数")
            result = math.log10(val) if base == "log" else math.log(val)
            self.expression = self._fmt(result)
            self._refresh_display()
            self.result_text.set(self._fmt(result))
            self.need_new_input = False
        except Exception as e:
            self._show_error(str(e))

    # ----------------------------------------------------------------
    #  内存
    # ----------------------------------------------------------------
    def mem_clear(self):
        self.memory = 0.0
        self.has_memory = False
        self.mem_indicator.config(text="")

    def mem_recall(self):
        if self.has_memory:
            if self.error:
                self.clear_all()
            self.expression = self._fmt(self.memory)
            self._refresh_display()
            self.result_text.set(self._fmt(self.memory))
            self.need_new_input = False

    def mem_add(self):
        try:
            val = self._safe_eval(self.expression) if self.expression else 0.0
            self.memory += val
            self.has_memory = True
            self.mem_indicator.config(text="M")
        except Exception:
            pass

    def mem_sub(self):
        try:
            val = self._safe_eval(self.expression) if self.expression else 0.0
            self.memory -= val
            self.has_memory = True
            self.mem_indicator.config(text="M")
        except Exception:
            pass

    # ----------------------------------------------------------------
    #  求值
    # ----------------------------------------------------------------
    def evaluate(self):
        if self.error:
            self.clear_all()
            return
        expr = self.expression.strip()
        if not expr:
            return

        opens = expr.count("(")
        closes = expr.count(")")
        if opens > closes:
            expr += ")" * (opens - closes)
            self.expression = expr
            self._refresh_display()

        try:
            result = self._safe_eval(expr)
            self.result_text.set(self._fmt(result))
            self.expression = self._fmt(result)
            self._refresh_display()
            self.need_new_input = True
        except ZeroDivisionError:
            self._show_error("除数不能为零")
        except ValueError as e:
            self._show_error(str(e))
        except OverflowError:
            self._show_error("数值溢出")
        except Exception:
            self._show_error("表达式错误")

    def _safe_eval(self, expr):
        # ---------- 预处理 ----------
        # 隐式乘法 (回调函数避免把 5e2 科学计数法破坏)
        def _implicit_mult(m):
            before, after = m.group(1), m.group(2)
            if before.isdigit() and after == 'e' and m.string[m.end():] and m.string[m.end():][0].isdigit():
                return m.group(0)  # 科学计数法: 5e2 → 保留
            return before + '*' + after

        expr = re.sub(r'(\d|\)|π|e)\s*(π|e|\()', _implicit_mult, expr)

        # π → math.pi
        expr = expr.replace("π", str(math.pi))

        # ^ → **
        expr = expr.replace("^", "**")

        # Exp 按钮产生的 e** (原 e^) → math.e**
        expr = re.sub(r'e\*\*', str(math.e) + '**', expr)

        # 替换 Euler e (非科学计数法)
        expr = self._replace_euler(expr)

        # ---------- 安全检查 ----------
        allowed = set("0123456789+-*/().%e ")
        for ch in expr:
            if ch not in allowed:
                raise ValueError(f"非法字符: {ch!r}")

        expr = expr.strip()
        if not expr:
            return 0.0

        # ---------- 求值 ----------
        try:
            result = eval(expr, {"__builtins__": {}}, {"abs": abs, "round": round})
        except SyntaxError:
            raise ValueError("表达式语法错误")

        if isinstance(result, complex):
            raise ValueError("结果为复数")
        return result

    @staticmethod
    def _replace_euler(expr):
        """将 Euler 数 e 替换为 math.e，保留科学计数法 (如 1e5)。"""
        parts = []
        i = 0
        while i < len(expr):
            ch = expr[i]
            if ch != 'e':
                parts.append(ch)
                i += 1
                continue

            before_digit = i > 0 and expr[i - 1].isdigit()
            after_digit = i + 1 < len(expr) and expr[i + 1].isdigit()

            if before_digit and after_digit:
                # 科学计数法: 1e5 → 保留
                parts.append('e')
            else:
                # Euler 数
                if before_digit:
                    parts.append('*')  # 隐式乘: 2e → 2*e
                parts.append(str(math.e))
                if after_digit:
                    parts.append('*')  # 隐式乘: e5 → e*5
            i += 1

        return ''.join(parts)

    # ----------------------------------------------------------------
    #  工具
    # ----------------------------------------------------------------
    def _fmt(self, value):
        if value is None:
            return "0"
        if isinstance(value, float):
            if abs(value) < 1e-15:
                return "0"
            if value == int(value) and abs(value) < 1e15:
                return str(int(value))
            return f"{value:.10g}"
        return str(value)

    def _show_error(self, msg):
        self.error = True
        self.result_text.set(f"错误: {msg}")
        self.display_text.set(self.expression)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()
