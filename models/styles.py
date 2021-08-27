import os

styles_files = os.listdir('styles')


#dark_green_style	= open('styles/dark-green.qss','r').read()
#white_blue_style	= open('styles/white-blue.qss','r').read()
#white_green_style	= open('styles/white-green.qss','r').read()
main_style			= open('styles/main.qss','r').read()

styles={

	'ui_style' : main_style
}


for file in styles_files:
	#dark_blue_style		= open('styles/dark-blue.qss','r').read()
	if file[:6] == 'style_':
		styles[file[6:].split('.')[0]]= open(os.path.join('styles',file),'r').read()


