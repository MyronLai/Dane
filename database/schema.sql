CREATE DATABASE DaneBotSchema;

CREATE TABLE Guilds (
    guild_id BIGINT NOT NULL PRIMARY KEY,
    cmd_prefix VARCHAR(1) NOT NULL DEFAULT '!',
    role_on_join BIGINT NOT NULL DEFAULT 0,
    mute_role  BIGINT NOT NULL DEFAULT 0
)

CREATE TABLE Users (
    client_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    joinDate DATE NOT NULL,
    PRIMARY KEY (client_id, guild_id)
)

CREATE TABLE UserLevelData (
    client_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    client_xp INT NOT NULL DEFAULT 0,
    client_level INT NOT NULL DEFAULT 1,
    PRIMARY KEY (client_id, guild_id)
)