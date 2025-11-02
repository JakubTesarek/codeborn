from codeborn.config import ArmyGeneratorConfig
from codeborn.model import Army, Bot, Location, Unit


async def starting_army(bot: Bot, location: Location, config: ArmyGeneratorConfig) -> None:
    """Create and persist a complete starting army for a bot."""
    army = await Army.create(bot=bot, location=location)
    await Unit.bulk_create(
        [Unit(army=army, type=unit_type, count=count) for unit_type, count in config.starting_units.items()]
    )
