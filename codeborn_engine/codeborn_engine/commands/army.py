from typing import Any
from structlog import BoundLogger

from codeborn_shared.model import Army, Location, Message, Unit

from codeborn_engine.agents import BotAgent
from codeborn_engine.commands import Router, error_response, success_response

router = Router()


@router.route('move')
async def move(message: Message, agent: BotAgent, logger: BoundLogger) -> dict[str, Any]:
    """Handle command messages received from bots.

    ```
    {
        'army_gid': 9db4e912-715d-4e28-8246-c90b3695fbc0,
        'location': {
            'x': 1,
            'y': 2
        }
    }
    ```
    """
    army = await Army.get_or_none(
        gid=message.payload['army_gid'],
        bot=agent.bot
    ).prefetch_related('units', 'location')

    if army is None:
        return error_response('Army not found')

    new_location = await Location.get_or_none(**message.payload['location'])

    if new_location is None:
        return error_response('Location not found')

    if army.location == new_location:
        return error_response('Already at destination')

    if not army.location.is_adjacent(new_location):
        return error_response('Destination not adjacent')

    for unit in army.units:
        if unit.stamina < new_location.terrain.movement_cost:
            return error_response('Not enough stamina')

    for unit in army.units:
        unit.stamina -= new_location.terrain.movement_cost
        await unit.save(update_fields=['stamina'])

    army.location = new_location
    await army.save(update_fields=['location_id'])

    return success_response(
        army=await army.dump(),
        location=await new_location.dump()
    )


@router.route('split')
async def split(message: Message, agent: BotAgent, logger: BoundLogger) -> dict[str, Any]:
    """Handle command messages received from bots.

    ```
    {
        'army_gid': 9db4e912-715d-4e28-8246-c90b3695fbc0,
        'units': {
            '5849091c-cf5c-46be-99a8-9619fb661751': 5,
            'ccfd535c-f894-4cf5-9e8e-b32261a83490': 2
        }
    }
    ```
    """
    army = await Army.get_or_none(
        gid=message.payload['army_gid'],
        bot=agent.bot
    ).prefetch_related('units', 'location')

    if army is None:
        return error_response('Army not found')

    if not any(message.payload['units'].values()):
        return error_response('No units to split')

    old_units = {unit.gid: unit.count for unit in army.units}

    for unit_gid, count in message.payload['units'].items():
        if count <= 0:
            return error_response(f'Invalid count for unit {unit_gid}')

        orig_unit = next((u for u in army.units if str(u.gid) == unit_gid), None)
        if orig_unit is None:
            return error_response(f'Unit {unit_gid} not found in army')

        if orig_unit.count < count:
            return error_response(f'Not enough units of type {unit_gid}')

        old_units[orig_unit.gid] -= count

    if all(count == 0 for count in old_units.values()):
        return error_response('Cannot split all units from army')

    new_army = Army(bot=agent.bot, location=army.location)
    await new_army.save()

    # Remove units from original army
    for unit_gid, count in old_units.items():
        orig_unit = next(u for u in army.units if u.gid == unit_gid)

        if orig_unit.count != count:
            if count == 0:
                await orig_unit.delete()
            else:
                orig_unit.count = count
                await orig_unit.save(update_fields=['count'])

        if new_count := message.payload['units'].get(str(unit_gid), 0):
            new_unit = Unit(
                army=new_army,
                type=orig_unit.type,
                count=new_count,
                stamina=orig_unit.stamina
            )
            await new_unit.save()

    await new_army.fetch_related('units', 'location')

    return success_response(
        orig=await army.dump(),
        new=await new_army.dump()
    )


@router.route('merge')
async def merge(message: Message, agent: BotAgent, logger: BoundLogger) -> dict[str, Any]:
    """Handle command messages received from bots.

    ```
    {
        'armies': [
            '5849091c-cf5c-46be-99a8-9619fb661751',
            'ccfd535c-f894-4cf5-9e8e-b32261a83490'
        ]
    }
    ```
    """
    armies_gids = set(message.payload['armies'])

    if len(armies_gids) < 2:
        return error_response('At least two armies required to merge')

    armies = []
    for army_gid in armies_gids:
        army = await Army.get_or_none(
            gid=army_gid,
            bot=agent.bot
        ).prefetch_related('units', 'location')

        if army is None:
            return error_response(f'Army {army_gid} not found')

        armies.append(army)

    target_army = armies[0]
    merged_armies = armies[1:]

    for army in merged_armies:
        if army.location != target_army.location:
            return error_response('All armies must be in the same location to merge')

        for unit in army.units:
            target_unit = next((u for u in target_army.units if u.type == unit.type), None)
            if target_unit is None:
                unit.army = target_army
                await unit.save(update_fields=['army_id'])
            else:
                total_count = target_unit.count + unit.count
                target_unit.stamina = (
                    (target_unit.stamina * target_unit.count) +
                    (unit.stamina * unit.count)
                ) / total_count
                target_unit.count = total_count
                await target_unit.save(update_fields=['count', 'stamina'])
                await unit.delete()
        await army.delete()
    await target_army.fetch_related('units', 'location')
    return success_response(army=await target_army.dump())
