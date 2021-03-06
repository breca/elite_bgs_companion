# Abandonware: New maintainers welcomed

# BGS Companion for Elite: Dangerous

![Example Build](https://i.imgur.com/vSCppvA.png)

![Carte Blanc Edition](https://i.imgur.com/cpI2vzF.png)

## Current Version: 0.94a

This application parses the player's journal file and extracts
information that pertains to the Elite Dangerous background simulation.

### Current feature list
* Tracking of (most) BGS related data generated by the player. This includes a set of logic to determine whether your actions have any effect given the current state of the system. i.e Cashing out Combat bonds in a system that is hosting Elections will not change influence and subsequently will not be recorded.
	
* Captures all types of transactions and collates it into a simple format where it can be easily pasted to Discord. For trading and smuggling, items traded are also captured and are also subject to the same logic checks. Starving people don't care about your Palladium.

* In addition to it's core function, the Companion also features a contextual advisor giving advice on what/what not to do given the current system state to increase your chosen factions influence or increase/decrease the system state. i.e If a system is having an Election, it'll tell you not to bother dropping your bounties there.

* It's got some clocks.

### Usage:

No configuration is required, just fire it up. When you're done playing,
or whenever you want, view your BGS stats, paste them into Discord and
then clear your data via the 'Clear and Exit' button.

### How it works:

The Companion app's primary function is to scrape and collate BGS data,
but it does some other stuff too.

Apart from providing some basic information about your status, this
application is mostly dormant until it detects that you have done some
sort of action that effects system influence - be it cashing combat
bonds, bounties, profitable trading, completing missions, donations,
etc. It then records that information into a database. It mashes all
this together so you can then bring up a report of all your data,
showing how much you raised, where and who for - and with a simple click
of a button, copies that data to your clipboard where it can be pasted
into the relevant Discord channel.

Your Elite Dangerous client automatically writes logs to
C:\Users\<yourname>\Saved Games\Frontier Developments\Elite Dangerous
When you first load the application it finds the NEWEST log there and
parses the entire thing. If you close it, it will remember where it
left off and keep collect data from the same journal, or if it detects
a new one, it will start parsing that.

## DISCLAIMER + TINFOIL NOTE

There is no authentication taking place here, this is all local. 
Block the application in your firewall if you're feeling paranoid.
Only data currently transmitted is for checking for updates and EDDN.
All that being said, use at your own risk, if this turns your PC into
molten slag, deletes all your cherished family photos, gives you brain
damage or makes you insult your grandmother, that's on you.

## License:

Copyright (C) 2018, CMDR Kalis for Radio Sidewinder.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

## Changelog:
	NOTE This branch is horrible and on life support. If you want to
	contribute, please use the development branch.

 * Version 0.94a
 
	Workaround to allows users to override path to their journals in settings.ini
	(i.e override_journal_location = Z:\Somewhere\Saved Games\Frontier Developments\Elite Dangerous)

 * Version 0.93a
 
	Hopefully fixes clock based CTD

 * Version 0.92a
 
 	Fixes hard-coded journal links.
	
 * Version 0.91a Hotfix
 
 	Fixes for data points/surface data point vouchers.
	
	Fixed Combat bonds being assigned the wrong faction.

 * Version 0.9a
 	Updated some events for Elite: Beyond.
	
	Now shows mission influence counts in mission copy/paste info
	Instead of tracking EVERY commodity, Trade data now lumps them
	into categories (all the game cares about).
	
	Additionally, trades with profit margins of over 700 credits
	are marked as 'High' trades, less than 700 as 'Low' Trades 
	as these have a larger/lesser affect.
	
	Trade losses are now tracked (not reported on yet), sorry..
	
	Altered window behaviour - child windows now appear next to
	parent window.
	
	Some groundwork to make future updates a bit more seamless.
	Anonymously sends updates to EDDN (enabled by default).
	
	Users can now opt-out of checking for updates at start of
	every session.
	
	Added options window and changed menu layout to accomodate.
 
 * Version 0.81a
	 Hotfix for lack of copy/paste and other issues brought about by
	 sloppy code refactoring and sleep deprivation.
	 
	 Attempted to fix update check from blocking. Not there yet. :(
	 
	 Improved location parsing.

 * Version 0.8a
	 Additional exception handling around database backend.
	 
	 Changed journal parsing behaviour - the application now remembers
	 it's position in the journal and will resume where it left off -
	 until it detects a new journal file, when it'll just use that
	 instead.
	 
	 Journal position and other stats are now inserted into the database
	 on exit.
	 
	 Added version checker.

 * Version 0.7a
	 Fixes for missing exploration/trade/smuggling faction data.
	 
	 Fixed ugly database call that potentially causes loss of
	 BGS data (Thanks Yojimbosan!).

 * Version 0.6a
  	 Cleaned up windows, added credits, added config file, modified
	 logging behaviour.

 * Version 0.5a - Here be dragons
	 Bugfixes maybe

 * Version 0.4a
 	 Tweaks to bounty/combat bond processing - now better reflects which
	 faction you're helping

 * Version 0.3a
	 Trade now determines whether you made a profit or not and reports
	 that info to the user in realtime.
	 
	 In addition to the normal BGS logic set, trade and smuggling are
	 now only recorded if a profit is made (and only the net profit
	 is added to the report).

 * Version 0.2a
	 Reimplemented missions. It's really hacky but it seems to work.
	 Whatever. Missions now track where you picked them up from (and
	 who) and adjusts BGS stats accordingly.
	 
	 Reformatted BGS stats page to better represent who/what you're
	 looking at.
	 
	 Now captures BGS data for other factions besides RSC.

 * Version 0.1a
	 Initial build.
