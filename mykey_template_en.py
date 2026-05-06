# ══════════════════════════════════════════════════════════════════════════════
#  GenericAgent — mykey.py configuration template (copy to mykey.py and fill in)
# ══════════════════════════════════════════════════════════════════════════════
#
#  ┌─────────────────────────────────────────────────────────────────────────┐
#  │ Quick start: 3 steps                                                     │
#  │  1. Copy this file to mykey.py                                           │
#  │  2. Fill in your apikey in the recommended configs below                 │
#  │  3. Run `python agentmain.py` or `python launch.pyw`                     │
#  └─────────────────────────────────────────────────────────────────────────┘
#
#  ────────── Session type quick reference ──────────
#
#  agentmain.py scans variables whose names contain 'api' / 'config' / 'cookie'
#  and picks the session class by keyword:
#
#      Variable keyword                       → Session class          → Tool protocol
#      ─────────────────────────────────────────────────────────────────────────
#      Contains 'native' + 'claude'          → NativeClaudeSession    → API native tool field
#      Contains 'native' + 'oai'            → NativeOAISession       → API native tool field
#      Contains 'claude' (no 'native')      → ClaudeSession          → text-protocol tools (deprecated)
#      Contains 'oai' (no 'native')         → LLMSession             → text-protocol tools (deprecated)
#      Contains 'mixin'                     → MixinSession           → multi-session failover
#                                                                       NativeClaudeSession and
#                                                                       NativeOAISession can be mixed
#
#  Priority is top-down: native_claude_xxx always becomes NativeClaudeSession.
#  If a variable named oai_claude_xxx still matches 'claude' first, it goes to
#  ClaudeSession. Name your variables to reflect what you intend.
#
#  ────────── Native vs non-Native ──────────
#
#  "Native" = tools are sent in the API's native `tool` field (function calling).
#  This is how Claude Code / Codex do it — models overtrained on the tool field
#  may ignore tool descriptions in any other format. Use Native to emulate CC.
#
#  "Non-Native" = tool descriptions are embedded in the text field (text protocol).
#  More compatible, but weaker for models overtrained on the native tool field
#  (e.g. Claude Opus/Sonnet). Deprecated — prefer Native for new setups.
#
#  → Recommendation: always use native_claude_config / native_oai_config first.
#
#  ────────── Prompt cache ──────────
#
#  NativeClaudeSession always sends the prompt-caching-scope beta header.
#  LLMSession / NativeOAISession auto-add cache_control: ephemeral to the last
#  two user messages when the model name contains 'claude'/'anthropic'.
#  prompt_cache defaults to True. Only set it to False if your upstream relay
#  rejects requests with cache_control fields.
#
# ══════════════════════════════════════════════════════════════════════════════
#  apibase auto-append rules:
#      'http://host:2001'                      → appends /v1/chat/completions
#      'http://host:2001/v1'                   → appends /chat/completions
#      'http://host:2001/v1/chat/completions'  → used as-is
#  NativeClaudeSession additionally appends ?beta=true for the Anthropic beta.
#
# ══════════════════════════════════════════════════════════════════════════════
#  Runtime overrides: in the GA REPL, type
#      /session.reasoning_effort=high
#      /session.thinking_type=adaptive
#      /session.thinking_budget_tokens=32768
#      /session.temperature=0.3
#      /session.max_tokens=16384
#  These setattr on the current session's backend, taking effect immediately
#  until you switch models or restart.
#  reasoning_effort values:  none / minimal / low / medium / high / xhigh
#  thinking_type values:     adaptive / enabled / disabled
#
# ══════════════════════════════════════════════════════════════════════════════
#  Complete field reference (BaseSession.__init__ order)
# ─── Auth / routing ─────────────────────────────────────────────────────────
#   apikey          Required. sk-ant-* prefix → x-api-key header; everything
#                   else (sk-*, cr_*, amp_*…) → Authorization: Bearer.
#                   Auto-detected by NativeClaudeSession.
#   apibase         Required. See auto-append rules above.
#   model           Required. Suffix '[1m]' triggers the context-1m-2025-08-07
#                   beta (stripped from the payload before sending).
#   name            Optional. Display name; also the credential key referenced
#                   by mixin_config['llm_nos']. Defaults to model if omitted.
#   proxy           Optional. Per-session HTTP proxy, e.g. 'http://127.0.0.1:2082'.
#                   If not set, the global proxy (if any) is used.
# ─── Capacity / timeouts ────────────────────────────────────────────────────
#   context_win     Default 24000 (NativeClaudeSession: 28000). History trim
#                   threshold — not a hard context limit.
#   max_retries     Default 1. Number of auto-retries for 429/408/5xx in
#                   the streaming client.
#   connect_timeout Connection timeout in seconds, default 5.
#   read_timeout    Stream read timeout in seconds, default 30.
# ─── Reasoning / thinking ──────────────────────────────────────────────────
#   reasoning_effort  OpenAI o-series or Responses API reasoning budget.
#                     For Claude: mapped to output_config.effort (xhigh → max).
#   thinking_type     Claude native thinking blocks:
#                     'adaptive'  (CC default) → model decides budget
#                     'enabled'                → requires thinking_budget_tokens
#                     'disabled'               → no thinking field sent
#   thinking_budget_tokens  Only effective when thinking_type='enabled'.
#                     Reference: low≈4096, medium≈10240, high≈32768
# ─── Sampling ──────────────────────────────────────────────────────────────
#   temperature     Default 1.0. Kimi/Moonshot forced to 1.0;
#                   MiniMax clamped to (0, 1].
#   max_tokens      Default 8192.
# ─── Transport ─────────────────────────────────────────────────────────────
#   stream          Default True. NativeClaudeSession uses SSE when True,
#                   single JSON response when False. Set False if your relay
#                   drops SSE connections mid-stream.
#   api_mode        'chat_completions' (default) or 'responses'.
#                   Only effective for LLMSession / NativeOAISession.
# ─── NativeClaudeSession exclusive ──────────────────────────────────────────
#   fake_cc_system_prompt
#                   Default False. CRITICAL: set to True for ALL third-party
#                   relays/proxies that mirror Claude Code protocol (CC switch,
#                   anyrouter, claude-relay-service, etc.). Not needed for the
#                   genuine Anthropic endpoint (sk-ant- keys).
#   user_agent      Default 'claude-cli/2.1.113 (external, cli)'.
#                   Override with any version string. Some relays (tabcode,
#                   anyrouter) whitelist by UA; pin an older version here if
#                   CC upgrades and your relay starts rejecting requests.
# ══════════════════════════════════════════════════════════════════════════════


# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                  ★ Recommended setup (start here) ★                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
#  We recommend mixin failover + multiple native sessions.
#  Fill in your apikey/apibase below and you're ready to go.


# ── Mixin failover (most recommended) ──────────────────────────────────────
#  llm_nos entries must match the 'name' field of the sessions they reference
#  (or use integer indices). Constraint: all referenced sessions must all be
#  Native or all non-Native; mixing Native with non-Native is not supported.
mixin_config = {
    'llm_nos': ['gpt-native'],   # priority order; mix Claude and GPT
    # 'llm_nos': ['cc-relay-1', 'cc-relay-2', 'gpt-native'],  # priority order
    'max_retries': 10,           # int; total retry budget across rotation
    'base_delay': 0.5,           # float seconds; exponential backoff start
    # 'spring_back': 300,        # int seconds; delay before falling back to first node
}


# ══════════════════════════════════════════════════════════════════════════════
#  1. NativeClaudeSession — Anthropic native protocol + native tools (preferred)
# ══════════════════════════════════════════════════════════════════════════════
#
#  Most users connect through a CC-switch-adapted Claude relay (not Anthropic
#  direct). These relays forward Claude Code protocol upstream and require
#  fake_cc_system_prompt=True. This is the most common community setup.

# ── 1a. CC switch relay (most common) ───────────────────────────────────────
#  These relays forward Claude Code protocol upstream. apikey formats vary
#  (sk-user-*, sk-*, cr_*, etc.) — all use Bearer auth. Must set
#  fake_cc_system_prompt=True.
# native_claude_config0 = {
#     'name': 'cc-relay-1',                        # display name & mixin reference
#     'apikey': 'sk-user-<your-relay-key>',        # non-sk-ant- prefix → Bearer auth
#     'apibase': 'https://<your-cc-switch-host>/claude/office',   # CC switch endpoint
#     'model': 'claude-opus-4-7',                  # or claude-sonnet-4-6
#     'fake_cc_system_prompt': True,               # REQUIRED for CC relay
#     'thinking_type': 'adaptive',
# }

