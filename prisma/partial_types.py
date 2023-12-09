from prisma.models import Event, Show

Show.create_partial("ShowWithoutRelations", exclude_relational_fields=True)
Event.create_partial("EventWithoutRelations", exclude_relational_fields=True)
