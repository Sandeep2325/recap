"""
MCP (Model Context Protocol) server over Streamable HTTP.

Clients POST JSON-RPC 2.0 messages to /mcp/ and get JSON responses back.
"""
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .tools import TOOLS, ToolError

SERVER_INFO = {'name': 'django-members', 'version': '1.0.0'}
SUPPORTED_VERSIONS = ['2025-06-18', '2025-03-26', '2024-11-05']

# JSON-RPC error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602


class RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def handle_initialize(params):
    requested = params.get('protocolVersion')
    version = requested if requested in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
    return {
        'protocolVersion': version,
        'capabilities': {'tools': {'listChanged': False}},
        'serverInfo': SERVER_INFO,
    }


def handle_tools_list(params):
    return {
        'tools': [
            {'name': name, 'description': t['description'], 'inputSchema': t['inputSchema']}
            for name, t in TOOLS.items()
        ]
    }


def handle_tools_call(params):
    name = params.get('name')
    if name not in TOOLS:
        raise RpcError(INVALID_PARAMS, f'Unknown tool: {name}')

    try:
        result = TOOLS[name]['handler'](**(params.get('arguments') or {}))
    except (ToolError, TypeError) as e:
        # Tool failures are reported inside the result so the model can see them.
        return {'content': [{'type': 'text', 'text': str(e)}], 'isError': True}

    return {
        'content': [{'type': 'text', 'text': json.dumps(result, default=str, indent=2)}],
        'isError': False,
    }


METHODS = {
    'initialize': handle_initialize,
    'ping': lambda params: {},
    'tools/list': handle_tools_list,
    'tools/call': handle_tools_call,
}


def process_message(message):
    """Handle one JSON-RPC message. Returns a response dict, or None for notifications."""
    if not isinstance(message, dict) or message.get('jsonrpc') != '2.0':
        return {'jsonrpc': '2.0', 'id': None,
                'error': {'code': INVALID_REQUEST, 'message': 'Invalid request'}}

    msg_id = message.get('id')
    method = message.get('method')

    # Notifications (e.g. notifications/initialized) and client responses have no reply.
    if msg_id is None or method is None:
        return None

    try:
        if method not in METHODS:
            raise RpcError(METHOD_NOT_FOUND, f'Method not found: {method}')
        result = METHODS[method](message.get('params') or {})
    except RpcError as e:
        return {'jsonrpc': '2.0', 'id': msg_id, 'error': {'code': e.code, 'message': e.message}}

    return {'jsonrpc': '2.0', 'id': msg_id, 'result': result}


@csrf_exempt
def mcp_endpoint(request):
    if request.method != 'POST':
        # This server does not open server-initiated SSE streams.
        return HttpResponse(status=405, headers={'Allow': 'POST'})

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'jsonrpc': '2.0', 'id': None,
                             'error': {'code': PARSE_ERROR, 'message': 'Parse error'}}, status=400)

    if isinstance(payload, list):
        responses = [r for r in map(process_message, payload) if r is not None]
    else:
        responses = process_message(payload)

    if not responses:
        return HttpResponse(status=202)
    return JsonResponse(responses, safe=False)
