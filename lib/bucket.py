'''
This is a bucket where I keep all the fat text variables.
'''

bugtext = '''
This is a work in progress. The coder is lazy and terrible. Many mistakes were made. Oh god, the shame.

If you can, please do the following:

Step 1: Process any BGS data that actually worked because we're going to delete your database.
Step 2: Close the companion.
Step 3: Edit the 'settings.ini' in your RSC Companion directory and change the LogLevel to 'debug' (without quotes)
Step 4: Remove the 'companion.db' file under 'etc' in your RSC Companion directory.
Step 5: Re-run the RSC companion - it will play back over the journal file, hopefully reproducing the issue, creating a nice big fat log.

When it's done..

Send Kalis a PM on discord, including:

* Your OS, OS version (i.e Windows 10)
* Details of what happened / How to reproduce the bug

..attach the 'companion.log' file in your RSC Companion directory to your report.

Don't forget to change the 'settings.ini' back to 'info' as debug mode can get pretty spammy. And weird things happen.

Note that if you can't be bothered, at least send the standard log file as it will at least give us a hint where to look.
The standard logs are okay, but don't tell us too much.

Sorry for the inconvenience!
'''

req_text = '''
Hit up Kalis on discord.
'''

credtext = '''
Cobbled together in a drunken haze by CMDR Kalis for Radio Sidewinder.

Thanks to CMDR Azrael Nixx, CMDR R.Sharpe for being willing test bunnies.
Special thanks to:
CMDR Choopsha for thorough testing and feedback from inception.
CMDR Yojimbosan for 9th dan black belt bug reporting-fu and hosting.

And of course, thanks to Black Bart for establishing an awesome community,
finding the signal and sharing it with everyone.

And thanks to you, dear crew member, for helping make Radio Sidewinder great.
'''

advisor_famine = ' is experiencing a famine!\nTrade/Smuggle Food and supply exploration data to help out.'
flavour_famine = ['\nI\'ll take a half pepperoni, half margarita.',
                  '\nPick me up a soda, too.',
                  '\nHow much room do you need to grow fungi? As mushroom as possible.',
                  '\nHave you eaten today?',
                  '\nWhat if soy milk is just regular milk introducing itself in Spanish?',
                  '\nA burger sounds great right now.'
                  ]

advisor_unrest = ' is experiencing Civil Unrest here.\nRedeem combat bonds or bounty hunt to help restore order.'
flavour_unrest = ['\nPut your police hat on.',
                     '\nWhere are the cops when you need them?',
                     '\nTime to play cops and robbers.',
                     '\nIt\'s clobbering time(TM)!',
                     '\nDon\'t forget your badge and gun.',
                     '\nI AM the law!',
                     '\n..and to think I was two days from retirement.',
                     '\nDon\'t drop your donut.',
                     '\nHide yo\' kids, hide yo\' - EXCEPTION: ai_colloquial_subroutine.is_failed: $SIGNIFICANT_OTHER not found.'
                    ]

advisor_boom = ' is BOOMING!\nGreat for trading and a nice place to sell exploration data. Don\'t trade on the black market here, though.'
flavour_boom = ['\nSell ALL the things!',
                     '\nMakin\' Bacon.',
                     '\nShow me the money!',
                     '\nShut up and take my commodities!',
                     '\nBUY! BUY! No, SELL! SELL!',
                     '\nIs the bank of Zaonce too big to fail?',
                     '\nBulls make money, bears make money, pigs get slaughtered.',
                     '\nThe easiest way to make a million credits on a trade is to start with two million.',
                     '\nThe trend is your friend.'
                    ]

advisor_war = ' is at war here.\nRedeem combat bonds or bounty hunt to increase our influence in this system.'
flavour_war = ['\nIf you\'re not here to win it, you\'re in the wrong place.',
               '\nI love the smell of hydrogen fuel in the morning.',
               '\nShow me your war face!',
               '\nYour faction needs you!',
               '\nSignal save us all.',
               '\nI want YOU\nfor the RSC Navy!',
               '\nLet me hear your battle cry!',
               '\nWhat are you waiting for? Those medals don\'t earn themselves.'
               ]

advisor_outbreak = ' is having an outbreak in this system!\nTrade/Smuggle Medicines and supply Exploration data to help out.'
flavour_outbreak = ['\n*cough*',
                    '\n*wheeze*',
                    '\nCould I get a tissue as well?',
                    '\nSignal protect us.',
                    '\nHope you\'ve had your Vitamin C.',
                    '\nProbably get yourself checked while you\'re here.',
                    '\nThey think this is bad? Wait until they find out about Space Madness.',
                    '\nPoor buggers.',
                    '\nI had a virus once myself. But enough about my love life.'
                    ]

advisor_retreat = ' is in retreat!\nDo anything you can to re-establish our influence here.'
flavour_retreat = ['\nNo, really, anything helps.',
                    '\nDon\'t let the signal die!'
                    ]

advisor_election = ' is taking part in an election in this system.\nTry to help out however you like, but leave your guns holstered, combat actions won\'t help here.'
flavour_election = ['\nHo-hum.',
                    '\nToo much red tape for me.',
                    '\nDid you vote today?',
                    '\nPerhaps a few tonnes of tea will speed things along?'
                    ]

advisor_expansion = ' is expanding to another system.\nDo anything you like to help, but exploration data is especially nice.'
flavour_expansion = ['\nDust off your scanner array.',
                    '\nHonestly this is a good problem to have.',
                    '\nHey, can you help me pack?'
                    ]

advisor_investment = ' is promoting investment here so they can expand to another system.\nDo anything you like to help, but exploration data is especially nice.'
flavour_investment = flavour_expansion



advisor_lockdown = ' is in lockdown here!\nRedeem combat bounties here to help lift the lockdown. '
flavour_lockdown = ['\nI can\'t even use the mission computer here.',
                    '\nYour faction needs you!',
                    '\nI hope this is just paranoia.'
                    ]
