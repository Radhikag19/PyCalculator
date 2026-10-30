import tkinter as tk
from tkinter import ttk
import math
import ast
import operator


# ============================================================
# SAFE EXPRESSION EVALUATOR (DEGREES ONLY)
# ============================================================

class SafeEvaluator:
    """
    Safely evaluates mathematical expressions using Python's AST.
    Only explicitly allowed operations, functions, and constants
    are supported. Trigonometric functions operate in degrees.
    """

    BIN_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }

    UNARY_OPS = {
        ast.UAdd: lambda x: x,
        ast.USub: operator.neg,
    }

    def __init__(self):
        self.funcs = {
            "sin": lambda x: math.sin(math.radians(x)),
            "cos": lambda x: math.cos(math.radians(x)),
            "tan": lambda x: math.tan(math.radians(x)),
            "sqrt": math.sqrt,
            "log": math.log,
            "abs": abs,
        }
        self.consts = {
            "pi": math.pi,
            "e": math.e,
        }

    def evaluate(self, expr: str):
        expr = expr.replace("^", "**")
        tree = ast.parse(expr, mode="eval")
        return self._eval(tree.body)

    def _eval(self, node):
        if isinstance(node, ast.BinOp):
            return self.BIN_OPS[type(node.op)](
                self._eval(node.left),
                self._eval(node.right),
            )

        if isinstance(node, ast.UnaryOp):
            return self.UNARY_OPS[type(node.op)](
                self._eval(node.operand)
            )

        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.funcs:
                args = [self._eval(arg) for arg in node.args]
                return self.funcs[node.func.id](*args)
            raise ValueError("Invalid function")

        if isinstance(node, ast.Name):
            if node.id in self.consts:
                return self.consts[node.id]
            raise ValueError("Unknown identifier")

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid constant")

        raise ValueError("Unsupported expression")


# ============================================================
# SCIENTIFIC CALCULATOR UI
# ============================================================

class ScientificCalculator(tk.Tk):
    """Modern scientific calculator with a secure evaluator."""

    def __init__(self):
        super().__init__()

        self.title("Scientific Calculator")
        self.geometry("420x560")
        self.minsize(380, 520)
        self.configure(bg="#1e1e1e")

        self.result_var = tk.StringVar()
        self.evaluator = SafeEvaluator()

        self._configure_style()
        self._create_widgets()
        self._bind_keys()
        self._center_window()

    # --------------------------------------------------------
    # WINDOW CENTERING
    # --------------------------------------------------------

    def _center_window(self):
        self.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

    # --------------------------------------------------------
    # STYLING
    # --------------------------------------------------------

    def _configure_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Display.TEntry",
            font=("Segoe UI", 22),
            padding=12,
            foreground="#ffffff",
            fieldbackground="#2d2d2d",
            borderwidth=0,
        )

        style.configure(
            "Calc.TButton",
            font=("Segoe UI", 13),
            padding=10,
            background="#3a3a3a",
            foreground="#ffffff",
            borderwidth=0,
        )

        style.map(
            "Calc.TButton",
            background=[("active", "#505050")],
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 13, "bold"),
            background="#007acc",
            foreground="#ffffff",
        )

        style.map(
            "Accent.TButton",
            background=[("active", "#1f8fff")],
        )

    # --------------------------------------------------------
    # UI CONSTRUCTION
    # --------------------------------------------------------

    def _create_widgets(self):
        display = ttk.Entry(
            self,
            textvariable=self.result_var,
            justify="right",
            style="Display.TEntry",
            state="readonly",
        )
        display.grid(row=0, column=0, columnspan=4,
                     sticky="nsew", padx=10, pady=12)

        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "%", "+"],
            ["(", ")", "^", "="],
            ["sin", "cos", "tan", "sqrt"],
            ["log", "pi", "C", "⌫"],
        ]

        for r, row in enumerate(buttons, start=1):
            for c, label in enumerate(row):
                style = "Accent.TButton" if label == "=" else "Calc.TButton"

                ttk.Button(
                    self,
                    text=label,
                    style=style,
                    command=lambda b=label: self._on_button_click(b),
                ).grid(row=r, column=c, sticky="nsew", padx=6, pady=6)

        for i in range(len(buttons) + 1):
            self.grid_rowconfigure(i, weight=1)
        for j in range(4):
            self.grid_columnconfigure(j, weight=1)

    # --------------------------------------------------------
    # KEY BINDINGS
    # --------------------------------------------------------

    def _bind_keys(self):
        self.bind("<Return>", lambda e: self._on_button_click("="))
        self.bind("<BackSpace>", lambda e: self._on_button_click("⌫"))
        self.bind("<Escape>", lambda e: self._on_button_click("C"))

        for ch in "0123456789+-*/().^%":
            self.bind(ch, lambda e, c=ch: self._on_button_click(c))

    # --------------------------------------------------------
    # BUTTON HANDLING
    # --------------------------------------------------------

    def _on_button_click(self, button):
        current = self.result_var.get()

        if button == "=":
            try:
                result = self.evaluator.evaluate(current)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.result_var.set(str(result))
            except Exception:
                self.result_var.set("Error")
            return

        if button == "C":
            self.result_var.set("")
            return

        if button == "⌫":
            self.result_var.set(current[:-1])
            return

        if button in ("sin", "cos", "tan", "sqrt", "log"):
            self.result_var.set(current + f"{button}(")
            return

        if button == "pi":
            self.result_var.set(current + "pi")
            return

        self.result_var.set(current + button)


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()
