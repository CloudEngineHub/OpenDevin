from openhands.core.config import OpenHandsConfig
from openhands.runtime.plugins import PluginRequirement

DEFAULT_PYTHON_PREFIX = [
    '/openhands/micromamba/bin/micromamba',
    'run',
    '-n',
    'openhands',
    'poetry',
    'run',
]
DEFAULT_MAIN_MODULE = 'openhands.runtime.action_execution_server'


def get_action_execution_server_startup_command(
    server_port: int,
    plugins: list[PluginRequirement],
    app_config: OpenHandsConfig,
    python_prefix: list[str] = DEFAULT_PYTHON_PREFIX,
    override_user_id: int | None = None,
    override_username: str | None = None,
    main_module: str = DEFAULT_MAIN_MODULE,
    python_executable: str = 'python',
) -> list[str]:
    sandbox_config = app_config.sandbox

    # Plugin args
    plugin_args = []
    if plugins is not None and len(plugins) > 0:
        plugin_args = ['--plugins'] + [plugin.name for plugin in plugins]

    # Browsergym stuffs
    browsergym_args = []
    if sandbox_config.browsergym_eval_env is not None:
        browsergym_args = [
            '--browsergym-eval-env'
        ] + sandbox_config.browsergym_eval_env.split(' ')

    username = override_username or (
        'openhands' if app_config.run_as_openhands else 'root'
    )
    user_id = override_user_id or (
        sandbox_config.user_id if app_config.run_as_openhands else 0
    )

    base_cmd = [
        *python_prefix,
        python_executable,
        '-u',
        '-m',
        main_module,
        str(server_port),
        '--working-dir',
        app_config.workspace_mount_path_in_sandbox,
        *plugin_args,
        '--username',
        username,
        '--user-id',
        str(user_id),
        '--git-user-name',
        app_config.git_user_name,
        '--git-user-email',
        app_config.git_user_email,
        *browsergym_args,
    ]

    if not app_config.enable_browser:
        base_cmd.append('--no-enable-browser')

    return base_cmd
