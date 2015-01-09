# Hora
Dinky little script to keep track of TV show airdates by leveraging [TheTVDB.com](http://thetvdb.com) favorites

Usage
=====
1. [Create an account](http://thetvdb.com/?tab=register) on TheTVDB.com
2. Add the shows you want to track to your TVDB favorites 
3. Get your "Account Identifier" from the [accounts page](http://thetvdb.com/?tab=userinfo) and add it to the config file at: _/settings/accounts/account[@name="TheTVDB"]/id_
4. Regeister a [new API Key](http://thetvdb.com/?tab=apiregister) and add the key to the config file at: _/apis/api["@name=TheTVDB"]/key_
5. Run the script: ```./hora.py config.xml```