# native_claude_config1 = {
#     'name': 'cc-relay-2',                        # display name & mixin reference
#     'apikey': 'sk-<your-second-relay-key>',
#     'apibase': 'https://<your-second-host>',
#     'model': 'claude-opus-4-7[1m]',              # [1m] triggers 1M-context beta
#     'fake_cc_system_prompt': True,
#     'thinking_type': 'adaptive',
#     'max_retries': 3,
#     'read_timeout': 300,                         # 1M-context responses may be slower
#     'stream': False,                             # set False if relay drops SSE
#     # 'user_agent': 'claude-cli/2.1.113 (external, cli)',
# }

# ── 1b. Anthropic official direct ───────────────────────────────────────────
#  Official endpoint. apikey starting with sk-ant- → auto x-api-key header.
#  Genuine Anthropic endpoint does NOT need fake_cc_system_prompt.
# native_claude_config_anthropic = {
#     'name': 'anthropic-direct',              # display name & mixin reference
#     'apikey': 'sk-ant-<your-anthropic-key>', # sk-ant- prefix → x-api-key header
#     'apibase': 'https://api.anthropic.com',  # NativeClaudeSession auto-appends ?beta=true
#     'model': 'claude-opus-4-7[1m]',          # [1m] triggers 1M-context beta
#     'thinking_type': 'adaptive',             # 'adaptive' | 'enabled' | 'disabled'
#     # 'thinking_type': 'enabled',
#     # 'thinking_budget_tokens': 32768,       # required if thinking_type='enabled'
#     # 'reasoning_effort': 'high',            # none|minimal|low|medium|high|xhigh
#     'temperature': 1,
#     'max_tokens': 32768,
#     # 'context_win': 800000,
#     # 'stream': True,                        # False → single JSON (when SSE is broken)
#     # 'max_retries': 3,
#     # 'connect_timeout': 10,
#     # 'read_timeout': 180,
#     # 'fake_cc_system_prompt': False,        # not needed for real Anthropic
# }

# ── 1c. CRS relay (Claude Max) ──────────────────────────────────────────────
#  CRS requires fake_cc_system_prompt=True
# native_claude_config_crs = {
#     'name': 'crs-claude-max',                # display name
#     'apikey': 'cr_<your-crs-key>',           # cr_ prefix → Bearer auth (64 hex chars)
#     'apibase': 'https://<your-crs-host>/api',# CRS Anthropic-compatible path
#     'model': 'claude-opus-4-7[1m]',          # [1m] triggers 1M beta
#     'fake_cc_system_prompt': True,           # REQUIRED; CRS validates CC system prompt
#     'thinking_type': 'adaptive',
#     # 'reasoning_effort': 'high',
#     'max_tokens': 32768,
#     'max_retries': 3,
#     'read_timeout': 180,
# }

# ── 1d. CRS Gemini Ultra (Antigravity channel) ──────────────────────────────
#  CRS wraps Google Antigravity (Gemini Ultra) as an Anthropic-style interface.
#  ⚠ This channel does NOT support SSE streaming — must set stream=False.
# native_claude_config_crs_gemini = {
#     'name': 'crs-gemini-ultra',              # display name
#     'apikey': 'cr_<your-crs-gemini-key>',    # cr_ prefix → Bearer
#     'apibase': 'https://<your-crs-gemini-host>/antigravity/api',
#     'model': 'claude-opus-4-7-thinking',     # or 'claude-opus-4-7[1m]' or 'claude-opus-4-7'
#     'stream': False,                         # Antigravity does not support SSE
#     'max_tokens': 32768,
#     'max_retries': 3,
#     'read_timeout': 180,
# }

# ── 1e. Zhipu GLM-5.1 (Anthropic-compatible protocol) ──────────────────────
#  Zhipu provides an Anthropic-compatible endpoint at /api/anthropic.
#  Variable name must contain 'native' + 'claude'. apikey is Zhipu format (xxx.yyy).
# native_claude_glm_config = {
#     'name': 'glm-5.1',                               # display name
#     'apikey': '<your-zhipu-apikey>',                 # e.g. f0f1b798xxxx.F8SSbzxxxx; non-sk-ant → Bearer
#     'apibase': 'https://open.bigmodel.cn/api/anthropic',  # Zhipu Anthropic-compatible endpoint
#     'model': 'glm-5.1',
#     'max_retries': 3,
#     'connect_timeout': 10,
#     'read_timeout': 180,
#     # 'fake_cc_system_prompt': False,                # Zhipu does not validate CC fingerprint
# }

