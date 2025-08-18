import graphene


class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"


# Create the schema instance
schema = graphene.Schema(query=Query)