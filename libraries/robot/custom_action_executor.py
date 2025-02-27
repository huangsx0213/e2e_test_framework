import ast
from typing import Any, Dict
import inspect


class CustomActionExecutor:
    def __init__(self, custom_actions: Dict[str, str]):
        self.custom_actions = custom_actions
        self.parsed_actions = {}

    def execute_custom_action(self, action_name: str, element=None, web_actions=None, *args, **kwargs):
        if action_name not in self.custom_actions:
            raise ValueError(f"Custom action '{action_name}' not found")

        if action_name not in self.parsed_actions:
            code = self.custom_actions[action_name]
            try:
                parsed = ast.parse(code)
                # self._check_code_safety(parsed, action_name)
                self.parsed_actions[action_name] = code
            except SyntaxError:
                raise ValueError(f"Syntax error in custom action '{action_name}'")

        # 创建一个新的命名空间来执行代码
        namespace = {'element': element, 'web_action': web_actions, **kwargs}
        exec(self.parsed_actions[action_name], namespace)

        if 'execute' not in namespace:
            raise ValueError(f"Custom action '{action_name}' must define an 'execute' function")

        execute_func = namespace['execute']
        sig = inspect.signature(execute_func)

        # 检查 execute 函数是否需要 element 参数
        if 'element' in sig.parameters:
            return execute_func(element, web_actions, *args, **kwargs)
        else:
            return execute_func(web_actions, *args, **kwargs)

    def _check_code_safety(self, node, action_name):
        allowed_nodes = (
            ast.Module,
            ast.FunctionDef,
            ast.ClassDef,
            ast.Return,
            ast.Expr,
            ast.Call,
            ast.Name,
            ast.Attribute,
            ast.arguments,
            ast.arg,
            ast.Constant,
            ast.List,
            ast.Dict,
            ast.If,
            ast.For,
            ast.While,
            ast.Compare,
            ast.BinOp,
            ast.UnaryOp,
            ast.Assign,
            ast.AugAssign,
            ast.Break,
            ast.Continue,
            ast.Pass,
        )

        if not isinstance(node, allowed_nodes):
            raise ValueError(f"Unsupported Python construct in custom action '{action_name}': {type(node).__name__}")

        # 递归检查子节点
        # for child in ast.iter_child_nodes(node):
        #     self._check_code_safety(child, action_name)

        # 检查是否使用了不允许的内建函数
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            disallowed_builtins = {'eval', 'exec', 'compile', '__import__', 'open'}
            if node.func.id in disallowed_builtins:
                raise ValueError(f"Use of '{node.func.id}' is not allowed in custom action '{action_name}'")