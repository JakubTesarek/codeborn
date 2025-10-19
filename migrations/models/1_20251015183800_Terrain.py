from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "location" ADD "terrain" VARCHAR(6) NOT NULL DEFAULT 'plains';
        COMMENT ON COLUMN "message"."type" IS 'heartbeat_response: heartbeat_response
heartbeat_request: heartbeat_request
user_log: user_log
state_sync: state_sync
command: command';
        ALTER TABLE "unit" ALTER COLUMN "stamina_snapshot" SET DEFAULT 1;
        COMMENT ON COLUMN "location"."terrain" IS 'plains: plains\nforest: forest';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "unit" ALTER COLUMN "stamina_snapshot" DROP DEFAULT;
        COMMENT ON COLUMN "message"."type" IS 'heartbeat_response: heartbeat_response
heartbeat_request: heartbeat_request
user_log: user_log';
        ALTER TABLE "location" DROP COLUMN "terrain";"""


MODELS_STATE = (
    "eJztWu1O4zgUfRUrv2akWQSdDoOq1UptKZruAB1B2V0NRZGbuK1FYmdiB4gQ7762m+84nR"
    "RaaEX/0OR+OPbx9fXxNY+GS23ksL2274ZGCzwaBLpIPOTkn4ABPS+VSgGHY0cZwthizLgP"
    "LS5kE+gwJEQ2YpaPPY4pkZZtAqQxGCOHkikmU8ApgCBgyN+TLdjUEk0IeR3jgOBfATI5nS"
    "I+Q75wub4RYkxs9IBY/OrdmhOMHDs3tCm2ZQtKYfLQU8Krq/7xiTKVPRmbFnUCl2TMvZDP"
    "KEnsgwDbe9JJ6qaIIB9yZGcGTwLHiTCKRfM+CwH3A5R01k4FNprAwJEQGn9OAmJJ5ID6kv"
    "zT/MsogSq/UoAuElmUyAnBhEs0Hp/mw0oHraSG/FT3W/viw+fDj2qUlPGpr5QKEuNJOUIO"
    "564K2RRKh1pQ9sRcDtKC2yqhjQUptmk0xuDGoL0+kilyMpCXRC3j8l4Qk2t4cqsNPYlGGb"
    "0T6iM8Jd9RqDDsi35AYiENZlGCu4qa2VjUUmmaJ3x4n+S1bFiI4YlBIa4G2G1fdtvHPSMX"
    "dvHKWwFyp5mmthe9QirSIyjDcAyt23vo22ZVPBLMWRnWTuR28v0COQleFbEomtguNBUytE"
    "EziOSwKqvchluUQAKnqtfy2/JLxQDT8JJs8FVzk2y01+AnILYHmADBKgALGUeuhpwsstQw"
    "k2vjQWpC42bHUV6dozyUgewTrsfxQYOijPaNXJSiS+Lnj8ZB82vz6PNh80iYqL4kkq8LEO"
    "2fDwuUJFwCqPA9A8WRLxsvw9WdQb9HAre0g+awy7gXEBSdXheChueIb7Ly6owULTD/HZGJ"
    "IAKMizbUbzH3VSDswgfTQWTKZ+L1cAGa/7Qv1FqeL2UqMvI8VZ9HiobUaIhfnS1YHBgxeu"
    "EeHB94Ny+K32QPPkOMQbV8SltwrFq4A7sZoxobcGQOIGPUwhJ+cI/5rLpKUMdjVyrYhG1Y"
    "ofHcjBn5vl661C5VY4agz8cIclOM2xOooRYoy0YkKxPflNm0JBoRdXBz6LQF4qeRBIAjk4"
    "XEaoH0eUQs6oo1ardA9PCctHxwVCMvHxxVJmapym+EYrIRx65mXo8jjX6dZP0Kcxqr9rI2"
    "G5uMdUgO+2e9y2H77IfsucvYL0cB0h72pKahpGFBWtoOk0bAv/3hNyBfwc/Bea+48BK74U"
    "950DdgwKlJ6L0J7eywY3Esys2iB0OHQk2i+/tycK6fwIxLYf7EGZaSaxtb/BNwMOM3ayM0"
    "adobB9jhgrvsyc+uKfNJLHITGq+LD2ft/4pLpns66BRnSjbQ2RUBd0XAtykCVvPnddJHVd"
    "HScMe40lVNHIPYogZrlLayEAPnd0Y6mqgz0RZqYqqhrrV25ZodT3wOT3TwdMZNTCaQcD9s"
    "gfy74od3YUaffxcs0BNs0UVEcMDoaUTmbVjwDjppk9Fr3GKizb2OCPQtEeAtMP8VbNKnjI"
    "3pvVi3glGmL89ilc06rLJZzSqbRVYpJtfFBJqMQI/NKNckeEE+KgpTOudCOEyk97oC4mBv"
    "fy0r6nhw1TntgR8XvW7/sh9xkYRGKqUUCQGeZ/6LXvu0AKxFA6JBs7LIl9i/10Jf4MlTiG"
    "1CDWqLTzh5z+084xg+gvaAOGG0m2zJmSfa+DJHnqjzuUJhuCTvzrjseHfyTz8v5N3bV2wt"
    "8u5MWGwU72aKz5Z5d3TQWcC7Y4s6vFvY/v6qtMJqV5XdBLaNJOE0PYp1xECSbj2kBbc35t"
    "v1d7Q8c93fr0Nd9/eruavU5SmDvDODflLlRZpI7VDqIEj0yGr9C/iORQPrAli/2FcRpZ3B"
    "4DRHDzr9YQHYq7NOTyD+Mc9ky7zMgYybSUV9WW5W9l4BP4sSwGZs7JtEx2qVoOcxv/xUZv"
    "12k/gGk7i7p69/T58N+Oja+oUgZK7gtwiHdRLfNvKxNTM01DfSLCS/MLX5Hf2thuEFxFbH"
    "ayurM1pWqynNREntZXR2E+oy1Sz2DvlM+0/N1Qw247Kd7LXx5UsN9iqsKtmr0uWJlVwaS4"
    "AYmW8ngGuh/+KLHOnOUtV36RmXt7pLXxuHWdmt+RI8Y/Xby9P/Uy3mKg=="
)
