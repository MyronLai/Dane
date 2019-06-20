CREATE DATABASE DaneBotSchema;

CREATE TABLE Guilds (
    guild_id BIGINT NOT NULL PRIMARY KEY,
    guild_owner BIGINT NOT NULL,
    guild_name VARCHAR(128) NOT NULL,
    total_members INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL
);

CREATE TABLE Users (
    client_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    joinDate DATE NOT NULL,
    PRIMARY KEY (client_id, guild_id)
);

CREATE TABLE UserLevelData (
    client_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    client_xp INT NOT NULL DEFAULT 0,
    client_level INT NOT NULL DEFAULT 1,
    PRIMARY KEY (client_id, guild_id)
);

CREATE TABLE GuildConfigurables(
    guild_id BIGINT NOT NULL,
    auto_role BIGINT NOT NULL DEFAULT 0,
    mute_role BIGINT NOT NULL DEFAULT 0,
    bot_channel BIGINT NOT NULL DEFAULT 0,
    mod_channel BIGINT NOT NULL DEFAULT 0,
    member_log BIGINT NOT NULL DEFAULT 0,
    FOREIGN KEY (guild_id) REFERENCES Guilds(guild_id)
);
-- create a virtual column that is the sum of bans and kicks
CREATE TABLE GuildMemberInfractions(
    guild_id BIGINT NOT NULL,
    client_id BIGINT NOT NULL,
    banned TINYINT(1) NOT NULL DEFAULT 0,
    bans INT NOT NULL DEFAULT 0,
    kicks INT NOT NULL DEFAULT 0,
    total INT AS (bans+kicks) VIRTUAL NOT NULL,
    PRIMARY KEY (guild_id, client_id)
);@

CREATE TABLE VoiceChannelSubscriptions(
    channel_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    client_id BIGINT NOT NULL,
    isSubscribed TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (channel_id, client_id),
    FOREIGN KEY (guild_id) REFERENCES Guilds (guild_id)
);

CREATE TABLE VoiceChannelWhitelist(
    channel_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    client_id BIGINT NOT NULL,
    whitelisted_user BIGINT NOT NULL,
    isWhitelisted TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (channel_id, client_id, whitelisted_user),
    FOREIGN KEY (guild_id) REFERENCES Guilds (guild_id)
);

CREATE TABLE GuildHelpMsg(
    guild_id BIGINT NOT NULL PRIMARY KEY,
    help_msg JSON NOT NULL,
    color INT NOT NULL DEFAULT 16027458,
    title VARCHAR(255) NOT NULL,
    footer VARCHAR(255) NOT NULL
);
