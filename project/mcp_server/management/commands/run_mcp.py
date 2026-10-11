from django.core.management.base import BaseCommand

from mcp_server.server import mcp


class Command(BaseCommand):
    help = 'Run the MCP server (stdio by default, or streamable HTTP).'

    def add_arguments(self, parser):
        parser.add_argument('--transport', choices=['stdio', 'streamable-http'], default='stdio')
        parser.add_argument('--host', default='127.0.0.1')
        parser.add_argument('--port', type=int, default=8001)

    def handle(self, *args, **options):
        if options['transport'] == 'stdio':
            # stdout carries the protocol, so don't print anything else here.
            mcp.run('stdio')
        else:
            self.stderr.write(f"MCP server on http://{options['host']}:{options['port']}/mcp")
            mcp.run('streamable-http', host=options['host'], port=options['port'])
