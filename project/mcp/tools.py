from django.db.models import Q

from api.serializers import MemberSerializer
from app1.models import Member


class ToolError(Exception):
    """Raised by a tool to report a failure back to the MCP client."""


MEMBER_FIELDS = {
    'firstname': {'type': 'string', 'description': 'First name'},
    'lastname': {'type': 'string', 'description': 'Last name'},
    'phone': {'type': 'integer', 'description': 'Phone number'},
    'joined_date': {'type': 'string', 'description': 'Join date (YYYY-MM-DD)'},
}


def _get_member(id):
    try:
        return Member.objects.get(id=id)
    except Member.DoesNotExist:
        raise ToolError(f'Member with id {id} not found')


def _save(serializer):
    if not serializer.is_valid():
        raise ToolError(f'Invalid data: {serializer.errors}')
    serializer.save()
    return serializer.data


def list_members(query=''):
    members = Member.objects.all().order_by('id')
    if query:
        members = members.filter(
            Q(firstname__icontains=query) | Q(lastname__icontains=query)
        )
    return MemberSerializer(members, many=True).data


def get_member(id):
    return MemberSerializer(_get_member(id)).data


def create_member(**fields):
    return _save(MemberSerializer(data=fields))


def update_member(id, **fields):
    return _save(MemberSerializer(_get_member(id), data=fields, partial=True))


def delete_member(id):
    member = _get_member(id)
    member.delete()
    return {'deleted': True, 'id': id}


TOOLS = {
    'list_members': {
        'handler': list_members,
        'description': 'List all members, optionally filtered by first or last name.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'query': {'type': 'string', 'description': 'Text to search in first/last name'},
            },
        },
    },
    'get_member': {
        'handler': get_member,
        'description': 'Get a single member by id.',
        'inputSchema': {
            'type': 'object',
            'properties': {'id': {'type': 'integer'}},
            'required': ['id'],
        },
    },
    'create_member': {
        'handler': create_member,
        'description': 'Create a new member.',
        'inputSchema': {
            'type': 'object',
            'properties': MEMBER_FIELDS,
            'required': ['firstname', 'lastname'],
        },
    },
    'update_member': {
        'handler': update_member,
        'description': 'Update fields of an existing member. Only the given fields are changed.',
        'inputSchema': {
            'type': 'object',
            'properties': {'id': {'type': 'integer'}, **MEMBER_FIELDS},
            'required': ['id'],
        },
    },
    'delete_member': {
        'handler': delete_member,
        'description': 'Delete a member by id.',
        'inputSchema': {
            'type': 'object',
            'properties': {'id': {'type': 'integer'}},
            'required': ['id'],
        },
    },
}
