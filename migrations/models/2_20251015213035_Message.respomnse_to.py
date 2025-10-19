from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "message" ADD "response_to" UUID;
        COMMENT ON COLUMN "message"."type" IS 'heartbeat_response: heartbeat_response
heartbeat_request: heartbeat_request
user_log: user_log
state_sync: state_sync
command: command
command_result: command_result';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "message" DROP COLUMN "response_to";
        COMMENT ON COLUMN "message"."type" IS 'heartbeat_response: heartbeat_response
heartbeat_request: heartbeat_request
user_log: user_log
state_sync: state_sync
command: command';"""


MODELS_STATE = (
    "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"
    "18ZhVvbWfAGesfrt5fl/IGpYrw=="
)
