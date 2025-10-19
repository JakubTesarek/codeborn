from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "location" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "x" INT NOT NULL,
    "y" INT NOT NULL,
    CONSTRAINT "uid_location_x_fdd557" UNIQUE ("x", "y")
);
COMMENT ON TABLE "location" IS 'A location in the system.';
CREATE TABLE IF NOT EXISTS "user" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "entry_point" VARCHAR(100) NOT NULL,
    "restart_requested" BOOL NOT NULL DEFAULT False,
    "last_heartbeat" TIMESTAMPTZ,
    "start_at" TIMESTAMPTZ
);
COMMENT ON TABLE "user" IS 'A user in the system.';
CREATE TABLE IF NOT EXISTS "army" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "location_id" UUID NOT NULL REFERENCES "location" ("gid") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "user" ("gid") ON DELETE CASCADE
);
COMMENT ON TABLE "army" IS 'An army belonging to a user.';
CREATE TABLE IF NOT EXISTS "message" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "type" VARCHAR(18) NOT NULL,
    "datetime" TIMESTAMPTZ NOT NULL,
    "payload" JSONB NOT NULL,
    "user_id" UUID NOT NULL REFERENCES "user" ("gid") ON DELETE CASCADE
);
COMMENT ON COLUMN "message"."type" IS 'heartbeat_response: heartbeat_response\nheartbeat_request: heartbeat_request\nuser_log: user_log';
COMMENT ON TABLE "message" IS 'A message associated with a user.';
CREATE TABLE IF NOT EXISTS "unit" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "type" VARCHAR(14) NOT NULL,
    "stamina_snapshot" DOUBLE PRECISION NOT NULL,
    "count" INT NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "army_id" UUID NOT NULL REFERENCES "army" ("gid") ON DELETE CASCADE,
    CONSTRAINT "uid_unit_type_2e00dc" UNIQUE ("type", "army_id")
);
COMMENT ON COLUMN "unit"."type" IS 'light_infantry: light_infantry\nheavy_infantry: heavy_infantry\nspearmen: spearmen\nlight_cavalry: light_cavalry\nheavy_cavalry: heavy_cavalry\narcher: archer\ncrossbowman: crossbowman';
COMMENT ON TABLE "unit" IS 'A unit in an army.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "dM3lrS7T18ZhVnZtvgTPWP328vw/LWlfSw=="
)
