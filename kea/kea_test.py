import inspect
from typing import Callable, Any, Union, TYPE_CHECKING
from .kea import Rule, MainPath, Initializer, LLMTask
from .utils import PRECONDITIONS_MARKER, RULE_MARKER, INITIALIZER_MARKER, MAINPATH_MARKER, LLMTASK_MARKER

if TYPE_CHECKING:
    from .android_pdl_driver import Android_PDL_Driver
    from .harmonyos_pdl_driver import HarmonyOS_PDL_Driver
    from .kea import Rule, MainPath

class KeaTest:
    """Each app property to be tested inherits from KeaTest

    In the future, app-agnostic properties (e.g., data loss detectors) 
    can be implemented in KeaTest so that the Kea users can directly 
    reuse these properties for functional validation.
    """
    pass

# `d` is the pdl driver for Android or HarmonyOS
d:Union["Android_PDL_Driver", "HarmonyOS_PDL_Driver", None] = None

def rule() -> Callable:
    """the decorator @rule

    A rule denotes an app property.
    """
    def accept(f):
        precondition = getattr(f, PRECONDITIONS_MARKER, ())
        rule = Rule(function=f, preconditions=precondition)

        def rule_wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        setattr(rule_wrapper, RULE_MARKER, rule)
        return rule_wrapper

    return accept


def precondition(precond: Callable[[Any], bool]) -> Callable:
    """the decorator @precondition

    The precondition specifies when the property could be executed.
    A property could have multiple preconditions, each of which is specified by @precondition.
    """
    def accept(f):
        def precondition_wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        rule:"Rule" = getattr(f, RULE_MARKER, None)
        if rule is not None:
            new_rule = rule.evolve(preconditions=rule.preconditions + (precond,))
            # new_rule = attr.evolve(rule, preconditions=rule.preconditions + (precond,))
            setattr(precondition_wrapper, RULE_MARKER, new_rule)
        else:
            setattr(
                precondition_wrapper,
                PRECONDITIONS_MARKER,
                getattr(f, PRECONDITIONS_MARKER, ()) + (precond,),
            )
        return precondition_wrapper

    return accept

def initializer():
    '''the decorator @initializer

    An initialize decorator behaves like a rule, but all ``@initializer()`` decorated
    methods will be called before any ``@rule()`` decorated methods, in an arbitrary
    order.  Each ``@initializer()`` method will be called exactly once per run, unless
    one raises an exception.
    '''

    def accept(f):
        def initialize_wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        initializer_func = Initializer(function=f)
        #rule = Rule(function=f, preconditions=())
        setattr(initialize_wrapper, INITIALIZER_MARKER, initializer_func)
        return initialize_wrapper

    return accept

def mainPath():
    """the decorator @mainPath

    A main path specifies a sequence of events which can lead to the UI state where 
    the preconditions of a rule hold.
    """
    def accept(f):
        def mainpath_wrapper(*args, **kwargs):
            source_code = inspect.getsource(f)
            code_lines = [line.strip() for line in source_code.splitlines() if line.strip()]
            code_lines = [line for line in code_lines if not line.startswith('def ') and not line.startswith('@') and not line.startswith('#')]
            return code_lines

        main_path = MainPath(function=f, path=mainpath_wrapper())
        setattr(mainpath_wrapper, MAINPATH_MARKER, main_path)
        return mainpath_wrapper

    return accept



def llmTask(description: str) -> Callable:
    """the decorator @llmTask

    用自然语言描述测试脚本的任务目标和验证目的。
    示例：
    @llmTask("验证用户登录功能，确保输入错误密码时显示提示信息")
    @rule()
    def test_login_failure(self):
        ...
    """

    def accept(func: Callable) -> Callable:
        # 创建LLMTask实例并附加到函数属性
        task = LLMTask(description=description, function=func)
        setattr(func, LLMTASK_MARKER, task)
        return func

    return accept
