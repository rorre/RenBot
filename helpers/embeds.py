import discord, aiohttp, config, osuapi

APIHandler = osuapi.APIWrapper(config.osu_token)

STAT_DICT = {
    0 : "Pending",
    1 : "Accepted",
    2 : "Modding",
    3 : "Done",
    4 : "Rejected"
}

async def generate_request_embed(**kwargs):
    beatmapset = await APIHandler.get_beatmaps(**kwargs)
    beatmap = beatmapset[0]
    embed = discord.Embed(title="**Mod Request**")

    embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap.beatmapset_id}l.jpg")
    embed.set_author(name=beatmap.creator, icon_url=f"https://a.ppy.sh/{beatmap.creator_id}?.png")
    embed.set_footer(text="Status: Pending")

    embed.add_field(name="Map Name", value="`{0.artist} - {0.title}`".format(beatmap), inline=True)
    embed.add_field(name="Diff count", value=f"`{len(beatmapset)}`", inline=True)

    return embed

async def generate_status_embed(status, reason="", **kwargs):
    beatmapset = await APIHandler.get_beatmaps(**kwargs)
    beatmap = beatmapset[0]
    embed = discord.Embed(title="**Mod Status**")

    embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap.beatmapset_id}l.jpg")
    embed.set_author(name=beatmap.creator, icon_url=f"https://a.ppy.sh/{beatmap.creator_id}?.png")
    embed.set_footer(text="Status: " + STAT_DICT[status])

    embed.add_field(name="Map Name", value="`{0.artist} - {0.title}`".format(beatmap), inline=True)
    embed.add_field(name="Diff count", value=f"`{len(beatmapset)}`", inline=True)

    if status == 4:
        embed.add_field(name="Reason", value=reason)

    return embed
