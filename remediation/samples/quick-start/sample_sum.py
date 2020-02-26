from jsonreme.consts import WS_OUTPUT


def sum_k(target, companion, params, workspace):
    if WS_OUTPUT not in workspace:
        workspace[WS_OUTPUT] = 0
    workspace[WS_OUTPUT] += target
