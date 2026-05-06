import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

comments_db = []

@strawberry.type
class Comment:
    id: str
    text: str
    author: str

@strawberry.input
class CreateCommentInput:
    text: str
    author: str

@strawberry.type
class Query:
    @strawberry.field
    def comments(self) -> list[Comment]:
        return comments_db
    
    @strawberry.field
    def comment(self, id: str) -> Comment | None:
        for c in comments_db:
            if c.id == id:
                return c
        return None
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_comment(self, input: CreateCommentInput) -> Comment:
        new_comment = Comment(id = str(len(comments_db) + 1), text = input.text, author = input.author)
        comments_db.append(new_comment)
        return new_comment

schema = strawberry.Schema(query=Query, mutation=Mutation)
app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
