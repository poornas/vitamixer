import bs4, os ,requests,time , io
from urllib.parse import urljoin	

def get_sitemap(): 
	if os.path.isfile('sitemap.text'):
		return

	smap = open("sitemap.xml","r")
	sitemap = bs4.BeautifulSoup(smap)
	with open('sitemap.text', 'w') as f:
		for line in sitemap.find_all('loc'):
			for string in line.stripped_strings:
				if string.startswith('https://www.vitamix.com/Recipes/'):
					f.write(string + '\n')


def make_recipe_folder():
	cwd = os.getcwd() + os.sep
	folder,subfolder = 'vitamix_folder', "css"
	print(cwd)
	try:
		if not os.path.isdir(cwd + folder):
			os.mkdir(cwd + folder)
		if not os.path.isdir(cwd + folder + os.sep + subfolder):
			os.mkdir(cwd + folder + os.sep + subfolder)
	except Exception as e:
		raise Exception(str(e))

def get_stylesheets():
    '''
    Get the stylesheets needed to display the pages properly.
    '''
    ## Get the first URL from the sitemap (assume all the pages are the same)
    with open('sitemap.text', 'r') as f:
        url = f.readline()
    url = url.strip('\n')
    print("???",url)
    if not url:
        raise Exception('No urls found in sitemap!')

    page = None

    for attempt in range(1, 4):

        page = requests.get(url)
        try:
            page.raise_for_status()
            break
        except requests.RequestException:
            time.sleep(attempt*10)

    if not page:
        raise Exception("Couldn't retrieve page: " + url)
    #print(page.text)
    soup = bs4.BeautifulSoup(page.text)
    sheets = []

    ## Get the sheets' urls
    for link in soup.find_all('link'):
        if 'stylesheet' in link.get('rel'):
        	print(link)
        	sheets.append(link.get('href'))

    ## Now get and save the sheets
    for link in sheets: 
    	#print(urljoin(url,link))
    	#link = 'http:' + link if link.startswith('//') else link
    	#print(link)
    	link = urljoin(url,link)
    	sheet = requests.get(link)
    	try:
    		sheet.raise_for_status()
    	except requests.RequestException:
    		continue
    	with io.open('vitamix_folder' + os.sep + 'css' + os.sep + link.split('/')[-1], 'w', encoding='utf-8') as css:
    		css.write(sheet.text)
    return sheets
def save_pages(css_links):
    '''
    Grab every web page in the BBC Food sitemap and
    save it as a local html file.
    '''
    cwd = os.getcwd()
    ## Build the new header data
    sep = os.sep
    for i, link in enumerate(css_links):
        css_links[i] = cwd + sep + 'vitamix_folder' + sep + 'css' + sep + link.split('/')[-1]

    ## Cycle through the sitemap grabbing each recipe
    with open('sitemap.text', 'r') as f:
        for line in f.readlines():
            line = line.strip('\n')
            page = requests.get(line)

            try:
                page.raise_for_status()
            except requests.RequestException:
                continue

            soup = bs4.BeautifulSoup(page.text)
            ## Update the header
            soup.head.clear()
            for link in css_links:
                new_link = soup.new_tag('link')
                new_link.attrs['rel'] = 'stylesheet'
                new_link.attrs['href'] = link
                soup.head.append(new_link)

            ## Remove unwanted elements
            soup.header.decompose()
            soup.footer.decompose()
            decomp = [soup.find('div', class_='upsell-link'),
                      soup.find('div', id='recipe-reviews'),
                      soup.find('div',class_="g-col print-hidden mtl"),
                      soup.find(['div','ul'], class_="print-hidden"),
                      soup.find('ul', id="SocialMediaButtons"),
                      soup.find('div', class_='related-recipes'),
                      soup.find('div', class_='recipe-questions')
                     ]

            for noscript in soup.find_all('noscript'):
                decomp.append(noscript)
            #for div in soup.find_all('div', class_='recipe-media'):
            #    decomp.append(div)
            
            for script in soup.find_all('script'):
                decomp.append(script)

            for ele in decomp:
                print(ele)
                if ele:
                    ele.decompose()

            ## Convert anchor tags into spans (links into text)
            tags = []
            for tag in soup.find_all('a'):
                tags.append(tag)
            for tag in tags:
                new_tag = soup.new_tag('span')
                new_tag.string = tag.text
                tag.replace_with(new_tag)

            ## Convert the soup back into html and save it to file
            html = soup.prettify()
            print(html)
            with io.open('vitamix_folder/' + line.split('/')[-1] + '.html', 'w', encoding='utf-8-sig') as html_page:
                html_page.write(html)
def main():
    get_sitemap()
    make_recipe_folder()
    stylesheets = get_stylesheets()
    save_pages(stylesheets)

if __name__ == '__main__':
    main()
