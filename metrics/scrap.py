from .models import ScholarProfile
import urllib.request
from bs4 import BeautifulSoup as soup 
import re
from django.utils import timezone
from .extract import rawauthorscounterurl, seleniumScraper, coAuthors, getnewCitations, getNpapersNcitationsTcitations
from metrics.newmetrics import Simple_Metrics

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"



class Scraper():
	def __init__(self, url, maxP, country):
		self.url= url
		self.maxP= maxP
		self.country= country

	def f(self):
		for i in range(0, 1000, 100):
			if (self.maxP <=i):
				pageSize = i
				break
                    									
		ncounter= 0
		bcounter= 0																					          
		Citations =[]  												# to count total numbers citations an author recieved. 
		title_list= []
		N_author_url= []
		author_names_list= []
		years= []

	
		for j in range(0,pageSize, 100):		#{ looping trough pages to get all the publications
			print ('1')
			S_url=self.url + "&cstart=" + str(j) +"&pagesize=100"
			print ('26')
			opener = AppURLopener()
			response = opener.urlopen(S_url)
			#with urllib.request.urlopen(S_url) as my_url:
			print ('2')
			page_html = response.read()	
			print ('3')


			response.close()	

			page_soup = soup(page_html, "html.parser")		

			if (j == 0):
				Name= page_soup.find('div', {'id': 'gsc_prf_in'})			# extracting the author's name
				scholar_name= Name.text
				print ('4')
			Years = page_soup.findAll('td', {'class': 'gsc_a_y'})
			print ('5')
			for year in Years:
				try:
					years.append(int(year.text))
				except:
					years.append(None)

			Titles = page_soup.findAll('td', {'class': 'gsc_a_t'})			# publication titles

			for title in Titles:
				Title = title.a.text
				x=Title.encode('utf-8')
				title_list.append(x.decode('utf-8', 'ignore'))				#title_list has all the titles
			print (title_list)
			info_page = page_soup.findAll('a', {'class' : 'gsc_a_at'})

			for author in info_page:										# loop to get all the pop up urls and then collect number of co-authors from there

				Author_names_link = author["data-href"]

				user=Author_names_link[53:65]

				n_input=Author_names_link[-12:]

				n_author_url="https://scholar.google.com.au/citations?user="+user+"&hl=en#d=gs_md_cita-d&u=%2Fcitations%3Fview_op%3Dview_citation%26hl%3Den%26user%3D"+user+"%26citation_for_view%3D"+user+"%3A"+n_input+"%26tzom%3D-330"

				N_author_url.append(n_author_url)

			authors_soup= page_soup.findAll('div', {'class': 'gs_gray'})

			less_authors_name=[]

			for a in authors_soup:
				less_authors_name.append(a.text)

			for i in range(0, len(less_authors_name), 2):
				author_names_list.append(less_authors_name[i])

			Citations_soup = page_soup.findAll('td', {'class': 'gsc_a_c'})
			
			for c in Citations_soup:
				p= c.text.encode('utf-8')
				r=p.decode('utf-8', 'ignore')
				q= re.findall('[0-9]+',r)
				Citations.append(q)
		
		CoauthsAndUrls= rawauthorscounterurl(author_names_list)

		url_to_counter= CoauthsAndUrls[1]

		n_author_names_list= CoauthsAndUrls[0]
		print ("d")

		coAuths= seleniumScraper(url_to_counter, N_author_url)
		print ('c')
		print (len(title_list), len(coAuths))

		number_of_coauths= coAuthors(n_author_names_list, coAuths)

		newCitations= getnewCitations(Citations)

		myvar= getNpapersNcitationsTcitations(number_of_coauths, newCitations, len(title_list))

		total_normalized_papers= myvar[0]

		normalized_citations= myvar[1]

		total_citations= myvar[2]

		q= ScholarProfile(author_name= Name.text, profile_url= self.url[-18:], publication_title= title_list,
		created_at= timezone.now())
		q.save()

		total_normalized_citations= int(sum(normalized_citations))
		#normalized_h_index= int(sum(n_citations)/len(title_list))

		nn_citations= normalized_citations[0:total_normalized_papers]
		nn_citations.sort(reverse= True)

		for i in nn_citations:
			ncounter+= 1
			print (ncounter, i)
			if(ncounter> i):
				normalized_h_index= ncounter-1
				break

		h_index= Simple_Metrics.h_index(newCitations)
		print (h_index)
		return (self.url)
		


