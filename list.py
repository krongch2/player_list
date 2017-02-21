from html.parser import HTMLParser
import codecs
import re
import urllib.request

s = []
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        # s.append('Start tag: {}'.format(tag))
        for attr in attrs:
            if attr[0] == 'onclick':
                s.append('*'*120 + '\n     attr: {}'.format(attr))
            else:
                s.append('     attr: {}'.format(attr))

    def handle_endtag(self, tag):
        pass
        # s.append('End tag  : {}'.format(tag))

    def handle_data(self, data):
        if data.strip():
            s.append('Data     : {}'.format(data))

    def handle_comment(self, data):
        s.append('Comment  : {}'.format(data))

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        s.append('Named ent: {}'.format(c))

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        s.append('Num ent  : {}'.format(c))

    def handle_decl(self, data):
        s.append('Decl     : {}'.format(data))

game_id = 480650
members = 'http://steamcommunity.com/games/{}/members?p={{}}'.format(game_id)
page = 1
players = []
while page < 31:
    with urllib.request.urlopen(members.format(page)) as response:
        html = response.read().decode("utf-8")
        title = re.search('<h1><a id="topNameLink" href=".+">(.+)</a></h1>', html).group(1)
        game_logo = re.search('<img src="(http://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/.+\.jpg)" border="0" />', html).group(1)
        h = '\n'.join(html.split('member list')[1].split('\n')[1:-1])
    print('Page {}'.format(page))
    parser = MyHTMLParser()
    parser.feed(h)
    output = '\n'.join(s)
    for player_data in output.split('\n' + '*'*120 + '\n')[1:]:
        if title in player_data:
            p = {}
            p['username'] = ''
            for line in player_data.split('\n'):
                match_profile = re.search("attr: \('href', '(.+)'\)", line)
                match_image = re.search("attr: \('src', '(.+)'\)", line)
                match_username = re.search("Data     : (.+)", line)
                if match_profile:
                    p['url_profile'] = match_profile.group(1)
                if match_image:
                    p['url_image'] = match_image.group(1)
                if not p['username'] and match_username:
                    p['username'] = match_username.group(1)
            p['title'] = title
            if not p in players:
                players.append(p)
    page += 1

template_player = """            <div onClick="top.location.href='{url_profile}'" class="friendBlock_in-game officerBlock">
                <div class="friendBlockIcon">
                    <div class="iconHolder_in-game"><div class="avatarIcon"><a href="{url_profile}"><img src="{url_image}" /></a></div></div>
                </div>
                <p><a class="linkFriend_in-game" href="{url_profile}">{username}</a><br />
                <span class="friendSmallTextO"><span class="linkFriend_in-game">In-Game<br/>{title}</span></span></p>
            </div>
"""
html_players = []
for p in players:
    html_players.append(template_player.format(**p))

with codecs.open('template.html', 'r', encoding='utf-8') as f:
    template_all = f.read()

with codecs.open('player_list.html', 'w', encoding='utf-8') as f:
    f.write(template_all.replace('Insert Member List', '\n'.join(html_players)).
    	replace('Insert Number', str(len(players))).
    	replace('Insert Game Title', title).
    	replace('Insert Game ID', str(game_id)).
    	replace('Insert Game Logo', game_logo))
