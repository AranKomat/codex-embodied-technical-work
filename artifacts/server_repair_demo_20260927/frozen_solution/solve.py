def solve(env) -> None:
    """Diagnose the missing GPU, install it using robot actions, and verify health."""
    try:
        from server_diagnostics import server_exec
    except ModuleNotFoundError:
        from _diagnostic_adapter import server_exec
    from stages import stage_1,stage_2,stage_3
    for command in ('nvidia-smi','lspci','healthcheck'):
        print(server_exec(env,command),flush=True)
    if bool(env.scene.success().all()):return
    for stage in (stage_1,stage_2,stage_3):
        stage.run(env)
        if not stage.check(env):
            print(server_exec(env,'healthcheck'),flush=True)
            return
    print(server_exec(env,'healthcheck'),flush=True)
    print('Physical verification: seated, released, and gripper clear.',flush=True)
