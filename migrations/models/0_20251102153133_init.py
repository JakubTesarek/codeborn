from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "location" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "x" INT NOT NULL,
    "y" INT NOT NULL,
    "terrain" VARCHAR(6) NOT NULL DEFAULT 'plains',
    CONSTRAINT "uid_location_x_fdd557" UNIQUE ("x", "y")
);
COMMENT ON COLUMN "location"."terrain" IS 'plains: plains\nforest: forest';
COMMENT ON TABLE "location" IS 'A location in the system.';
CREATE TABLE IF NOT EXISTS "user" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "max_bots" INT NOT NULL DEFAULT 1
);
COMMENT ON TABLE "user" IS 'A user in the system.';
CREATE TABLE IF NOT EXISTS "bot" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "entry_point" VARCHAR(100),
    "restart_requested" BOOL NOT NULL DEFAULT False,
    "last_heartbeat" TIMESTAMPTZ,
    "start_at" TIMESTAMPTZ,
    "enabled" BOOL NOT NULL DEFAULT True,
    "user_id" UUID NOT NULL REFERENCES "user" ("gid") ON DELETE CASCADE,
    CONSTRAINT "uid_bot_user_id_a1200f" UNIQUE ("user_id", "name")
);
COMMENT ON TABLE "bot" IS 'A bot account linked to a user.';
CREATE TABLE IF NOT EXISTS "army" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "bot_id" UUID NOT NULL REFERENCES "bot" ("gid") ON DELETE CASCADE,
    "location_id" UUID NOT NULL REFERENCES "location" ("gid") ON DELETE CASCADE
);
COMMENT ON TABLE "army" IS 'An army belonging to a user.';
CREATE TABLE IF NOT EXISTS "botmemory" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "data" JSONB NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "bot_id" UUID NOT NULL UNIQUE REFERENCES "bot" ("gid") ON DELETE CASCADE
);
COMMENT ON TABLE "botmemory" IS 'Memory record of a bot.';
CREATE TABLE IF NOT EXISTS "githubaccount" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "github_id" INT NOT NULL UNIQUE,
    "login" VARCHAR(100) NOT NULL,
    "access_token" VARCHAR(200) NOT NULL,
    "token_type" VARCHAR(50) NOT NULL,
    "scope" VARCHAR(200) NOT NULL,
    "avatar_url" VARCHAR(300),
    "last_update" TIMESTAMPTZ,
    "user_id" UUID NOT NULL UNIQUE REFERENCES "user" ("gid") ON DELETE CASCADE
);
COMMENT ON TABLE "githubaccount" IS 'A GitHub account linked to a user.';
CREATE TABLE IF NOT EXISTS "githubrepo" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "github_id" INT NOT NULL UNIQUE,
    "name" VARCHAR(200) NOT NULL,
    "full_name" VARCHAR(200) NOT NULL,
    "size" INT NOT NULL,
    "clone_url" VARCHAR(300) NOT NULL,
    "html_url" VARCHAR(300) NOT NULL,
    "remote_version" VARCHAR(10),
    "remote_sha" VARCHAR(40),
    "github_account_id" UUID NOT NULL REFERENCES "githubaccount" ("gid") ON DELETE CASCADE
);
COMMENT ON TABLE "githubrepo" IS 'A GitHub repository linked to an account.';
CREATE TABLE IF NOT EXISTS "message" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "type" VARCHAR(18) NOT NULL,
    "datetime" TIMESTAMPTZ NOT NULL,
    "response_to" UUID,
    "payload" JSONB NOT NULL,
    "bot_id" UUID NOT NULL REFERENCES "bot" ("gid") ON DELETE CASCADE
);
COMMENT ON COLUMN "message"."type" IS 'heartbeat_response: heartbeat_response\nheartbeat_request: heartbeat_request\nbot_log: bot_log\nstate_sync: state_sync\nmemory_download: memory_download\nmemory_upload: memory_upload\ncommand: command\ncommand_result: command_result';
COMMENT ON TABLE "message" IS 'A message associated with a user.';
CREATE TABLE IF NOT EXISTS "unit" (
    "gid" UUID NOT NULL PRIMARY KEY,
    "type" VARCHAR(14) NOT NULL,
    "stamina_snapshot" DOUBLE PRECISION NOT NULL DEFAULT 1,
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
)
