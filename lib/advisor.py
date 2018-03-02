from . import bucket
from . import log
import random

def advisor(runtime):
        data = "I've got nothing."
        if runtime['target_faction_state'] in ['War', 'CivilWar']:
            log.debug('Showing advisor text for War, CivilWar')
            data = runtime['target_faction'] + bucket.advisor_war + random.choice(bucket.flavour_war)
        elif runtime['target_faction_state'] in ['Outbreak']:
            log.debug('Showing advisor text for Outbreak')
            data = runtime['target_faction'] + bucket.advisor_outbreak + random.choice(bucket.flavour_outbreak)
        elif runtime['target_faction_state'] in ['Famine']:
            log.debug('Showing advisor text for Famine')
            data = runtime['target_faction'] + bucket.advisor_famine + random.choice(bucket.flavour_famine)
        elif runtime['target_faction_state'] in ['Boom']:
            log.debug('Showing advisor text for Boom')
            data = runtime['target_faction'] + bucket.advisor_boom + random.choice(bucket.flavour_boom)
        elif runtime['target_faction_state'] in ['CivilUnrest']: #REVIEW confirm CivilUnrest type
            log.debug('Showing advisor text for CivilUnrest')
            data = runtime['target_faction'] + bucket.advisor_unrest + random.choice(bucket.flavour_unrest)
        elif runtime['target_faction_state'] in ['Expansion']:
            log.debug('Showing advisor text for Expansion')
            data = runtime['target_faction'] + bucket.advisor_expansion + random.choice(bucket.flavour_expansion)
        elif runtime['target_faction_state'] in ['Election']: #REVIEW confirm election type
            log.debug('Showing advisor text for Election')
            data = runtime['target_faction'] + bucket.advisor_election + random.choice(bucket.flavour_election)
        elif runtime['target_faction_state'] in ['Retreat']: #REVIEW confirm Retreat type
            log.debug('Showing advisor text for Retreat')
            data = runtime['target_faction'] + bucket.advisor_retreat + random.choice(bucket.flavour_retreat)
        elif runtime['target_faction_state'] in ['Investment']: #REVIEW confirm Investment type
            log.debug('Showing advisor text for Investment')
            data = runtime['target_faction'] + bucket.advisor_investment + random.choice(bucket.flavour_investment)
        elif runtime['target_faction_state'] in ['Lockdown']: #REVIEW confirm Lockdown type
            log.debug('Showing advisor text for Lockdown')
            data = runtime['target_faction'] + bucket.advisor_lockdown + random.choice(bucket.flavour_lockdown)
        return data