# ── 1f. MiniMax Anthropic path (recommended — no extra <think> tags) ────────
#  MiniMax offers both OAI and Anthropic-compatible endpoints (same key):
#    - /v1             → chat/completions (LLMSession)
#    - /anthropic      → Anthropic Messages (NativeClaudeSession)
#  Anthropic path is cleaner; OAI path may return <think> tags (M2.7 built-in
#  thinking). Temperature auto-clamped to (0, 1]. Supports M2.7 / M2.5, 204K ctx.
# native_claude_config_minimax = {
#     'name': 'minimax-anthropic',                   # display name
#     'apikey': 'sk-<your-minimax-key>',             # same key as OAI path
#     'apibase': 'https://api.minimaxi.com/anthropic',  # Anthropic Messages endpoint
#     'model': 'MiniMax-M2.7',
#     'max_retries': 3,
#     # 'fake_cc_system_prompt': False,              # MiniMax does not validate CC fingerprint
# }

# ── 1g. Kimi for Coding (Anthropic-compatible CC relay) ────────────────────
#  Kimi's official /coding path for Claude Code / Codex, using Anthropic protocol.
#  Different from the Moonshot OAI path (section 2b): model uses 'kimi-for-coding'.
#  Official requirement: must relay CC system prompt → fake_cc_system_prompt=True.
#  Docs: https://www.kimi.com/code/docs/third-party-tools/other-coding-agents.html
# native_claude_config_kimi = {
#     'name': 'kimi-coding',                   # display name & mixin reference
#     'apikey': 'sk-kimi-<your-kimi-coding-key>',  # Bearer auth
#     'apibase': 'https://api.kimi.com/coding',# Anthropic-compatible endpoint
#     'model': 'kimi-for-coding',              # official coding model id
#     'fake_cc_system_prompt': True,           # REQUIRED; official hard requirement
#     'thinking_type': 'adaptive',
# }

# ══════════════════════════════════════════════════════════════════════════════
#  2. NativeOAISession — OpenAI protocol + native tools
# ══════════════════════════════════════════════════════════════════════════════
#  Variable name must contain 'native' + 'oai'. Uses OpenAI chat/completions or
#  responses endpoints with native function-calling tool fields (matching the
#  Claude Code / Codex approach). Suitable for GPT/o-series, Gemini, or any
#  OAI-compatible provider with native tool support.

native_oai_config = {
    'name': 'gpt-native',                           # display name & mixin reference
    'apikey': 'sk-<your-openai-key>',                # Bearer auth
    'apibase': 'https://api.openai.com/v1',          # auto-appends /chat/completions
    'model': 'gpt-5.4',                              # gpt-5 / o-series
    'api_mode': 'chat_completions',                  # 'chat_completions' (default) | 'responses'
    # 'reasoning_effort': 'high',                    # none|minimal|low|medium|high|xhigh
    'max_retries': 3,
    'connect_timeout': 10,
    'read_timeout': 120,
    # 'temperature': 1.0,
    # 'max_tokens': 8192,
    # 'proxy': 'http://127.0.0.1:2082',
    # 'context_win': 16000,
}

# ── Responses API variant ───────────────────────────────────────────────────
#  Targets OpenAI /v1/responses. reasoning_effort is written as
#  payload.reasoning.effort in responses mode; /session.reasoning_effort=high
#  overrides it at runtime.
# native_oai_config_responses = {
#     'name': 'gpt-responses',                       # display name
#     'apikey': 'sk-<your-openai-key>',
#     'apibase': 'https://api.openai.com/v1',        # auto-appends /responses (api_mode=responses)
#     'model': 'gpt-5.4',
#     'api_mode': 'responses',
#     'reasoning_effort': 'high',
#     'max_retries': 2,
#     'read_timeout': 120,
# }


# ══════════════════════════════════════════════════════════════════════════════
#  3. Legacy non-Native sessions (LLMSession / ClaudeSession) — deprecated
# ══════════════════════════════════════════════════════════════════════════════
#  ⚠ May be removed in a future version. New users should use Native configs.
#  Non-Native embeds tool descriptions in the text field — more compatible but
#  weaker for models overtrained on native tool fields.
#  Variable name containing 'oai' (no 'native') → LLMSession
#  Variable name containing 'claude' (no 'native') → ClaudeSession
#
# oai_config = {
#     'name': 'my-oai-proxy',
#     'apikey': 'sk-<your-proxy-key>',
#     'apibase': 'http://<your-proxy-host>:2001',      # auto-appends /v1/chat/completions
#     'model': 'gpt-5.4',                              # or claude-opus-4-7, gemini-3-flash, etc.
#     'api_mode': 'chat_completions',
#     # 'reasoning_effort': 'high',
#     'max_retries': 3,
#     'connect_timeout': 10,
#     'read_timeout': 120,
# }


