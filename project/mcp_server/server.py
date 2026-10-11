"""
MCP server exposing the Member model as tools.

Run it with:  python manage.py run_mcp
"""
from django.db.models import Q
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from api.serializers import MemberSerializer
from app1.models import Member

mcp = MCPServer('django-members', instructions='Manage club members stored in the Django database.')


def _get_member(id):
    try:
        return Member.objects.get(id=id)
    except Member.DoesNotExist:
        raise ToolError(f'Member with id {id} not found')


def _save(serializer):
    if not serializer.is_valid():
        raise ToolError(f'Invalid data: {serializer.errors}')
    serializer.save()
    return dict(serializer.data)


def _fields(**fields):
    """Drop arguments the caller did not pass."""
    return {k: v for k, v in fields.items() if v is not None}


@mcp.tool()
def list_members(query: str = '') -> list[dict]:
    """List all members, optionally filtered by first or last name."""
    members = Member.objects.all().order_by('id')
    if query:
        members = members.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        )
    return [dict(m) for m in MemberSerializer(members, many=True).data]


@mcp.tool()
def get_member(id: int) -> dict:
    """Get a single member by id."""
    return dict(MemberSerializer(_get_member(id)).data)


@mcp.tool()
def create_member(firstname: str, lastname: str, phone: int | None = None,
                  joined_date: str | None = None) -> dict:
    """Create a new member. joined_date must be YYYY-MM-DD."""
    data = _fields(firstname=firstname, lastname=lastname, phone=phone, joined_date=joined_date)
    return _save(MemberSerializer(data=data))


@mcp.tool()
def update_member(id: int, firstname: str | None = None, lastname: str | None = None,
                  phone: int | None = None, joined_date: str | None = None) -> dict:
    """Update fields of an existing member. Only the given fields are changed."""
    data = _fields(firstname=firstname, lastname=lastname, phone=phone, joined_date=joined_date)
    return _save(MemberSerializer(_get_member(id), data=data, partial=True))


@mcp.tool()
def delete_member(id: int) -> dict:
    """Delete a member by id."""
    _get_member(id).delete()
    return {'deleted': True, 'id': id}
