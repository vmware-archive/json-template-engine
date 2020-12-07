from jsonreme.consts import WS_OUTPUT


def before_my_key_1(target, companion, params, workspace):
    workspace[WS_OUTPUT]['before_my_key_1'] = f"reme: path {workspace['__crp']} {target}"


def after_my_key_1(target, companion, params, workspace):
    workspace[WS_OUTPUT]['after_my_key_1'] = f"reme: path {workspace['__crp']} {target}"


def after_my_sub_key_1_(target, companion, params, workspace):
    workspace[WS_OUTPUT]['after_my_sub_key_1_'] = f"reme: path {workspace['__crp']} {target}"


def after_my_sub_key_1_0(target, companion, params, workspace):
    workspace[WS_OUTPUT]['after_my_sub_key_1_0'] = f"reme: path {workspace['__crp']} {target}"


def after_my_sub_key_1_1(target, companion, params, workspace):
    workspace[WS_OUTPUT]['after_my_sub_key_1_1'] = f"reme: path {workspace['__crp']} {target}"


def after_my_sub_key_1_2(target, companion, params, workspace):
    workspace[WS_OUTPUT]['after_my_sub_key_1_2'] = f"reme: path {workspace['__crp']} {target}"


def after_my_sub_key_2(target, companion, params, workspace):
    workspace[WS_OUTPUT]['after_my_sub_key_1_2'] = f"reme: path {workspace['__crp']} {target}"
