from sc2 import AbilityId, UnitTypeId
from sc2.unit import Unit


class Evaluator:
    def __init__(self, bot):
        self.bot = bot

    def base_is_depleted(self, th: Unit) -> bool:  # evaluator
        mfs = self.bot.mineral_field.closer_than(15, th).filter(lambda x: x.mineral_contents > 0)
        return mfs.empty

    def should_build_scv(self) -> bool:  # decision
        room = 0
        for th in self.bot.townhalls.filter(lambda x: not self.base_is_depleted(x)):
            room += th.surplus_harvesters

        for ref in self.bot.structures(UnitTypeId.REFINERY).filter(lambda x: x.vespene_contents > 0):
            room += ref.surplus_harvesters

        # produce a few more harvesters than needed early on
        # so new bases can be saturated faster
        # don't build if orbitals should be prioritized first
        orbitals_needed = self.bot.townhalls.ready.amount - (self.bot.structures(UnitTypeId.ORBITALCOMMAND)
                                                             | self.bot.structures(UnitTypeId.ORBITALCOMMANDFLYING)
                                                             | self.bot.structures(UnitTypeId.PLANETARYFORTRESS)).amount
        if orbitals_needed > 0:
            for th in self.bot.townhalls.filter(lambda x: not x.is_idle):
                if (th.orders[0].ability.id == AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND
                        or th.orders[0].ability.id == AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS):
                    orbitals_needed -= 1

        # make sure i build workers if i lose them in the beginning
        return self.bot.workers.amount < 14 or (self.bot.workers.amount < 75 and room < 16
                                                and (not self.bot.construction_manager.building_requirements_satisfied(
                        UnitTypeId.ORBITALCOMMAND) or orbitals_needed <= 0))

    def should_build_supply(self) -> bool:  # evaluator
        # TODO: rewrite logic for need supply
        # my rate of production ?   my wanted rate ?  current rate ?
        below_supply_cap = self.bot.supply_cap < 200
        depots_in_production = self.bot.already_pending(UnitTypeId.SUPPLYDEPOT)
        early_game_condition = self.bot.supply_left < 6 and self.bot.supply_used >= 13 and depots_in_production < 1
        later_game_condition = self.bot.supply_left < 12 and self.bot.supply_cap >= 40 and depots_in_production <= 2

        # return below_supply_cap
        return below_supply_cap and (early_game_condition or later_game_condition)

    def should_morph_orbital(self):
        return True

    def should_morph_pf(self):
        return False

    def evaluate_economy(self):
        recommended_actions = []
        if self.should_build_scv():
            priority_tuple = (UnitTypeId.SCV, 1)
            recommended_actions.append(priority_tuple)
        if self.should_morph_orbital():
            priority_tuple = (AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND, 1)
            recommended_actions.append(priority_tuple)
        if self.should_morph_pf():
            priority_tuple = (AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS, 1)
            recommended_actions.append(priority_tuple)

        return recommended_actions

    def should_build_rax(self) -> bool:
        rax_count = len(self.bot.structures.of_type(UnitTypeId.BARRACKS))
        fact_count = len(self.bot.structures.of_type(UnitTypeId.FACTORY))
        starport_count = len(self.bot.structures.of_type(UnitTypeId.STARPORT))
        base_count = len(self.bot.bases)

        # TODO SOME LOGIC FOR PRODUCTION / INCOME / BASES  RATIO

        wanted_raxes = base_count * 2
        # logger.error(f"base_count {base_count}")
        # logger.error(f"rax_count {rax_count}")
        if rax_count < wanted_raxes:
            return True

        return False

    def evaluate_supply(self):
        recommended_actions = []
        if self.should_build_supply():
            priority_tuple = (UnitTypeId.SUPPLYDEPOT, 1)
            recommended_actions.append(priority_tuple)

        return recommended_actions
