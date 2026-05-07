# ══════════════════════════════════════════════════════════════════════════════
#  GenericAgent — mykey.py configuration template (copy to mykey.py and fill in)
# ══════════════════════════════════════════════════════════════════════════════
#
#  Quick start:
#    1. Copy this file to mykey.py
#    2. Fill in ONE working config below
#    3. Run `python agentmain.py` or `python launch.pyw`
#
#  Config discovery:
#  GA scans variables whose names contain 'api' / 'config' / 'cookie'. The
#  variable name decides the Session type:
#
#      name contains                    → Session class        → Tool protocol
#      ─────────────────────────────────────────────────────────────────────
#      'native' + 'claude'              → NativeClaudeSession  → API native tools
#      'native' + 'oai'                 → NativeOAISession     → API native tools
#      'mixin'                          → MixinSession         → failover wrapper
#      'claude' without 'native'        → ClaudeSession        → text tools (legacy)
#      'oai' without 'native'           → LLMSession           → text tools (legacy)
#
#  Prefer Native sessions for new setups. Native means tools are sent through
#  the model provider's official tool/function-calling field, which works best
#  with Claude, GPT, Gemini, and other modern tool-trained models.
#
#  Runtime overrides in the REPL:
#      /session.reasoning_effort=high
#      /session.thinking_type=adaptive
#      /session.temperature=0.3
#      /session.max_tokens=16384
#
#  apibase auto-append rules:
#      http://host:2001                     → /v1/chat/completions is appended
#      http://host:2001/v1                  → /chat/completions is appended
#      http://host:2001/v1/chat/completions → used as-is
#
#  Common fields:
#    name            Display name; also used by mixin_config['llm_nos'].
#    apikey          Required. sk-ant-* uses x-api-key; others use Bearer auth.
#    apibase         Required. Base URL or full endpoint; see auto-append rules.
#    model           Required. Claude model suffix '[1m]' enables the 1M beta.
#    context_win     History trimming threshold, not a hard model context limit.
#    max_tokens      Max response tokens; default is 8192.
#    max_retries     Retry budget for transient HTTP failures.
#    read_timeout    Stream read timeout in seconds.
#    proxy           Per-session HTTP proxy; global proxy is defined near bottom.
#
# ══════════════════════════════════════════════════════════════════════════════


# ── 1. NativeClaudeSession — Anthropic or Anthropic-compatible endpoint ──────
# Official Anthropic direct usage: use an sk-ant-* key and keep
# fake_cc_system_prompt disabled/omitted.
#
# For Claude Code protocol relays / CC switch style gateways, use the same
# NativeClaudeSession shape but set fake_cc_system_prompt=True and point apibase
# at the relay endpoint.
native_claude_config = {
    'name': 'claude',                         # display name & mixin reference
    'apikey': 'sk-ant-<your-anthropic-key>',
    'apibase': 'https://api.anthropic.com',
    'model': 'claude-opus-4-7[1m]',           # or 'claude-sonnet-4-6'
    'thinking_type': 'adaptive',              # 'adaptive' | 'enabled' | 'disabled'
    # 'thinking_budget_tokens': 32768,        # required if thinking_type='enabled'
    # 'reasoning_effort': 'high',             # low | medium | high | xhigh
    # 'max_tokens': 32768,
    # 'max_retries': 3,
    # 'read_timeout': 180,
    # 'fake_cc_system_prompt': True,          # only for CC-style relays
}


# ── 2. NativeOAISession — OpenAI or OpenAI-compatible endpoint ───────────────
# Uses native function calling. Good for OpenAI, Gemini-through-OAI-compatible
# providers, and relays that support the standard tool_calls field.
native_oai_config = {
    'name': 'gpt',                            # display name & mixin reference
    'apikey': 'sk-<your-openai-key>',
    'apibase': 'https://api.openai.com/v1',
    'model': 'gpt-5.4',                       # or 'o4', 'gpt-5.3-codex', etc.
    'api_mode': 'chat_completions',           # or 'responses' for /v1/responses
    # 'reasoning_effort': 'high',             # none|minimal|low|medium|high|xhigh
    # 'max_retries': 3,
    # 'read_timeout': 120,
}


# ── 3. Mixin failover (optional) ─────────────────────────────────────────────
# List sessions by their 'name'. If one fails, the next is tried automatically.
# Constraint: all referenced sessions must be Native, or all must be legacy;
# mixing Native and non-Native sessions in one mixin is not supported.
# mixin_config = {
#     'llm_nos': ['claude', 'gpt'],
#     'max_retries': 5,
#     'base_delay': 0.5,
#     # 'spring_back': 300,                   # seconds before retrying first node
# }


# ── 4. Legacy text-protocol sessions (not recommended for new setups) ────────
# Kept for compatibility with older relays. Prefer Native sessions above.
# oai_config = {
#     'name': 'legacy-oai',
#     'apikey': 'sk-<your-key>',
#     'apibase': 'http://<your-proxy-host>:2001',
#     'model': 'gpt-5.4',
# }


# ── 5. Global HTTP proxy (optional) ──────────────────────────────────────────
# Applies to every session that doesn't set its own 'proxy' field.
# proxy = 'http://127.0.0.1:7890'


# ── 6. Chat platform integrations (optional) ─────────────────────────────────
# Unset platforms are ignored by their corresponding frontend scripts.
# tg_bot_token = '...'
# tg_allowed_users = [123456789]
# qq_app_id = '123456789'
# qq_app_secret = '...'
# qq_allowed_users = ['your_user_openid']      # omit or ['*'] to allow all users
# fs_app_id = 'cli_xxxxxxxxxxxxxxxx'
# fs_app_secret = '...'
# fs_allowed_users = ['ou_xxxxxxxxxxxxxxxx']   # omit or ['*'] to allow all users
# wecom_bot_id = 'your_bot_id'
# wecom_secret = '...'
# wecom_allowed_users = ['your_user_id']       # omit or ['*'] to allow all users
# dingtalk_client_id = 'your_app_key'
# dingtalk_client_secret = '...'
# dingtalk_allowed_users = ['your_staff_id']   # omit or ['*'] to allow all users


# ── 7. Optional tracing ──────────────────────────────────────────────────────
# langfuse_config = {
#     'public_key': 'pk-lf-...',
#     'secret_key': 'sk-lf-...',
#     'host': 'https://cloud.langfuse.com',
# }
