from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "location"."terrain" IS 'plains: plains
forest: forest
swamp: swamp';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "location"."terrain" IS 'plains: plains
forest: forest';"""


MODELS_STATE = (
    "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"
)
