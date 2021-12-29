import re, io, os, requests
from colorama import Fore
from colorama import Style
from bs4 import BeautifulSoup
from colorama import init
init()

URL = input('\nEnter URL: ')
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

regex = r'https://www(\d{1,3}).zippyshare.com/v/([a-zA-Z\d]{8})/file.html'
match = re.match(regex, URL)
if match:
	pre =  match.group(1)
	
for script in soup.find_all('script'):
	if 'document.getElementById(\'dlbutton\').href' in script.decode_contents():
		scscr = script.decode_contents()
		break
	else:
		scscr = None

scripts = io.StringIO(scscr).readlines()

_vars = {}
init_url = None
nump = None
file_url = None

for script in scripts:
	# Finding vars that contain numbers
	vars = re.compile(r'(var ([a-zA-Z]) = )([0-9%]{1,})(;)')
	found = vars.search(script)
	if found:
		_name = found.group(2)
		_value = found.group(3)
		_vars[_name] = _value
		
	# Finding url download button
	if script.strip().startswith('document.getElementById(\'dlbutton\')'):
		regex_n = r'(document\.getElementById\(\'dlbutton\'\)\.href = \")' \
							'(\/[a-zA-Z]\/[a-zA-Z0-9]{1,}\/)\"\+' \
							'(\([a-zA-Z] \+ [a-zA-Z] \+ [a-zA-Z] - [0-9]\))\+\"(\/.{1,})\";'
		rdl = re.compile(regex_n)
		res = rdl.search(script)
		if res:
			init_url = res.group(2)
			nump = res.group(3)
			enc_fname = res.group(4)
		else:
			raise ParserError('Invalid pattern')

fn = _vars.get('n').split('%')
fb = _vars.get('b').split('%')
n_ = int(fn[0]) % 2 
b_ = int(fb[0]) % 3 
z_ = int(_vars.get('z'))

final_num = n_ + b_ + z_ - 3 # isn't this cool? lol look at the js codes
file_url = "https://www{}.zippyshare.com{}{}{}".format(pre, init_url, final_num, enc_fname)
enc_fname = enc_fname.replace("/","")

print(f'Downloading \033[36m{enc_fname}{Style.RESET_ALL}')
#print(file_url)
os.system(f'aria2c {file_url} -x 16 -s 16 -j 16 -k 1M --file-allocation=none')