# ══════════════════════════════════════════════════════════════════════════════
#  4. Other Native-compatible providers
# ══════════════════════════════════════════════════════════════════════════════

# ── 4a. MiniMax OAI path (/v1 chat/completions) ────────────────────────────
#  OAI path may return <think> tags (M2.7 built-in thinking). Anthropic path
#  (1f) is cleaner. Temperature auto-clamped to (0, 1]. Supports M2.7/M2.5, 204K ctx.
# oai_config_minimax = {
#     'name': 'minimax-oai',
#     'apikey': 'sk-<your-minimax-key>',               # e.g. sk-cp-xxxxxxxxx; Bearer auth
#     'apibase': 'https://api.minimaxi.com/v1',        # OAI-compatible endpoint
#     'model': 'MiniMax-M2.7',                         # name contains 'minimax' → temp clamped to (0.01, 1.0]
#     'context_win': 50000,
# }

# ── 4b. Kimi / Moonshot (OAI-compatible) ───────────────────────────────────
#  Note: Kimi/Moonshot temperature is forced to 1.0 by llmcore.py regardless
#  of what you set here.
# oai_config_kimi = {
#     'name': 'kimi-k2',
#     'apikey': 'sk-<your-moonshot-key>',            # Bearer auth
#     'apibase': 'https://api.moonshot.cn/v1',       # Moonshot OAI endpoint
#     'model': 'kimi-k2-turbo-preview',              # name contains 'kimi'/'moonshot' → temp forced 1.0
#     # 'temperature': 0.3,                          # ← ignored; llmcore overrides to 1.0
# }

# ── 4c. OpenRouter (OAI protocol multi-model relay) ─────────────────────────
#  OpenRouter is the most general multi-model OAI relay: https://openrouter.ai/api/v1
#  Use provider/model format for the model field (e.g. anthropic/claude-opus-4-7).
# oai_config_openrouter = {
#     'name': 'openrouter-claude',                   # display name & mixin reference
#     'apikey': 'sk-or-<your-openrouter-key>',       # OpenRouter key format: sk-or-xxx; Bearer auth
#     'apibase': 'https://openrouter.ai/api/v1',     # auto-appends /chat/completions
#     'model': 'anthropic/claude-opus-4-7',          # provider/model format
#     'max_retries': 3,
#     'connect_timeout': 10,
#     'read_timeout': 120,
# }


# ══════════════════════════════════════════════════════════════════════════════
#  Global HTTP proxy (shared by all sessions that don't set their own 'proxy')
# ══════════════════════════════════════════════════════════════════════════════
# proxy = 'http://127.0.0.1:2082'


# ══════════════════════════════════════════════════════════════════════════════
#  Chat platform integrations (optional; unset entries won't start adapters)
# ══════════════════════════════════════════════════════════════════════════════
# tg_bot_token = '84102K2gYZ...'
# tg_allowed_users = [6806...]
# qq_app_id = '123456789'
# qq_app_secret = 'xxxxxxxxxxxxxxxx'
# qq_allowed_users = ['your_user_openid']           # omit or ['*'] to allow all QQ users
# fs_app_id = 'cli_xxxxxxxxxxxxxxxx'
# fs_app_secret = 'xxxxxxxxxxxxxxxx'
# fs_allowed_users = ['ou_xxxxxxxxxxxxxxxx']        # omit or ['*'] to allow all Feishu users
# wecom_bot_id = 'your_bot_id'
# wecom_secret = 'your_bot_secret'
# wecom_allowed_users = ['your_user_id']            # omit or ['*'] to allow all WeCom users
# wecom_welcome_message = 'Hello, I am online.'
# dingtalk_client_id = 'your_app_key'
# dingtalk_client_secret = 'your_app_secret'
# dingtalk_allowed_users = ['your_staff_id']        # omit or ['*'] to allow all DingTalk users

# Optional: Langfuse tracing. No impact when not set.
# langfuse_config = {
#     'public_key': 'pk-lf-...',
#     'secret_key': 'sk-lf-...',
#     'host': 'https://cloud.langfuse.com',   # or self-hosted address
# }
